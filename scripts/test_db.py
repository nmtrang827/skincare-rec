import requests

payload = {
    "profile": {"Acne_Severity": 5, "Dryness_Severity": 3},
    "products": [{"name": "Test Product", "price": "£10"}]
}

res = requests.post("http://127.0.0.1:5000/save_results", json=payload)
print("Save:", res.json())

result_id = res.json()["id"]
res2 = requests.get(f"http://127.0.0.1:5000/results/{result_id}")
print("Fetch:", res2.json())