# author: Dominik Salvet
# login: xsalve03

import os

# file path constants
DATASET_DIR = "dataset" # the root path of the uncompressed dataset
IGNORED_EXTS_PATH = "ignored_exts" # ignored file extensions

# runtime environment configuration
NUM_THREADS = os.cpu_count() # defaults to number of CPU HW threads
PROGRESS_REPORT_INTERVAL = 1 # in seconds
