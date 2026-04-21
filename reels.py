import requests, random, os, shutil, json, time

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"
PAGE_ID = "105592899263357"
ACCESS_TOKEN = "EAAUz6DTBwUABQ0ZBpy9aqpGiElqfJXJnt5Pi4gD23ZC5yzrvOH3dzyvhQmcvhzKVEYaUZCEtRb6vPyPvLM8VM8fBlYdoYbaMLVWWmV76FMbUIlIcRMu9Nr9J9J1omhzci5K498ajGxx4vgJZBIyzfQThc5zCV1XtW9hpJZCVZCIfjsB5EqkCMTOz8RfAaAN4lLuioSy6vWbozsaQvPX3cZD"

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
# FETCH VIDEO
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
# MUSIC SYSTEM
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
# ADD MUSIC + FORMAT
# -------------------------
def add_music():
    music = get_music()
    if not music:
        return False

    probe = os.popen(
        'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video.mp4'
    ).read().strip()

    width, height = map(int, probe.split(','))
    print(f"📐 Resolution: {width}x{height}")

    if height > width:
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    else:
        vf = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"

    os.system(f"""
    ffmpeg -y -i video.mp4 -stream_loop -1 -i "{music}" \
    -shortest \
    -vf "{vf}" \
    -c:v libx264 -preset fast -pix_fmt yuv420p \
    -c:a aac -b:a 128k -r 30 final.mp4
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
# GITHUB RAW URL
# -------------------------
def get_github_raw_url(file_path):
    repo = "AnthonyKingkruger/image-fb"
    branch = "main"
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"

# -------------------------
# FACEBOOK UPLOAD (URL)
# -------------------------
def upload_to_facebook_url(video_url):
    print("📤 Upload via URL...")

    endpoint = f"https://graph-video.facebook.com/v18.0/{PAGE_ID}/videos"

    res = requests.post(endpoint, data={
        "access_token": ACCESS_TOKEN,
        "file_url": video_url,
        "description": "🔥 Dream Car Reel #cars #reels #viral"
    })

    print("📊 FB RESPONSE:", res.json())

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

    # 🔥 Generate GitHub URL
    raw_url = get_github_raw_url(reel_path)
    print("🌐 Raw URL:", raw_url)

    # 🔥 Upload to Facebook
    upload_to_facebook_url(raw_url)

    print("🎬 DONE")

# -------------------------
if __name__ == "__main__":
    main()
