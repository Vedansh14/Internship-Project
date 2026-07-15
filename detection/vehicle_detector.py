from ultralytics import YOLO


class VehicleDetector:
    """Detects vehicles in video frames using YOLOv8."""

    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        """Run YOLOv8 detection on a frame and return results."""
        results = self.model(frame)
        return results
