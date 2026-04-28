import requests
import json

# Test adding new students
url_add = "http://127.0.0.1:5000/teacher/add_students"
new_students_data = {
    "students": [
        {
            "name": "Alice Wonderland",
            "class": "1A",
            "marks": {
                "telugu": 90,
                "hindi": 85,
                "english": 95,
                "maths": 100,
                "science": 92,
                "social": 88
            }
        }
    ]
}

response_add = requests.post(url_add, json=new_students_data)
print("Add Students Result:", response_add.json())

# Check if student was added
url_get = "http://127.0.0.1:5000/get_students_by_class/1A"
response_get = requests.get(url_get)
students = response_get.json()
print("Students in 1A after addition:", json.dumps(students, indent=2))
