# author: Dominik Salvet
# login: xsalve03

import os
import re

# file path constants
# the default dataset contains all archives with size of <=20MB
DATASET_DIR = "dataset" # the root path of the uncompressed dataset

IGNORED_DIRS_PATH = "ignored_dirs" # ignored directory names
IGNORED_EXTS_PATH = "ignored_exts" # ignored file extensions
CRYPTO_ADDRS_PATH = "crypto_addrs" # contains regex of various crypto addresses

RESULTS_PATH = "results.json"

# runtime environment configuration
NUM_THREADS = os.cpu_count() # in default, use same amount as HW threads available
PROGRESS_REPORT_INTERVAL = 1 # in seconds

CONTINUOUS_PROCESSING = True # enable for processing files as soon as they load
CONTINUOUS_BUFF_SIZE = 100_000 # size of buffer when continuous processing enabled

# filtering options
ADDR_PRE_CHARS = r" \(" # possible characters before the address occurrence
ADDR_POST_CHARS = r" \)\.\,\?\!"

# when a crypto address is matched, search for first occurrences of items below
SEARCH_FOR_FIRST_EMAIL = True # email address
SEARCH_FOR_FIRST_AMOUNT = True # amount of money

# regular expressions of extra file content info (see above)
EMAIL_RE = re.compile(r'[\w\.\-]+@[\w\.\-]+') # email regex, if used
AMOUNT_RE = re.compile(r'[\$]\d+(\.\d+)?')
