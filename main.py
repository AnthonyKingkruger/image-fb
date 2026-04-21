import requests
import random
import os
import json
import time
import hashlib

UNSPLASH_KEY = "ggQlxeOt1owC5MtUHiuItv6eQAsZ4mAd5QKzq8QFfFw"
PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

USED_FILE = "used_images.json"
CAPTION_FILE = "used_captions.json"

KEYWORDS = [
    "sports car","luxury car","supercar","bmw car",
    "audi car","mercedes car","ferrari car","lamborghini"
]

# ---------------------------
# JSON SAFE HANDLER
# ---------------------------
def load_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
        return []

    try:
        with open(file, "r") as f:
            content = f.read().strip()

            if not content:
                return []

            data = json.loads(content)

            # 🔥 handle old format (ints)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], int):
                print("⚠️ Old format detected, resetting")
                return []

            return data

    except:
        print(f"⚠️ Corrupted JSON fixed: {file}")
        with open(file, "w") as f:
            json.dump([], f)
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------
# HASH
# ---------------------------
def get_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

# ---------------------------
# FETCH PEXELS
# ---------------------------
def fetch_pexels():
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": random.choice(KEYWORDS),
        "per_page": 30,
        "page": random.randint(1,50)
    }
    headers = {"Authorization": PEXELS_API_KEY}

    try:
        data = requests.get(url, headers=headers, params=params).json()
        return data.get("photos", [])
    except:
        return []

# ---------------------------
# FETCH UNSPLASH
# ---------------------------
def fetch_unsplash():
    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": random.choice(KEYWORDS),
        "count": 10,
        "client_id": UNSPLASH_KEY
    }

    try:
        data = requests.get(url, params=params).json()
        return data if isinstance(data, list) else []
    except:
        return []

# ---------------------------
# GET IMAGE (ANTI DUPLICATE)
# ---------------------------
def get_image():
    used = load_json(USED_FILE)

    for attempt in range(5):
        print("Attempt:", attempt+1)

        photos = fetch_pexels() + fetch_unsplash()
        random.shuffle(photos)

        for p in photos:
            try:
                if "src" in p:
                    img_id = "pexels_" + str(p["id"])
                    img_url = p["src"]["large"]
                else:
                    img_id = "unsplash_" + str(p["id"])
                    img_url = p["urls"]["regular"]
            except:
                continue

            hash_val = get_hash(img_url)

            already = any(
                isinstance(item, dict) and
                (item.get("id") == img_id or item.get("hash") == hash_val)
                for item in used
            )

            if not already:
                print("✅ NEW IMAGE:", img_id)

                used.append({
                    "id": img_id,
                    "hash": hash_val
                })

                if len(used) > 300:
                    used = used[-150:]

                save_json(USED_FILE, used)
                return img_url

        print("Retrying...")

    return None

# ---------------------------
# CAPTIONS
# ---------------------------
def get_caption():
    if not os.path.exists("captions.txt"):
        return "Dream Car 🚗🔥"

    with open("captions.txt") as f:
        captions = [c.strip() for c in f.readlines() if c.strip()]

    used = load_json(CAPTION_FILE)

    available = [c for c in captions if c not in used]

    if not available:
        used = []
        available = captions

    caption = random.choice(available)
    used.append(caption)

    save_json(CAPTION_FILE, used)
    return caption

def get_hashtags():
    if not os.path.exists("hashtags.txt"):
        return "#cars #supercars #luxurycars"

    with open("hashtags.txt") as f:
        return random.choice(f.readlines()).strip()

def final_caption():
    extras = ["🔥","🚗","😎","💯"]
    return f"{get_caption()} {random.choice(extras)}\n\n{get_hashtags()}"

# ---------------------------
# FACEBOOK POST
# ---------------------------
def upload_to_facebook(image_url, caption):
    url = f"https://graph.facebook.com/{PAGE_ID}/photos"

    data = {
        "url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    try:
        res = requests.post(url, data=data)
        if res.status_code == 200:
            print("Posted Successfully ✅")
        else:
            print("Facebook Error ❌:", res.text)
    except Exception as e:
        print("Upload failed:", e)

# ---------------------------
# MAIN
# ---------------------------
def main():
    print("🚀 START")

    image_url = get_image()

    if not image_url:
        print("No unique image found ❌")
        return

    caption = final_caption()

    print("Posting...")
    time.sleep(random.randint(2,5))

    upload_to_facebook(image_url, caption)

# ---------------------------
if __name__ == "__main__":
    main()
