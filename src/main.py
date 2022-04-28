# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import re # used for regular expressions
import queue # thread safe job queue
import threading # used for multithreading
from time import sleep

import config # import custom configuration file


# global variables
ignored_exts = set() # using set for quick search

files_q = queue.Queue() # queue for loaded files

# counters for progress monitoring
loaded_count = 0
processed_lock = threading.Lock()
processed_count = 0 # must use the above lock for modification


def main():
    global ignored_exts

    with open(config.IGNORED_EXTS_PATH) as ie_file:
        ignored_exts = set(ie_file.read().splitlines())
    
    # create progress monitor thread
    thread = threading.Thread(target=progress_monitor)
    thread.setDaemon(True) # will be ended on main thread exit automatically
    thread.start()

    # due to thread load balance distribution, load file paths first
    # so that the user knows total number of files to be processed
    load_files(config.DATASET_DIR) # fill up the queue
    
    # create as many threads as there are physically present in CPU
    for _ in range(os.cpu_count()): # because only these threads will be truly active
        thread = threading.Thread(target=process_files)
        thread.setDaemon(True) # killed on exit
        thread.start()

    files_q.join() # wait for the queue to be empty
    print("done")


def load_files(dataset):
    global loaded_count

    # go through all files in given directory (recursively)
    for dirpath, _, filenames in os.walk(dataset):
        for filename in filenames:
            if is_candidate_file(filename):
                file_path = os.path.join(dirpath, filename)
                files_q.put(file_path) # add file path to queue
                loaded_count += 1


def is_candidate_file(filename):
    # remove "@..." and "?..." parts of the file
    ext = re.sub(r"(\@|\?).*$", "", filename)
    # keep only the last file extension
    ext = re.sub(r"(^[^\.]*$|^([^\.]*\.)*)", "", ext)
    
    ext = ext.lower() # to match also UPPERCASE extensions
    # due performance, no file MIME type check here
    return not ext in ignored_exts


def progress_monitor():
    print("processed / loaded files")
    while True: # thread function, will be ended on main thread exit
        loaded_count_k = int(loaded_count / 1000)
        processed_count_k = int(processed_count / 1000)
        print(processed_count_k, "k / ", loaded_count_k, "k", sep="")
        sleep(config.PROGRESS_REPORT_INTERVAL)


def process_files():
    global processed_lock, processed_count

    while True:
        file_path = files_q.get()

        for _ in range(100):
            a = file_path
    
        with processed_lock:
            processed_count += 1
        files_q.task_done()


main() # the entry point of the program
