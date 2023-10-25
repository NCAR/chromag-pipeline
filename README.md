# ChroMag calibration pipeline

## Requirements

- Python 3.7 or later

## Installation

The ChroMag pipeline software can be installed via `pip`:

``` bash
pip install chromag
```

Or from source:

``` bash
pip install /path/to/chromag-pipeline
```

If you intend to make changes to the code, you should install the development
dependencies with:

``` bash
pip install -e /path/to/chromag-pipeline[dev]
```

Changes in the source code will immediately be used in subsequent running of the
code.

## Running

``` bash
$ chromag --help
usage: chromag [-h] [-v] {cat,log,ls,end-of-day,eod} ...

ChroMag pipeline 0.1.0

positional arguments:
  {cat,log,ls,end-of-day,eod}
                        sub-command help
    cat                 display file header
    log                 display, and optionally filter, log output
    ls                  list files with extra ChroMag-specific info
    end-of-day (eod)    run end-of-day pipeline

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

Help for each sub-command can be obtained as well, e.g.:

``` bash
$ chromag eod --help
usage: chromag end-of-day [-h] [-f CONFIGURATION_FILENAME] [date-expr ...]

positional arguments:
  date-expr             dates to run on in the form YYYYMMDD including lists (using commas) and
                        ranges (using hyphens where end date is not included)

options:
  -h, --help            show this help message and exit
  -f CONFIGURATION_FILENAME, --configuration-filename CONFIGURATION_FILENAME
                        Configuration filename
```

## Development

### Testing

``` bash
pytest tests
```

### Linting

To get perform static analysis on the source code to check for common patterns
that might cause errors or other problems, run `pylint` from the root directory
of the repository:

``` bash
pylint chromag tests
```
