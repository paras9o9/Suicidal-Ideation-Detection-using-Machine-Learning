import os, json, glob, argparse, sys
from datetime import datetime

RAW_DIR = "/home/paras9o9/my-code/data/raw"
MERGED_JSON = "data/merged/all_posts.json"

MERGED_META = "data/merged/all_posts.meta.json"
MERGED_CSV = "data.merged/all_posts.csv"

SCHEMA_FIELDS = [
    "id", "title", "text", "meme_text", "had_image", "image_path", "subreddit", "created_utc", "score", "num_comments", "url", "text_length", "prelim_label", "collection-data", "source_file"
]

def load_json_safe(fp):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Skipping unreadable JSON: {fp} ({e})")
        return None

def iter_posts_from_file(fp):
    data = load_json_safe(fp)
    if data is None:
        return
    if isinstance(data, dict) and "posts" in data and isinstance(data["posts"], list):
        for p in data["posts"]:
            yield p
    elif isinstance(data, list):
        for p in data:
            yield p
    else:
        return

def normalize_post(p, source_file):
    post_text = p.get("id")
    return {
        "id": p.get("id"),
        "title": p.get("title", ""),
        "text": post_text,
        "meme_text": (p.get("meme_text", "") or ""),
        "had_image": p.get("had_image", bool(p.get("image_path"))),
        "subreddit": p.get("subreddit"),
        "created_utc": p.get("created_utc"),
        "score": p.get("score"),
        "num_comments": p.get("num_comments"),
        "url": p.get("url"),
        "text_length": p.get("text_length", len(post_text)),
        "prelim_label": p.get("prelim_label"),
        "collection-data": p.get("collection_data"),
        "source_file": source_file
    }

def load_meta():
    if os.path.exists(MERGED_JSON):
        meta = load_json_safe(MERGED_META)
        if isinstance(meta, dict):
            meta.setdefault("seen_ids", [])
            meta.setdefault("last_run", None)
            meta.setdefault("num_files", {})
            return meta
    return {"seen_ids": [], "last_run": None, "indexed_files": {}}


def save_meta(meta):
    os.makedirs(os.path.dirname(MERGED_META), exist_ok=True)
    with open(MERGED_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

def load_existing_merged():
    if not os.path.exists(MERGED_JSON):
        return []
    data = load_json_safe(MERGED_JSON)
    return data if isinstance(data, list) else []

def write_merged_json(items):
    os.makedirs(os.path.dirname(MERGED_JSON), exist_ok=True)

    tmp = MERGED_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
    os.replace(tmp, MERGED_JSON)

def export_csv(items, csv_path=MERGED_CSV):
    import csv
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_FIELDS)
        writer.writeheader()
        for p in items:
            writer.writerow({k: p.get(k) for k in SCHEMA_FIELDS})
            writer.writeheader()
            for p in items:
                writer.writerow({k: p.get(k) for k in SCHEMA_FIELDS})

def export_csv(items, csv_path=MERGED_CSV):
    import csv
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_FIELDS)
        writer.writeheader()
        for p in items:
            writer.writerow({k: p.get(k) for k in SCHEMA_FIELDS})

def find_raw_files():

    base_path = "/home/paras9o9/my-code/data/raw"
    
    print(f"--- Searching in: {base_path} ---")
    
    json_files = []
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    json_files.append(full_path)
        
        json_files.sort() 
        
    print(f"--- Found {len(json_files)} JSON files ---")
    if json_files:
        print(f"--- First few files: ---")
        for f in json_files[:3]:
            print(f"    {os.path.basename(f)}")
        print(f"--- Last few files: ---")
        for f in json_files[-3:]:
            print(f"    {os.path.basename(f)}")
    
    return json_files
    
def merge_incremental(export_csv_flag=False):
    existing = load_existing_merged()
    meta= load_meta()
    seen_ids = set(meta.get("seen_ids", []))

    if not seen_ids and existing:
        for p in existing:
            pid = p.get("id")
            if pid:
                seen_ids.add(pid)

    merged = existing[:]
    new_count = 0
    files = find_raw_files()

    for fp in files:
        try:
            stat = os.stat(fp)
            sig = f"{stat.st_mtime_ns}:{stat.st_size}"
        except Exception:
            sig = None

        indexed = meta["indexed_files"].get(fp)
        if indexed and sig and indexed == sig:
            continue

        file_new = 0
        for p in iter_posts_from_file(fp):
            pid = p.get("id")
            if not pid or pid in seen_ids:
                continue
            norm = normalize_post(p, source_file=fp)
            merged.append(norm)
            seen_ids.add(pid)
            new_count += 1
            file_new += 1

        if sig:
            meta["indexed_files"][fp] = sig
        
        if file_new:
            print(f"{file_new:4d} new from {fp}")

    if new_count:
        write_merged_json(merged)
        meta["seen_ids"] = list(seen_ids)
        meta["last_run"] = datetime.now().isoformat()
        save_meta(meta)
        print(f"Added {new_count} new posts. Total: {len(merged)}")
        if export_csv_flag:
            export_csv(merged)
            print(f"CSV written: {MERGED_CSV}")
    else:
        print(f"No new posts found. Total remains: {len(merged)}")

def main():
    parser = argparse.ArgumentParser(description="Incrementally merge raw Reddit collections into a single dateset.")
    parser.add_argument("--export-csv", action="store_true", help="Also export a CSV snapshot of hte merged data.")
    args = parser.parse_args()

    merge_incremental(export_csv_flag=args.export_csv)
    print("--- Merge script finished ---")

if __name__ == "__main__":
    main()