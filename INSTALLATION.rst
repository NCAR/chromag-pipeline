.. highlight:: shell

============
Installation
============

Download and install a recent `Anaconda`_ distribution, following the
installation instructions from the distribution. Make sure to update your shell
path environment variable to include the `bin` directory of the Anaconda
installation.

.. _Anaconda: https://www.anaconda.com/download/


Stable release
--------------

To install the latest stable version of the ChroMag pipeline, run this command
in your terminal:

.. code-block:: console

    $ pip install chromag

This is the preferred method to install the ChroMag pipeline, as it will always
install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for the ChroMag pipeline can be downloaded from the `Github repo`_.

You can clone the public repository using your choice of HTTPS (password) or
SSH (key):

.. code-block:: console

    $ git clone https://github.com/NCAR/chromag-pipeline.git

or

.. code-block:: console

    $ git clone git://github.com/NCAR/chromag-pipeline.git

Alternatively, download the `tarball`_ and unzip it:

.. code-block:: console

    $ curl -OL https://github.com/NCAR/chromag-pipeline/archive/refs/heads/master.zip
    $ unzip master.zip

Once you have a copy of the source, you can install it with a few options
geared for those who want to make changes to the source code:

.. code-block:: console

    $ pip install -e '/path/to/chromag-pipeline[dev]'

The ``-e`` will install `chromag` in "develop mode" so the changes in the
source code are immediately reflected in behavior without a re-install. The
``[dev]`` at the end will install the `dev` dependencies for testing and
building the docs as well as the standard dependencies.

To handle changes you make in the build system, e.g., new dependencies, you
might have to reinstall:

.. code-block:: console

    $ pip install --upgrade -e '/path/to/chromag-pipeline[dev]'

.. _Github repo: https://github.com/NCAR/chromag-pipeline
.. _tarball: https://github.com/NCAR/chromag-pipeline/tarball/master
