import cv2
from darkflow.net.build import TFNet


def get_yolo_results(tfnet, frame):
    """Get the TFNet reuslts without drawing"""
    return tfnet.return_predict(frame)


def get_and_draw_yolo_results(tfnet, frame):
    """Get the TFNet results and draw them"""
    results = tfnet.return_predict(frame)
    frame = draw_yolo_results(results, frame)
    return frame, results


def draw_yolo_results(results, img):
    """Draw the YOLO results on the frame"""
    for result in results:
        # Ignore birds and keyboards...
        if "bird" in result['label'] or "keyboard" in result['label']:
            continue
        x = result['topleft']['x']
        y = result['topleft']['y']
        w = result['bottomright']['x'] - x
        h = result['bottomright']['y'] - y
        cv2.rectangle(img, (x, y), (x + w, y + h), (get_color_from_label(result['label'])), 4)
        cv2.putText(img, "{}: {}".format(result['label'], "%.2f" % result['confidence']), (x, y - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    return img


def get_color_from_label(label):
    if label == "car" or label == "truck" or label == "bus":
        return 15, 0, 214
    if label == "person":
        return 255, 168, 9
    if label == "bicycle":
        return 255, 101, 162
    return 0, 227, 251


def main():
    tfnet = TFNet({"model": "cfg/yolo.cfg", "load": "weights/yolo.weights", "threshold": 0.6, "gpu": 1.0})
    rear_video = cv2.VideoCapture()
    rear_video.open("Rear.mp4")
    front_video = cv2.VideoCapture()
    front_video.open("Front.mp4")
    out = cv2.VideoWriter('YOLO_Output.mp4', cv2.VideoWriter_fourcc(*'X264'), 30.0, (1920, 1080))

    while rear_video.isOpened() and front_video.isOpened():
        ret_rear, frame_rear = rear_video.read()
        ret_front, frame_front = front_video.read()
        if not ret_front or not ret_rear:
            break
        frame_rear, results = get_and_draw_yolo_results(tfnet, frame_rear)
        for result in results:
            # Filter out any non-vehicles:
            if not (result["label"] == "car" or result["label"] == "truck" or result["label"] == "bus"):
                continue
            if (1920 / 3) <= result['topleft']['x'] < ((1920 / 3) * 2):
                x = result['topleft']['x']
                y = result['topleft']['y']
                w = result['bottomright']['x'] - x
                h = result['bottomright']['y'] - y
                frame_front = cv2.resize(frame_front, (w, h))
                try:
                    frame_rear[y:y+h, x:x+w] = frame_front
                except ValueError:
                    pass
                break
        out.write(frame_rear)
    cv2.destroyAllWindows()
    rear_video.release()
    front_video.release()
    out.release()


if __name__ == "__main__":
    main()
