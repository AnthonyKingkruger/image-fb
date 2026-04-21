import requests, random, os, shutil, json

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "104123296096469"
ACCESS_TOKEN = "EAALFZBIn3zJkBP7myOZCmZC3bcZBFNZBkmLZCveW8Q2QyW7igoHNBrZCLYKgQZB5Vm85RZAW6x2RbOl2SnuuPbxl6CkMLC5HfzPrTpgZBqTCIChy9Q1lXdlX5PZADmAKb9gtZA1oOpZAFCDjNfvZASZCtaFd3ZC1uugDwTYfylaTg6JmYS5rXNKOxZA7TMZBO1DXjHRyZB3hF1Y74ScrPUQbJQZBhFofRLyB6hIZD"

KEYWORDS = ["sports car", "luxury car", "supercar"]

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
# FETCH VIDEO (ANTI DUPLICATE)
# -------------------------
def fetch_video():
    used = load_json(USED_FILE, [])

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

            save_json(USED_FILE, used)

            return v["video_files"][0]["link"]

    return None

def get_video():
    for _ in range(5):
        v = fetch_video()
        if v:
            return v
    return None

# -------------------------
# DOWNLOAD VIDEO
# -------------------------
def download_video(url):
    video = requests.get(url).content
    with open("video.mp4", "wb") as f:
        f.write(video)

# -------------------------
# REMOVE AUDIO
# -------------------------
def remove_audio():
    os.system("ffmpeg -y -i video.mp4 -an -c:v copy silent.mp4")

# -------------------------
# BALANCED MUSIC SYSTEM
# -------------------------
def get_music():
    files = [f for f in os.listdir("music") if f.endswith(".mp3")]

    if not files:
        return None

    state = load_json(MUSIC_FILE, {"queue": [], "used": []})

    if not state["queue"]:
        state["queue"] = files.copy()
        random.shuffle(state["queue"])
        state["used"] = []

    song = state["queue"].pop(0)
    state["used"].append(song)

    if not state["queue"]:
        state["queue"] = files.copy()
        random.shuffle(state["queue"])
        state["used"] = []

    save_json(MUSIC_FILE, state)

    return os.path.join("music", song)

# -------------------------
# ADD MUSIC
# -------------------------
def add_music():
    music = get_music()
    if not music:
        return False

    # get video resolution
    probe = os.popen(
        'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video.mp4'
    ).read().strip()

    width, height = map(int, probe.split(','))

    print(f"📐 Resolution: {width}x{height}")

    # -------------------------
    # CASE 1: VERTICAL VIDEO
    # -------------------------
    if height > width:
        print("📱 Vertical → convert to 1080x1920")

        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

    # -------------------------
    # CASE 2: HORIZONTAL VIDEO
    # -------------------------
    else:
        print("🖥 Horizontal → convert to 1920x1080")

        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"

    # -------------------------
    # FINAL FFMPEG
    # -------------------------
    os.system(f"""
    ffmpeg -y -i video.mp4 -stream_loop -1 -i "{music}" \
    -shortest \
    -vf "{vf}" \
    -c:v libx264 -preset fast -pix_fmt yuv420p \
    -c:a aac -b:a 128k -r 30 final.mp4
    """)

    return True# -------------------------
# SAVE REEL
# -------------------------
def save_reel():
    os.makedirs("reels", exist_ok=True)

    i = 1
    while True:
        name = f"reels/reel_{i}.mp4"
        if not os.path.exists(name):
            shutil.copy("final.mp4", name)   # copy instead of move
            return name
        i += 1

# -------------------------
# FACEBOOK UPLOAD
# -------------------------
def upload_to_facebook(video_path):
    print("📤 Uploading to Facebook...")

    if not os.path.exists(video_path):
        print("❌ Video file not found")
        return

    try:
        # STEP 1: START
        start_res = requests.post(
            f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels",
            data={
                "upload_phase": "start",
                "access_token": ACCESS_TOKEN
            }
        ).json()

        print("🟡 START RESPONSE:", start_res)

        upload_url = start_res.get("upload_url")
        video_id = start_res.get("video_id")

        if not upload_url or not video_id:
            print("❌ START FAILED")
            return

        # STEP 2: UPLOAD
        file_size = os.path.getsize(video_path)

        with open(video_path, "rb") as f:
            upload_res = requests.post(
                upload_url,
                data=f,
                headers={
                    "Authorization": f"OAuth {ACCESS_TOKEN}",
                    "offset": "0",
                    "file_size": str(file_size),
                    "Content-Type": "application/octet-stream"
                }
            )

        print("🟡 UPLOAD STATUS:", upload_res.status_code)
        print("🟡 UPLOAD RESPONSE:", upload_res.text)

        if upload_res.status_code != 200:
            print("❌ Upload failed")
            return

        # STEP 3: FINISH (FIXED)
        finish_res = requests.post(
            f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels",
            data={
                "upload_phase": "finish",
                "video_id": video_id,
                "description": "🔥 Dream Car Reel #cars #reels #viral",
                "access_token": ACCESS_TOKEN
            }
        ).json()

        print("🟢 FINISH RESPONSE:", finish_res)

        if "success" in finish_res or finish_res.get("id"):
            print("✅ Reel Published Successfully 🚀")
        else:
            print("⚠️ Upload ok but publish unclear")

    except Exception as e:
        print("❌ FB Upload Error:", str(e))
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

    reel_path = save_reel()

    upload_to_facebook(reel_path)

    print("🎬 DONE")

if __name__ == "__main__":
    main()
