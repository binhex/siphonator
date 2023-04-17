import sqlite3
import sqlite_utils
import lib.siphonator.tools_various as siphonator_tools_various

# TODO once we have all imdb details in the database then any index title that matches an existing processed title can use the same imdb details without the need to contact imdb

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
            "download_link": str,
            "magnet_url": str,
            "category": str,
            "imdb_id": str,
            "imdb_title": str,
            "imdb_year": str,
            "imdb_poster_url": str,
            "imdb_plot_summary": str,
            "imdb_plot_outline": str,
            "imdb_rating": str,
            "imdb_votes": str,
            "imdb_title_type": str,
            "imdb_running_time_in_minutes": str,
            "imdb_genre_list": str,
            "imdb_director_list": str,
            "imdb_writer_list": str,
            "imdb_cast_list": str,
            "imdb_character_list": str,
            "imdb_languages_list": str,
            'imdb_country_list': str,
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
            "index_details": (self.index_dict.get('index_details')),
            "index_pubdate": (self.index_dict.get('index_pubdate')),
            "index_seeders": (self.index_dict.get('index_seeders')),
            "index_peers": (self.index_dict.get('index_peers')),
            "index_size": (self.index_dict.get('index_size')),
            "index_size_mb": (self.index_dict.get('index_size_mb')),
            "torrent_url": (self.index_dict.get('torrent_url')),
            "download_link": (self.index_dict.get('download_link')),
            "magnet_url": (self.index_dict.get('magnet_url')),
            "category": (self.index_dict.get('category')),
            "imdb_id": (self.index_dict.get('imdb_id')),
            "imdb_title": (self.index_dict.get('imdb_title')),
            "imdb_year": (self.index_dict.get('imdb_year')),
            "imdb_poster_url": (self.index_dict.get('imdb_poster_url')),
            "imdb_plot_summary": (self.index_dict.get('imdb_plot_summary')),
            "imdb_plot_outline": (self.index_dict.get('imdb_plot_outline')),
            "imdb_rating": (self.index_dict.get('imdb_rating')),
            "imdb_votes": (self.index_dict.get('imdb_votes')),
            "imdb_title_type": (self.index_dict.get('imdb_title_type')),
            "imdb_running_time_in_minutes": (self.index_dict.get('imdb_running_time_in_minutes')),
            "imdb_genre_list": (self.index_dict.get('imdb_genre_list')),
            "imdb_director_list": (self.index_dict.get('imdb_director_list')),
            "imdb_writer_list": (self.index_dict.get('imdb_writer_list')),
            "imdb_cast_list": (self.index_dict.get('imdb_cast_list')),
            "imdb_character_list": (self.index_dict.get('imdb_character_list')),
            "imdb_languages_list": (self.index_dict.get('imdb_languages_list')),
            "imdb_country_list": (self.index_dict.get('imdb_country_list')),
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
            "download_link",
            "magnet_url",
            "category",
            "imdb_id",
            "imdb_title",
            "imdb_year",
            "imdb_poster_url",
            "imdb_plot_summary",
            "imdb_plot_outline",
            "imdb_rating",
            "imdb_votes",
            "imdb_title_type",
            "imdb_running_time_in_minutes",
            "imdb_genre_list",
            "imdb_director_list",
            "imdb_writer_list",
            "imdb_cast_list",
            "imdb_character_list",
            "imdb_languages_list",
            'imdb_country_list',
        ))

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
        custom_title_full_compare = tools_various_instance.custom_title_full_compare(index_title)

        # get index title with sqlite wildcard char '%'
        custom_title_sqlite_query = tools_various_instance.custom_title_sqlite(index_title)
        self.logger_instance.debug(u"Database index title query is '%s'" % custom_title_sqlite_query)

        # query database, note this maybe subject to sqlite injection as I am dynamically setting table and column
        sqlite_result_generator = db_sqlite_connection.query("SELECT %s FROM %s WHERE %s LIKE ?" % (sqlite_column, sqlite_table, sqlite_column), (custom_title_sqlite_query,))

        for sqlite_result in sqlite_result_generator:

            # get index_title from sqlite query
            index_title_sqlite_result = sqlite_result.get('index_title')

            # get comparison dictionary for index title from sqlite query
            tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
            custom_title_full_compare_sqlite = tools_various_instance.custom_title_full_compare(index_title_sqlite_result)

            # compare index title against sqlite query index title
            if custom_title_full_compare == custom_title_full_compare_sqlite:

                return True

        return False

    def upgrade_database(self):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # get db_version from existing database
        disk_db_version_gen = db_sqlite_connection.query("PRAGMA user_version")

        # get db on disk version
        disk_db_version_list = [(i.get('user_version')) for i in disk_db_version_gen]
        disk_db_version = disk_db_version_list[0]

        # if database is up to date then do nothing
        if self.db_version == disk_db_version:

            return

        # if v1 then upgrade to v2 by adding in the missing column
        if disk_db_version == 1:

            db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN imdb_country_origins_list text")
            self.set_db_version(2)

        # if v2 then upgrade to v3 by rename columns
        if disk_db_version == 2:

            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_genres_list TO imdb_genre_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_country_origins_list TO imdb_country_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_spoken_languages_list TO imdb_languages_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_credits_director_list TO imdb_director_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_credits_writer_list TO imdb_writer_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_credits_cast_list TO imdb_cast_list")
            db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_credits_character_list TO imdb_character_list")
            self.set_db_version(3)

        # set db to current version
        self.set_db_version(self.db_version)

        # delete db

    def set_db_version(self, version):

        # create database connection
        db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        db_sqlite_connection.execute( "PRAGMA user_version = {v:d}".format(v=version) )

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
