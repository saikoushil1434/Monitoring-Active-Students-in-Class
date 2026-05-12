import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["attention_db"]
students_collection = db["students"]

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    student_name = data.get("name")

    if not student_name:
        return jsonify({"error": "Name required"}), 400

    # If student already exists, just return ID
    student = students_collection.find_one({"name": student_name})
    if student:
        return jsonify({"student_id": student["student_id"]})

    # Generate new student ID
    count = students_collection.count_documents({})
    student_id = f"S{count+1:03}"

    students_collection.insert_one({
        "student_id": student_id,
        "name": student_name,
        "total_attentive": 0,
        "total_distracted": 0,
        "last_state": None,
        "last_seen": None
    })

    return jsonify({"student_id": student_id})

@app.route("/log", methods=["POST"])
def log():
    data = request.get_json()
    student_id = data.get("student_id")
    state = data.get("state")

    if not student_id or not state:
        return jsonify({"error": "Bad Request"}), 400

    students_collection.update_one(
        {"student_id": student_id},
        {"$inc": {f"total_{state}": 1},
         "$set": {"last_state": state, "last_seen": datetime.now()}}
    )

    return jsonify({"message": "Logged"})

@app.route("/students", methods=["GET"])
def get_students():
    students = students_collection.find()
    result = []
    for s in students:
        s["_id"] = str(s["_id"])
        result.append(s)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
