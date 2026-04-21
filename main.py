import requests
import random
import os
import json

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

USED_FILE = "used_images.json"

# 🔹 Load used images
def load_used():
    if os.path.exists(USED_FILE):
        with open(USED_FILE, "r") as f:
            return json.load(f)
    return []

# 🔹 Save used images
def save_used(data):
    with open(USED_FILE, "w") as f:
        json.dump(data, f)

# 🔹 Get car image from Pexels
def get_car_image():
    url = "https://api.pexels.com/v1/search"
    
    queries = ["sports car", "luxury car", "supercar", "bmw car", "audi car"]
    query = random.choice(queries)

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": 20
    }

    res = requests.get(url, headers=headers, params=params)
data = res.json()

if "photos" not in data:
    print("API Error:", data)
    return None

    used = load_used()

    for photo in res["photos"]:
        img_url = photo["src"]["large"]

        if img_url not in used:
            used.append(img_url)
            save_used(used)
            return img_url

    return None

# 🔹 Upload to Facebook
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

# 🔹 Main
def main():
    image_url = get_car_image()

    if not image_url:
        print("No new image found")
        return

    caption = "Luxury Car 🚗🔥\n\n#cars #supercars #luxurycars #carlover"

    upload_to_facebook(image_url, caption)

if __name__ == "__main__":
    main()
