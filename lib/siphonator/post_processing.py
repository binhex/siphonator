import os
import lib.siphonator.torrent_clients as torrent_clients
import lib.siphonator.db_sqlite as db_sqlite


class PostProcess(object):

    def __init__(self, logger_instance, config_dict, init_dict):

        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict)
        self.db_sqlite_instance = db_sqlite.DbSqlite(self.logger_instance, init_dict)

    def post_process(self):

        if not self.config_dict['post_process']['post_process_enabled']:
            return False

        # returns dict of all torrents in completed state with torrent_name, torrent_tag and torrent_file_list
        torrent_completed_dict_list = self.torrent_clients_instance.qbittorrent_identify_completed_torrents()

        # iterate over completed torrents dict
        for torrent_completed_dict in torrent_completed_dict_list:

            # do not uncomment this until we are sure its working!
            # self.remove_completed_torrents(torrent_completed_dict)

            # get the list of files for the torrent
            self.delete_unwanted_files(torrent_completed_dict)

            # rename completed files
            self.rename_completed_files(torrent_completed_dict)

            # move completed files
            self.move_completed_files(torrent_completed_dict)

    def remove_completed_torrents(self, torrent_completed_dict):

        if not self.config_dict['post_process']['remove_completed']:
            return False

        # remove torrent from completed, this is required otherwise errors will show up as missing files once moved
        self.torrent_clients_instance.qbittorrent_delete_torrent(torrent_completed_dict.get('torrent_tag'), False, 'completed')

    def delete_unwanted_files(self, torrent_completed_dict):

        if not self.config_dict['post_process']['delete_unwanted_files']:
            return False

        torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')
        torrent_save_path = torrent_completed_dict.get('torrent_save_path')

        delete_files_less_than_kb = self.config_dict['post_process']['delete_files_less_than_kb']
        delete_file_ext_list = self.config_dict['post_process']['delete_file_ext_list']

        def delete_file(path):

            if os.path.isfile(path):
                try:
                    os.remove(path)
                    self.logger_instance.info(f"Successfully deleted file '{path}'")
                except OSError as e:

                    self.logger_instance.info(f"Failed to delete file from path '{path}', error is '{e.strerror}'")
            else:
                self.logger_instance.info(f"Failed to delete file from path '{path}' as the file does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for the 'Default save path' match qBittorrent")

        # iterate over list containing dictionary of files in the torrent
        for torrent_file_dict in torrent_file_dict_list:

            torrent_file_name = torrent_file_dict.get('file_name')
            torrent_completed_dict.get('torrent_file_list')

            torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

            # get torrent file extension, [1:] removes period
            torrent_file_ext = os.path.splitext(torrent_file_path)[1][1:]

            if delete_file_ext_list:

                for delete_file_ext in delete_file_ext_list:

                    # check config delete extension matches file extension in torrent file path
                    if delete_file_ext == torrent_file_ext:

                        delete_file(torrent_file_path)

            if delete_files_less_than_kb:

                torrent_file_size = torrent_file_dict.get('file_size')

                # use bitwise operation to convert from bytes to kilobytes
                torrent_file_size_kb = torrent_file_size >> 10

                # if torrent file_size is less than minimum size defined in config then delete
                if int(torrent_file_size_kb) < int(delete_files_less_than_kb):

                    self.logger_instance.info(f"file size {torrent_file_size_kb}KB for filepath '{torrent_file_path}' is less than minimum file size {delete_files_less_than_kb}KB defined in config file, deleting file...")

                    delete_file(torrent_file_path)

    def rename_completed_files(self, torrent_completed_dict):

        if not self.config_dict['post_process']['rename_completed']:
            return False

        # send torrent_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return here
        read_database_simple_bool, query_result = self.db_sqlite_instance.read_database_simple('history', 'torrent_tag', torrent_completed_dict.get('torrent_tag'))

        # get imdb title ad year, used for rename
        if query_result:

            imdb_title = query_result.get('imdb_title')
            imdb_year = query_result.get('imdb_year')
            imdb_title_year = f"{imdb_title} ({imdb_year})"

        # get filepath for main video file from torrent details

        # create folder imdb_title_year if the torrent main video file is not in a folder and movie it there

        # if folder does exist and main video file is in there then rename it to imdb_title_year

    def move_completed_files(self, torrent_completed_dict):

        if not self.config_dict['post_process']['move_completed']:
            return False

        # move folder from completed to path defined in config
