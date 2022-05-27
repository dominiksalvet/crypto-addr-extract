#-------------------------------------------------------------------------------
# Copyright 2022 Dominik Salvet
# https://github.com/dominiksalvet/crypto-addr-extract
#-------------------------------------------------------------------------------

import os
import re
from typing import Counter


exts_set = set()
exts_list = []
first_occs = {}

for dirpath, _, filenames in os.walk("dataset"):
    for filename in filenames:
        ext = re.sub(r'(\@|\?).*$', '', filename)
        ext = re.sub(r'(^[^\.]*$|^([^\.]*\.)*)', '', ext)
        ext = ext.lower()
        if ext.isnumeric():
            ext = ""

        if not ext in exts_set:
            first_occs[ext] = os.path.join(dirpath, filename)
            exts_set.add(ext)
        exts_list.append(ext)

num_occs = Counter(exts_list)

print("file extension     occurrences  first occurrence")
print("------------------------------------------------")
for occ in num_occs:
    print(occ.ljust(17), str(num_occs[occ]).ljust(11), first_occs[occ], sep="  ")
