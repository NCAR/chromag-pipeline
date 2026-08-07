# -*- coding: utf-8 -*-

"""Utilities for communicating with the database.
"""

import configparser
import os

import mysql
import mysql.connector


DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLE_NAMES = ["chromag_level0", "chromag_level1", "chromag_web"]


def get_table_definition(table_name: str):
    """Read the `{table_name}.tbl` file in this directory and return it."""
    table_filename = os.path.join(DATABASE_DIR, table_name + ".tbl")
    with open(table_filename, "r") as f:
        table_definition = f.read()
    return table_definition


def delete_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Deletes a database table of the given name, e.g., "chromag_level0", if
    it exists.
    """
    cursor.execute(f"drop table if exists {table_name}")


def create_table(cursor: mysql.connector.cursor_cext.CMySQLCursor, table_name: str):
    """Creates a database table of the given name, e.g., "chromag_level0"."""
    table_definition = get_table_definition(table_name)

    # create table
    cursor.execute(table_definition)


def get_connection(config_filename: str, config_section: str):
    cp = configparser.ConfigParser()
    cp.read(config_filename)
    host = cp.get(config_section, "host")
    user = cp.get(config_section, "user")
    password = cp.get(config_section, "password")
    port = cp.get(config_section, "port")
    database = cp.get(config_section, "database")
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    return connection


def initialize_tables(config_filename: str, config_section: str):
    connection = get_connection(config_filename, config_section)
    cursor = connection.cursor()

    # [TODO]: add logging and error checking

    for t in reversed(TABLE_NAMES):
        delete_table(cursor, t)

    for t in TABLE_NAMES:
        create_table(cursor, t)

    cursor.close()
    connection.close()
