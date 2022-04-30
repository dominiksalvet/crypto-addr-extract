# author: Dominik Salvet
# login: xsalve03

import os

# file path constants
DATASET_DIR = "dataset" # the root path of the uncompressed dataset

IGNORED_DIRS_PATH = "ignored_dirs" # ignored directory names
IGNORED_EXTS_PATH = "ignored_exts" # ignored file extensions
CRYPTO_ADDRS_PATH = "crypto_addrs" # contains regex of various crypto addresses

# runtime environment configuration
NUM_THREADS = os.cpu_count() # defaults to number of CPU HW threads
PROGRESS_REPORT_INTERVAL = 1 # in seconds

CONTINUOUS_PROCESSING = False # enable for processing files as soon as they load
CONTINUOUS_BUFF_SIZE = 100_000 # size of buffer when continuous processing enabled
