# author: Dominik Salvet
# login: xsalve03

import os

# file path constants
DATASET_DIR = "dataset" # the root path of the uncompressed dataset

ACCEPTED_EXTS_PATH = "accepted_exts" # accepted file extensions
REFUSED_EXTS_PATH = "refused_exts" # refused file extensions

# other configuration
PROGRESS_REPORT_INTERVAL = 1 # in seconds
NUM_THREADS = os.cpu_count() # defaults to number of CPU HW threads
