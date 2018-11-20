import cv2
import datetime

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    # Set the capture to be 1920 x 1080 @ 30FPS:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Set the file save to be an MJPG type, at 1920 x 1080 @ 30FPS
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    out = cv2.VideoWriter('video_feed.avi', fourcc, 30.0, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    while cap.isOpened():
        try:
            ret, frame = cap.read()
            if not ret:
                continue

            # Put the time string in blue at the top left of the frame
            toPut = str(datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3])
            cv2.putText(frame, toPut, (20, 60), cv2.FONT_HERSHEY_PLAIN, 3.0, (255, 0, 0), thickness=1, lineType=cv2.LINE_AA)

            out.write(frame)
            cv2.imshow("Video with timestamp", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except KeyboardInterrupt:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
