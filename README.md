# vaers_db

## Graphical tool to check out the C-19 VAERS data

* Automatic data cleanup
* Ability to filter on age, gender, severity
* Two modes: Total number of events in time vs Lot-based analysis

--> For screen shots see the 'Issues' tab.



### Input Data

You need to obtain the data from:

https://vaers.hhs.gov/data/datasets.html

The 4 needed files are: 202[01]VAERS[DATA,VAX].csv .
Cleaning up is necessary because the data contains a lot of non-basic ASCII characters, which my Python processing chain doesn't like. Get rid of those, for example using sed, or vim:
:%s/[^\x00-\x7F]//g
As an example, for the 2021 data this resulted in '12532 substitutions on 4946 lines'
I don't use the 'SYMPTOMS' files (as they contain free-format textual stuff not reaily usable).

The code reads this cleaned data from CSV, tries to correct some of the intrinsic issues (like the free-text lot names) and then stores everything in an object dump (using dill (which is based on pickle)). This is in fact a cache. The speed-up is gigantic (like 100x easy).

.CSV files -> vxdb.bin

Then, I extract from that all-vaxxes database a COVID-only version, with some bells and whistles:

vxdb.bin -> covvxdb.bin

If one of the .bin files is present, it will use it. Therefore if you download new .csv files, remove all .bin files. The new, updated .bin files are then automatically generated on first use. Note that this conversion costs minutes.

I guess it's a bad idea to accept anyone else's .bin files; pickle and dill both warn that this is dangerous because of the possibility to hack your system.

For a bit of proper application management:

* In the installation directory, run 'python3 covvxdb.py'. This will generate the .BIN files needed for fast access., and will make sure no writing in the installation directory is required.
* The python scripts will assume installation at user_home_dir/vaers_db . To change this, set VX_PY_BASE_DIR to the actual directory.
* The user file selectors will by default go to the user's home directory. A better default can be set using the VX_PY_USER_DATA_DIR variable


### Code

I'm an ex-C++ programmer and tend to not use Python in all of its shiny flexible power. Going all-out feels too dangerous. I do think Python is beautiful, and if you can handle its power - why not. I found a bit of precise and more explicit, dumb-like working improves the quality of what I produce and shortens the time-to-release.

I try to write code that explains itself, hence the longer names and pretty strict usage of naming conventions.

For the UI, I'm using Qt because I'm familiar with it, and it simply does the job well. I'm using a thin convenience layer to make life easier (PyQt itself is huge and I need only a few things in specific ways).

I'm sure a lot of optimisations can be applied, but unless they significantly improve the functionality I'll pass.

### Running

The app is developed using Python 3.8 . I've minimised dependencies, but still:
* For creating cache files: 'dill' (an improved variant of 'pickle')
* For the UI: 'PyQt5' - including PyQtChart.
Both are available from the Ubuntu package manager (python3-dill and python3-pyqt5.qtchart)

To start, just run:

python3 ui_cov.py

... but you can use quite a few scripts stand-alone, for example to generate .bin files, or run with the debug dataset. For that, just add 'd' to the command line, as in:

python3 vxdb.py d

By default, the software handles events using per-week bins. If you want to see it per-day, add 'DAY' to the command line of cov_ui.py, as in:
python3 cov_ui.py DAY

The date used is the vaxx date (not the report or incidence date).
