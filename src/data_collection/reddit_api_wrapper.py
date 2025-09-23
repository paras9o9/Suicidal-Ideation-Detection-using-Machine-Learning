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

### SI keywords filtering for r/depression ###
def contains_si_keywords(text):
    si_keywords = [
        # Direct SI expression
        # (1st Batch)
        'kill myself', 'end my life', 'suicidal', 'suicide', 'don\'t want to live', 'no reason to live', 'plan to die', 'take my own life', 'end it all', 'better off dead', 'goodbye note', 'final message', 'attempted suicide',
        # (2nd Batch)
        'unalive', 'cease to exist', 'don\'t want to exist', 'sleep forever',
        'not wake up', 'leave this world', 'no longer here',
        
        # Need phrase-based matching
        'life isn\'t worth it', 'tired of living', 'better off without me',
        'nobody needs me', 'waste of space', 'ruin everything',    

        # High-intent phrases
         'planned everything', 'set date', 'can\'t be stopped',
         'end tonight', 'won\'t be here tomorrow',

        # Preparation behaviors
        'goodbye message', 'giving away things', 'delete account',
        'last post', 'last day', 'this is it',

        # Hindi phrases (excellent addition)
        'chhod dena hai sab', 'khatam karna hai', 'ab aur nahi',
        'mar jaunga', 'mar jaungi', 'jaane ka time aa gaya'

        ]

    text_lower = text.lower()
    for keyword in si_keywords:
        if keyword in text_lower:
            return True
    return False

### Assigning preliminary label based on subreddit and content ###
def get_preliminary_label(subreddit_name, title, text):
    if subreddit_name == 'SuicideWatch':
        return 'SI'
    elif subreddit_name == 'depression':
        if contains_si_keywords(title + " " + text):
            return 'SI_EXCLUDED'
        return 'MH'
    elif subreddit_name in ['BPD', 'Vent']:
        return 'MH'
    elif subreddit_name in ['college', 'collegeIndia', 'TwentiesIndia']:
        return 'NEU'
    elif subreddit_name in ['teenagers', 'suicidebywords', 'memes', 'darkjokes', 
                            'IndianDankMemes', 'dankmemes', '2meirl4meirl']:
        return 'HUMOR'
    else:
        return 'UNKNOWN'

### Collecting meme image urls from submission
def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def download_image(url, subreddit_name, post_id, image_dir='data/images'):
    os.makedirs(image_dir, exist_ok=True)
    filename = f"{subreddit_name}_{post_id}{os.path.splitext(url)[-1]}"
    filepath = os.path.join(image_dir, filename)
    try:
        response = requests.get(url)
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
            print("Extracted {len(text)} characters")
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
def collect_subreddit_posts(reddit, subreddit_name, limit=10, delay=0.5):
    posts = []

    min_lengths = {
        'SuicideWatch': 100,
        'depression': 200,
        'Vent': 200,
        'college': 80,
        'collegeIndia': 80,
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

    try:
        print(f"\n Collecting from r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)

        for submission in subreddit.hot(limit=limit):
            has_valid_text = (
                submission.selftext and 
                len(submission.selftext.strip()) >= min_length and 
                submission.selftext.strip() not in ['[deleted]', '[removed]']
            )
            is_image_post = hasattr(submission, 'url') and is_image_url(submission.url)

            if not (has_valid_text or is_image_post):
                continue

            post_text_for_labeling = submission.selftext if submission.selftext else ""
            prelim_label = get_preliminary_label(subreddit_name, submission.title, post_text_for_labeling)
                
            if prelim_label == 'SI_EXCLUDED':
                print(f"Skipped SI post from r/depression: {submission.title[:50]}...")
                continue

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
                'collection_date': datetime.now().isoformat()
                }
            posts.append(post_data)
                

            print(f"[{prelim_label}] Title: {submission.title[:60]}...")
            if has_valid_text:
                print(f"Text: {submission.selftext[:80]}...")
            if meme_text:
                clean_meme_text = meme_text.replace('\n', ' ')[:80]
                print(f"Meme Text: {clean_meme_text}...")
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
                'script_version': '2.0'             
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
        'SI': ['SuicideWatch'],
        'MH': ['depression', 'BPD', 'Vent'],
        'NEU': ['college', 'collegeIndia', 'TwentiesIndia'],
        'HUMOR': ['teenagers', 'suicidebywords', 'memes', 'darkjokes', 
                  'IndianDankMemes', 'dankmemes', '2meirl4meirl']
    }

    all_subreddit = []

    for category, subs in target_subreddit.items():
        all_subreddit.extend(subs)


    all_collected_posts = {}

    for subreddit_name in all_subreddit:
        posts = collect_subreddit_posts(reddit, subreddit_name, limit=50)

        if posts:
            filepath = save_posts_to_json(posts, subreddit_name)
            all_collected_posts[subreddit_name] = {
                'count': len(posts),
                'file': filepath,
                'labels': {}
            }

            for post in posts:
                label = post['prelim_label']
                all_collected_posts[subreddit_name]['labels'][label] = \
                    all_collected_posts[subreddit_name]['labels'].get(label, 0) + 1             
        else:
            all_collected_posts[subreddit_name] = {
                'count': 0,
                'file': None,
                'labels': {}
            }

        time.sleep(2)

    print("\n" + "="*70)
    print("COLLECTION SUMMARY")
    print("="*70)

    total_posts = 0
    images_posts = 0
    label_totals = {}

    for subreddit, info in all_collected_posts.items():
        if info['file']:
            print(f"r/{subreddit}: {info['count']} posts => {info['file']}")
            for label, count in info['labels'].items():
                print(f" {label}: {count} posts")
                if label in label_totals:
                    label_totals[label] += count
        else:
            print(f"r/{subreddit}: {info['count']} posts (no file created)")
        total_posts += info['count']

    for subreddit_name in all_subreddit:
        if all_collected_posts[subreddit_name]['file']:
            pass

    print(f"Label Distribution:")
    for label, count in label_totals.items():
        print(f" {label}: {count} posts")

    print(f"Total post collected: {total_posts}")
    print("Data collection complete!")

if __name__ == "__main__":
    main()