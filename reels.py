import requests, random, os

PEXELS_API_KEY ="oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"

KEYWORDS = ["sports car", "luxury car", "supercar"]

# create folder
os.makedirs("reels", exist_ok=True)

# move file
if os.path.exists("final.mp4"):
    os.rename("final.mp4", "reels/reel.mp4")
    print("Moved to reels folder ✅")
else:
    print("final.mp4 not found ❌")

# -------------------------
# 1. Fetch Video
# -------------------------
def fetch_video():
    url = "https://api.pexels.com/videos/search"

    params = {
        "query": random.choice(KEYWORDS),
        "per_page": 5
    }

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    data = requests.get(url, headers=headers, params=params).json()
    videos = data.get("videos", [])

    if not videos:
        return None

    return videos[0]["video_files"][0]["link"]

# -------------------------
# 2. Download Video
# -------------------------
def download_video(url):
    video = requests.get(url).content
    with open("video.mp4", "wb") as f:
        f.write(video)

# -------------------------
# 3. Remove Audio
# -------------------------
def remove_audio():
    os.system("ffmpeg -y -i video.mp4 -an silent.mp4")

# -------------------------
# 4. Get Random Music
# -------------------------
def get_music():
    folder = "music"

    if not os.path.exists(folder):
        print("music folder missing ❌")
        return None

    files = [f for f in os.listdir(folder) if f.endswith(".mp3")]

    if not files:
        print("no music files ❌")
        return None

    return os.path.join(folder, random.choice(files))

# -------------------------
# 5. Add Music Loop
# -------------------------
def add_music():
    music = get_music()

    if not music:
        return

    print("Using music:", music)

    os.system(f"""
    ffmpeg -y -i silent.mp4 -stream_loop -1 -i "{music}" \
    -shortest -vf "scale=1080:1920" \
    -c:v libx264 -c:a aac final.mp4
    """)

# -------------------------
# MAIN
# -------------------------
def main():
    print("🚀 START REEL")

    video_url = fetch_video()

    if not video_url:
        print("No video found ❌")
        return

    download_video(video_url)
    remove_audio()
    add_music()

    print("✅ DONE → final.mp4")

# -------------------------
if __name__ == "__main__":
    main()
