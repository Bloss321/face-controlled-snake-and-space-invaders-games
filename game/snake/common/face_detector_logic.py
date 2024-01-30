import cv2
import dlib

from game.snake.common.helper import Direction
from _dlib_pybind11 import shape_predictor
import math
from statistics import mean


# for detecting head movements
def translate_head_movement(initial_point, new_point, last_direction):
    direction = last_direction  # if no direction is detected, snake continues in previous direction
    # check if movement is left/right if change in x-axis > change in y
    if abs(new_point[0] - initial_point[0]) > abs(new_point[1] - initial_point[1]):
        if new_point[0] - initial_point[0] < -20:  # was all 30 - now 20
            direction = Direction.LEFT
        elif new_point[0] - initial_point[0] > 20:
            direction = Direction.RIGHT
    # check if movement is up/down - change in y-axis > change in x
    elif abs(new_point[1] - initial_point[1]) > abs(new_point[0] - initial_point[0]):
        if new_point[1] - initial_point[1] < -20:
            direction = Direction.UP  # switched round
        elif new_point[1] - initial_point[1] > 20:
            direction = Direction.DOWN
    return direction


# for detecting if the mouth is open
# if threshold > 1.75, mouth is open???
def is_mouth_open(threshold, face: shape_predictor):  # threshold is 1.5 when closed, > 1.75 when open
    mar = mouth_aspect_ratio(face)
    if mar > threshold:
        return True
    else:
        return False


# calculates the mouth aspect ratio
def mouth_aspect_ratio(face: shape_predictor):  # threshold is 0.79
    a = euclidean_dist(face.part(50), face.part(60))
    b = euclidean_dist(face.part(51), face.part(59))
    c = euclidean_dist(face.part(52), face.part(58))
    d = euclidean_dist(face.part(53), face.part(57))
    e = euclidean_dist(face.part(54), face.part(56))
    horizontal = euclidean_dist(face.part(49), face.part(55))

    ratio = (a + b + c + d + e) / (2 * horizontal)

    return ratio


def euclidean_dist(p, q):
    p_arr = [p.x, p.y]
    q_arr = [q.x, q.y]
    return math.dist(p_arr, q_arr)


# for detecting eyebrow raises

def are_eyebrows_raised(threshold, face: shape_predictor):  # tuple of new & old eyebrow coordinate arrays??
    right_eyebrow = eyebrow_points(face, 18, 22)  # right eyebrow: landmarks 18-22
    left_eyebrow = eyebrow_points(face, 23, 27)  # left eyebrow: landmarks 23-27

    right_eyebrow_landmarks_mean = sum(right_eyebrow) / 2
    left_eyebrow_landmarks_mean = sum(left_eyebrow) / 2

    # should really have a threshold for the x points??? what if someone moves from left to right??
    # how do we anticipate the threshold if someone is moving the head around in the game?
    # do I also take in a direction - different threshold points based on this?
    if right_eyebrow_landmarks_mean > threshold and left_eyebrow_landmarks_mean > threshold:
        return [True, right_eyebrow_landmarks_mean, left_eyebrow_landmarks_mean]
    # raised = 585
    # lowered = 590 - 600
    else:
        return [False, right_eyebrow_landmarks_mean, left_eyebrow_landmarks_mean]


def eyebrow_points(face: shape_predictor, start, end):
    landmark_points = []
    for landmark in range(start, end + 1):
        landmark_points.append(face.part(landmark).y)
    return landmark_points


def detect_smile(face: shape_predictor, threshold):
    ratio = detect_smile_ratio(face)

    if ratio > threshold:
        return True
    else:
        return False


def detect_smile_ratio(face: shape_predictor):
    left_corner = face.part(49)
    right_corner = face.part(55)

    smile_width = abs(left_corner.x - right_corner.x)
    jaw_width = abs(face.part(3).x - face.part(15).x)

    ratio = smile_width/jaw_width

    return ratio


# rescale output video showing facial landmarks
def resize_video_output(frame, scale):  # scale given as decimal e.g. 0.75
    height = int(frame.shape[0] * scale)
    width = int(frame.shape[1] * scale)
    new_dimension = (width, height)
    return cv2.resize(frame, new_dimension, interpolation=cv2.INTER_AREA)


class Calibrate:
    # vid_capture = cv2.VideoCapture(0)
    face_detector = dlib.get_frontal_face_detector()
    face_landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def general_calibration(self, vid_capture):
        print("Has started working")
        window_name = "Calibration"
        smile_ratios = []  # smile calibration
        nose_points_x = []  # centre of nose calibration - x
        nose_points_y = []  # centre of nose calibration - y
        mouth_aspect_ratios = []  # mouth opening calibration
        counter = 0

        while counter < 100:
            x, frame = vid_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_detector(gray)
            for face in faces:

                face_landmarks = self.face_landmark_predictor(gray, face)

                # for centre of nose
                centre = face_landmarks.part(30)
                nose_points_x.append(centre.x)
                nose_points_y.append(centre.y)

                # for smile
                smile_ratio = detect_smile_ratio(face_landmarks)
                smile_ratios.append(smile_ratio)

                # for mouth opening
                mar = mouth_aspect_ratio(face_landmarks)
                mouth_aspect_ratios.append(mar)

                for n in range(0, 68):
                    x = face_landmarks.part(n).x
                    y = face_landmarks.part(n).y
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), 1)

            cv2.imshow(window_name, frame)
            counter += 1

            key = cv2.waitKey(1)
            if key == 27:
                break

        vid_capture.release()
        cv2.destroyAllWindows()

        avg_centre_x = mean(nose_points_x)
        avg_centre_y = mean(nose_points_y)
        avg_centre = (avg_centre_x + (0.1 * avg_centre_x), avg_centre_y + (0.1 * avg_centre_y))

        avg_smile_ratio = mean(smile_ratios)
        avg_mouth_aspect_ratio = mean(mouth_aspect_ratios)

        # add 10% to the result
        calibration_dict = {
            "centre_of_nose": avg_centre,
            "smile threshold": avg_smile_ratio + (0.1 * avg_smile_ratio),
            "mouth_open_threshold": avg_mouth_aspect_ratio + (0.2 * avg_mouth_aspect_ratio)
        }

        return calibration_dict
