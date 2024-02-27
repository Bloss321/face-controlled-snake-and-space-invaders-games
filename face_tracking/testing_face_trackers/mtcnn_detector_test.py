import time
from statistics import mean

import cv2
import psutil
from mtcnn import MTCNN

# Uses deep learning - MTCNN model


def main():
    # Initialize the MTCNN face detection model
    detector = MTCNN()

    # Open a video capture object (0 for default camera)
    cap = cv2.VideoCapture('medium, head movements.mp4')  # Use 0 for default camera or specify the video file path
    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Unable to open the video file.")
        exit()

    execution_times = []
    cpu_usage = []
    memory_usage = []

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()

        if not ret:
            break

        # Measure the execution time for face detection
        start_time = time.time()

        # Before face detection starts
        initial_cpu_usage = psutil.cpu_percent()
        initial_memory_usage = psutil.virtual_memory().percent

        # Detect faces using MTCNN
        faces = detector.detect_faces(frame)

        # Calculate the execution time
        execution_time = time.time() - start_time
        execution_times.append(execution_time)

        # After face detection completes
        final_cpu_usage = psutil.cpu_percent()
        final_memory_usage = psutil.virtual_memory().percent

        # Draw rectangles around the detected faces
        for face in faces:
            x, y, width, height = face['box']
            cv2.rectangle(frame, (x, y), (x+width, y+height), (255, 0, 0), 2)

        # Display the frame with face rectangles
        cv2.imshow('Face Detection', frame)


        # Calculate differences
        cpu_usage_difference = final_cpu_usage - initial_cpu_usage
        memory_usage_difference = final_memory_usage - initial_memory_usage

        cpu_usage.append(cpu_usage_difference)
        memory_usage.append(memory_usage_difference)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()
    # calculate & print the average execution times
    avg_execution_time = mean(execution_times)
    print("Average execution time: " + str(round(avg_execution_time, 3)) + " seconds")
    print("\n")
    print("Average Cpu usage difference " + str(mean(cpu_usage)))
    print("Average memory usage difference " + str(mean(memory_usage)))


if __name__ == "__main__":
    main()

# Notes on performance:

# very laggy and slow
# computationally intensive
# kinda works with extreme lighting
# seems to work a little with occlusion

