import cv2
import mediapipe as mp
from mediapipe.python.solutions.face_mesh import FaceMesh

from game.snake.common.helper import Direction

from statistics import mean


# create a check/determine movement class
# global boolean variables
# is_smiling
#

# for detecting head movements, returns a Direction
def mp_translate_head_movement(initial_point: tuple, current_point: tuple, last_direction):
    # Calculate the angles for head movement detection
    head_movement_up_down = initial_point[1] - current_point[1]  # y coordinates  # e.g. nose_landmark.y
    head_movement_left_right = initial_point[0] - current_point[0]  # x coordinates

    direction = last_direction
    if abs(head_movement_up_down) > abs(head_movement_left_right):
        if head_movement_up_down > 0.03:
            direction = Direction.UP
        elif head_movement_up_down < -0.03:
            direction = direction.DOWN
    elif abs(head_movement_left_right) > abs(head_movement_up_down):
        if head_movement_left_right > 0.03:
            direction = direction.LEFT
        elif head_movement_left_right < -0.03:
            direction = direction.RIGHT
    return direction


def is_mouth_open(upper_lip_landmarks: list, lower_lip_landmarks: list, last_avg_inner_lips_dist):
    # find the absolute distances between corresponding landmarks for the upper & lower inner lips
    lips_inner_dist = [abs(x - y) for x, y in zip(lower_lip_landmarks, upper_lip_landmarks)]
    mean_lips_inner_dist = mean(lips_inner_dist)

    if mean_lips_inner_dist - last_avg_inner_lips_dist > 0.018:
        return True
    else:
        return False


# return boolean
def are_eyebrows_raised():
    pass


def is_smiling(threshold, face_mesh: FaceMesh):
    pass


# rescale output video showing facial landmarks
def resize_video_output(frame, scale):  # scale given as decimal e.g. 0.75
    height = int(frame.shape[0] * scale)
    width = int(frame.shape[1] * scale)
    new_dimension = (width, height)
    return cv2.resize(frame, new_dimension, interpolation=cv2.INTER_AREA)


class Calibrate:
    # mp_face_detection = mp.solutions.face_detection
    # mp_face_mesh = mp.solutions.face_mesh

    def general_calibration(self, vid_capture, face_mesh, mp_face_mesh):
        print("Has started working")

        neutral_positions = {
            "avg_left_eyebrow": [],
            "avg_right_eyebrow": [],
            "nose_tip_x": [],
            "nose_tip_y": [],
            "avg_lips_inner_dist": []

        }

        calibrate_message = "Calibrating neutral face position. Please keep your face neutral for a few seconds."
        calibrate_message += " Press 'q' to finish calibration."

        # Perform face mesh detection for calibration
        while len(neutral_positions["nose_tip_x"]) < 200:  # Collect neutral data for a few seconds
            ret, frame = vid_capture.read()
            if not ret:
                break

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform face mesh detection
            mesh_results = face_mesh.process(rgb_frame)

            if mesh_results.multi_face_landmarks:
                for landmarks in mesh_results.multi_face_landmarks:
                    # Extract specific facial landmarks for calibration

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
                    lips_inner_dist = [abs(x - y) for x, y in
                                       zip(lips_lower_inner_landmarks, lips_upper_inner_landmarks)]
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
                    neutral_positions["avg_left_eyebrow"].append(mean(left_eyebrow_landmarks))
                    neutral_positions["avg_right_eyebrow"].append(mean(right_eyebrow_landmarks))
                    neutral_positions["nose_tip_x"].append(nose_landmark.x)
                    neutral_positions["nose_tip_y"].append(nose_landmark.y)
                    neutral_positions["avg_lips_inner_dist"].append(mean_lips_inner_dist)

                    # draw the face mesh
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

            # Display calibration instructions
            cv2.putText(frame, calibrate_message, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Display the output frame
            cv2.imshow("Face Calibration", frame)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Calculate average values for neutral face position

        calibration_dict = {
            "centre_of_nose": "centre",
            "smile threshold": 0.54,
            "mouth_open_threshold": 0.018
        }

        neutral_face_position = {
            key: sum(values) / len(values) for key, values in neutral_positions.items()
        }

        # vid_capture.release()
        cv2.destroyAllWindows()  # rather than destroying window; return this value too and use it
        print("Calibration complete. You can now perform facial movements.")
        return neutral_face_position

    def __mean_lip_dist(self):
        pass
