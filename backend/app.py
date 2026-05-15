from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

client = MongoClient(
    "mongodb+srv://Sai_Koushil_2003:Koushil%402003@cluster0.tez0v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Database
DB = client["attention_db"]
students = DB["students"]

# =============================
# LOGIN
# =============================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name required"}), 400

    student = students.find_one({"name": name})

    if student:
        return jsonify({"student_id": student['student_id']})

    count = students.count_documents({})
    student_id = f"S{count+1:03}"

    students.insert_one({
        "student_id": student_id,
        "name": name,
        "total_attentive": 0,
        "total_distracted": 0,
        "last_state": "unknown",
        "last_seen": None
    })

    return jsonify({"student_id": student_id})

# =============================
# LOG ATTENTION
# =============================
@app.route('/log', methods=['POST'])
def log_attention():
    data = request.get_json()

    student_id = data.get('student_id')
    state = data.get('state')

    if not student_id or not state:
        return jsonify({"error": "Invalid request"}), 400

    students.update_one(
        {"student_id": student_id},
        {
            "$inc": {
                f"total_{state}": 1
            },
            "$set": {
                "last_state": state,
                "last_seen": datetime.now()
            }
        }
    )

    return jsonify({"message": "updated"})

# =============================
    app.run(host='0.0.0.0', port=port)