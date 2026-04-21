import requests, random, os, shutil, json

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
USED_FILE = "used_videos.json"

KEYWORDS = ["sports car", "luxury car", "supercar"]

# -------------------------
# JSON helpers
# -------------------------
def load_used():
    if not os.path.exists(USED_FILE):
        with open(USED_FILE, "w") as f:
            json.dump([], f)
        return []

    try:
        with open(USED_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_used(data):
    with open(USED_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -------------------------
# Fetch video (anti-duplicate)
# -------------------------
def fetch_video():
    used = load_used()

    url = "https://api.pexels.com/videos/search"

    params = {
        "query": random.choice(KEYWORDS),
        "per_page": 10,
        "page": random.randint(1, 20)
    }

    headers = {"Authorization": PEXELS_API_KEY}

    data = requests.get(url, headers=headers, params=params).json()
    videos = data.get("videos", [])

    random.shuffle(videos)

    for v in videos:
        vid_id = str(v["id"])

        if vid_id not in used:
            used.append(vid_id)

            if len(used) > 200:
                used = used[-100:]

            save_used(used)

            return v["video_files"][0]["link"]

    return None

def get_video():
    for _ in range(5):
        v = fetch_video()
        if v:
            return v
    return None

# -------------------------
# Download
# -------------------------
def download_video(url):
    video = requests.get(url).content
    with open("video.mp4", "wb") as f:
        f.write(video)

# -------------------------
# Remove audio
# -------------------------
def remove_audio():
    os.system("ffmpeg -y -i video.mp4 -an -c:v copy silent.mp4")

# -------------------------
# Music
# -------------------------
def get_music():
    files = [f for f in os.listdir("music") if f.endswith(".mp3")]
    return os.path.join("music", random.choice(files)) if files else None

def add_music():
    music = get_music()
    if not music:
        return False

    os.system(f"""
    ffmpeg -y -i silent.mp4 -stream_loop -1 -i "{music}" \
    -shortest -c:v copy -c:a aac final.mp4
    """)

    return True

# -------------------------
# Save reel (no overwrite)
# -------------------------
def save_reel():
    os.makedirs("reels", exist_ok=True)

    i = 1
    while True:
        name = f"reels/reel_{i}.mp4"
        if not os.path.exists(name):
            shutil.move("final.mp4", name)
            break
        i += 1

# -------------------------
# MAIN
# -------------------------
def main():
    print("🚀 START")

    video = get_video()
    if not video:
        print("No video ❌")
        return

    download_video(video)
    remove_audio()

    if not add_music():
        return

    save_reel()
    print("✅ Reel saved")

if __name__ == "__main__":
    main()
