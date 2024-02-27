from statistics import mean
import cv2
import dlib
import time


# facial landmark detection (HOG)
# + SVM??

class DlibFacialLandmarkDetector:
    def __init__(self, video, num_of_landmarks):
        self.video = video
        self.num_of_landmarks = num_of_landmarks

    def run_detector(self):
        vid_capture = cv2.VideoCapture(self.video)
        face_detector = dlib.get_frontal_face_detector()
        face_landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        execution_times = []

        while True:
            x, frame = vid_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Measure the execution time for face detection
            start_time = time.time()

            faces = face_detector(gray)

            # Calculate the execution time
            execution_time = time.time() - start_time
            execution_times.append(execution_time)

            for face in faces:

                face_landmarks = face_landmark_predictor(gray, face)

                for n in range(0, self.num_of_landmarks):
                    x = face_landmarks.part(n).x
                    y = face_landmarks.part(n).y
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), 1)

            cv2.imshow("Face Landmarks", frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

        vid_capture.release()
        cv2.destroyAllWindows()
        # calculate & print the average execution times
        avg_execution_time = mean(execution_times)
        print("Average execution time: " + str(round(avg_execution_time, 3)) + " seconds")


if __name__ == "__main__":
    detector = DlibFacialLandmarkDetector(0, 68)
    detector.run_detector()

# Notes on performance:

# Works better than haar cascades model
# fairly low performance with dark skin
# seems speedy - need to check
# does not work with extreme head movements
# works well even with occlusion (hand in face)
