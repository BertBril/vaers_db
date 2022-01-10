Download zip files from:

https://vaers.hhs.gov/data/datasets.html

You only need the 2020 and 2021 zip files.

Unpack these zip files. Then, cleanup non-basic ASCII characters from the file, for example using sed, or vim:
:%s/[^\x00-\x7F]//g
You may also want to get rid of a lot of other bad stuff in there.

Those 4 cleaned up files will be scanned and the results will be put in fast access cache files.
