import sqlite3
import sqlite_utils
import lib.siphonator.tools_various as siphonator_tools_various

class DbSqlite(object):

    def __init__(self, logger_instance, **kwargs):

        self.logger_instance = logger_instance
        self.index_dict = kwargs
        self.db_filepath = self.index_dict.get('db_filepath')
        self.db_version = self.index_dict.get('db_version')

    def create_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        db_sqlite_connection.execute( "PRAGMA user_version = {v:d}".format(v=self.db_version) )

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
    # TODO send kwargs to here, not init, and then strip out duplicate instances for dbsqlite calls in index_proxy
    def write_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        db_sqlite_connection["history"].insert_all([{
            "index_title": (self.index_dict.get('index_title')),
            "result": (self.index_dict.get('result')),
            "result_details": (self.index_dict.get('result_details')),
        }], pk="id", column_order=("index_title", "result", "result_details"))

    def read_database_simple(self, sqlite_table, sqlite_column, index_title):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # query database, note this maybe subject to sqlite injection as i am dynamically setting table and column
        sqlite_result_generator = db_sqlite_connection.query("SELECT %s FROM %s WHERE %s LIKE ?" % (sqlite_column, sqlite_table, sqlite_column), ('%'+index_title+'%',))

        for sqlite_result in sqlite_result_generator:

            # if index title already in database then return True
            if index_title in (sqlite_result.get('index_title')):

                return True

        return False

    def read_database_adv(self, sqlite_table, sqlite_column, index_title):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # get comparison dictionary from index_title
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
        custom_title_full_compare_dict = tools_various_instance.custom_title_full_compare(index_title)
        custom_title_full_compare = custom_title_full_compare_dict.get('custom_title_full_compare')

        # get index title with sqlite wildcard char '%'
        custom_title_sqlite_dict = tools_various_instance.custom_title_sqlite(index_title)
        custom_title_sqlite_query = custom_title_sqlite_dict.get('custom_title_sqlite')
        self.logger_instance.debug(u"Database index title query is '%s'" % custom_title_sqlite_query)

        # query database, note this maybe subject to sqlite injection as I am dynamically setting table and column
        sqlite_result_generator = db_sqlite_connection.query("SELECT %s FROM %s WHERE %s LIKE ?" % (sqlite_column, sqlite_table, sqlite_column), (custom_title_sqlite_query,))

        for sqlite_result in sqlite_result_generator:

            # get index_title from sqlite query
            index_title_sqlite_result = sqlite_result.get('index_title')

            # get comparison dictionary for index title from sqlite query
            tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
            custom_title_full_compare_sqlite_dict = tools_various_instance.custom_title_full_compare(index_title_sqlite_result)
            custom_title_full_compare_sqlite = custom_title_full_compare_sqlite_dict.get('custom_title_full_compare')

            # compare index title against sqlite query index title
            if custom_title_full_compare == custom_title_full_compare_sqlite:

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

        #c lose database
        db_sqlite_connection.close()