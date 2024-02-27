import mediapipe as mp
import cv2

# Replace with your actual landmarks
landmarks = {
    'rightEyebrowUpper': [156, 70, 63, 105, 66, 107, 55, 193],
    'rightEyebrowLower': [35, 124, 46, 53, 52, 65],
    'leftEyebrowUpper': [383, 300, 293, 334, 296, 336, 285, 417],
    'leftEyebrowLower': [265, 353, 276, 283, 282, 295]
}

def calculate_vertical_distance(landmarks, eyebrow_type):
    upper_points = landmarks[f'{eyebrow_type}Upper']
    lower_points = landmarks[f'{eyebrow_type}Lower']

    # Calculate the vertical distance between upper and lower eyebrow points
    distance = sum([landmarks[point][1] for point in upper_points]) / len(upper_points) - \
               sum([landmarks[point][1] for point in lower_points]) / len(lower_points)

    return distance

def are_eyebrows_raised(landmarks, threshold=10):
    # Calculate the vertical distances for both eyebrows
    right_eyebrow_distance = calculate_vertical_distance(landmarks, 'rightEyebrow')
    left_eyebrow_distance = calculate_vertical_distance(landmarks, 'leftEyebrow')

    # Check if either of the eyebrows is raised based on the threshold
    return right_eyebrow_distance > threshold and left_eyebrow_distance > threshold

def main():
    cap = cv2.VideoCapture(0)
    with mp.solutions.face_mesh.FaceMesh() as face_mesh:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Perform face mesh detection
            result = face_mesh.process(frame)
            if result.multi_face_landmarks:
                for face_landmarks in result.multi_face_landmarks:
                    # Extract landmark points for each eyebrow
                    landmarks_dict = {}
                    for idx, point in enumerate(face_landmarks.landmark):
                        landmarks_dict[idx] = {'x': point.x, 'y': point.y}

                    # Check if eyebrows are raised
                    if are_eyebrows_raised(landmarks_dict):
                        print("Eyebrows raised!")
                        cv2.putText(frame, "Eyebrows raised!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
