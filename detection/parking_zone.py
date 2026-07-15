import cv2

class ParkingZone:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, frame):

        cv2.rectangle(
            frame,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (0,0,255),
            3
        )

        cv2.putText(
            frame,
            "NO PARKING ZONE",
            (self.x1, self.y1-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,0,255),
            2
        )

    def inside(self, x, y):

        return (
            self.x1 <= x <= self.x2
            and
            self.y1 <= y <= self.y2
        )