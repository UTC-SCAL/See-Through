"""Fetches video camera data to be served in a generator."""
import cv2

class VideoCamera(object):
    """A class handling VideoCamera functionality."""

    def __init__(self):
        """."""
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        """Safely frees the webcam resource."""
        self.video.release()

    def get_frame(self):
        """Get a single frame at a time from the webcam."""
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
