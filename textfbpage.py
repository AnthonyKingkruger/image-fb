import requests
import random

# 🔑 ENV VARIABLES (GitHub Secrets se aayengi)
OPENAI_API_KEY = "${OPENAI_API_KEY}"
PAGE_ID = "${PAGE_ID}"
FB_ACCESS_TOKEN = "${FB_ACCESS_TOKEN}"

categories = [
    "luxury cars",
    "supercars",
    "sports cars",
    "car lifestyle",
    "success motivation"
]

def generate_content():
    category = random.choice(categories)

    prompt = f"""
Create viral social media content about: "{category}"

Format:

TITLE:
(write catchy title)

STORY:
(100-150 words emotional story)

HASHTAGS:
(5-8 hashtags)
"""

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.9
        }
    )

    data = res.json()
    return data["choices"][0]["message"]["content"]


def post_to_facebook(content):
    res = requests.post(
        f"https://graph.facebook.com/{PAGE_ID}/feed",
        data={
            "message": content,
            "access_token": FB_ACCESS_TOKEN
        }
    )
    print("FB RESPONSE:", res.json())


def main():
    content = generate_content()
    print("\n🔥 CONTENT:\n", content)
    post_to_facebook(content)


if __name__ == "__main__":
    main()
