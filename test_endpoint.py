import requests

url = "http://127.0.0.1:8000/api/v1/generate-assessment"

payload = {
    "course_id": "ML101",
    "module_id": "M3",
    "content_type": "text",
    "content_source": {
        "type": "inline",
        "text": "Supervised learning uses labeled data. Unsupervised finds patterns.",
    },
    "total_questions": 4,
}

response = requests.post(url, json=payload)

# Check status
if response.status_code == 200:
    data = response.json()
    print("Assessment generated successfully!")
    print(data)
else:
    print(f"Error {response.status_code}: {response.text}")
