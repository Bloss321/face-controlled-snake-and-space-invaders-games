import time
from statistics import mean

import cv2
from deepface import DeepFace


# DeepFace uses MTCNN

def main():
    # Open a video capture object (0 for default camera)
    cap = cv2.VideoCapture('medium, head movements.mp4')
    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Unable to open the video file.")
        exit()

    execution_times = []

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()

        if not ret:  # added
            break

        # Measure the execution time for face detection
        start_time = time.time()

        # Use deepface to detect faces in the frame
        result = DeepFace.extract_faces(frame, enforce_detection=False)

        # Calculate the execution time
        execution_time = time.time() - start_time
        execution_times.append(execution_time)

        # Check if a face was detected
        d: list[(str, any)] = list(result[0].items())
        facial_area_tuple = d[-2]
        facial_area: dict = facial_area_tuple[1]
        # facial_area: dict = result[-2].get('facial_area')
        # if face not detected draw a bounding box around the face
        if facial_area is not None:
            x = facial_area.get('x')
            y = facial_area.get('y')
            w = facial_area.get('w')
            h = facial_area.get('h')
            # x, y, w, h = result[-2].get('facial_area')
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Display the frame with face rectangles
        cv2.imshow('Real-Time Face Detection', frame)

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

# not accurate
# fails with occlusion
# lighting seems to be a problem
# seems pretty fast?
# fairs worse than other CNN libraries

