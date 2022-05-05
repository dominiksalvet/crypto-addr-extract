# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import re # used for regular expressions
import queue # thread safe job queue
import threading # used for multithreading
from time import sleep # sleeping for progress monitor thread
import json # used for final output records

import config # import custom configuration file


# prepare regular expressions (constants)
REMOVE_PROP_RE = re.compile(r"(\@|\?).*$")
KEEP_LAST_EXT_RE = re.compile(r"(^[^\.]*$|^([^\.]*\.)*)")
REMOVE_DATASET_DIR = re.compile(r"^" + config.DATASET_DIR + r"/")
KEEP_ONLY_FIRST_DIR = re.compile(r"/.*$")

# global variables
ignored_dirs = set() # using sets for quick search
ignored_exts = set()

common_addr_re = None # common regex for all crypto addresses
cryptos = [] # pairs of crypto symbol and its address regex

filepaths_q = queue.Queue() # queue for prepared filepaths

# counters for progress monitoring
prepared_count = 0
# each thread for processing files has its own counter
# e.g., for deploying to a system with high number of CPUs
processed_counts = [0] * config.NUM_THREADS
matches_counts = [0] * config.NUM_THREADS # number of total addresses found

# dictionary of final records
found_records = {}
found_records_lock = threading.Lock()

print_report = True # as long as set, a thread prints the progress report


def main():
    global ignored_dirs, ignored_exts, common_addr_re, cryptos, print_report

    with open(config.IGNORED_DIRS_PATH) as id_file:
        ignored_dirs = set(id_file.read().splitlines())
    with open(config.IGNORED_EXTS_PATH) as ie_file:
        ignored_exts = set(ie_file.read().splitlines())
    
    with open(config.CRYPTO_ADDRS_PATH) as ar_file:
        # first line is common regex for all crypto addresses
        common_addr = ar_file.readline().strip(os.linesep)
        crypto_strs = ar_file.read().splitlines() # read the rest

    # compile all loaded regex (match priority is determined by their order in file)
    pre_chars = config.ADDR_PRE_CHARS; post_chars = config.ADDR_POST_CHARS
    common_addr_re = re.compile("[" + pre_chars + "]" + common_addr + "[" + post_chars + "]")

    for crypto_str in crypto_strs:
        crypto_symbol, crypto_addr = crypto_str.split(" ", maxsplit=1)
        cryptos.append((crypto_symbol, re.compile(crypto_addr)))
    
    # create progress monitor thread
    progThread = threading.Thread(target=progress_monitor)
    progThread.setDaemon(True) # will be ended on main thread exit automatically
    progThread.start()

    # when not using continuous processing, user knows the total number of files
    # to be processed as soon as possible
    if not config.CONTINUOUS_PROCESSING:
        load_filepaths(config.DATASET_DIR) # fill up the queue
        # create as many threads as there are physically present in CPU
        # there are also other threads, but only these will be truly active
        spawn_process_files_threads(config.NUM_THREADS)
    else:
        filepaths_q.maxsize = config.CONTINUOUS_BUFF_SIZE
        spawn_process_files_threads(config.NUM_THREADS)
        load_filepaths(config.DATASET_DIR)

    filepaths_q.join() # wait for the queue to be empty
    print_report = False # synchronize output
    progThread.join()

    print_current_progress() # last report
    # summary with no number shortening
    print(sum(matches_counts), "matches in", sum(processed_counts), "files")
    print("writing results to", config.RESULTS_PATH)

    final_found_records = {"addresses": found_records} # add header
    with open(config.RESULTS_PATH, "w") as rp_file:
        json.dump(final_found_records, rp_file, indent=4)


def load_filepaths(dataset):
    global prepared_count

    if not os.path.isdir(dataset):
        print("directory", dataset, "does not exist")
        quit(1)

    # go through all files in given directory (recursively)
    for dirpath, dirnames, filenames in os.walk(dataset, topdown=True):
        # pruning the search (matches also UPPERCASE ignored directory names)
        dirnames[:] = [d for d in dirnames if d.lower() not in ignored_dirs]
        for filename in filenames:
            if is_filename_accepted(filename):
                filepath = os.path.join(dirpath, filename)
                filepaths_q.put(filepath) # add filepath to queue
                prepared_count += 1


def spawn_process_files_threads(num_thread):
    for t_num in range(num_thread):
        thread = threading.Thread(target=process_files, args=(t_num,))
        thread.setDaemon(True) # killed on exit
        thread.start()


def is_filename_accepted(filename):
    # remove "@..." and "?..." parts of the file
    ext = REMOVE_PROP_RE.sub("", filename)
    # keep only the last file extension
    ext = KEEP_LAST_EXT_RE.sub("", ext)

    ext = ext.lower() # to match also UPPERCASE extensions
    return not ext in ignored_exts


def progress_monitor():
    print("total matches <== processed files / prepared files")
    while print_report:
        print_current_progress()
        sleep(config.PROGRESS_REPORT_INTERVAL)


def print_current_progress():
    if prepared_count < 10_000:
        prepared_divisor = 1
        prepared_suff = ""
    elif prepared_count < 10_000_000:
        prepared_divisor = 1_000
        prepared_suff = "k"
    else:
        prepared_divisor = 1_000_000
        prepared_suff = "M"

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

    matches_count = sum(matches_counts)
    if matches_count < 10_000:
        matches_divisor = 1
        matches_suff = ""
    elif matches_count < 10_000_000:
        matches_divisor = 1_000
        matches_suff = "k"
    else:
        matches_divisor = 1_000_000
        matches_suff = "M"
    
    prepared_count_str = str(int(prepared_count / prepared_divisor))
    prepared_count_str += prepared_suff
    processed_count_str = str(int(processed_count / processed_divisor))
    processed_count_str += processed_suff
    matches_count_str = str(int(matches_count / matches_divisor))
    matches_count_str += matches_suff

    print(matches_count_str, "<==", processed_count_str, "/", prepared_count_str)


# main function for working threads
def process_files(t_num):
    global processed_counts

    while True:
        filepath = filepaths_q.get()

        with open(filepath, encoding="ascii", errors="replace") as file:
            file_content = file.read()
            matches = common_addr_re.finditer(file_content)
            for match in matches:
                addr = match.group(0)[1:-1] # remove pre and post characters
                symbol = get_crypto_symbol(addr) # categorize crypto address
                if symbol: # if address recognized
                    site_name = get_site_name(filepath)
                    add_found_record(addr, symbol, site_name, filepath)
                    matches_counts[t_num] += 1

        # increase processed files count for current thread
        processed_counts[t_num] += 1
        filepaths_q.task_done()


def get_crypto_symbol(crypto_addr):
    for crypto_symbol, crypto_addr_re in cryptos:
        if crypto_addr_re.search(crypto_addr):
            return crypto_symbol


def get_site_name(filepath):
    siteName = REMOVE_DATASET_DIR.sub("", filepath)
    siteName = KEEP_ONLY_FIRST_DIR.sub("/", siteName) # with slash
    
    if siteName[-1] != "/": # individual files in datatset directory
        siteName = "unknown"
    else:
        siteName = siteName[:-1] # remove unnecessary "/"

    return siteName


def add_found_record(addr, symbol, site_name, filepath):
    with found_records_lock:
        if addr in found_records:
            found_records[addr]["count"] += 1
        else:
            found_records[addr] = {"symbol": symbol, "count": 1, "sites": {}}
        
        if site_name in found_records[addr]["sites"]:
            if filepath not in found_records[addr]["sites"][site_name]:
                found_records[addr]["sites"][site_name].append(filepath)
        else:
            found_records[addr]["sites"][site_name] = [filepath]


main() # the entry point of the program
