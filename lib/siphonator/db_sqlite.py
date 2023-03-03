import sqlite3
import sqlite_utils


class DbSqlite(object):

    def __init__(self, logger_instance, db_filepath):

        self.logger_instance = logger_instance
        self.db_filepath = db_filepath

    def create_database(self, db_version):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        db_sqlite_connection.execute( "PRAGMA user_version = {v:d}".format(v=db_version) )

        # create tables with columns if it doesn't already exist
        db_sqlite_connection["history"].create({
            "id": int,
            "index_title": str,
            "result": str,
            "result_details": str,
            "imdb_id": str,
            "imdb_name": str,
            "imdb_rating": str,
            "imdb_votes": str,
            "imdb_chars": str,
            "imdb_director": str,
            "imdb_writer": str,
            "imdb_plot": str
        }, pk="id", if_not_exists=True)

        # duplicate table
        try:

            db_sqlite_connection["history"].duplicate("queued")

        except sqlite3.OperationalError:

            pass

    def write_database(self, **kwargs):

        index_dict = kwargs

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        db_sqlite_connection["history"].insert_all([{
            "index_title": (index_dict.get('index_title')),
            "result": (index_dict.get('result')),
            "result_details": (index_dict.get('result_details')),
        }], pk="id", column_order=("index_title", "result", "result_details"))

    def read_database(self, sqlite_table, sqlite_column, index_title):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # query database, note this maybe subject to sqlite injection as i am dynamically setting table and column
        sqlite_result_generator = db_sqlite_connection.query("SELECT %s FROM %s WHERE %s LIKE ?" % (sqlite_column, sqlite_table, sqlite_column), ('%'+index_title+'%',))

        for sqlite_result in sqlite_result_generator:

            # if index title already in database then return True
            if index_title in (sqlite_result.get('index_title')):

                return True

        return False

        # append to db

        # upgrade db

        # delete db

    def vacuum_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # compress db
        db_sqlite_connection.vacuum()

    def close_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        db_sqlite_connection.close()