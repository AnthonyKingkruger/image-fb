import requests, random, os, shutil, json, time

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

USED_FILE = "used_videos.json"
MUSIC_FILE = "music_state.json"

# -------------------------
# JSON helpers
# -------------------------
def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
        return default
    try:
        return json.load(open(file))
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# -------------------------
# RANDOM TEXT
# -------------------------
def get_random_line(file):
    if not os.path.exists(file):
        return ""
    with open(file, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return random.choice(lines) if lines else ""

# -------------------------
# 🔥 VIRAL VIDEO PICKER
# -------------------------
def fetch_viral_video():
    used = load_json(USED_FILE, [])

    url = "https://api.pexels.com/videos/search"

    params = {
        "query": random.choice([
            "BMW",
    "Audi",
    "Mercedes",
    "Lamborghini",
    "Ferrari",
    "Porsche",
    "Bugatti",
    "McLaren",
    "Rolls Royce",
    "Bentley",
    "Nissan",
    "Tesla",
    "Range Rover",
    "Jaguar",
    "Maserati",
    "Aston Martin",
    "Chevrolet",
    "Ford Mustang",
    "Dodge",
    "Koenigsegg"
        ]),
        "per_page": 15,
        "page": random.randint(1, 20)
    }

    headers = {"Authorization": PEXELS_API_KEY}
    data = requests.get(url, headers=headers, params=params).json()
    videos = data.get("videos", [])

    best_video = None
    best_score = 0

    for v in videos:
        vid_id = str(v["id"])
        if vid_id in used:
            continue

        text = str(v).lower()

        # 🔥 STRICT CAR FILTER
        if not any(k in text for k in ["car", "supercar", "vehicle", "automobile"]):
            continue

        score = 0

        # HD filter
        if v["width"] < 720:
            continue

        # orientation
        if v["height"] > v["width"]:
            score += 2

        # duration
        d = v["duration"]
        if d < 5:
            continue
        elif d <= 15:
            score += 3
        elif d <= 25:
            score += 1

        # keywords boost
        for k in ["supercar", "luxury", "night", "cinematic", "speed"]:
            if k in text:
                score += 2

        if score > best_score:
            best_score = score
            best_video = v

    if not best_video:
        return None

    used.append(str(best_video["id"]))
    if len(used) > 200:
        used = used[-100:]
    save_json(USED_FILE, used)

    # best quality file
    best_file = max(best_video["video_files"], key=lambda x: x.get("width", 0))

    return best_file["link"]

# -------------------------
# DOWNLOAD VIDEO
# -------------------------
def download_video(url):
    video = requests.get(url).content
    with open("video.mp4", "wb") as f:
        f.write(video)

# -------------------------
# MUSIC SYSTEM
# -------------------------
def get_music():
    files = [f for f in os.listdir("music") if f.endswith(".mp3")]
    return os.path.join("music", random.choice(files)) if files else None

# -------------------------
# ADD MUSIC (FIXED)
# -------------------------
def add_music():
    music = get_music()
    if not music:
        return False

    print("🎵 Using:", music)

    os.system(f"""
    ffmpeg -y -i video.mp4 -stream_loop -1 -i "{music}" \
    -map 0:v:0 -map 1:a:0 \
    -shortest \
    -c:v libx264 -preset fast -pix_fmt yuv420p \
    -c:a aac -b:a 192k \
    final.mp4
    """)

    return True

# -------------------------
# SAVE REEL
# -------------------------
def save_reel():
    os.makedirs("reels", exist_ok=True)
    i = 1
    while True:
        name = f"reels/reel_{i}.mp4"
        if not os.path.exists(name):
            shutil.copy("final.mp4", name)
            return name
        i += 1

# -------------------------
# FB UPLOAD (RETRY)
# -------------------------
def upload_to_facebook(video_path):
    title = get_random_line("titles.txt")
    desc = get_random_line("descriptions.txt")

    url = f"https://graph-video.facebook.com/v19.0/{PAGE_ID}/videos"

    for i in range(1, 4):
        print(f"📤 Attempt {i}")

        try:
            with open(video_path, "rb") as f:
                res = requests.post(
                    url,
                    files={"source": f},
                    data={
                        "access_token": ACCESS_TOKEN,
                        "title": title,
                        "description": desc
                    }
                )

            data = res.json()
            print("📊", data)

            if "id" in data:
                print("✅ SUCCESS")
                return True

        except Exception as e:
            print("⚠️", e)

        time.sleep(5)

    print("❌ FAILED")
    return False

# -------------------------
# MAIN
# -------------------------
def main():
    print("🚀 START")

    video = fetch_viral_video()
    if not video:
        print("No video ❌")
        return

    download_video(video)

    if not add_music():
        return

    reel_path = save_reel()

    upload_to_facebook(reel_path)

    print("🎬 DONE")

# -------------------------
if __name__ == "__main__":
    main()
