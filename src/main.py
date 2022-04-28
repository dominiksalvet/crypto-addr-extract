# author: Dominik Salvet
# login: xsalve03

import os # used for working with file/directory paths
import magic # used for file type identification

import config # import custom configuration file


# global variables
accepted_exts = set() # using sets for quick search
refused_exts = set()
extra_mimes = set()


def main():
    global accepted_exts, refused_exts, extra_mimes

    with open(config.ACCEPTED_EXTS_PATH) as ae_file:
        accepted_exts = set(ae_file.read().splitlines())
    with open(config.REFUSED_EXTS_PATH) as re_file:
        refused_exts = set(re_file.read().splitlines())
    with open(config.EXTRA_MIMES_PATH) as em_file:
        extra_mimes = set(em_file.read().splitlines())

    extract_dir(config.DATASET_DIR)


def extract_dir(dir):
    for root, _, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            if is_candidate_file(file_path):
                extract_file(file_path)


def is_candidate_file(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower() # to match also UPPERCASE extensions

    # filter first only based on the filename (quicker)
    if ext in accepted_exts:
        return True
    elif ext in refused_exts:
        return False
    else: # filter files based on their content (slower)
        mime_type = magic.from_file(file_path, mime=True)
        return (mime_type.startswith('text/') or
                mime_type in extra_mimes)


# TODO: finish this function
def extract_file(file_path):
    print(file_path)


main() # the entry point of the program
