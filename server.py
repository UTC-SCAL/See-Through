"""A multithreaded server for processing two images through YOLO."""

import copy
import sys
import threading
from yolo_pipeline import *
from utils import *
from flask import Flask, render_template, Response

c = threading.Condition()
flag = 1
f = None

app = Flask(__name__)


def worker(ip):
    """The worker in charge of merging images, performing YOLO processing, etc."""
    global flag
    global img
    global f
    stream = open_stream_safely(ip)
    stream_data = bytes()
    yolo = None
    fps = None
    frames_rec_number = 9
    allow = False
    while not stream.closed:
        if frames_rec_number % 100 == 0:
            frames_rec_number = 9
        frames_rec_number = frames_rec_number + 1
        stream_data += stream.read(4096)
        a = stream_data.find(b'\xff\xd8')
        b = stream_data.find(b'\xff\xd9')

        if a != -1 and b != -1:
            if not timestamp_is_good(stream_data):
                print("Rear image too old, renewing stream...")
                del stream
                del stream_data
                stream = open_stream_safely(ip)
                stream_data = bytes()
                continue
            time_sent = extract_timestamp(stream_data)
            frame_number = extract_frame_number(stream_data)
            jpg = stream_data[a:b + 2]
            stream_data = stream_data[b + 2:]
            remote_frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            temp_list = list()
            temp_list.append(time.time())
            time_processed = temp_list[0] - time_sent
            """ UNCOMMENT BELOW LINE TO ENABLE HTTP TRANSFER BENCHMARKS """
            # print("Frame number {} took {} seconds to send over HTTP".format(frame_number, time_processed))
            if frames_rec_number % 10 == 0 or not allow:
                border_frame = copy.deepcopy(remote_frame)

                border_frame[:, 0:200, 0] = 0
                border_frame[:, 0:200, 1] = 0
                border_frame[:, 0:200, 2] = 0

                border_frame[:, 440:640, 0] = 0
                border_frame[:, 440:640, 1] = 0
                border_frame[:, 440:640, 2] = 0

                yolo_result_black, coords, detected_type, yolo, fps = vehicle_detection_yolo(border_frame)
                yolo_frame, coord_black, detected_type = draw_results(remote_frame, yolo, fps)

                if (detected_type == "car" or detected_type == "bus") and len(coords) > 0:
                    bb_start_x = coords[0][0][0]
                    bb_start_y = coords[0][0][1]
                    bb_w = coords[0][1][0]
                    bb_h = coords[0][1][1]

                    center_x_start = int(((bb_start_x + bb_w)/2) - ((bb_w/2)/3))
                    center_y_start = int(((bb_start_y + bb_h)/2) - ((bb_h/2)/3))

                    c.acquire()
                    if flag == 0:
                        flag = 1
                        c.notify_all()
                    c.release()
                    img_frame = cv2.resize(img, (int(bb_w/3), int(bb_h/3)))
                    try:
                        yolo_frame[center_y_start:center_y_start + img_frame.shape[0], center_x_start:center_x_start + img_frame.shape[1]] = img_frame
                    except ValueError:
                        pass
                f = yolo_frame
                print("Total processing time added an additional {} seconds.".format(frame_number, (time.time() - temp_list[0]) + time_processed))
                allow = True
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return
            elif allow:
                yolo_frame, cords_two, detected_type_two = draw_results(remote_frame, yolo, fps)
                if (detected_type == "car" or detected_type == "bus") and len(coords) > 0:
                    bb_start_x = coords[0][0][0]
                    bb_start_y = coords[0][0][1]
                    bb_w = coords[0][1][0]
                    bb_h = coords[0][1][1]

                    center_x_start = int(((bb_start_x + bb_w)/2) - ((bb_w/2)/3))
                    center_y_start = int(((bb_start_y + bb_h)/2) - ((bb_h/2)/3))
                    c.acquire()
                    if flag == 0:
                        flag = 1
                        c.notify_all()
                    c.release()
                    img_frame = cv2.resize(img, (int(bb_w/3), int(bb_h/3)))
                    try:
                        yolo_frame[center_y_start:center_y_start+img_frame.shape[0], center_x_start:center_x_start+img_frame.shape[1]] = img_frame
                    except ValueError:
                        pass
                f = yolo_frame
                print("YOLO processing for frame {} added an additional {} seconds.".format(frame_number, time.time() - temp_list[0]))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return
            else:
                print("ERROR")
            del temp_list


def front_worker(ip):
    """The worker in charge of simple encoding the image and evaluating the timestamp."""
    global img
    global flag
    # Connect to the video stream & declare a byte stream.
    stream = open_stream_safely(ip)
    stream_data = bytes()
    frames_rec_number = 9
    while not stream.closed:
        frames_rec_number = frames_rec_number + 1
        # Extracts the image from the bytestream
        stream_data += stream.read(4096)
        a = stream_data.find(b'\xff\xd8')
        b = stream_data.find(b'\xff\xd9')
        # If the index of these special characters can be found:
        if a != -1 and b != -1:
            if not timestamp_is_good(stream_data):
                print("Front image too old, renewing stream...")
                del stream
                del stream_data
                stream = open_stream_safely(ip)
                stream_data = bytes()
                continue
            # Decodes the frame from bytes to an imagez
            jpg = stream_data[a:b + 2]
            stream_data = stream_data[b + 2:]
            remote_frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            c.acquire()
            if flag == 1:
                img = remote_frame
                flag = 0
                c.notify_all()
            c.release()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                return


@app.route('/')
def index():
    """Where the server URL directs to."""
    return render_template('index.html')


def gen():
    """A generator for the processed YOLO image."""
    while True:
        frame = get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    """."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def get_frame():
    """Retrieve the decoded frame."""
    global f
    ret, jpeg = cv2.imencode('.jpg', f)
    return jpeg.tobytes()


def get_ips():
    """Get the IPs and do some arg checking too."""
    if len(sys.argv) != 3:
        print('Invalid launch arguments. Run via:')
        print('python server.py <front_ip:port_number> <rear_ip:port_number>')
        sys.exit(0)
    return 'http://{}/video_feed'.format(sys.argv[1]), 'http://{}/video_feed'.format(sys.argv[2])


if __name__ == '__main__':
    """Get the IPs and start the thread workers."""
    front_ip, rear_ip = get_ips()
    t = threading.Thread(target=worker, args=(rear_ip,))
    t2 = threading.Thread(target=front_worker, args=(front_ip,))
    t.start()
    t2.start()
    app.run(host='', port=5002, debug=False)
