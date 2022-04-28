# author: Dominik Salvet
# login: xsalve03

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

        if not ext in exts_set:
            first_occs[ext] = os.path.join(dirpath, filename)
            exts_set.add(ext)
        exts_list.append(ext)

num_occs = Counter(exts_list)

print("file extension\toccurrences\tfirst occurrence")
print("------------------------------------------------")
for occ in num_occs:
    print(occ, num_occs[occ], first_occs[occ], sep = "\t\t")
