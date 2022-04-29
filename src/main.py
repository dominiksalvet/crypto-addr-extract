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

    print_current_progress() # last report
    print("processed", sum(processed_counts), "files")


def load_filepaths(dataset):
    global loaded_count
    mime_cache = {} # dictionary of [<filepath/ext>]=+-num

    # go through all files in given directory (recursively)
    for dirpath, _, filenames in os.walk(dataset):
        for filename in filenames:
            if is_file_accepted(dirpath, filename, mime_cache):
                filepath = os.path.join(dirpath, filename)
                filepaths_q.put(filepath) # add filepath to queue
                loaded_count += 1


def is_file_accepted(dirpath, filename, mime_cache):
    # remove "@..." and "?..." parts of the file
    ext = re.sub(r"(\@|\?).*$", "", filename)
    # keep only the last file extension
    ext = re.sub(r"(^[^\.]*$|^([^\.]*\.)*)", "", ext)
    ext = ext.lower() # to match also UPPERCASE extensions

    # first check only filepath filters [very fast]
    if config.IGNORE_GIT_REPOS and ".git" in dirpath:
        print(os.path.join(dirpath, filename))
        return False
    elif config.USE_MIME and ext in accepted_exts:
        return True
    elif ext in refused_exts:
        return False
    elif not config.USE_MIME:
        return True

    # try to identify file based on MIME cache [fast]
    mime_key = dirpath + "/" + ext
    mime_val = mime_cache.get(mime_key) # read cache

    if mime_val is not None: # cache hit
        if mime_val >= config.MIME_CACHE_THRESHOLD:
            return True
        elif mime_val <= -config.MIME_CACHE_THRESHOLD:
            return False
    else: # cache miss
        mime_val = mime_cache[mime_key] = 0 # create cache item
    
    # cache item does not have enough values => collect next [slow]
    filepath = os.path.join(dirpath, filename)
    mime_type = magic.from_file(filepath, mime=True)

    # reset counters if different decision than previous ones
    if mime_type.startswith("text/"):
        if mime_val < 0:
            mime_val = 0
        
        mime_cache[mime_key] = mime_val + 1
        return True
    else:
        if mime_val > 0:
            mime_val = 0

        mime_cache[mime_key] = mime_val - 1
        return False


def progress_monitor():
    print("processed files / loaded filepaths")
    while True: # thread function, will be ended on main thread exit
        print_current_progress()
        sleep(config.PROGRESS_REPORT_INTERVAL)


def print_current_progress():
    if loaded_count < 10_000:
        loaded_divisor = 1
        loaded_suff = ""
    elif loaded_count < 10_000_000:
        loaded_divisor = 1_000
        loaded_suff = "k"
    else:
        loaded_divisor = 1_000_000
        loaded_suff = "M"

    processed_count = sum(processed_counts)
    if processed_count < 10_000:
        processed_divisor = 1
        processed_suff = ""
    elif processed_count < 10_000_000:
        processed_divisor = 1_000
        processed_suff = "k"
    else:
        processed_divisor = 1_000_000
        processed_suff = "M"
    
    loaded_count_str = str(int(loaded_count / loaded_divisor))
    loaded_count_str += loaded_suff
    processed_count_str = str(int(processed_count / processed_divisor))
    processed_count_str += processed_suff

    print(processed_count_str, "/", loaded_count_str)


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
