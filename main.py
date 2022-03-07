import os
# import time
import cv2
import shutil
import rle
import numpy
import multiprocessing
from db_connect import create_connection_db, insert_line_db

session = create_connection_db()


def reading_process(queue_frames, len_frames, queue_time, file_name):
    capture = cv2.VideoCapture("./in/" + file_name)
    for i in range(len_frames):
        ret, frame = capture.read()
        if ret:
            start = capture.get(cv2.CAP_PROP_POS_MSEC)
            queue_time.put(start)
            queue_frames.put(frame)
            # print("first process", i, multiprocessing.current_process(), time.time(),"\n")
        else:
            queue_frames.put(None)
            queue_time.put(None)


def refactor_frame_process(queue_frames, queue_res, len_frames):
    for i in range(len_frames):
        frame = queue_frames.get()
        if not isinstance(frame, numpy.ndarray):
            continue
        frame = cv2.resize(frame, (200, 200))
        frame = cv2.threshold(
            frame, 128,
            255, cv2.THRESH_BINARY)[1]
        frame_str = (str(frame).replace("[", "").replace("]", "").replace("...", "").
                     replace("\n", "").replace(" ", "").
                     replace("255", "255,").replace("0", "0,"))
        frame_lst = (frame_str[:-1]).split(",")
        rle_str = (str(rle.encode(frame_lst)).replace("'", ""))
        queue_res.put(rle_str)
        # print("second process", multiprocessing.current_process(), time.time(),"\n")


def saving_in_db_process(queue_frames, len_frames, queue_time, file_name):
    for i in range(len_frames):
        time_stamp = queue_time.get()
        if not isinstance(time_stamp, float):
            continue
        rle_str = queue_frames.get()
        insert_line_db(session, file_name, i, str(time_stamp), rle_str)
        # print("third process", multiprocessing.current_process(), time.time(),"\n")


if __name__ == '__main__':

    frames_queue = multiprocessing.Queue()
    res_queue = multiprocessing.Queue()
    time_queue = multiprocessing.Queue()
    try:
        os.mkdir("./out")
    except FileExistsError:
        pass
    for filename in os.listdir("./in"):
        cap = cv2.VideoCapture("./in/" + filename)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        p1 = multiprocessing.Process(target=reading_process,
                                     args=(frames_queue, length,
                                           time_queue, filename, ), name="p1")
        p2 = multiprocessing.Process(target=refactor_frame_process,
                                     args=(frames_queue, res_queue, length,), name="p2")
        p3 = multiprocessing.Process(
                                    target=saving_in_db_process,
                                    args=(res_queue, length, time_queue, filename), name="p3",)
        processes = [p1, p2, p3]

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        shutil.move("./in/" + filename, "./out/" + filename)
