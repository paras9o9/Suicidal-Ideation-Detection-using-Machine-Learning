import json
import os
from datetime import datetime
from collections import defaultdict
import random

def load_all_json_files(data_dir="data/raw"):
    """
    Load all JSON files from the data directory recursively
    """
    all_posts = []
    collection_files = []
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'posts' in data:
                            all_posts.extend(data['posts'])
                            collection_files.append(filepath)
                            print(f"✅ Loaded {len(data['posts'])} posts from {file}")
                except Exception as e:
                    print(f"❌ Error loading {file}: {e}")
    
    print(f"\n📊 Total files loaded: {len(collection_files)}")
    print(f"📊 Total posts before deduplication: {len(all_posts)}")
    return all_posts


def deduplicate_posts(posts):
    """
    Remove duplicate posts based on post ID
    Keeps the first occurrence
    """
    seen_ids = set()
    unique_posts = []
    duplicates = 0
    
    for post in posts:
        post_id = post.get('id')
        if post_id not in seen_ids:
            seen_ids.add(post_id)
            unique_posts.append(post)
        else:
            duplicates += 1
    
    print(f"\n🔍 Deduplication Results:")
    print(f"   Unique posts: {len(unique_posts)}")
    print(f"   Duplicates removed: {duplicates}")
    
    return unique_posts


def separate_by_label(posts):
    """
    Separate posts by their preliminary labels
    """
    categorized = defaultdict(list)
    
    for post in posts:
        label = post.get('prelim_label', 'UNKNOWN')
        categorized[label].append(post)
    
    return categorized


def calculate_quality_score(post):
    """
    Calculate quality score for prioritizing posts
    Higher scores = higher priority for inclusion
    """
    score = 0
    
    # Text length score (normalized)
    text_length = post.get('text_length', 0)
    score += min(text_length / 500, 2.0)  # Max 2 points for length
    
    # SI confidence score (for borderline cases)
    si_confidence = post.get('si_confidence', 0)
    score += si_confidence * 2  # Max 2 points
    
    # Multimodal content bonus
    if post.get('had_image') and post.get('meme_text'):
        score += 1.5
    
    # Engagement score (normalized)
    score += min(post.get('score', 0) / 100, 1.0)  # Max 1 point
    score += min(post.get('num_comments', 0) / 50, 1.0)  # Max 1 point
    
    return score


def stratified_sample(posts_by_label, target_count, priority_labels=None):
    """
    Perform stratified sampling to select target_count posts
    maintaining proportional representation across labels
    """
    if priority_labels is None:
        priority_labels = ['MH', 'HUMOR', 'NEU']
    
    # Calculate current distribution
    total_available = sum(len(posts_by_label[label]) for label in priority_labels)
    
    if total_available <= target_count:
        # If we have fewer posts than target, take all
        sampled = []
        for label in priority_labels:
            sampled.extend(posts_by_label[label])
        return sampled
    
    # Calculate proportional targets for each label
    sampled = []
    for label in priority_labels:
        label_posts = posts_by_label[label]
        label_proportion = len(label_posts) / total_available
        label_target = int(target_count * label_proportion)
        
        # Sort by quality score and take top posts
        sorted_posts = sorted(label_posts, key=calculate_quality_score, reverse=True)
        sampled.extend(sorted_posts[:label_target])
        
        print(f"   {label}: Selected {label_target} / {len(label_posts)} posts")
    
    return sampled


def merge_datasets_with_strategy(existing_dataset_path=None, target_si_ratio=0.25):
    """
    Main merging function that implements the selective merging strategy
    
    Parameters:
    - existing_dataset_path: Path to existing merged dataset (if any)
    - target_si_ratio: Target ratio for SI posts (default 0.25 = 25%)
    """
    print("="*70)
    print("🔄 DATASET MERGING WITH SELECTIVE SAMPLING")
    print("="*70)
    
    # Step 1: Load all posts from collection runs
    all_new_posts = load_all_json_files("data/raw")
    
    # Step 2: Deduplicate
    unique_posts = deduplicate_posts(all_new_posts)
    
    # Step 3: Separate by label
    posts_by_label = separate_by_label(unique_posts)
    
    print("\n📈 Label Distribution in New Data:")
    for label, posts in sorted(posts_by_label.items()):
        print(f"   {label}: {len(posts)} posts")
    
    # Step 4: Load existing dataset if provided
    existing_posts = []
    if existing_dataset_path and os.path.exists(existing_dataset_path):
        with open(existing_dataset_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Handle both dictionary and list formats
            if isinstance(existing_data, dict):
                existing_posts = existing_data.get('posts', existing_data.get('data', []))
            elif isinstance(existing_data, list):
                existing_posts = existing_data
            else:
                print(f"⚠️  Unknown data format: {type(existing_data)}")
                existing_posts = []
        
            print(f"\n📂 Loaded existing dataset: {len(existing_posts)} posts")

    
    # Step 5: Merge all SI posts
    si_posts = posts_by_label.get('SI', [])
    si_candidate_posts = posts_by_label.get('SI_CANDIDATE', [])
    
    print(f"\n✅ Adding ALL SI-positive cases:")
    print(f"   SI: {len(si_posts)} posts")
    print(f"   SI_CANDIDATE: {len(si_candidate_posts)} posts")
    
    merged_posts = existing_posts.copy()
    merged_posts.extend(si_posts)
    merged_posts.extend(si_candidate_posts)
    
    total_si = len(si_posts) + len(si_candidate_posts) + sum(1 for p in existing_posts if p.get('prelim_label') in ['SI', 'SI_CANDIDATE'])
    
    # Step 6: Calculate target non-SI count
    target_total = int(total_si / target_si_ratio)
    target_non_si = target_total - total_si
    
    print(f"\n🎯 Target Distribution (SI ratio: {target_si_ratio*100}%):")
    print(f"   Total SI posts: {total_si}")
    print(f"   Target total posts: {target_total}")
    print(f"   Target non-SI posts: {target_non_si}")
    print(f"   Currently have: {len(existing_posts)} existing posts")
    
    # Step 7: Stratified sampling of non-SI posts
    current_non_si = len(existing_posts) - sum(1 for p in existing_posts if p.get('prelim_label') in ['SI', 'SI_CANDIDATE'])
    additional_non_si_needed = max(0, target_non_si - current_non_si)
    
    print(f"\n🔍 Selecting {additional_non_si_needed} additional non-SI posts:")
    
    if additional_non_si_needed > 0:
        sampled_non_si = stratified_sample(
            posts_by_label,
            additional_non_si_needed,
            priority_labels=['MH', 'HUMOR', 'NEU']
        )
        merged_posts.extend(sampled_non_si)
    
    # Step 8: Final deduplication
    merged_posts = deduplicate_posts(merged_posts)
    
    # Step 9: Generate statistics
    final_distribution = defaultdict(int)
    for post in merged_posts:
        final_distribution[post.get('prelim_label', 'UNKNOWN')] += 1
    
    print("\n" + "="*70)
    print("📊 FINAL MERGED DATASET STATISTICS")
    print("="*70)
    
    total_final = len(merged_posts)
    for label, count in sorted(final_distribution.items()):
        percentage = (count / total_final * 100) if total_final > 0 else 0
        print(f"   {label}: {count} posts ({percentage:.1f}%)")
    
    print(f"\n✅ Total merged posts: {total_final}")
    
    # Calculate actual SI ratio
    actual_si = final_distribution['SI'] + final_distribution.get('SI_CANDIDATE', 0)
    actual_ratio = (actual_si / total_final * 100) if total_final > 0 else 0
    print(f"📈 Actual SI ratio: {actual_ratio:.1f}%")
    
    return merged_posts


def save_merged_dataset(posts, output_dir="data/merged"):
    """
    Save the merged dataset to a JSON file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"merged_dataset_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Prepare metadata
    label_counts = defaultdict(int)
    for post in posts:
        label_counts[post.get('prelim_label', 'UNKNOWN')] += 1
    
    data_to_save = {
        'merge_info': {
            'merge_timestamp': datetime.now().isoformat(),
            'total_posts': len(posts),
            'label_distribution': dict(label_counts),
            'merge_strategy': 'selective_with_stratified_sampling',
            'script_version': '1.0'
        },
        'posts': posts
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(filepath)
    print(f"\n💾 Merged dataset saved:")
    print(f"   File: {filepath}")
    print(f"   Size: {file_size / (1024*1024):.2f} MB")
    
    return filepath


def main():
    """
    Main execution function
    """
    # Option 1: Merge without existing dataset (start fresh)
    # merged_posts = merge_datasets_with_strategy(
    #     existing_dataset_path=None,  # Set to your existing dataset path if you have one
    #     target_si_ratio=0.25  # Target 25% SI posts
    # )
    
    # Option 2: Merge with existing dataset
    merged_posts = merge_datasets_with_strategy(
        existing_dataset_path="data/merged/all_posts.json",
        target_si_ratio=0.25
    )
    
    # Save the merged dataset
    output_path = save_merged_dataset(merged_posts)
    
    print("\n" + "="*70)
    print("🎉 MERGING COMPLETE!")
    print("="*70)
    print(f"✅ Merged dataset ready at: {output_path}")
    print("\n💡 Next Steps:")
    print("   1. Review SI_CANDIDATE posts manually if needed")
    print("   2. Apply SMOTE or class weighting during model training")
    print("   3. Use stratified train-test split to preserve class distribution")


if __name__ == "__main__":
    main()
