import requests
import random
import os
import json

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

USED_FILE = "used_images.json"
CAPTION_FILE = "used_captions.json"

MAX_USED = 100

# 🔥 Single category (customize here)
KEYWORDS = [
    "sports car",
    "luxury car",
    "bmw car",
    "audi car",
    "supercar",
    "lamborghini",
    "ferrari"
]

# ---------------------------
# Auto create + load JSON
# ---------------------------
def load_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)
        return []
    
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ---------------------------
# Get image from Pexels
# ---------------------------
def get_image():
    url = "https://api.pexels.com/v1/search"

    query = random.choice(KEYWORDS)
    print("Keyword:", query)

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": 15
    }

    res = requests.get(url, headers=headers, params=params)

    try:
        data = res.json()
    except:
        print("Invalid response ❌")
        return None

    if "photos" not in data:
        print("Pexels error:", data)
        return None

    used = load_json(USED_FILE)

    for photo in data["photos"]:
        img_id = photo["id"]
        img_url = photo["src"]["large"]

        if img_id not in used:
            used.append(img_id)

            # 🔥 limit control
            if len(used) > MAX_USED:
                used = used[-50:]

            save_json(USED_FILE, used)
            return img_url

    return None

# ---------------------------
# Caption system
# ---------------------------
def get_caption():
    with open("captions.txt") as f:
        captions = [c.strip() for c in f.readlines()]

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
    with open("hashtags.txt") as f:
        return random.choice(f.readlines()).strip()

def final_caption():
    extras = ["🔥", "🚗", "😎", "💯"]

    return f"{get_caption()} {random.choice(extras)}\n\n{get_hashtags()}"

# ---------------------------
# Facebook Upload
# ---------------------------
def upload_to_facebook(image_url, caption):
    url = f"https://graph.facebook.com/{PAGE_ID}/photos"

    data = {
        "url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    res = requests.post(url, data=data)

    if res.status_code == 200:
        print("Posted ✅")
    else:
        print("Error ❌", res.text)

# ---------------------------
# Main
# ---------------------------
def main():
    print("Start...")

    image_url = get_image()

    if not image_url:
        print("No image found ❌")
        return

    caption = final_caption()

    time.sleep(random.randint(2,5))  # human delay

    upload_to_facebook(image_url, caption)

if __name__ == "__main__":
    main()
