import cv2
import mediapipe as mp
import numpy as np

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh


def head_pose_estimator():
    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        ret, frame = cap.read()
        if not ret:
            print("Capture not readable")

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.mult_face_landmarks:
                for face_landmarks in mp_face_mesh.FACEMESH_TESSELATION:

                    # draw the face mesh
                    for connection in mp_face_mesh.FACEMESH_TESSELATION:
                        edge1, edge2 = connection
                        start_point = face_landmarks.landmark[edge1]
                        end_point = face_landmarks.landmark[edge2]
                        # Convert normalized coordinates to pixel coordinates
                        ih, iw, _ = frame.shape
                        start_x, start_y = int(start_point.x * iw), int(start_point.y * ih)
                        end_x, end_y = int(end_point.x * iw), int(end_point.y * ih)
                        # Draw line between landmarks
                        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

                    # relevant 2D face landmarks for head pose estimation
                    right_eye_outer_corner = face_landmarks.landmark[33]
                    left_eye_outer_corner = face_landmarks.landmark[263]
                    right_lip_outer_corner = face_landmarks.landmark[61]
                    left_lip_outer_corner = face_landmarks.landmark[291]
                    chin = face_landmarks.landmark[199]
                    centre_of_nose = 1

                    landmarks_1 = [33, 263, 61, 291, 199, 1]
                    relevant_landmarks = []
                    # convert to 3d landmarks - world coordinates?
                    for mark in landmarks_1:
                        landmark = face_landmarks.landmark[mark]
                        relevant_landmarks.append((landmark.x, landmark.y, landmark.z))

                    # convert to 3D landmarks
                    # relevant_landmarks = np.array([[point.x, point.y, point.z] for point in face_landmarks.landmark])

                    # calibrate camera





