import praw
import requests
from PIL import Image
import pytesseract
import os, time, json
from datetime import datetime
from dotenv import load_dotenv
from prawcore import ResponseException, RequestException

### Loading environment var ###
load_dotenv()

### Authenticating Reddit API ###
def get_reddit_instance():
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        reddit.user.me()
        print("Reddit authentication successful")
        return reddit
    
    except Exception as e:
        print(f"Reddit authentication failed: {e}")
        return None

### SI keywords filtering for r/depression ###
def contains_si_keywords(text):
    si_keywords = {
        # Direct/Active SI expressions
        'direct': [
            'kill myself', 'end my life', 'suicidal', 'suicide', 'take my own life', 
            'end it all', 'attempted suicide', 'plan to die', 'commit suicide',
            'killing myself', 'hang myself', 'shoot myself', 'overdose'
        ],
        
        # Passive SI expressions (death wishes without active plan)
        'passive': [
            'don\'t want to live', 'no reason to live', 'better off dead',
            'wish i was dead', 'wish i were dead', 'hope i don\'t wake up',
            'don\'t want to exist', 'don\'t want to be here', 'no longer here',
            'cease to exist', 'sleep forever', 'not wake up', 'leave this world',
            'want to disappear', 'just disappear', 'don\'t see the point',
            'no point in living', 'life has no meaning', 'no purpose', 
            'tired of living', 'exhausted from living', 'can\'t keep living'
        ],
        
        # Indirect/coded expressions
        'indirect': [
            'unalive', 'final message', 'goodbye note', 'last post',
            'this is it', 'end tonight', 'won\'t be here tomorrow',
            'just want to be done', 'want it all to stop', 'can\'t do this anymore',
            'can\'t keep doing this', 'give up on life', 'checked out',
            'want to go home', 'ready to go', 'time to go'
        ],
        
        # Worthlessness and burden themes (strong SI indicators)
        'burden': [
            'life isn\'t worth it', 'better off without me', 'burden to everyone',
            'nobody needs me', 'waste of space', 'ruin everything', 'world without me',
            'everyone would be better', 'shouldn\'t exist', 'mistake to be born'
        ],
        
        # Preparation/planning behaviors
        'preparation': [
            'planned everything', 'set date', 'can\'t be stopped',
            'giving away things', 'delete account', 'last day',
            'made arrangements', 'got everything ready', 'writing goodbye'
        ],
        
        # Regional language phrases
        'hindi': [
            'chhod dena hai sab', 'khatam karna hai', 'ab aur nahi',
            'mar jaunga', 'mar jaungi', 'jaane ka time aa gaya',
            'jee nahi sakta', 'zinda nahi rehna'
        ]
    }

    text_lower = text.lower()
    matched_categories = []

    for category, keywords in si_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched_categories.append(category)
                break
    return len(matched_categories) > 0, matched_categories

def calculate_si_confidence(text, title, subreddit_name):
    combined_text = f"{title} {text}".lower()
    has_si, categories = contains_si_keywords(combined_text)

    if not has_si:
        return 0.0

    weights = {
        'direct': 1.0,
        'preparation': 0.95,
        'passive': 0.7,
        'burden': 0.6,
        'indirect': 0.5,
        'hindi': 0.8
    }

    scores = [weights.get(cat, 0.5) for cat in categories]
    base_score = max(scores) if scores else 0.0

    subreddit_multipliers = {
        'SuicideWatch': 1.0,
        'selfHarm': 0.9,
        'AdultSelfHarm': 0.9,
        'mentalhealth': 0.8,
        'MentalHealthSupport': 0.8,
        'SelfHate': 0.85,
        'depression': 0.7
    }

    multiplier = subreddit_multipliers.get(subreddit_name, 0.5)
    confidence = min(base_score * multiplier, 1.0)

    return round(confidence, 2)

def contains_graphic_selfharm(text):

    nssi_only_keywords = [
        'cutting myself', 'burned myself', 'scratched myself',
        'hit myself', 'pulled my hair', 'bruised myself',
        'harm scars', 'self injury tools', 'cutting tools',
        'fresh cuts', 'blood from'
    ]

    text_lower = text.lower()

    has_nssi = any(keyword in text_lower for keyword in nssi_only_keywords)
    has_si, _ = contains_si_keywords(text)

    return has_nssi and not has_si

### Assigning preliminary label based on subreddit and content ###
def get_preliminary_label(subreddit_name, title, text):

    combined_text = f"{title} {text}"

    si_confidence = calculate_si_confidence(text, title, subreddit_name)

    if subreddit_name in ['selfharm', 'AdultSelfHarm']:
        if contains_graphic_selfharm(combined_text):
            return 'NSSI_FILTERED', 0.0
        
    if subreddit_name == 'SuicideWatch':
        return 'SI', 1.0

    if subreddit_name in ['selfharm', 'AdultSelfHarm']:
        if si_confidence >= 0.6:
            return 'SI', si_confidence
        else:
            return 'MH', 0.5

    elif subreddit_name in ['mentalhealth', 'MentalHealthSupport', 'SelfHate']:
        if si_confidence >= 0.6:
            return 'SI', si_confidence
        else:
            return 'MH', 0.5
        
    elif subreddit_name == 'depression':
        if si_confidence >= 0.5:
            return 'SI_EXCLUDED', si_confidence
        return 'MH', 0.3
    
    elif subreddit_name in ['BPD', 'Vent']:
        if si_confidence >= 0.6:
            return 'SI_CANDIDATE', si_confidence
        return 'MH', 0.3

    elif subreddit_name in ['college', 'collegeIndia', 'TwentiesIndia']:
        return 'NEU', 0.0

    elif subreddit_name in ['teenagers', 'suicidebywords', 'memes', 'darkjokes', 
                            'IndianDankMemes', 'dankmemes', '2meirl4meirl']:
        return 'HUMOR', 0.0

    else:
        return 'UNKNOWN', 0.0

### Collecting meme image urls from submission
def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def download_image(url, subreddit_name, post_id, image_dir='data/images'):
    os.makedirs(image_dir, exist_ok=True)
    filename = f"{subreddit_name}_{post_id}{os.path.splitext(url)[-1]}"
    filepath = os.path.join(image_dir, filename)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def extract_text_from_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return ""
    try:
        print(f"Processing image: {os.path.basename(image_path)}")
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)

        os.remove(image_path)
        print(f"Deleted image after OCR: {os.path.basename(image_path)}")

        if text:
            print(f"Extracted {len(text)} characters")
        else:
            print("No text found in image")

        return text
    
    except Exception as e:
        print(f"OCR error for {image_path}: {e}")

        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Deleted problematic image: {os.path.basename(image_path)}")
        except Exception as del_e:
            print(f"Error deleting image: {del_e}")
        return ""

### Collecting subreddit posts ###
def collect_subreddit_posts(reddit, subreddit_name, limit=10, delay=0.5, sorting_modes=['hot', 'new']):
    posts = []

    min_lengths = {
        'SuicideWatch': 100,
        'depression': 200,
        'Vent': 200,
        'BPD': 150,
        # New SI-related subreddits
        'mentalhealth': 80,
        'MentalHealthSupport': 80,
        'selfharm': 100,
        'AdultSelfHarm': 100,
        'SelfHate': 100,
         # Neutral
        'college': 80,
        'collegeIndia': 80,
        'TwentiesIndia': 80,
        # Humor
        'teenagers': 30,
        'suicidebywords': 20,
        'memes': 10, 
        'darkjokes': 50, 
        'IndianDankMemes': 10,
        'dankmemes': 10,
        '2meirl4meirl': 20
    }

    min_length = min_lengths.get(subreddit_name, 50)
    seen_ids = set()

    try:
        print(f"\n Collecting from r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)

        for mode in sorting_modes:
            print(f"  Fetching '{mode}' posts...")
            
            if mode == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif mode == 'new':
                submissions = subreddit.new(limit=limit)
            elif mode == 'top':
                submissions = subreddit.top(time_filter='week', limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                if submission.id in seen_ids:
                    continue
                seen_ids.add(submission.id)
                
                has_valid_text = (
                    submission.selftext and 
                    len(submission.selftext.strip()) >= min_length and 
                    submission.selftext.strip() not in ['[deleted]', '[removed]']
                )
                is_image_post = hasattr(submission, 'url') and is_image_url(submission.url)

                if not (has_valid_text or is_image_post):
                    continue

                post_text_for_labeling = submission.selftext if submission.selftext else ""
                prelim_label_result = get_preliminary_label(subreddit_name, submission.title, post_text_for_labeling)
                
                if isinstance(prelim_label_result, tuple):
                    prelim_label, confidence = prelim_label_result
                else:
                    prelim_label = prelim_label_result
                    confidence = 0.0
                    
                if prelim_label in ['SI_EXCLUDED', 'NSSI_FILTERED']:
                    print(f"Filtered: {prelim_label} - {submission.title[:50]}...")
                    continue

                # Handle images
                meme_text = None
                if is_image_post:
                    image_file = download_image(submission.url, subreddit_name, submission.id)
                    if image_file:
                        meme_text = extract_text_from_image(image_file)

                post_text = submission.selftext if submission.selftext else ""

                post_data = {
                'id': submission.id,
                'title': submission.title,
                'text': post_text,
                'image_path': None,
                'meme_text': meme_text,
                'had_image': is_image_post,
                'subreddit': subreddit_name,
                'created_utc': submission.created_utc,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'url': submission.url,
                'text_length': len(post_text),
                'prelim_label': prelim_label,
                'si_confidence': confidence,
                'collection_mode': mode,
                'collection_date': datetime.now().isoformat()
                }
                posts.append(post_data)
                
                confidence_marker = f"[{confidence:.2f}]" if confidence > 0 else ""
                print(f"[{prelim_label}]{confidence_marker} Title: {submission.title[:60]}...")
                if has_valid_text:
                    print(f"  Text: {submission.selftext[:80]}...")
                if meme_text:
                    clean_meme_text = meme_text.replace('\n', ' ')[:80]
                    print(f"  Meme Text: {clean_meme_text}...")
                print("-" * 50)

                time.sleep(delay)
    except ResponseException as e:
        print(f"API Error for r/{subreddit_name}: {e}")
    except Exception as e:
        print(f"Unexpected error for r/{subreddit_name}: {e}")
    print(f"Collected {len(posts)} valid posts from r/{subreddit_name}")
    return posts

### Saving posts to JSON file ###
def save_posts_to_json(posts, subreddit_name, data_dir="data/raw"):
    if not posts:
        print("No posts to save.")
        return None
    
    try:
        now = datetime.now()
        data_dir = os.path.join(data_dir, now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"))
        os.makedirs(data_dir, exist_ok=True)

        timestamp = now.strftime('%H%M%S_%f')[:-3]
        filename = f"{subreddit_name}_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)

        data_to_save = {
            'collection_info': {
                'subreddit': subreddit_name,
                'post_count': len(posts),
                'collection_timestamp': now.isoformat(),
                'script_version': '3.0'             
            },
            'posts': posts
        }


        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(filepath)
        print(f"Saved {len(posts)} posts from r/{subreddit_name}")
        print(f"File: {filepath}")
        print(f"Size: {file_size/1024:.2f} KB")
        
        return filepath

    except Exception as e:
        print(f"Error saving posts: {e}")
        return None

### Main function to collect posts from multiple subreddit 
def main():
    reddit = get_reddit_instance()
    if not reddit:
        print("Cannot proceed without Reddit connection")
        return
    
    target_subreddit = {
        'SI': ['SuicideWatch', 'selfharm', 'AdultSelfHarm'],  # High SI probability
        'MH': ['depression', 'BPD', 'Vent', 'mentalhealth', 'MentalHealthSupport', 'SelfHate'],  # Mental health with SI screening
        'NEU': ['college', 'collegeIndia', 'TwentiesIndia'],
        'HUMOR': ['teenagers', 'suicidebywords', 'memes', 'darkjokes', 
                  'IndianDankMemes', 'dankmemes', '2meirl4meirl']
    }

    all_subreddit = []

    for category, subs in target_subreddit.items():
        all_subreddit.extend(subs)


    all_collected_posts = {}

    for subreddit_name in all_subreddit:

        sorting_modes = ['hot', 'new'] if subreddit_name in ['SuicideWatch', 'selfharm', 'AdultSelfHarm'] else ['hot']
        posts = collect_subreddit_posts(reddit, subreddit_name, limit=50, sorting_modes=sorting_modes)

        if posts:
            filepath = save_posts_to_json(posts, subreddit_name)
            all_collected_posts[subreddit_name] = {
                'count': len(posts),
                'file': filepath,
                'labels': {},
                'si_candidates': 0
            }

            for post in posts:
                label = post['prelim_label']
                all_collected_posts[subreddit_name]['labels'][label] = \
                    all_collected_posts[subreddit_name]['labels'].get(label, 0) + 1
                if label == 'SI_CANDIDATE':
                    all_collected_posts[subreddit_name]['si_candidates'] += 1

        else:
            all_collected_posts[subreddit_name] = {
                'count': 0,
                'file': None,
                'labels': {},
                'si_candidates': 0
            }

        time.sleep(2)

    print("\n" + "="*70)
    print("COLLECTION SUMMARY")
    print("="*70)

    total_posts = 0
    label_totals = {}
    total_si_candidates = 0

    for subreddit, info in all_collected_posts.items():
        if info['file']:
            print(f"\nr/{subreddit}: {info['count']} posts => {os.path.basename(info['file'])}")
            for label, count in info['labels'].items():
                print(f"  • {label}: {count} posts")
                label_totals[label] = label_totals.get(label, 0) + count
            
            if info['si_candidates'] > 0:
                print(f"{info['si_candidates']} posts need manual SI review")
                total_si_candidates += info['si_candidates']
        else:
            print(f"\nr/{subreddit}: {info['count']} posts (no file created)")
        total_posts += info['count']

    print("\n" + "="*70)
    print("LABEL DISTRIBUTION:")
    for label, count in sorted(label_totals.items()):
        percentage = (count / total_posts * 100) if total_posts > 0 else 0
        print(f"  {label}: {count} posts ({percentage:.1f}%)")
    
    if total_si_candidates > 0:
        print(f"\nMANUAL REVIEW NEEDED: {total_si_candidates} SI_CANDIDATE posts")
        print("   These posts show SI signals and should be manually validated.")

    print(f"\nTotal posts collected: {total_posts}")
    print("="*70)
    print("Data collection complete!")

if __name__ == "__main__":
    main()