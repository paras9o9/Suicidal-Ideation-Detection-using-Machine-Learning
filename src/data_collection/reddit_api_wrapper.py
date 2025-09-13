import praw
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
    elif subreddit_name == 'Vent':
        return 'MH'
    elif subreddit_name == ['college', 'collegeIndia']:
        return 'NEU'
    else:
        return 'UNKNOWN'

### Collecting subreddit posts ###
def collect_subreddit_posts(reddit, subreddit_name, limit=10, delay=0.5):
    posts = []

    min_lengths = {
        'SuicideWatch': 100,
        'depression': 200,
        'Vent': 200,
        'college': 80,
        'collegeIndia': 80
    }

    min_lengths = min_lengths.get(subreddit_name, 50)

    try:
        print(f"\n Collecting from r/{subreddit_name} (min_length: {min_lengths})...")
        subreddit = reddit.subreddit(subreddit_name)

        for submission in subreddit.hot(limit=limit):
            if (submission.selftext and len(submission.selftext.strip()) >= min_lengths and submission.selftext.strip() not in ['[deleted]', '[removed]']):

                prelim_label = get_preliminary_label(subreddit_name, submission.title, submission.selftext)
                
                if prelim_label == 'SI_EXCLUDED':
                    print(f"Skipped SI post from r/depression: {submission.title[:50]}...")
                    continue

                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'text': submission.selftext,
                    'subreddit': subreddit_name,
                    'created_utc': submission.created_utc,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'url': submission.url,
                    'text_length': len(submission.selftext),
                    'prelim_label': prelim_label,
                    'collection_date': datetime.now().isoformat()
                }
                posts.append(post_data)

                print(f"[{prelim_label}] Title: {submission.title[:60]}...")
                print(f"Text: {submission.selftext[:80]}...")
                print(f"Length: {len(submission.selftext)} chars")
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
        'NEU': ['college', 'collegeIndia', 'TwentiesIndia']
    }

    all_subreddits = []

    for category, subs in target_subreddit.items():
        all_subreddits.extend(subs)


    all_collected_posts = {}

    for subreddit_name in all_subreddits:
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

    print(f"Label Distribution:")
    for label, count in label_totals.items():
        print(f" {label}: {count} posts")

    print(f"Total post collected: {total_posts}")
    print("Data collection complete!")

if __name__ == "__main__":
    main()