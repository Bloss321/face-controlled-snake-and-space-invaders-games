from statistics import mean

import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh


# needs to be an option to re-calibrate if the user presses r: game will pause as re-calibration occurs
def calibrate_neutral_face(face_mesh, cap):
    # to detect eyebrow movement calculate diff between top of eye & top of eyebrow
    # to detect mouth open, check if the average vertical dist between upper & lower inner lips is >5%?
    #   lipsUpperInner: [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
    #   lipsLowerInner: [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
    neutral_positions = {
        "left_eye_y": [],
        "right_eye_y": [],
        "left_eye_x": [],
        "right_eye_x": [],
        "avg_left_eyebrow": [],
        "avg_right_eyebrow": [],
        "nose_tip_x": [],
        "nose_tip_y": [],
        "avg_lips_inner_dist": []

    }

    calibrate_message = "Calibrating neutral face position. Please keep your face neutral for a few seconds."
    calibrate_message += " Press 'q' to finish calibration."

    # Perform face mesh detection for calibration
    while len(neutral_positions["nose_tip_x"]) < 200:  # Collect neutral data for a few seconds, change to checking the nose_tip data
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform face mesh detection
        mesh_results = face_mesh.process(rgb_frame)

        if mesh_results.multi_face_landmarks:
            for landmarks in mesh_results.multi_face_landmarks:
                # Extract specific facial landmarks for calibration
                left_eye_landmark = landmarks.landmark[386]  # Left eye top
                right_eye_landmark = landmarks.landmark[159]  # Right eye top

                nose_landmark = landmarks.landmark[4]  # centre of nose

                # mesh landmark locations for upper & lower inner lips
                mesh_lips_upper_inner = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
                mesh_lips_lower_inner = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

                lips_upper_inner_landmarks = []
                for lip_landmark in mesh_lips_upper_inner:
                    lips_upper_inner_landmarks.append(landmarks.landmark[lip_landmark].y)
                lips_lower_inner_landmarks = []
                for lips_landmark in mesh_lips_lower_inner:
                    lips_lower_inner_landmarks.append(landmarks.landmark[lips_landmark].y)

                # find the absolute distances between corresponding landmarks for the upper & lower inner lips
                lips_inner_dist = [abs(x - y) for x, y in zip(lips_lower_inner_landmarks, lips_upper_inner_landmarks)]
                mean_lips_inner_dist = mean(lips_inner_dist)

                # check if eyebrows are raised
                mesh_eyebrow_left = [383, 300, 293, 334, 296, 336, 285, 417]
                mesh_eyebrow_right = [156, 70, 63, 105, 66, 107, 55, 193]

                left_eyebrow_landmarks = []
                for eyebrow_landmark in mesh_eyebrow_left:
                    left_eyebrow_landmarks.append(landmarks.landmark[eyebrow_landmark].y)
                right_eyebrow_landmarks = []
                for eyebrow_landmark in mesh_eyebrow_right:
                    right_eyebrow_landmarks.append(landmarks.landmark[eyebrow_landmark].y)

                # Store neutral face position data
                neutral_positions["left_eye_y"].append(left_eye_landmark.y)
                neutral_positions["right_eye_y"].append(right_eye_landmark.y)
                neutral_positions["left_eye_x"].append(left_eye_landmark.x)
                neutral_positions["right_eye_x"].append(right_eye_landmark.x)
                neutral_positions["avg_left_eyebrow"].append(mean(left_eyebrow_landmarks))
                neutral_positions["avg_right_eyebrow"].append(mean(right_eyebrow_landmarks))
                neutral_positions["nose_tip_x"].append(nose_landmark.x)
                neutral_positions["nose_tip_y"].append(nose_landmark.y)
                neutral_positions["avg_lips_inner_dist"].append(mean_lips_inner_dist)

        # Display calibration instructions
        cv2.putText(frame, calibrate_message, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Display the output frame
        cv2.imshow("Face Calibration", frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Calculate average values for neutral face position

    neutral_face_position = {
        key: sum(values) / len(values) for key, values in neutral_positions.items()
    }

    print("Calibration complete. You can now perform facial movements.")
    cv2.destroyAllWindows()  # rather than destroying window; return this value too and use it
    return neutral_face_position


def main():
    # Initialize MediaPipe Face Detection module
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.3)

    # Initialize MediaPipe Face Mesh module
    face_mesh = mp_face_mesh.FaceMesh()

    # OpenCV video capture
    cap = cv2.VideoCapture(0)  # Use 0 for default camera or specify the video file path

    # Calibrate neutral face position
    neutral_face_position = calibrate_neutral_face(face_mesh, cap)
    # print(neutral_face_position)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform face detection
        detection_results = face_detection.process(rgb_frame)

        # Perform face mesh detection
        mesh_results = face_mesh.process(rgb_frame)

        if mesh_results.multi_face_landmarks:
            for landmarks in mesh_results.multi_face_landmarks:
                # Extract specific facial landmarks for analysis
                left_eye_landmark = landmarks.landmark[159]  # Left eye top
                right_eye_landmark = landmarks.landmark[145]  # Right eye top
                nose_landmark = landmarks.landmark[4]  # centre of nose

                # Calculate the angles for head movement detection
                head_movement_up_down = neutral_face_position.get("nose_tip_y") - nose_landmark.y
                head_movement_left_right = neutral_face_position.get("nose_tip_x") - nose_landmark.x

                # calculate the distances for neutral

                min_head_up_down_diff = abs(0.01 * neutral_face_position.get("nose_tip_y")) + neutral_face_position.get(
                    "nose_tip_y")
                min_head_left_right_diff = abs(
                    0.01 * neutral_face_position.get("nose_tip_x")) + neutral_face_position.get("nose_tip_x")

                # check if mouth open
                # mesh landmark locations for upper & lower inner lips
                mesh_lips_upper_inner = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
                mesh_lips_lower_inner = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

                lips_upper_inner_landmarks = []
                for lip_landmark in mesh_lips_upper_inner:
                    lips_upper_inner_landmarks.append(landmarks.landmark[lip_landmark].y)
                lips_lower_inner_landmarks = []
                for lips_landmark in mesh_lips_lower_inner:
                    lips_lower_inner_landmarks.append(landmarks.landmark[lips_landmark].y)

                # find the absolute distances between corresponding landmarks for the upper & lower inner lips
                lips_inner_dist = [abs(x - y) for x, y in zip(lips_lower_inner_landmarks, lips_upper_inner_landmarks)]
                mean_lips_inner_dist = mean(lips_inner_dist)

                # check if eyebrows are raised
                mesh_eyebrow_left = [383, 300, 293, 334, 296, 336, 285, 417]
                mesh_eyebrow_right = [156, 70, 63, 105, 66, 107, 55, 193]

                left_eyebrow_landmarks = []
                for eyebrow_landmark in mesh_eyebrow_left:
                    left_eyebrow_landmarks.append(landmarks.landmark[eyebrow_landmark].y)
                right_eyebrow_landmarks = []
                for eyebrow_landmark in mesh_eyebrow_right:
                    right_eyebrow_landmarks.append(landmarks.landmark[eyebrow_landmark].y)

                mean_left_eyebrow = mean(left_eyebrow_landmarks)
                mean_right_eyebrow = mean(right_eyebrow_landmarks)

                left_eyebrow_diff = abs(mean_left_eyebrow - neutral_face_position.get("avg_left_eyebrow"))
                right_eyebrow_diff = abs(mean_right_eyebrow - neutral_face_position.get("avg_right_eyebrow"))

                # Output messages based on movements
                movement_message = "Head in centre"
                if abs(head_movement_up_down) > abs(head_movement_left_right):
                    if head_movement_up_down > 0.03:
                        movement_message = "Head turned up" + str(head_movement_up_down)
                    elif head_movement_up_down < -0.03:
                        movement_message = "Head turned down" + str(head_movement_up_down)
                elif abs(head_movement_left_right) > abs(head_movement_up_down):
                    # movement_message = "head in centre"
                    if head_movement_left_right > 0.04:
                        movement_message = "Head turned right " + str(head_movement_left_right)
                    elif head_movement_left_right < -0.04:
                        movement_message = "Head turned left " + str(head_movement_left_right)
                else:
                    movement_message = "No significant movement " + str(head_movement_up_down) + " " + str(
                        min_head_up_down_diff)

                # have a check for eyebrows_raised by checking that head had not moved up/down
                # possibly that the difference in the nose isn't too much
                if movement_message == "Head in centre" and left_eyebrow_diff > 0.01 and right_eyebrow_diff > 0.014:
                    # if left_eyebrow_diff > 0.01 and right_eyebrow_diff > 0.014 and 0.01 > head_movement_up_down >
                    # -0.03:
                    movement_message = "Eyebrows raised"

                if mean_lips_inner_dist - neutral_face_position.get("avg_lips_inner_dist") > 0.018:
                    movement_message = "Mouth opened"

                # check if person is smiling
                def detect_smile(threshold):
                    ratio = detect_smile_ratio()

                    if ratio > threshold:
                        return True
                    else:
                        return False

                def detect_smile_ratio():
                    left_corner = landmarks.landmark[61]
                    right_corner = landmarks.landmark[291]

                    smile_width = abs(left_corner.x - right_corner.x)
                    # landmarks for the top of the jaw on either side of the face
                    jaw_width = abs(landmarks.landmark[147].x - landmarks.landmark[401].x)

                    ratio = smile_width / jaw_width

                    return ratio

                if detect_smile(0.54):
                    movement_message = "Smiling " + str(detect_smile_ratio())

                for connection in mp_face_mesh.FACEMESH_TESSELATION:
                    edge1, edge2 = connection
                    start_point = landmarks.landmark[edge1]
                    end_point = landmarks.landmark[edge2]

                    # Convert normalized coordinates to pixel coordinates
                    ih, iw, _ = frame.shape
                    start_x, start_y = int(start_point.x * iw), int(start_point.y * ih)
                    end_x, end_y = int(end_point.x * iw), int(end_point.y * ih)

                    # Draw line between landmarks
                    cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

                # Visualize the results on the frame
                cv2.putText(frame, movement_message, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Display the output frame
        cv2.imshow("Face Detection and Analysis", frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture and close all windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
