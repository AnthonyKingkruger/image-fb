import requests
import random
import os
import urllib.parse

PAGE_ID = "116388161520753"
ACCESS_TOKEN = "EAAOA47EFHGsBP9zVZCsr6OZASk8tbd8f8EVnmpfI3H9ZCvzdrHIXPc4qdHkk0VZBey0OZCbzytSspHA03qTh4vAFribHQjAdR41kIgqOEHsBxhH8Qkp50HDweRmHM7TLtmXeR9tAwdYKr4t67gyYYXdDULSXDhujoavpqgnEAmLs663CaZBfIcZCB4CjiED8LHRspkZD"

def generate_prompt():
    brands = ["Ferrari", "Lamborghini", "BMW", "Audi", "Mercedes"]
    scenes = ["city night", "mountain road", "sunset highway", "rain street"]

    return f"{brands} sports car driving on {scenes}, shot with Canon EOS R5, 85mm lens, f1.8, depth of field, motion blur, realistic lighting, cinematic color grading, ultra photorealistic, highly detailed, 8k, no CGI, no cartoon"

def generate_image(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024"
    
    img_data = requests.get(url).content
    
    with open("image.jpg", "wb") as f:
        f.write(img_data)
    
    return "image.jpg"

def upload_to_facebook(prompt, image_path):
    url = f"https://graph.facebook.com/{PAGE_ID}/photos"

    data = {
        "caption": f"{prompt} 🚗🔥\n\n#cars #supercars #luxurycars #carlover #automotive",
        "access_token": ACCESS_TOKEN
    }

    with open(image_path, "rb") as f:
        files = {"source": f}
        res = requests.post(url, files=files, data=data)

    if res.status_code == 200:
        print("Posted successfully ✅")
    else:
        print("Error ❌:", res.text)

def main():
    prompt = generate_prompt()
    print("Prompt:", prompt)
    
    image = generate_image(prompt)
    upload_to_facebook(prompt, image)

if __name__ == "__main__":
    main()
