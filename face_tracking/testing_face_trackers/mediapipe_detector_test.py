import time
import cv2
import mediapipe as mp
from statistics import mean

import psutil

# Mediapipe uses CNN to detect facial landmarks (in the form of a mesh)
# Seems to use Mask R-CNN or some other form of R-CNN

mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh


def main():
    # Initialize MediaPipe Face Detection module
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.3)
    # Initialize MediaPipe Face Mesh module
    face_mesh = mp_face_mesh.FaceMesh()
    # OpenCV video capture
    cap = cv2.VideoCapture('medium, head movements.mp4')  # Use 0 for default camera or specify the video file path
    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Unable to open the video file.")
        exit()

    execution_times = []
    cpu_usage = []
    memory_usage = []

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Measure the execution time for face detection
        start_time = time.time()

        # Before face detection starts
        initial_cpu_usage = psutil.cpu_percent()
        initial_memory_usage = psutil.virtual_memory().percent

        # Perform face detection
        detection_results = face_detection.process(rgb_frame)

        # After face detection completes
        final_cpu_usage = psutil.cpu_percent()
        final_memory_usage = psutil.virtual_memory().percent

        # Calculate the execution time
        execution_time = time.time() - start_time
        execution_times.append(execution_time)

        if detection_results.detections:
            for detection in detection_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                    int(bboxC.width * iw), int(bboxC.height * ih)

                # Draw bounding box around the face
                cv2.rectangle(frame, bbox, (0, 255, 0), 2)

        # Perform face mesh detection
        mesh_results = face_mesh.process(rgb_frame)

        if mesh_results.multi_face_landmarks:
            for landmarks in mesh_results.multi_face_landmarks:
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

        # Display the output frame
        cv2.imshow("Face Detection and Mesh", frame)

        # Calculate differences
        cpu_usage_difference = final_cpu_usage - initial_cpu_usage
        memory_usage_difference = final_memory_usage - initial_memory_usage

        cpu_usage.append(cpu_usage_difference)
        memory_usage.append(memory_usage_difference)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture and close all windows
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

# very accurate and precise
# works well with low lighting
# handles dark skin
# still works with occlusion
# need to check speed
