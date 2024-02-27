import face_recognition
import cv2
import time
from statistics import mean

# face_recognition uses HoG + SVM + CNN (mostly for recognition, but also for landmark detection??)
# apparently uses MTCNN - need to double-check this


def main():
    # Open a video capture object (0 for default camera)
    cap = cv2.VideoCapture(0)
    execution_times = []

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()

        # Measure the execution time for face detection
        start_time = time.time()

        # Find all face locations in the frame
        face_locations = face_recognition.face_locations(frame)

        # Calculate the execution time
        execution_time = time.time() - start_time
        execution_times.append(execution_time)

        # Draw rectangles around the detected faces
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

        # Display the frame with face rectangles
        cv2.imshow('Face Detection', frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()
    # calculate & print the average execution times
    avg_execution_time = mean(execution_times)
    print("Average execution time: " + str(round(avg_execution_time, 3)) + " seconds")


if __name__ == "__main__":
    main()

# Notes on performance:

# pretty accurate
# speed?
# works fairly well with occlusion - not as good as Mediapipe
# works better than non CNN models with illumination, but fails a little with extreme lighting
