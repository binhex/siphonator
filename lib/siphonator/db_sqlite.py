import sqlite_utils
import os

class DbSqlite(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance

    def create_database(self, db_path, db_version):

        db_filepath = os.path.join(db_path, u"siphonator.db")

        # create database if it doesnt already exist
        db = sqlite_utils.Database(db_filepath)

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        db.execute( "PRAGMA user_version = {v:d}".format(v=db_version) )

        # create tables with columns if it doesn't already exist
        db_tables = ['history', 'queued']

        for db_table in db_tables:

            db[db_table].create({
                "id": int,
                "imdb_id": str,
                "imdb_name": str,
                "imdb_rating": str,
                "imdb_votes": str,
                "imdb_chars": str,
                "imdb_director": str,
                "imdb_writer": str,
                "imdb_plot": str
            }, pk="id", if_not_exists=True)

        # append to db

        # upgrade db

        # delete db

        # compress db