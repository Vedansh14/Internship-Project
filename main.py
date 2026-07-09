import cv2
from ultralytics import YOLO

# Load YOLOv8 pretrained model
model = YOLO("yolov8n.pt")

# Open video
cap = cv2.VideoCapture("video/traffic.mp4")

if not cap.isOpened():
    print("Error: Could not open video file 'video/traffic.mp4'")
    exit(1)

# Vehicle class IDs in COCO dataset
VEHICLE_CLASSES = [2, 3, 5, 7]

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Run YOLO prediction
    results = model(frame)

    # Process detections
    for result in results:
        boxes = result.boxes

        for box in boxes:
            cls = int(box.cls[0])

            if cls in VEHICLE_CLASSES:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                confidence = float(box.conf[0])

                label = model.names[cls]

                # Draw rectangle
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # Draw label
                cv2.putText(
                    frame,
                    f"{label} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

    # Display output
    cv2.imshow("Vehicle Detection", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()