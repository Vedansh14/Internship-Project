from detection.vehicle_detector import VehicleDetector
from detection.parking_zone import ParkingZone
from config import *

import cv2

detector = VehicleDetector()

zone = ParkingZone(
    ZONE_X1,
    ZONE_Y1,
    ZONE_X2,
    ZONE_Y2
)

cap = cv2.VideoCapture("video/traffic.mp4")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    zone.draw(frame)

    results = detector.detect(frame)

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])

            if cls in VEHICLE_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cx = (x1+x2)//2
                cy = (y1+y2)//2

                cv2.rectangle(
                    frame,
                    (x1,y1),
                    (x2,y2),
                    (0,255,0),
                    2
                )

                if zone.inside(cx,cy):
                    cv2.putText(
                        frame,
                        "IN NO PARKING",
                        (x1,y2+20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,0,255),
                        2
                    )

    cv2.imshow("Detection",frame)

    if cv2.waitKey(1)==27:
        break

cap.release()
cv2.destroyAllWindows()