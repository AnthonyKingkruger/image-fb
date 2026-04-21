import requests, random, os, shutil, json

PEXELS_API_KEY = "oajVHU4u6uH2lLQPwlmof4vAe4kROKDBUMa183iGllxVQyDBx7Mf8w40"

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
# REMOVE AUDIO (FAST)
# -------------------------
def remove_audio():
    os.system("ffmpeg -y -i video.mp4 -an -c:v copy silent.mp4")

# -------------------------
# BALANCED MUSIC SYSTEM 🔥
# -------------------------
def get_music():
    files = [f for f in os.listdir("music") if f.endswith(".mp3")]

    if not files:
        print("No music ❌")
        return None

    state = load_json(MUSIC_FILE, {"queue": [], "used": []})

    if not state["queue"]:
        state["queue"] = files.copy()
        random.shuffle(state["queue"])
        state["used"] = []

    song = state["queue"].pop(0)
    state["used"].append(song)

    if not state["queue"]:
        print("🔁 Music cycle reset")
        state["queue"] = files.copy()
        random.shuffle(state["queue"])
        state["used"] = []

    save_json(MUSIC_FILE, state)

    return os.path.join("music", song)

# -------------------------
# ADD MUSIC LOOP (NO RESIZE)
# -------------------------
def add_music():
    music = get_music()

    if not music:
        return False

    print("Using music:", music)

    os.system(f"""
    ffmpeg -y -i silent.mp4 -stream_loop -1 -i "{music}" \
    -shortest -c:v copy -c:a aac final.mp4
    """)

    return True

# -------------------------
# SAVE REEL (NO OVERWRITE)
# -------------------------
def save_reel():
    os.makedirs("reels", exist_ok=True)

    if not os.path.exists("final.mp4"):
        print("❌ final.mp4 not found")
        return

    i = 1
    while True:
        name = f"reels/reel_{i}.mp4"
        if not os.path.exists(name):
            shutil.move("final.mp4", name)
            print(f"✅ Saved as {name}")
            break
        i += 1

# -------------------------
# MAIN
# -------------------------
def main():
    print("🚀 START REEL")

    video = get_video()
    if not video:
        print("No video ❌")
        return

    download_video(video)
    remove_audio()

    if not add_music():
        return

    save_reel()

    print("🎬 DONE")

# -------------------------
if __name__ == "__main__":
    main()
