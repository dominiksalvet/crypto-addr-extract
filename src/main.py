# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import re # used for regular expressions
import queue

import config # import custom configuration file


# global variables
ignored_exts = set() # using set for quick search

files_q = queue.Queue() # queue for loaded files


def main():
    global ignored_exts

    with open(config.IGNORED_EXTS_PATH) as ie_file:
        ignored_exts = set(ie_file.read().splitlines())

    load_files(config.DATASET_DIR)
    process_files()

def load_files(dataset):
    # go through all files in given directory (recursively)
    for dirpath, _, filenames in os.walk(dataset):
        for filename in filenames:
            if is_candidate_file(filename):
                file_path = os.path.join(dirpath, filename)
                files_q.put(file_path) # add file path to queue


def is_candidate_file(filename):
    # remove '@...' and '?...' parts of the file
    ext = re.sub(r'(\@|\?).*$', '', filename)
    # keep only the last file extension
    ext = re.sub(r'(^[^\.]*$|^([^\.]*\.)*)', '', ext)
    
    ext = ext.lower() # to match also UPPERCASE extensions
    # due performance, no file MIME type check here
    return not ext in ignored_exts


def process_files():
    while not files_q.empty():
        a = files_q.get()


main() # the entry point of the program
