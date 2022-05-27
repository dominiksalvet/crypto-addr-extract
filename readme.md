# Cryptocurrency Addresses Extractor

The main focus of this program is to extract cryptocurrency addresses from given unstructured dataset. This dataset is expected to be quite big and the content of its files heterogenous. As the speed of processing is key, it was required to come up with optimizations, which would accelerate processing files. The examined dataset is accessible at https://archive.org/download/dnmarchives.

As Python is considered one of the most used programming languages for data science, it was an obvious choice, even though comparing with other, compiled, languages it may lack behind a bit in terms of performance. Nevertheless, if choosing C++ for example, it would take much longer programming time to create a program like this. Hence, Python is the used programming languge. Only standard libraries were used.

> This program was created within a course of my master's studies.

## Implementation Details

The program itself is implemented in file `main.py` (it is not that decomposed to break into multiple files). To its run, it also requires a configuration file `config.py`. We can summarize how the program works in the following steps (they will be examinated in detail later):

1. Load configuration
2. Spawn appropriate threads
3. Walk through dataset
4. Process files in threads
5. If matched, add to found records
6. Write found records to a file

### 1. Load configuration

When the program starts up, first it loads configuration from `config.py`. Since the program does not expect any arguments, all user configuration is stored in this file. Mainly, all important file paths are placed here. Also, there are other configuration such as threads number, buffer size, and similar.

The following file paths are included in `config.py`, and the files of these paths also include some kind of configuration (they are loaded to program variables). Here is their list:

* `ignored_dirs` - ignored directory names
* `ignored_exts` - ignored file extensions
* `crypto_addrs` - cryptocurrency address regular expressions

The `ignored_dirs` contains directory names, one for each line, and the target file is ignored on input if it contains this directory anywhere in its path (more on implementation later). The `ignored_exts` contains a list of ignored file extensions (one per line, case insensitive if stored in lowercase form). The `crypto_addrs` contains lines with format `<crypto_symbol> <regex>` (e.g., `btc ([13]|bc1)[a-zA-HJ-NP-Z0-9]{25,39}`). The exception from this is the first line, which must contain a common regular expression of all listed regular expressions.

### 2. Spawn appropriate threads

Since the performance is important, it was inevitable to utilize multithreading. Even though this program is very storage/memory intensive, increasing thread count may improve performance.

First, there is a progress monitor thread, and its main task is to report progress in user-friendly form. It reports the number of loaded filepaths (during dataset walking), the number of processed files, and the number found addresses. The default period of progress reporting is one second.

Also, main work threads are spawned here, and they take jobs (i.e., filepaths) from a thread-safe queue and process them individually. Based on configuration, it is possible to spawn those after loading the file paths, so that the user knows the number of files to be processed as soon as possible (lower performance, though). Otherwise, a queue buffer is used and its size is defined in the `config.py` file.

### 3. Walk through dataset

The dataset is expected to be a directory of unstructured data (so it must be already uncompressed). Here is the part, where early optimizations are performed, since when reaching a directory, whose name matches with some in the `ignored_dirs` file, it will be pruned from further file walk. All further processing works with filepaths that belong to files (directories are omitted). If the currect file of the file walk has a file extension, which is listed in the `ignored_exts` file, it is automatically skipped.

Once a file is passed through these quick filters, its path is added to a thread-safe queue of files to be processed. The number of loaded filepaths for progress monitor is increased.

### 4. Process files in threads

Each thread has its own counter of processed files and the number of found addresses. Those counters are added together, each type separately, and then used when reporting progress. The main job of each thread is to take a filepath from the filepath queue, load its content, process it accordingly, and repeat as long as there are items in the queue (remember that the queue is thread-safe).

Once we have the file content read in a variable, we try to match the common cryptocurrency regular expression on the content and keep all the matches. Then, for each match, we need to identify, which type of cryptocurrency it is based on lines from the `crypto_addrs` file. It is also possible that it does not belong to any recognized address, in which case the match is skipped since obviously, it was a false positive.

If it was a know currency, we extract the site name based on its filepath. Then, in default, we try to extract the first email address and money amount occurrences from the file as a simple context indicator. Even though email addresses are not vastly present in my subset of dataset and may be distorted when using this approach, I consider them better identity signs than usernames or crypto exchange names (since they should be unique and non-transferable). Also, for performance and universality reasons, I was unable to perform any more complex file parsing than optimized regular expressions (note that once an email is found, further search is skipped). The money amount indicator should hint us about the importance of the match.

Once the above information is collected, it is stored to found records.

### 5. Add to found records

The found records are implemented as a multi-level nested dictionary, which offers very convenient access. There is an inserting algorithm involved, which prevents inserting duplicate data, and bloating the final results. Also, if no occurrence of email or money amout was found for the currently inserted item, it inserts a simpler leaf item.

The dictionary is designed in the way that if a cryptocurrency address was found in multiple sites, it cluster the results together in one record. Also, the counting of address occurrences is performed here.

### 6. Write found records to a file

The standard library `json` directly contains a function to store a dictionary into a file. The program uses it, and stores the found records to the `results.json` file in default. It respects the following structure template:

```
addresses:
    <address>:
        symbol: <symbol>
        count: <count>
        sites:
            <site name>
                <filepath>
                ...
            ...
    ...
```

> Optionally, `<filepath>` may have an array of `<email>` and `<amount>`. Each is present only if it exists. The `...` expression means array of the above item with the same level of indentation. 

## File Extension Analysis

For the purpose of this project, a simple Python program for creating a summary of file extensions used in files of a directory was developed. It was crucial when determining the default contents of the `ignored_exts` file. It is implemented in the `extensions.py` file.

## Achieved Results

Due to my lower laptop performance (i5-7200U, 8 GB RAM, 256 GB SSD), I had to choose a smaller dataset. Hence, my dataset consists of all archives, whose size is less or equal to 20 MB. These are the dataset details:

* `dataset`
  * Total number of files and directories: 795 936
    * 760 257 are files
  * 20,3 GB in size

Experiments performed on my laptop and my dataset:

* 3574 matches, processed 670 154 files (some were filtered out)
* Executed for 5 minutes and 4 seconds
* Final `results.json` file has the size of 499 728 bytes
* The estimated time to process the whole dataset is roughly 6 hours
