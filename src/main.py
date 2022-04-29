# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import re # used for regular expressions
import queue # thread safe job queue
import threading # used for multithreading
from time import sleep # sleeping for progress monitor thread
import magic # used for precise file type identification

import config # import custom configuration file


# global variables
accepted_exts = set() # using sets for quick search
refused_exts = set()

filepaths_q = queue.Queue() # queue for loaded filepaths

# counters for progress monitoring
loaded_count = 0
# each thread for processing files has its own counter
# e.g., for deploying to a system with high number of CPUs
processed_counts = [0] * config.NUM_THREADS


def main():
    global accepted_exts, refused_exts

    with open(config.ACCEPTED_EXTS_PATH) as ae_file:
        accepted_exts = set(ae_file.read().splitlines())
    with open(config.REFUSED_EXTS_PATH) as ie_file:
        refused_exts = set(ie_file.read().splitlines())
    
    # create progress monitor thread
    thread = threading.Thread(target=progress_monitor)
    thread.setDaemon(True) # will be ended on main thread exit automatically
    thread.start()

    # due to thread load balance distribution, load filepaths first
    # so that the user knows total number of files to be processed
    load_filepaths(config.DATASET_DIR) # fill up the queue
    
    # create as many threads as there are physically present in CPU
    # there are also other threads, but only these will be truly active
    for t_num in range(config.NUM_THREADS):
        thread = threading.Thread(target=process_files, args=(t_num,))
        thread.setDaemon(True) # killed on exit
        thread.start()

    filepaths_q.join() # wait for the queue to be empty
    print("done")


def load_filepaths(dataset):
    global loaded_count

    # go through all files in given directory (recursively)
    for dirpath, _, filenames in os.walk(dataset):
        for filename in filenames:
            if is_file_accepted(dirpath, filename):
                filepath = os.path.join(dirpath, filename)
                filepaths_q.put(filepath) # add filepath to queue
                loaded_count += 1


def is_file_accepted(dirpath, filename):
    # remove "@..." and "?..." parts of the file
    ext = re.sub(r"(\@|\?).*$", "", filename)
    # keep only the last file extension
    ext = re.sub(r"(^[^\.]*$|^([^\.]*\.)*)", "", ext)
    ext = ext.lower() # to match also UPPERCASE extensions

    # first check file extension filters (quicker)
    if ext in accepted_exts:
        return True
    elif ext in refused_exts:
        return False
    else: # use precise MIME file type identification (slower)
        filepath = os.path.join(dirpath, filename)
        mime_type = magic.from_file(filepath, mime=True)
        return mime_type.startswith("text/")


def progress_monitor():
    print("processed files / loaded filepaths")
    while True: # thread function, will be ended on main thread exit
        loaded_count_k = int(loaded_count / 1000)
        processed_count_k = int(sum(processed_counts) / 1000)
        print(processed_count_k, "k / ", loaded_count_k, "k", sep="")
        sleep(config.PROGRESS_REPORT_INTERVAL)


def process_files(t_num):
    global processed_counts

    while True:
        filepath = filepaths_q.get()

        # TODO: replace with useful work
        for _ in range(100):
            a = filepath

        # increase processed files count for current thread
        processed_counts[t_num] += 1
        filepaths_q.task_done()


main() # the entry point of the program
