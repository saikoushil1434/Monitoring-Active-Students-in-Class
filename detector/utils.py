# utils.py
import time


class IDGenerator:
def __init__(self):
self.counter = 0


def next(self):
self.counter += 1
return f"S{self.counter:03d}"


# Simple in-memory tracker record
class TrackedFace:
def __init__(self, fid, bbox, timestamp):
self.id = fid
self.bbox = bbox
self.first_seen = timestamp
self.last_seen = timestamp
self.attentive_time = 0.0
self.distracted_time = 0.0
self.current_state = None # 'attentive' or 'distracted'


def update_seen(self, bbox, timestamp):
self.bbox = bbox
self.last_seen = timestamp