import sqlite3
import sqlite_utils
import lib.siphonator.tools_various as siphonator_tools_various


class DbSqlite(object):

    def __init__(self, logger_instance, init_dict, result_dict=None):

        self.logger_instance = logger_instance
        self.init_dict = init_dict
        self.result_dict = result_dict
        self.db_version = init_dict['db_version']
        self.db_filepath = init_dict['db_filepath']

    def create_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        self.set_db_version(self.db_version)

        # create tables with columns if it doesn't already exist
        db_sqlite_connection["history"].create({
            "id": int,
            "index_title": str,
            "result": str,
            "result_details": str,
            "index_details": str,
            "index_pubdate": str,
            "index_seeders": str,
            "index_peers": str,
            "index_size": str,
            "index_size_mb": str,
            "torrent_url": str,
            "magnet_url": str,
            "category": str,
            "imdb_id": str,
            "imdb_title": str,
            "imdb_year": str,
            "imdb_poster_url": str,
            "imdb_trailer_url": str,
            "imdb_plot_summary": str,
            "imdb_plot_outline": str,
            "imdb_rating": str,
            "imdb_votes": str,
            "imdb_title_type": str,
            "imdb_running_time_in_minutes": str,
            "imdb_genres_list": str,
            "imdb_credits_director_list": str,
            "imdb_credits_writer_list": str,
            "imdb_credits_cast_list": str,
            "imdb_credits_character_list": str,
            "imdb_language_list": str,
            'imdb_country_list': str,
        }, pk="id", if_not_exists=True)

        # duplicate table
        try:

            db_sqlite_connection["history"].duplicate("queued")

        except sqlite3.OperationalError:

            pass

    def write_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        db_sqlite_connection["history"].insert_all([{
            "index_title": (self.result_dict.get('index_title')),
            "result": (self.result_dict.get('result')),
            "result_details": (self.result_dict.get('result_details')),
            "index_details": (self.result_dict.get('index_details')),
            "index_pubdate": (self.result_dict.get('index_pubdate')),
            "index_seeders": (self.result_dict.get('index_seeders')),
            "index_peers": (self.result_dict.get('index_peers')),
            "index_size": (self.result_dict.get('index_size')),
            "index_size_mb": (self.result_dict.get('index_size_mb')),
            "torrent_url": (self.result_dict.get('torrent_url')),
            "magnet_url": (self.result_dict.get('magnet_url')),
            "category": (self.result_dict.get('category')),
            "imdb_id": (self.result_dict.get('imdb_id')),
            "imdb_title": (self.result_dict.get('imdb_title')),
            "imdb_year": (self.result_dict.get('imdb_year')),
            "imdb_poster_url": (self.result_dict.get('imdb_poster_url')),
            "imdb_trailer_url": (self.result_dict.get('imdb_trailer_url')),
            "imdb_plot_summary": (self.result_dict.get('imdb_plot_summary')),
            "imdb_plot_outline": (self.result_dict.get('imdb_plot_outline')),
            "imdb_rating": (self.result_dict.get('imdb_rating')),
            "imdb_votes": (self.result_dict.get('imdb_votes')),
            "imdb_title_type": (self.result_dict.get('imdb_title_type')),
            "imdb_running_time_in_minutes": (self.result_dict.get('imdb_running_time_in_minutes')),
            "imdb_genres_list": (self.result_dict.get('imdb_genres_list')),
            "imdb_credits_director_list": (self.result_dict.get('imdb_credits_director_list')),
            "imdb_credits_writer_list": (self.result_dict.get('imdb_credits_writer_list')),
            "imdb_credits_cast_list": (self.result_dict.get('imdb_credits_cast_list')),
            "imdb_credits_character_list": (self.result_dict.get('imdb_credits_character_list')),
            "imdb_language_list": (self.result_dict.get('imdb_language_list')),
            "imdb_country_list": (self.result_dict.get('imdb_country_list')),
        }], pk="id", column_order=(
            "index_title",
            "result",
            "result_details",
            "index_details",
            "index_pubdate",
            "index_seeders",
            "index_peers",
            "index_size",
            "index_size_mb",
            "torrent_url",
            "magnet_url",
            "category",
            "imdb_id",
            "imdb_title",
            "imdb_year",
            "imdb_poster_url",
            "imdb_trailer_url",
            "imdb_plot_summary",
            "imdb_plot_outline",
            "imdb_rating",
            "imdb_votes",
            "imdb_title_type",
            "imdb_running_time_in_minutes",
            "imdb_genres_list",
            "imdb_credits_director_list",
            "imdb_credits_writer_list",
            "imdb_credits_cast_list",
            "imdb_credits_character_list",
            "imdb_language_list",
            'imdb_country_list',
        ))

    def read_database_simple(self, sqlite_table, sqlite_column, index_title):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # query database, note this maybe subject to sqlite injection as I am dynamically setting table and column
        sqlite_result_generator = db_sqlite_connection.query(f"SELECT {sqlite_column} FROM {sqlite_table} WHERE {sqlite_column} LIKE ?", ('%'+index_title+'%',))

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
        custom_title_full_compare = tools_various_instance.custom_title_full_compare(index_title)

        # get index title with sqlite wildcard char '%'
        custom_title_sqlite_query = tools_various_instance.custom_title_sqlite(index_title)
        self.logger_instance.debug(f"Database index title query is '{custom_title_sqlite_query}'")

        # query database, note this maybe subject to sqlite injection as I am dynamically setting table and column
        sqlite_result_generator = db_sqlite_connection.query(f"SELECT {sqlite_column} FROM {sqlite_table} WHERE {sqlite_column} LIKE ?", (custom_title_sqlite_query,))

        for sqlite_result in sqlite_result_generator:

            # get index_title from sqlite query
            index_title_sqlite_result = sqlite_result.get('index_title')

            # get comparison dictionary for index title from sqlite query
            tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
            custom_title_full_compare_sqlite = tools_various_instance.custom_title_full_compare(index_title_sqlite_result)

            # compare index title against sqlite query index title
            if custom_title_full_compare in custom_title_full_compare_sqlite:

                return True

        return False

    def upgrade_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # get db version on disk
        disk_db_version = self.get_db_version()

        # if database is up-to-date then do nothing
        if self.db_version == disk_db_version:

            return

        # if v1 then upgrade to v2 by adding in the missing column
        if disk_db_version == 1:

            db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN imdb_country_origins_list text")

            self.set_db_version(2)

        # if v2 then upgrade to v3 by renaming column
        if disk_db_version == 2:

            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_country_origins_list TO imdb_country_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_spoken_languages_list TO imdb_language_list")

            self.set_db_version(3)

        # if v3 then upgrade to v4 by adding in the missing column
        if disk_db_version == 3:

            db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN imdb_trailer_url text")

            self.set_db_version(4)

        # set db to current version, all upgrades performed
        self.set_db_version(self.db_version)

    def set_db_version(self, version):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        db_sqlite_connection.execute("PRAGMA user_version = {v:d}".format(v=version))

    def get_db_version(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # get db_version from existing database
        disk_db_version_gen = db_sqlite_connection.query("PRAGMA user_version")

        # get db on disk version
        disk_db_version_list = [(i.get('user_version')) for i in disk_db_version_gen]
        disk_db_version = disk_db_version_list[0]

        return disk_db_version

    def vacuum_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # compress db
        db_sqlite_connection.vacuum()

    def close_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # close database
        db_sqlite_connection.close()

    def delete_database(self):

        pass
