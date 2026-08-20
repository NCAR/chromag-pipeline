# -*- coding: utf-8 -*-

"""Utilities for connecting to the database.
"""

import configparser
import errno
import os

import mysql.connector


def get_db_info(config_filename: str, config_section: str):
    """Read a configuration file with the login information for the database.
    The config file should have sections like::

        [mgalloy@server]
        host     : server.hao.ucar.edu
        user     : mgalloy
        password : MYPASSWORD
        port     : 3306
        database : MLSO

    This routine needs the file path for the config file and the section to use.
    """
    cp = configparser.ConfigParser()
    cp.read(config_filename)

    host = cp.get(config_section, "host")
    user = cp.get(config_section, "user")
    password = cp.get(config_section, "password")
    database = cp.get(config_section, "database")

    return host, user, password, database


def get_connection(config_filename: str, config_section: str):
    """Make connection to database given the configuration filename and section
    within it with login details for the database. Returns connection.
    """
    if config_filename is None:
        raise NameError("database configuration filename is not defined")

    if not os.path.exists(config_filename):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config_filename
        )

    if config_section is None:
        raise NameError("database configuration section is not defined")

    host, user, password, database = get_db_info(config_filename, config_section)

    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )

    return connection
