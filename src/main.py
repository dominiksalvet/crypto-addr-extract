# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import re # used for regular expressions
import queue # thread safe job queue
import threading # used for multithreading
from time import sleep # sleeping for progress monitor thread

import config # import custom configuration file


# global variables
ignored_dirs = set() # using sets for quick search
ignored_exts = set()

common_addr_re = None # common regex for all crypto addresses
cryptos = [] # pairs of crypto symbol and its address regex

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
    global ignored_dirs, ignored_exts, common_addr_re, cryptos

    with open(config.IGNORED_DIRS_PATH) as id_file:
        ignored_dirs = set(id_file.read().splitlines())
    with open(config.IGNORED_EXTS_PATH) as ie_file:
        ignored_exts = set(ie_file.read().splitlines())
    
    with open(config.CRYPTO_ADDRS_PATH) as ar_file:
        # first line is common regex for all crypto addresses
        common_addr = ar_file.readline().strip(os.linesep)
        crypto_strs = ar_file.read().splitlines() # read the rest

    # compile all loaded regex
    common_addr_re = re.compile(common_addr)
    for crypto_str in crypto_strs:
        crypto_symbol, crypto_addr = crypto_str.split(" ", maxsplit=1)
        cryptos.append((crypto_symbol, re.compile(crypto_addr)))
    
    # create progress monitor thread
    thread = threading.Thread(target=progress_monitor)
    thread.setDaemon(True) # will be ended on main thread exit automatically
    thread.start()

    # not using continuous processing in default, so that the user knows the total
    # number of files to be processed as soon as possible
    if not config.CONTINUOUS_PROCESSING:
        load_filepaths(config.DATASET_DIR) # fill up the queue
        # create as many threads as there are physically present in CPU
        # there are also other threads, but only these will be truly active
        spawn_process_files_threads(config.NUM_THREADS)
    else: # this approach may be used for lower memory consumption
        filepaths_q.maxsize = config.CONTINUOUS_BUFF_SIZE
        spawn_process_files_threads(config.NUM_THREADS)
        load_filepaths(config.DATASET_DIR)

    filepaths_q.join() # wait for the queue to be empty

    print_current_progress() # last report
    print("processed", sum(processed_counts), "files")


def load_filepaths(dataset):
    global loaded_count

    # go through all files in given directory (recursively)
    for dirpath, dirnames, filenames in os.walk(dataset, topdown=True):
        # pruning the search (matches also UPPERCASE ignored directory names)
        dirnames[:] = [d for d in dirnames if d.lower() not in ignored_dirs]
        for filename in filenames:
            if is_filename_accepted(filename):
                filepath = os.path.join(dirpath, filename)
                filepaths_q.put(filepath) # add filepath to queue
                loaded_count += 1


def spawn_process_files_threads(num_thread):
    for t_num in range(num_thread):
        thread = threading.Thread(target=process_files, args=(t_num,))
        thread.setDaemon(True) # killed on exit
        thread.start()


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

        # # replace unknown bytes with a question mark "?"
        # with open(filepath, encoding="ascii", errors="replace") as file:
        #     file_content = file.read()
        #     matches = common_addr_re.findall(file_content)
        #     for match in matches:
        #         for crypto_symbol, crypto_addr_re in cryptos:
        #             if crypto_addr_re.match(match):
        #                 print(filepath, crypto_symbol, match)

            # result = re.search(r'[^a-zA-Z0-9][a-zA-Z0-9]{26,95}[^a-zA-Z0-9]', file_content)
            # if result:
            #     result = re.search(r'0x[a-fA-F0-9]{40}', result.group())
            #     if result:
            #         print(filepath, result.group())


        # try:
        #     with open(filepath, encoding="ascii") as file:
        #         file_content = file.read()
        #         crypto_addr = re.search(r'[^a-zA-Z0-9][a-zA-Z0-9]{26,95}[^a-zA-Z0-9]', file_content)
        #         if crypto_addr:
        #             correct_cnt += 1
        # except UnicodeDecodeError:
        #     with open(filepath, encoding="ascii", errors="replace") as file:
        #         file_content = file.read()
        #         crypto_addr = re.search(r'[^a-zA-Z0-9][a-zA-Z0-9]{26,95}[^a-zA-Z0-9]', file_content)
        #         if crypto_addr:
        #             error_cnt += 1
        
        # if correct_cnt % 1000 == 0 or error_cnt % 1000 == 0:
        #     print(correct_cnt, error_cnt)


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
