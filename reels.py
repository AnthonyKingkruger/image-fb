# =========================
# 🔧 CONFIG (EDIT HERE)
# =========================

SEARCH_KEYWORDS = [
    "BMW","Audi","Mercedes","Lamborghini","Ferrari",
    "Porsche","Bugatti","McLaren","Rolls Royce","Bentley",
    "Nissan","Tesla","Range Rover","Jaguar","Maserati"
]

BOOST_KEYWORDS = ["supercar","luxury","night","cinematic","speed"]

MIN_DURATION = 5
MAX_DURATION = 20
MIN_WIDTH = 720
VERTICAL_ONLY = True

# =========================
# IMPORTS
# =========================
import requests, random, os, shutil, json, time, hashlib, subprocess

# =========================
# ENV (SECURE)
# =========================
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PAGE_ID = os.getenv("PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

# =========================
# STATE FILES
# =========================
USED_FILE = "used_videos.json"
MUSIC_FILE = "music_state.json"
HASH_FILE = "reel_hash.json"
CAPTION_FILE = "caption_state.json"
RUN_LOG = "run_log.json"

# =========================
# JSON HELPERS
# =========================
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

# =========================
# RANDOM TEXT
# =========================
def get_random_line(file):
    if not os.path.exists(file):
        return ""
    with open(file, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return random.choice(lines) if lines else ""

# =========================
# MUSIC (NO REPEAT)
# =========================
def get_music():
    files = [f for f in os.listdir("music") if f.endswith(".mp3")]
    if not files:
        return None, None

    state = load_json(MUSIC_FILE, {"used": []})
    available = [f for f in files if f not in state["used"]]

    if not available:
        state["used"] = []
        available = files

    music = random.choice(available)
    state["used"].append(music)
    save_json(MUSIC_FILE, state)

    print("🎵 Using:", music)
    return os.path.join("music", music), music

# =========================
# CAPTION (NO REPEAT)
# =========================
def get_caption():
    state = load_json(CAPTION_FILE, {"used": []})

    title = get_random_line("titles.txt")
    desc = get_random_line("descriptions.txt")

    tries = 0
    while title in state["used"] and tries < 10:
        title = get_random_line("titles.txt")
        tries += 1

    state["used"].append(title)
    save_json(CAPTION_FILE, state)

    return title, desc

# =========================
# HASH
# =========================
def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# =========================
# FETCH VIDEO
# =========================
def fetch_video():
    used = load_json(USED_FILE, [])

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}

    params = {
        "query": random.choice(SEARCH_KEYWORDS),
        "per_page": 15,
        "page": random.randint(1, 20)
    }

    data = requests.get(url, headers=headers, params=params).json()
    videos = data.get("videos", [])

    best, best_score = None, 0

    for v in videos:
        vid = str(v["id"])
        if vid in used:
            continue

        text = str(v).lower()

        if v["width"] < MIN_WIDTH:
            continue

        if VERTICAL_ONLY and v["height"] < v["width"]:
            continue

        if v["duration"] < MIN_DURATION or v["duration"] > MAX_DURATION:
            continue

        score = sum(2 for k in BOOST_KEYWORDS if k in text)

        if score > best_score:
            best_score = score
            best = v

    if not best:
        return None

    used.append(str(best["id"]))
    save_json(USED_FILE, used[-200:])

    file = max(best["video_files"], key=lambda x: x.get("width", 0))

    return {
        "url": file["link"],
        "id": str(best["id"]),
        "query": params["query"]
    }

# =========================
# DOWNLOAD
# =========================
def download(video):
    r = requests.get(video["url"])
    with open("video.mp4", "wb") as f:
        f.write(r.content)

# =========================
# ADD MUSIC (100% ATTACHED)
# =========================
def add_music():
    music_path, music_name = get_music()
    if not music_path:
        return False, None

    cmd = [
        "ffmpeg","-y",
        "-i","video.mp4",
        "-stream_loop","-1",
        "-i", music_path,
        "-filter_complex",
        "[0:v]scale=1080:1920,setsar=1[v];[1:a]volume=0.4[a]",
        "-map","[v]","-map","[a]",
        "-shortest",
        "-r","30",
        "-c:v","libx264","-preset","fast","-crf","23",
        "-c:a","aac","-b:a","192k",
        "final.mp4"
    ]

    subprocess.run(cmd, check=True)
    return True, music_name

# =========================
# SAVE REEL
# =========================
def save_reel():
    os.makedirs("reels", exist_ok=True)

    hashes = load_json(HASH_FILE, [])
    h = get_hash("final.mp4")

    if h in hashes:
        print("⚠️ Duplicate reel skipped")
        return None

    hashes.append(h)
    save_json(HASH_FILE, hashes[-200:])

    i = 1
    while True:
        name = f"reels/reel_{i}.mp4"
        if not os.path.exists(name):
            shutil.copy("final.mp4", name)
            return name
        i += 1

# =========================
# UPLOAD
# =========================
def upload(video, title, desc):
    url = f"https://graph-video.facebook.com/v19.0/{PAGE_ID}/videos"

    for i in range(5):
        try:
            with open(video, "rb") as f:
                r = requests.post(
                    url,
                    files={"source": f},
                    data={
                        "access_token": ACCESS_TOKEN,
                        "title": title,
                        "description": desc
                    }
                )
            if "id" in r.json():
                print("✅ Uploaded")
                return True
        except:
            pass

        time.sleep(2 ** i)

    return False

# =========================
# LOG RUN
# =========================
def log_run(data):
    logs = load_json(RUN_LOG, [])
    logs.append(data)
    save_json(RUN_LOG, logs[-200:])

# =========================
# CLEANUP
# =========================
def cleanup():
    for f in ["video.mp4","final.mp4"]:
        if os.path.exists(f):
            os.remove(f)

# =========================
# MAIN
# =========================
def main():
    print("🚀 START")

    video = fetch_video()
    if not video:
        return

    download(video)

    ok, music_name = add_music()
    if not ok:
        return

    reel = save_reel()
    if not reel:
        return

    title, desc = get_caption()
    upload(reel, title, desc)

    log_run({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "video_id": video["id"],
        "query": video["query"],
        "music": music_name,
        "title": title,
        "file": reel
    })

    cleanup()
    print("🎬 DONE")

if __name__ == "__main__":
    main()
