# =========================
# 🔧 CONFIG
# =========================

SEARCH_KEYWORDS = [
    "BMW","Audi","Mercedes","Lamborghini","Ferrari",
    "Porsche","Bugatti","McLaren","Rolls Royce","Bentley",
    "Nissan","Tesla","Range Rover","Jaguar","Maserati"
]
MIN_DURATION = 5
MAX_DURATION = 60
# =========================
# IMPORTS
# =========================
import requests, random, os, shutil, json, time, hashlib, subprocess

# =========================
# ENV
# =========================
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PAGE_ID = os.getenv("PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

# =========================
# FILES
# =========================
USED_FILE = "used_videos.json"
MUSIC_FILE = "music_state.json"
HASH_FILE = "reel_hash.json"
CAPTION_FILE = "caption_state.json"
RUN_LOG = "run_log.json"
KEYWORD_FILE = "keyword_state.json"

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

    return os.path.join("music", music), music

# =========================
# CAPTION
# =========================
def get_caption():
    title = get_random_line("titles.txt")
    desc = get_random_line("descriptions.txt")
    return title, desc

# =========================
# HASH
# =========================
def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# =========================
# FETCH VIDEO (ROTATION + GUARANTEE)
# =========================
def fetch_video():
    used = load_json(USED_FILE, [])
    state = load_json(KEYWORD_FILE, {"index": 0})

    keyword = SEARCH_KEYWORDS[state["index"] % len(SEARCH_KEYWORDS)]
    state["index"] += 1
    save_json(KEYWORD_FILE, state)

    print("🔍 Keyword:", keyword)

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}

    for page in range(1, 6):
        params = {"query": keyword, "per_page": 30, "page": page}
        data = requests.get(url, headers=headers, params=params).json()
        videos = data.get("videos", [])

        for v in videos:
    vid = str(v["id"])
    if vid in used:
        continue

    # ✅ ADD THIS HERE
    if v["duration"] < MIN_DURATION or v["duration"] > MAX_DURATION:
        continue

            used.append(vid)
            save_json(USED_FILE, used[-200:])

            file = max(v["video_files"], key=lambda x: x.get("width", 0))

            return {
                "url": file["link"],
                "id": vid,
                "query": keyword
            }

    # fallback
    fallback = ["car","supercar","luxury car","sports car"]
    fb = random.choice(fallback)

    data = requests.get(url, headers=headers, params={"query": fb, "per_page": 10}).json()
    v = data["videos"][0]
    file = max(v["video_files"], key=lambda x: x.get("width", 0))

    return {
        "url": file["link"],
        "id": str(v["id"]),
        "query": fb
    }

# =========================
# DOWNLOAD
# =========================
def download(video):
    r = requests.get(video["url"])
    with open("video.mp4", "wb") as f:
        f.write(r.content)

# =========================
# ADD MUSIC + AUTO UPSCALE
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

        "-vf",
        "scale='if(gt(iw,ih),1920,1080)':'if(gt(iw,ih),1080,1920)',setsar=1",

        "-map","0:v:0",
        "-map","1:a:0",

        "-shortest",
        "-r","30",

        "-c:v","libx264",
        "-preset","fast",
        "-crf","23",

        "-c:a","aac",
        "-b:a","192k",

        "final.mp4"
    ]

    subprocess.run(cmd, check=True)
    return True, music_name

# =========================
# SAVE REEL (NO DUPLICATE)
# =========================
def save_reel():
    os.makedirs("reels", exist_ok=True)

    hashes = load_json(HASH_FILE, [])
    h = get_hash("final.mp4")

    if h in hashes:
        print("⚠️ Duplicate skipped")
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
# LOG
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
    download(video)

    ok, music = add_music()
    if not ok:
        return

    reel = save_reel()
    if not reel:
        return

    title, desc = get_caption()
    upload(reel, title, desc)

    log_run({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "video": video["id"],
        "keyword": video["query"],
        "music": music,
        "file": reel
    })

    cleanup()
    print("🎬 DONE")

if __name__ == "__main__":
    main()
