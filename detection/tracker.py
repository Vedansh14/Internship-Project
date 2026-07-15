from ultralytics import YOLO

class VehicleTracker:

    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def track(self, frame):
        results = self.model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        return results