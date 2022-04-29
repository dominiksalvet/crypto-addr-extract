# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import re # used for regular expressions
import queue # thread safe job queue
import threading # used for multithreading
from time import sleep # sleeping for progress monitor thread

import config # import custom configuration file


# global variables
ignored_exts = set() # using set for quick search

filepaths_q = queue.Queue() # queue for loaded filepaths

# counters for progress monitoring
loaded_count = 0
# each thread for processing files has its own counter
# e.g., for deploying to a system with high number of CPUs
processed_counts = [0] * config.NUM_THREADS

# prepare regular expressions
remove_prop_re = re.compile(r"(\@|\?).*$")
keep_last_ext_re = re.compile(r"(^[^\.]*$|^([^\.]*\.)*)")


def main():
    global ignored_exts

    with open(config.IGNORED_EXTS_PATH) as ie_file:
        ignored_exts = set(ie_file.read().splitlines())
    
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

    # go through all files in given directory (recursively)
    for dirpath, _, filenames in os.walk(dataset):
        for filename in filenames:
            if is_filename_accepted(filename):
                filepath = os.path.join(dirpath, filename)
                filepaths_q.put(filepath) # add filepath to queue
                loaded_count += 1


def is_filename_accepted(filename):
    # remove "@..." and "?..." parts of the file
    ext = remove_prop_re.sub("", filename)
    # keep only the last file extension
    ext = keep_last_ext_re.sub("", ext)

    ext = ext.lower() # to match also UPPERCASE extensions
    return not ext in ignored_exts


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

        # try:
        #     with open(filepath, encoding="ascii") as file:
        #         file_content = file.read()
        #         if magic.from_buffer(file_content, mime=True).startswith("text/"):
        #             crypto_addr = re.search(r'[^a-zA-Z0-9][a-zA-Z0-9]{26,95}[^a-zA-Z0-9]', file_content)
        #             if crypto_addr:
        #                 print(filepath, crypto_addr)
        # except UnicodeDecodeError:
        #     pass


            # result = re.search(r'BEGIN PGP.*END PGP', file_content)
            # if result:
            #     print(result)

        # with open(filepath, encoding='utf-8', errors='ignore') as file:
        #     a = file.read()

        # try:
        #     with open(filepath) as file:
        #         file_content = file.read()
        #         # result = re.search(r'BEGIN PGP PUBLIC KEY BLOCK.*END PGP PUBLIC KEY BLOCK', file_content)
        #         result = re.search(r'[a-zA-Z0-9]*[a-zA-Z0-9]{25}[a-zA-Z0-9]*', file_content)
        #         if result:
        #             print(filepath)
        # except:
        #     with open(filepath, "rb") as file:
        #         file_content = file.read()

        # increase processed files count for current thread
        processed_counts[t_num] += 1
        filepaths_q.task_done()


main() # the entry point of the program
