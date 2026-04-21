import requests
import random

# Facebook config
PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

def generate_prompt():
    topics = ["beautiful beach sunset", "green village fields", "mountain landscape", "river nature view"]
    return random.choice(topics)

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    img_data = requests.get(url).content
    
    with open("image.jpg", "wb") as f:
        f.write(img_data)
    
    return "image.jpg"

def upload_to_facebook(prompt, image_path):
    url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    
    files = {
        "source": open(image_path, "rb")
    }
    
    data = {
        "caption": f"{prompt} 🌍✨\n\n#nature #travel #beautiful",
        "access_token": ACCESS_TOKEN
    }

    res = requests.post(url, files=files, data=data)
    print(res.text)

def main():
    prompt = generate_prompt()
    print("Prompt:", prompt)
    
    image = generate_image(prompt)
    upload_to_facebook(prompt, image)

if __name__ == "__main__":
    main()
