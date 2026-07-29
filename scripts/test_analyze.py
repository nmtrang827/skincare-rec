import requests

url = "http://127.0.0.1:5000/analyze"
image_path = r"C:\Users\trang\Downloads\levle0_55.jpg"

with open(image_path, "rb") as f:
    response = requests.post(url, files={"image": f})

print(response.json())