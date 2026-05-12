# attention.py
import numpy as np
import math


# EAR (eye aspect ratio) helpers
def eye_aspect_ratio(eye):
# eye: array of 6 (x,y) points (2D)
A = np.linalg.norm(eye[1] - eye[5])
B = np.linalg.norm(eye[2] - eye[4])
C = np.linalg.norm(eye[0] - eye[3])
if C == 0:
return 0.0
ear = (A + B) / (2.0 * C)
return ear


# head pose helper (solvePnP)
def get_head_pose(image_points, camera_matrix, dist_coeffs=np.zeros((4,1))):
# 3D model points of a generic face
model_points = np.array([
(0.0, 0.0, 0.0), # nose tip
(0.0, -330.0, -65.0), # chin
(-225.0, 170.0, -135.0), # left eye corner
(225.0, 170.0, -135.0), # right eye corner
(-150.0, -150.0, -125.0), # left mouth corner
(150.0, -150.0, -125.0) # right mouth corner
], dtype=np.float64)


success, rotation_vector, translation_vector = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
rmat, _ = cv2.Rodrigues(rotation_vector)
pose_mat = cv2.hconcat((rmat, translation_vector))
_, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
pitch, yaw, roll = [float(angle) for angle in euler_angles]
return (pitch, yaw, roll), rotation_vector, translation_vecto