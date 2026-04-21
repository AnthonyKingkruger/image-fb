import requests, random, os, shutil, json, time

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

USED_FILE = "used_videos.json"
MUSIC_FILE = "music_state.json"

# -------------------------
# RANDOM TEXT (TITLE + DESC)
# -------------------------
def get_random_line(file):
    if not os.path.exists(file):
        return ""

    with open(file, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    return random.choice(lines) if lines else ""

# -------------------------
# FETCH VIDEO
# -------------------------
def fetch_video():
    url = "https://api.pexels.com/videos/search"

    params = {
        "query": random.choice(["supercar", "luxury car", "sports car"]),
        "per_page": 10
    }

    headers = {"Authorization": PEXELS_API_KEY}
    data = requests.get(url, headers=headers, params=params).json()
    videos = data.get("videos", [])

    if not videos:
        return None

    return videos[0]["video_files"][0]["link"]

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
        print("❌ No music")
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
# FB UPLOAD (WITH RETRY 🔥)
# -------------------------
def upload_to_facebook(video_path):
    title = get_random_line("titles.txt")
    desc = get_random_line("descriptions.txt")

    print("📝 Title:", title)
    print("📝 Desc:", desc)

    url = f"https://graph-video.facebook.com/v19.0/{PAGE_ID}/videos"

    for attempt in range(1, 4):
        print(f"📤 Attempt {attempt}...")

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
            print("📊 Response:", data)

            if "id" in data:
                print("✅ Upload Success 🚀")
                return True

        except Exception as e:
            print("⚠️ Error:", e)

        time.sleep(5)

    print("❌ Failed after 3 attempts")
    return False

# -------------------------
# MAIN
# -------------------------
def main():
    print("🚀 START")

    video = fetch_video()
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
