# author: Dominik Salvet
# login: xsalve03

import os


# file path constants
DATASET_DIR = "dataset" # the root path of the uncompressed dataset

ACCEPTED_EXTS_PATH = "accepted_exts" # accepted file extensions
REFUSED_EXTS_PATH = "refused_exts" # refused file extensions


# runtime environment configuration
NUM_THREADS = os.cpu_count() # defaults to number of CPU HW threads
PROGRESS_REPORT_INTERVAL = 1 # in seconds


# file filtering configuration
IGNORE_GIT_REPOS=True # when enabled, files of .git directories are ignored

# MIME type file identification (improves file filtering quality)
USE_MIME = True # when disabled, uses only refused extensions file to decide
MIME_CACHE_THRESHOLD = 2 # number of subsequent identical results to use cache
