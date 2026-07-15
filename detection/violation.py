import time

class ViolationManager:

    def __init__(self):
        self.entry_times = {}

    def update(self, track_id, inside_zone):

        current = time.time()

        if inside_zone:

            if track_id not in self.entry_times:
                self.entry_times[track_id] = current

            elapsed = current - self.entry_times[track_id]

            return elapsed

        else:

            if track_id in self.entry_times:
                del self.entry_times[track_id]

            return 0