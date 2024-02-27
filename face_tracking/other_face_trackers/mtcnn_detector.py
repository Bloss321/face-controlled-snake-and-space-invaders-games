import cv2
from mtcnn import MTCNN

# Uses deep learning - MTCNN model


def main():
    # Initialize the MTCNN face detection model
    detector = MTCNN()

    # Open a video capture object (0 for default camera)
    cap = cv2.VideoCapture(0)

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()

        # Detect faces using MTCNN
        faces = detector.detect_faces(frame)

        # Draw rectangles around the detected faces
        for face in faces:
            x, y, width, height = face['box']
            cv2.rectangle(frame, (x, y), (x+width, y+height), (255, 0, 0), 2)

        # Display the frame with face rectangles
        cv2.imshow('Face Detection', frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

# Notes on performance:

# very laggy and slow
# computationally intensive
# kinda works with extreme lighting
# seems to work a little with occlusion

