import sqlite_utils
import src.siphonator.tools_filters as siphonator_tools_filters


class DbSqlite(object):

    def __init__(self, logger_instance, init_dict, result_dict=None):

        self.logger_instance = logger_instance
        self.result_dict = result_dict
        self.db_version = init_dict['db_version']
        self.db_filepath = init_dict['db_filepath']
        self.db_sqlite_connection = sqlite_utils.Database(self.db_filepath)

    def create_tables(self):

        self.logger_instance.info(f"DB filepath '{self.db_filepath}' exists and is a sqlite database, but has no tables or data, performing initial creation of tables...")

        # create tables with columns if it doesn't already exist
        self.db_sqlite_connection["history"].create({
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
            "torrent_tag": str,
            "magnet_url": str,
            "category": str,
            "verified": str,
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

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        self.set_db_version(self.db_version)

    def write_database(self):

        self.db_sqlite_connection["history"].insert_all([{
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
            "torrent_tag": (self.result_dict.get('torrent_tag')),
            "magnet_url": (self.result_dict.get('magnet_url')),
            "category": (self.result_dict.get('category')),
            "verified": (self.result_dict.get('verified')),
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
            "torrent_tag",
            "magnet_url",
            "category",
            "verified",
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

    def read_database_simple(self, sqlite_table, sqlite_column, sqlite_query):

        # query database, note this maybe subject to sqlite injection as I am dynamically setting table and column
        sqlite_result_generator = self.db_sqlite_connection.query(f"SELECT * FROM {sqlite_table} WHERE {sqlite_column} LIKE ?", ('%'+sqlite_query+'%',))

        for sqlite_result in sqlite_result_generator:

            # if sqlite query already in database then return True
            if sqlite_query in (sqlite_result.get(sqlite_column)):

                return sqlite_result

        return None

    def read_database_adv(self, sqlite_table, sqlite_column, sqlite_query):

        tools_filters_instance = siphonator_tools_filters.ToolsFilters(self.logger_instance)

        # note we do this as opposed to reading from result_dict as we have not run index_name (from tools_filters) at this point
        sqlite_query_sanitised = tools_filters_instance.sanitise(sqlite_query)
        sqlite_query_compare = tools_filters_instance.compare(sqlite_query_sanitised)

        # if the sanitised title is none (badly formatted index title) then return
        if not sqlite_query_compare:
            return False

        # construct sqlite query with sqlite wildcard char '%'
        custom_title_sqlite_query = tools_filters_instance.sqlite_query(sqlite_query)
        self.logger_instance.debug(f"Database query is '{custom_title_sqlite_query}'")

        # query database, note this maybe subject to sqlite injection as I am dynamically setting table and column
        sqlite_result_generator = self.db_sqlite_connection.query(f"SELECT * FROM {sqlite_table} WHERE {sqlite_column} LIKE ?", (custom_title_sqlite_query,))

        for sqlite_result in sqlite_result_generator:

            # get result based on sqlite column name
            sqlite_result_column_filter = sqlite_result.get(sqlite_column)

            # get comparison dictionary for column name from sqlite query
            sqlite_result_column_filter_sanitised = tools_filters_instance.sanitise(sqlite_result_column_filter)
            sqlite_result_column_filter_compare = tools_filters_instance.compare(sqlite_result_column_filter_sanitised)

            if not sqlite_result_column_filter_compare:
                continue

            # compare sqlite query against sqlite query index title
            if sqlite_query_compare in sqlite_result_column_filter_compare:
                return sqlite_result

        return None

    def read_database_value(self, table_name, column_name, condition_column, condition_value):
        """
        Read a specific value from a database table and column.

        :param table_name: Name of the table to read from.
        :param column_name: Name of the column to read.
        :param condition_column: The column to use in the WHERE clause.
        :param condition_value: The value to match in the WHERE clause.
        :return: The value from the specified column, or None if no match is found.
        """
        try:
            # Construct the SQL query
            query = f"SELECT {column_name} FROM {table_name} WHERE {condition_column} = ?"

            # Execute the query with parameterized values to prevent SQL injection
            result = self.db_sqlite_connection.query(query, (condition_value,))

            # Fetch the first result
            for row in result:
                return row.get(column_name)

            # If no result is found, return None
            return None
        except Exception as e:
            # Log the error
            self.logger_instance.error(f"Failed to read from database: {e}")
            return None

    def write_database_value(self, table_name, column_name, value, condition_column, condition_value):
        """
        Write a specific value in a database table and column.

        :param table_name: Name of the table to update.
        :param column_name: Name of the column to update.
        :param value: The new value to set.
        :param condition_column: The column to use in the WHERE clause.
        :param condition_value: The value to match in the WHERE clause.
        :return: True if the update was successful, False otherwise.
        """
        try:
            # Construct the SQL query
            query = f"UPDATE {table_name} SET {column_name} = ? WHERE {condition_column} = ?"

            # Execute the query with parameterized values to prevent SQL injection
            self.db_sqlite_connection.execute(query, (value, condition_value))

            # Commit the transaction to save changes
            self.db_sqlite_connection.conn.commit()

            # Log the update
            self.logger_instance.info(f"Updated table '{table_name}', set '{column_name}' = '{value}' where '{condition_column}' = '{condition_value}'")
            return True
        except Exception as e:
            # Log the error
            self.logger_instance.error(f"Failed to update database: {e}")
            return False

    def upgrade_database(self, pragma_user_version):

        # if database is up-to-date then do nothing
        if self.db_version == pragma_user_version:
            self.logger_instance.debug(f"Required db version '{self.db_version}' and db version on disk '{pragma_user_version}' match, no upgrade required")
            return

        self.logger_instance.debug(f"Required db version '{self.db_version}' and db version on disk '{pragma_user_version}' do not match, upgrade required")

        # if v1 then upgrade to v2 by adding in the missing column
        if pragma_user_version == 1:
            self.logger_instance.debug(f"Upgrading db version on disk '{pragma_user_version}' to '{int(pragma_user_version)+1}'...")
            self.db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN imdb_country_origins_list text")
            self.set_db_version(2)

        # if v2 then upgrade to v3 by renaming column
        if pragma_user_version == 2:
            self.logger_instance.debug(f"Upgrading db version on disk '{pragma_user_version}' to '{int(pragma_user_version)+1}'...")
            self.db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_country_origins_list TO imdb_country_list")
            self.db_sqlite_connection.execute("ALTER TABLE history RENAME COLUMN imdb_spoken_languages_list TO imdb_language_list")
            self.set_db_version(3)

        # if v3 then upgrade to v4 by adding in the missing column
        if pragma_user_version == 3:
            self.logger_instance.debug(f"Upgrading db version on disk '{pragma_user_version}' to '{int(pragma_user_version)+1}'...")
            self.db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN imdb_trailer_url text")
            self.set_db_version(4)

        # if v4 then upgrade to v5 by adding in the missing column
        if pragma_user_version == 4:
            self.logger_instance.debug(f"Upgrading db version on disk '{pragma_user_version}' to '{int(pragma_user_version)+1}'...")
            self.db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN torrent_tag text")
            self.set_db_version(5)

        # if v5 then upgrade to v6 by adding in the missing column
        if pragma_user_version == 5:
            self.logger_instance.debug(f"Upgrading db version on disk '{pragma_user_version}' to '{int(pragma_user_version)+1}'...")
            self.db_sqlite_connection.execute("ALTER TABLE history ADD COLUMN verified text")
            self.set_db_version(6)

    def set_db_version(self, version):

        # set database version to track when db upgrades/downgrades are required, v:d validates that db_version is an integer
        self.db_sqlite_connection.execute("PRAGMA user_version = {v:d}".format(v=version))

    def get_pragma_user_version(self):
        """
        Get the user version of the database.
        :return: The integer value of the user version.
        """
        try:
            # Execute the PRAGMA query to get the user version
            pragma_user_version_gen = self.db_sqlite_connection.query("PRAGMA user_version")

            # Extract the user_version from the generator
            for row in pragma_user_version_gen:
                return row.get('user_version', False)  # Default to False if 'user_version' is not found

            # If no rows are returned, default to False
            return False
        except Exception as e:
            # Log the error and return False as a fallback
            self.logger_instance.error(f"Failed to get PRAGMA user_version: {e}")
            return False

    def vacuum_database(self):

        # compress db
        self.db_sqlite_connection.vacuum()

    def close_database(self):

        # close database
        self.db_sqlite_connection.close()

    def delete_database(self):

        pass
