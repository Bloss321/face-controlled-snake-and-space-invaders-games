from statistics import mean
import cv2
import dlib
import time

import psutil


# facial landmark detection (HOG)
# + SVM??

class DlibFacialLandmarkDetector:
    def __init__(self, video, num_of_landmarks):
        self.video = video
        self.num_of_landmarks = num_of_landmarks

    def run_detector(self):
        vid_capture = cv2.VideoCapture(self.video)
        if not vid_capture.isOpened():
            print("Error: Unable to open the video file.")
            exit()
        face_detector = dlib.get_frontal_face_detector()
        face_landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        execution_times = []
        cpu_usage = []
        memory_usage = []

        while True:
            x, frame = vid_capture.read()
            # if the video is over, break the loop
            if not x:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Measure the execution time for face detection
            start_time = time.time()

            # Before face detection starts
            initial_cpu_usage = psutil.cpu_percent()
            initial_memory_usage = psutil.virtual_memory().percent

            faces = face_detector(gray)

            # After face detection completes
            final_cpu_usage = psutil.cpu_percent()
            final_memory_usage = psutil.virtual_memory().percent

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

            # Calculate differences
            cpu_usage_difference = final_cpu_usage - initial_cpu_usage
            memory_usage_difference = final_memory_usage - initial_memory_usage

            cpu_usage.append(cpu_usage_difference)
            memory_usage.append(memory_usage_difference)

            key = cv2.waitKey(1)
            if key == 27:
                break

        vid_capture.release()
        cv2.destroyAllWindows()
        # calculate & print the average execution times
        avg_execution_time = mean(execution_times)
        print("Average execution time: " + str(round(avg_execution_time, 3)) + " seconds")
        print("\n")
        print("Average Cpu usage difference " + str(mean(cpu_usage)))
        print("Average memory usage difference " + str(mean(memory_usage)))


if __name__ == "__main__":
    detector = DlibFacialLandmarkDetector('medium, head movements.mp4', 68)
    detector.run_detector()

# Notes on performance:

# Works better than haar cascades model
# fairly low performance with dark skin
# seems speedy - need to check
# does not work with extreme head movements
# works well even with occlusion (hand in face)
