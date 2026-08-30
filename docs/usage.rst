=====
Usage
=====

The functionality of the ChroMag pipeline is exposed from the `chromag` command
line utility. It has various subcommands to run the pipeline and perform
various ancillary actions related to pipeline outputs::

    $ chromag --help
    usage: chromag [-h] [-v] {archive,cat,clearday,createdb,log,ls,ps,end-of-day,eod,reprocess} ...

    ChroMag pipeline 0.0.2-dev [b9175a3]

    positional arguments:
    {archive,cat,clearday,createdb,log,ls,ps,end-of-day,eod,reprocess}
                            sub-command help
        archive             archive data of the given level and dates
        cat                 display file header of the given ChroMag FITS file
        clearday            clear results for the given date(s)
        createdb            create the ChroMag database tables
        log                 display, and optionally filter, log output from the ChroMag pipeline
        ls                  list ChroMag files with extra ChroMag-specific info
        ps                  list running ChroMag processes
        end-of-day (eod)    run end-of-day pipeline on the given dates
        reprocess           reprocess the given dates

    options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit


end-of-day (eod) subcommand
---------------------------

The end-of-day subcommand runs the ChroMag pipeline

::

    $ chromag eod --help
    usage: chromag end-of-day [-h] [-f CONFIGURATION_FILENAME] [date-expr ...]

    positional arguments:
    date-expr             dates to run on in the form YYYYMMDD including lists (using commas) and ranges
                            (using hyphens where end date is not included)

    options:
    -h, --help            show this help message and exit
    -f, --configuration-filename CONFIGURATION_FILENAME
                            Configuration filename


reprocess subcommand
--------------------
