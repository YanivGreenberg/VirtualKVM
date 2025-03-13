from enum import Enum,auto
from observer import Subject


class Direction(Enum):

    RIGHT = auto()
    LEFT = auto()
    DOWN = auto()
    UP = auto()


class ScreenEdgeDetector(Subject):

    subscribers = []  # List of subscribers (observers)

    def __init__(self, threshold=10, region=None):
        self.threshold = threshold
        if region is None:
            region = {"width": 0, "height": 0}  
        self.width = region["width"]
        self.height = region["height"]

    @staticmethod
    def notify(direction):
        """Notify all subscribers (observers) with the given direction."""
        for sub in ScreenEdgeDetector.subscribers:
            sub.update(direction) 

    @staticmethod
    def attach(observer):
        """Attach an observer to the subject (if not already attached)."""
        if observer not in ScreenEdgeDetector.subscribers:
            ScreenEdgeDetector.subscribers.append(observer)

    @staticmethod
    def detach(observer):
        """Detach an observer from the subject (if attached)."""
        if observer in ScreenEdgeDetector.subscribers:
            ScreenEdgeDetector.subscribers.remove(observer)

    def detect_moving_to_edge(self, x, y, velocity_x, velocity_y):
        if x <= self.threshold and velocity_x < 0:
            self.notify(Direction.LEFT)
        if x >= self.width - self.threshold and velocity_x > 0:
            self.notify(Direction.RIGHT)
        if y <= self.threshold and velocity_y < 0:
            self.notify(Direction.UP)
        if y >= self.height - self.threshold and velocity_y > 0:
            self.notify(Direction.DOWN)

