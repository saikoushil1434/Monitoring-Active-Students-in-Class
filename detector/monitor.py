import cv2
import numpy as np
import time
import requests
import mediapipe as mp
from math import hypot

# ==============================
# ASK STUDENT ID FROM LOGIN PAGE
# ==============================
STUDENT_ID = input("Enter your assigned Student ID from Login: ")
print(f"🎓 Tracking attention for Student ID: {STUDENT_ID}")

# ==============================
# BACKEND API
# ==============================
BACKEND_LOG_ENDPOINT = "https://monitoring-active-students-in-class-1.onrender.com/log"
EAR_THRESHOLD = 0.20
YAW_THRESHOLD = 20.0
REPORT_INTERVAL = 5.0  # send log every 5 seconds

# MediaPipe
mp_face_mesh = mp.solutions.face_mesh

# Camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("❌ Camera not available")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Camera calibration for head pose
focal_length = width
center = (width / 2, height / 2)
camera_matrix = np.array([
    [focal_length, 0, center[0]],
    [0, focal_length, center[1]],
    [0, 0, 1]
], dtype="double")
dist_coeffs = np.zeros((4, 1))

# Track time
last_report_time = time.time()

# ==============================
# FUNCTIONS
# ==============================
def eye_aspect_ratio(eye_points):
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    C = np.linalg.norm(eye_points[0] - eye_points[3])
    return (A + B) / (2.0 * C) if C > 0 else 0.0

def get_head_pose(image_points):
    model_points = np.array([
        (0.0, 0.0, 0.0),
        (0.0, -330.0, -65.0),
        (-225.0, 170.0, -135.0),
        (225.0, 170.0, -135.0),
        (-150.0, -150.0, -125.0),
        (150.0, -150.0, -125.0)
    ])
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    rmat, _ = cv2.Rodrigues(rotation_vector)
    pose_mat = cv2.hconcat((rmat, translation_vector))
    _, _, _, _, _, _, eulerAngles = cv2.decomposeProjectionMatrix(pose_mat)
    return float(eulerAngles[0]), float(eulerAngles[1]), float(eulerAngles[2])

# ==============================
# MAIN LOOP
# ==============================
print("🎥 Monitoring started.... Press 'q' to quit")

with mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1) as face_mesh:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            lm = result.multi_face_landmarks[0].landmark
            def p(idx): return np.array([lm[idx].x * width, lm[idx].y * height], dtype=np.float64)

            # EAR
            left_eye_idx = [33, 160, 158, 133, 153, 144]
            right_eye_idx = [263, 387, 385, 362, 380, 373]
            left_eye = np.array([p(i) for i in left_eye_idx])
            right_eye = np.array([p(i) for i in right_eye_idx])
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2

            # Head pose
            image_points = np.array([p(1), p(152), p(33), p(263), p(61), p(291)])
            try:
                pitch, yaw, roll = get_head_pose(image_points)
            except:
                yaw = 0.0

            attentive = not (ear < EAR_THRESHOLD or abs(yaw) > YAW_THRESHOLD)
            state = "attentive" if attentive else "distracted"

            # Send log every interval
            now = time.time()
            if now - last_report_time >= REPORT_INTERVAL:
                payload = {"student_id": STUDENT_ID, "state": state}
                try:
                    requests.post(BACKEND_LOG_ENDPOINT, json=payload, timeout=1)
                    print(f"📡 Sent => {STUDENT_ID}: {state}")
                except Exception as e:
                    print("⚠️ Failed to send log:", e)

                last_report_time = now

            # Visual label
            cv2.putText(frame, state, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if attentive else (0, 0, 255), 2)

        cv2.imshow("Student Monitoring", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("🛑 Monitoring stopped.")
