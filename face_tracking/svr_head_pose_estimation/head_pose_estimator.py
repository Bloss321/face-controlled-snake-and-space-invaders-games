import cv2
import os
import csv
import pickle
import numpy as np
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import joblib


# stores face landmarks for each of the images from the dataset in csv file
def face_landmarks_for_dataset(undetectable_images: list, csv_file_path):
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

    # path wherever the AFLW200 images are stored. Could not store in folder due to space constraints
    directory = ".../AFLW2000"

    for filename in os.listdir(directory):
        if filename.endswith(".jpg") and filename not in undetectable_images:
            # read the image
            image_path = os.path.join(directory, filename)
            # read corresponding MAT file with image labels
            mat_file = image_path.replace("jpg", "mat")
            hpe_dict = get_hpe_image_info(mat_file)
            # [pitch, yaw, roll] angles
            hpe_data_list = [hpe_dict.get("pitch")[0], hpe_dict.get("yaw")[0], hpe_dict.get("roll")[0]]

            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image_rgb)

            if results.multi_face_landmarks:  # if MediaPipe is able to detect landmarks
                for facial_landmarks in results.multi_face_landmarks:
                    data_row = [filename] + hpe_data_list + list(
                        np.array([[point.x, point.y, point.z] for point in facial_landmarks.landmark]).flatten())

                    with open(csv_file_path, 'a', newline='') as file:
                        writer = csv.writer(file, delimiter=',')
                        writer.writerow(data_row)


def train_svr_model_with_data(csv_file_name):
    import pandas as pd
    data_frame = pd.read_csv(csv_file_name)
    hpe_angles = data_frame[['pitch', 'yaw', 'roll']].values
    landmarks = data_frame.drop(data_frame.columns[:4], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(landmarks, hpe_angles, test_size=0.2, random_state=42)

    # instantiate the SVR models
    svr_pitch = SVR(kernel='rbf', C=1.0, gamma='scale')
    svr_yaw = SVR(kernel='rbf', C=1.0, gamma='scale')
    svr_roll = SVR(kernel='rbf', C=1.0, gamma='scale')

    # then train the models
    svr_pitch.fit(X_train, y_train[:, 0])
    svr_yaw.fit(X_train, y_train[:, 1])
    svr_roll.fit(X_train, y_train[:, 2])

    # save trained svr models as .pkl files
    joblib.dump(svr_pitch, 'new_model/svr_pitch_model_2.pkl')
    joblib.dump(svr_yaw, 'new_model/svr_yaw_model_2.pkl')
    joblib.dump(svr_roll, 'new_model/svr_roll_model_2.pkl')

    # predict on test data
    pitch_pred = svr_pitch.predict(X_test)
    yaw_pred = svr_yaw.predict(X_test)
    roll_pred = svr_roll.predict(X_test)

    # evaluate model using mean squared error
    mse_pitch = mean_squared_error(y_test[:, 0], pitch_pred)
    mse_yaw = mean_squared_error(y_test[:, 1], yaw_pred)
    mse_roll = mean_squared_error(y_test[:, 2], roll_pred)

    # mean absolute error
    mae_pitch = mean_absolute_error(y_test[:, 0], pitch_pred)
    mae_yaw = mean_absolute_error(y_test[:, 1], yaw_pred)
    mae_roll = mean_absolute_error(y_test[:, 2], roll_pred)

    # r-squared value/ root mean squared value
    r2_pitch = r2_score(y_test[:, 0], pitch_pred)
    r2_yaw = r2_score(y_test[:, 1], yaw_pred)
    r2_roll = r2_score(y_test[:, 2], roll_pred)

    # print results and save to file
    print("Mean Squared Error (Pitch):", mse_pitch)
    print("Mean Squared Error (Yaw):", mse_yaw)
    print("Mean Squared Error (Roll):", mse_roll)

    print("Mean Absolute Error (Pitch):", mae_pitch)
    print("Mean Absolute Error (Yaw):", mae_yaw)
    print("Mean Absolute Error (Roll):", mae_roll)

    print("R-Squared Value (Pitch):", r2_pitch)
    print("R-Squared Value (Yaw):", r2_yaw)
    print("R-Squared Value (Roll):", r2_roll)

    print("X_train: ", X_train)
    print("X_test: ", X_test)
    print("y_train: ", y_train)
    print("y_test: ", y_test)


def face_tracker_using_model():
    pass


# load corresponding MAT file for each image, each AFLW2000 image has MAT file with HPE labels
def get_hpe_image_info(mat_file):
    from scipy.io import loadmat
    mat_data = loadmat(mat_file)  # load MAT file
    pose_params = mat_data['Pose_Para']

    pitch_angle = pose_params[:, 0]
    yaw_angle = pose_params[:, 1]
    roll_angle = pose_params[:, 2]

    hpe_dict = {
        "pitch": pitch_angle,
        "yaw": yaw_angle,
        "roll": roll_angle
    }
    return hpe_dict


# returns the list of undetectable images stored in "undetectable_images.txt" as these will not be used to train
def get_undetectable_images_from_file(image_txt_file):
    with open(image_txt_file, "r") as file:
        # read txt file line by line
        lines = file.readlines()
        image_list = [line.strip() for line in lines]
        return image_list


# function to store the head pose estimation and angle for the image's face-mesh landmarks
def initialise_file(csv_file_path):
    face_landmark_count = 468  # MediaPipe's face mesh model provides 468 landmarks
    # head orientation: pitch, yaw, roll
    face_landmarks_for_hpe = ['image name'] + ['pitch', 'yaw', 'roll']
    for landmark in range(1, face_landmark_count + 1):
        for landmark_coord in ['x', 'y', 'z']:
            face_landmarks_for_hpe.append(landmark_coord + str(landmark))

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(face_landmarks_for_hpe)


# returns list of images from AFLW2000-3D dataset where faces were not detected by MediaPipe's face-mesh model
def get_mp_undetectable_images():
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

    directory = "C:/Users/blchn/Documents/Bsc Computer Science/Year 4/Individual Project/Dataset Images/AFLW2000"

    undetectable_images = []

    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            # Read the image
            image_path = os.path.join(directory, filename)
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image_rgb)

            if not results.multi_face_landmarks:
                undetectable_images.append(filename)

    output_file = "undetectable_images.txt"
    with open(output_file, "w") as file:
        for img in undetectable_images:
            file.write(img + "\n")

    print("List of undetected images written to", output_file)
    # return undetectable_images


def check_svr_model_with_tracker():

    # Load SVR models from .pkl files
    svr_pitch = joblib.load('svr_pitch_model.pkl')
    svr_yaw = joblib.load('svr_yaw_model.pkl')
    svr_roll = joblib.load('svr_roll_model.pkl')

    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing_utils = mp.solutions.drawing_utils
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # flip frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True
        rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            # Extract landmarks from the first detected face
            landmarks = results.multi_face_landmarks[0].landmark

            # Extract 3D coordinates of facial landmarks
            landmarks_3d = np.array([[lm.x, lm.y, lm.z] for lm in landmarks]).flatten()

            # Predict head pose angles using SVR models
            pitch = np.degrees(svr_pitch.predict([landmarks_3d])[0])
            yaw = np.degrees(svr_yaw.predict([landmarks_3d])[0])
            roll = np.degrees(svr_roll.predict([landmarks_3d])[0])

            direction = "neutral"

            if roll > 15:   # testing values to ensure that the head pose estimator works
                direction = "lean right"
            elif roll < -15:
                direction = "lean left"
            elif pitch > 20:
                direction = "up"
            elif pitch < -20:
                direction = "down"
            elif yaw > 30:
                direction = "right"
            elif yaw < -30:
                direction = "left"

            # Optionally, visualize predicted head pose angles on the frame
            cv2.putText(frame, f' Direction: {direction} Pitch: {pitch:.2f}, Yaw: {yaw:.2f}, Roll: {roll:.2f}',
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the frame
        cv2.imshow('Head Pose Estimation', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # create csv file to hold data from dataset for testing & training
    initialise_file('hpe_face_landmarks.csv')

    # run dataset images through MediaPipe's face-mesh dectector
    # filter out the undetectable images so that they won't be used for traning
    undetectable_images = get_undetectable_images_from_file('undetectable_images.txt')

    # corresponding face landmarks for the dataset
    face_landmarks_for_dataset(undetectable_images, 'hpe_face_landmarks.csv')

    train_svr_model_with_data('hpe_face_landmarks.csv')

    # test trained model in real-time with webcam
    check_svr_model_with_tracker()

