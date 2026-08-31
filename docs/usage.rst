=====
Usage
=====

The functionality of the ChroMag pipeline is exposed through the ``chromag``
command line utility. It has many subcommands to run the pipeline and perform
various ancillary actions related to pipeline outputs::

    $ chromag -h
    usage: chromag [-h] [-v] {archive,cat,clearday,createdb,log,ls,ps,process,reprocess} ...

    ChroMag pipeline 0.0.2-dev [b9175a3*]

    positional arguments:
    {archive,cat,clearday,createdb,log,ls,ps,process,reprocess}
                            sub-command help
        archive             archive data of the given level and dates
        cat                 display file header of the given ChroMag FITS file
        clearday            clear results for the given date(s)
        createdb            create the ChroMag database tables
        log                 display, and optionally filter, log output from the ChroMag pipeline
        ls                  list ChroMag files with extra ChroMag-specific info
        ps                  list running ChroMag processes
        process             run pipeline on the given dates
        reprocess           reprocess the given dates

    options:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit


Configuration file
------------------

Several of the ``chromag`` utility subcommands require a configuration file to
define required and optional values, e.g., where raw data is found, where to
put the processed data, where to put the logs, etc.

``chromag/config/chromag.config.spec.cfg`` defines the options that are found in
a configuration file. The minimal configuration file needed is::

    [raw]
    # need to specify either basedir OR routing_file
    basedir        : /path/to/data
    routing_file   : /path/to/routing/file.cfg

    [process]
    # need to specify either basedir OR routing_file
    basedir        : /path/to/put/data
    routing_file   : /path/to/routing/file.cfg

    [logging]
    basedir        : /path/to/put/logs

There are many other options for creating engineering plots, sending
notifications, specifying whether to archive and/or publish various products,
and many other actions.


``process``/``reprocess`` subcommands
-------------------------------------

The ``process`` and ``reprocess`` subcommands run the ChroMag pipeline. The
``reprocess`` subcommand clears any previous results before doing the same work
the ``process`` subcommand does.

The options for running the ``process`` subcommand are::

    $ chromag process --help
    usage: chromag process [-h] [-f CONFIGURATION_FILENAME] [date-expr ...]

    positional arguments:
    date-expr             dates to run on in the form YYYYMMDD including lists (using commas) and ranges
                            (using hyphens where end date is not included)

    options:
    -h, --help            show this help message and exit
    -f, --configuration-filename CONFIGURATION_FILENAME
                            Configuration filename

The dates can specified in many ways:

- ``chromag process -f /path/to/config/file.cfg 20250813``
- ``chromag process -f /path/to/config/file.cfg 20250812,20250813``
- ``chromag process -f /path/to/config/file.cfg 20250812 20250813``
- ``chromag process -f /path/to/config/file.cfg 20250812-20250815`` (inclusive
  start date and exclusive end date, so this processes 20250812, 20250813, and
  20250814)