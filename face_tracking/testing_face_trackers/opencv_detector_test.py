import time
from statistics import mean

import cv2
import psutil


# Opencv uses the Viola Jones Haar Cascade Classifier
# Eigen-faces, Fisher-faces and LBPH typically used for facial recognition

def main():

    # Load the pre-trained Haar Cascade face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Measure the execution time for face detection
        start_time = time.time()

        # Before face detection starts
        initial_cpu_usage = psutil.cpu_percent()
        initial_memory_usage = psutil.virtual_memory().percent

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # After face detection completes
        final_cpu_usage = psutil.cpu_percent()
        final_memory_usage = psutil.virtual_memory().percent

        # Calculate the execution time
        execution_time = time.time() - start_time
        execution_times.append(execution_time)

        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

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

# very inaccurate, only detects my face in high lighting
# not great for dark skin, also skin seems to blend with the background
# seems pretty fast - still need to check
# cannot handle occlusion at all
