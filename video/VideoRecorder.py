# lyy. init version 2021/08/30
import argparse
import time
import os
import cv2
import logging

import ipdb
lg = logging.getLogger(__name__)
logging.basicConfig(format = logging.BASIC_FORMAT)
lg.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--device', type = str, default='/dev/video0', help = 'for example:/dev/video0')
parser.add_argument('-t', '--target_dir', type = str, default='.', help = 'the dir to save image and video, default .')
parser.add_argument('-r', '--resolution', type = str, default='640x480', help = 'set resolution, widht*height')

args = parser.parse_args()
lg.info(args)

def draw_help(frame, recording):
    offset = 25
    pos = [0, 15]
    font_scale = 0.8
    cv2.putText(frame, f"recording" if recording else "preview", tuple(pos), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0, 0, 255))
    pos[1] += offset
    h, w = frame.shape[:2]
    cv2.putText(frame, f"resolution:{w}x{h}", tuple(pos), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0, 0, 255))
    pos[1] += offset
    cv2.putText(frame, f"press 'q' to quit this program", tuple(pos), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0, 0, 255))
    pos[1] += offset
    cv2.putText(frame, f"press 's' to save image", tuple(pos), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0, 0, 255))
    pos[1] += offset
    cv2.putText(frame, f"press 'v' to save video", tuple(pos), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0, 0, 255))


def parse_resolution(resolution_str):
    tokens = resolution_str.split('*')
    if len(tokens) != 2:
        tokens = resolution_str.split('x')
    assert len(tokens) == 2, f'resoltuion flag should be wxh or w*h format, but get {resolution_str}'
    w, h = int(tokens[0]), int(tokens[1])
    return w, h

def input_is_video(input_name):
    _, ext = os.path.splitext(input_name)
    return ext in ['.avi', '.mp4', '.mov']

def main(args):
    cap = cv2.VideoCapture(args.device)
    if not cap.isOpened():
        lg.error(f'can not open device {args.device}')
        return 
    fps = None
    if not input_is_video(args.device):
        w, h = parse_resolution(args.resolution)
        ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        assert ret, f'can not set frame widht {w}'
        ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        assert ret, f'can not set frame height {h}' 
        fps = cap.get(cv2.CAP_PROP_FPS)
        lg.info(f'get fps {fps} from devcie')
    videoWriter = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            lg.error(f'can not retrive frame')
            break
        if videoWriter is not None:
            videoWriter.write(frame)
        draw_help(frame, recording = videoWriter is not None)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if key == ord('s'):
            # save picture
            os.makedirs(args.target_dir, exist_ok= True)
            file_name =os.path.join(args.target_dir, time.strftime("%H_%M_%S.png"))
            lg.info(f'writing image to {file_name}')
            ret = cv2.imwrite(file_name, frame)
            assert ret, f'can not wite frame to {file_name}'
        elif key == ord('v'):
            # save video
            if videoWriter is None:
                os.makedirs(args.target_dir, exist_ok= True)
                file_name =os.path.join(args.target_dir, time.strftime("%H_%M_%S.avi"))
                lg.info(f'ready to save video to {file_name}')
                videoWriter = cv2.VideoWriter(file_name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps if fps else 20, (w, h))
            else:
                videoWriter.release()
                videoWriter = None
        elif key == ord('q'):
            break
        else:
            pass

if __name__ == '__main__':
    main(args)