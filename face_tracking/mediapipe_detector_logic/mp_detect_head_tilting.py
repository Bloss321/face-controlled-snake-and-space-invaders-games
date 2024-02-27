import cv2
import mediapipe as mp
import numpy as np


def detect_head_tilt():
    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe Face Mesh
            results = face_mesh.process(rgb_frame)

            # Draw landmarks on the face
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    # Extract relevant facial landmarks for head pose estimation
                    landmarks = np.array([[point.x, point.y, point.z] for point in face_landmarks.landmark])
                    # Calculate the direction vectors for roll (tilting)
                    roll_vector = landmarks[33] - landmarks[2]
                    # Calculate angles using dot products
                    roll_angle = np.arcsin(roll_vector[0] / np.linalg.norm(roll_vector))
                    # Convert angles from radians to degrees
                    roll_degrees = np.degrees(roll_angle)
                    # Display tilt angles
                    cv2.putText(frame, f"Roll: {roll_degrees:.2f}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                                2)
                    print(roll_degrees)
                    print("\n\n")

                    # check for tilting for directions
                    direction = "neutral"
                    if roll_degrees >= -25:
                        direction = "right"
                    if roll_degrees <= -40:
                        direction = "left"

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
                    # Visualize the results on the frame
                    cv2.putText(frame, "some text", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # Display the frame
            cv2.imshow('Head Pose Estimation', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_head_tilt()
