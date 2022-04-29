# author: Dominik Salvet
# login: xsalve03

import os

# file path constants
IGNORED_EXTS_PATH = "ignored_exts" # ignored file extensions
DATASET_DIR = "dataset" # the root path of the uncompressed dataset

# other configuration
PROGRESS_REPORT_INTERVAL = 1 # in seconds
HW_THREAD_COUNT = os.cpu_count()
