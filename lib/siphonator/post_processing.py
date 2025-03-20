import os
import pathlib
import lib.siphonator.torrent_clients as torrent_clients
import lib.siphonator.db_sqlite as db_sqlite
import lib.siphonator.tools_various as tools_various


class PostProcess(object):

    def __init__(self, logger_instance, config_dict, init_dict, qbt_client):

        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict, qbt_client)
        self.db_sqlite_instance = db_sqlite.DbSqlite(self.logger_instance, init_dict)
        self.qbt_client = qbt_client

    def post_process(self):

        if not self.config_dict['post_process']['post_process_enabled']:
            return False

        # returns dict of all torrents in completed state with torrent_name, torrent_hash, torrent_tag and torrent_file_list
        torrent_completed_dict_list = self.torrent_clients_instance.qbittorrent_identify_completed_torrents()

        # if dict is empty due to not reaching ratio or bad qbt client then return
        if not torrent_completed_dict_list:
            return False

        # iterate over completed torrents dict
        for torrent_completed_dict in torrent_completed_dict_list:

            # do not uncomment this until we are sure its working!
            #self.remove_completed_torrents(torrent_completed_dict)

            # remove unwanted files based on extension or file size
            self.delete_unwanted_files(torrent_completed_dict)

            # rename completed folders and files
            absolute_completed_path, imdb_title_year = self.rename_completed_files(torrent_completed_dict)

            # move from completed to library
            self.move_to_library(absolute_completed_path, imdb_title_year)

    def remove_completed_torrents(self, torrent_completed_dict):

        if not self.config_dict['post_process']['remove_completed']:
            return False

        torrent_hash = torrent_completed_dict.get('torrent_hash')

        # remove torrent from completed, this is required before performing rename/move operations, otherwise the torrent will be a missing files state (error)
        self.torrent_clients_instance.qbittorrent_delete_torrent(torrent_hash, False, 'completed')

    def delete_unwanted_files(self, torrent_completed_dict):

        if not self.config_dict['post_process']['delete_unwanted_files']:
            return False

        torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')
        torrent_save_path = torrent_completed_dict.get('torrent_save_path')

        delete_unwanted_ext_list = self.config_dict['post_process']['delete_unwanted_ext_list']
        delete_unwanted_min_kb = self.config_dict['post_process']['delete_unwanted_min_kb']

        def delete_file(path):

            if not os.path.isfile(path):

                self.logger_instance.info(f"Failed to delete file from path '{path}' as the file does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for the 'Default save path' match qBittorrent")

            tools_various.delete_files(self.logger_instance, path)

        # iterate over list containing dictionary of files in the torrent
        for torrent_file_dict in torrent_file_dict_list:

            torrent_file_name = torrent_file_dict.get('file_name')
            torrent_completed_dict.get('torrent_file_list')

            torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

            # get torrent file extension, [1] gets second part of split filename (extension), and [1:] removes period
            torrent_file_ext = os.path.splitext(torrent_file_path)[1][1:]

            if delete_unwanted_ext_list:

                for delete_unwanted_ext in delete_unwanted_ext_list:

                    # check config delete extension matches file extension in torrent file path
                    if delete_unwanted_ext == torrent_file_ext:

                        self.logger_instance.info(f"file extension '{torrent_file_ext}' for torrent completed filepath '{torrent_file_path}' matches delete file extension '{delete_unwanted_ext}' from config, deleting file...")
                        delete_file(torrent_file_path)

            if delete_unwanted_min_kb:

                torrent_file_size = torrent_file_dict.get('file_size')

                # use bitwise operation to convert from bytes to kilobytes
                torrent_file_size_kb = torrent_file_size >> 10

                # if torrent file_size is less than minimum size defined in config then delete
                if int(torrent_file_size_kb) < int(delete_unwanted_min_kb):

                    self.logger_instance.info(f"file size {torrent_file_size_kb}KB for torrent completed filepath '{torrent_file_path}' is less than minimum file size {delete_unwanted_min_kb}KB defined in config file, deleting file...")
                    delete_file(torrent_file_path)

    def rename_completed_files(self, torrent_completed_dict):

        # send torrent_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return here
        read_database_simple_bool, query_result = self.db_sqlite_instance.read_database_simple('history', 'torrent_tag', torrent_completed_dict.get('torrent_tag'))

        # get imdb title ad year, used for rename
        if not query_result:
            return False

        imdb_title = query_result.get('imdb_title')
        imdb_year = query_result.get('imdb_year')
        imdb_title_year = f"{imdb_title} ({imdb_year})"

        # get list of files in torrent
        torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')

        # sort the list of dictionaries by 'file_size' in descending order (largest first)
        sorted_file_size_dict_list = sorted(torrent_file_dict_list, key=lambda x: x['file_size'], reverse=True)

        # get first dictionary from the list, as this is the largest file size
        sorted_file_size_dict = sorted_file_size_dict_list[0]

        # get torrent file path
        torrent_rel_file_path = sorted_file_size_dict.get('file_name')

        # get qbittorrent root save path
        root_save_path = torrent_completed_dict.get('torrent_save_path')

        # construct path to completed imdb path and file path
        torrent_abs_file_path = os.path.join(root_save_path, torrent_rel_file_path)

        if not self.config_dict['post_process']['rename_completed']:

            return torrent_abs_file_path, imdb_title_year

        # get torrent file extension, [1:] removes period
        torrent_file_ext = os.path.splitext(torrent_rel_file_path)[1][1:]

        # get filename from file path
        torrent_file_name = os.path.basename(torrent_rel_file_path)

        # get directory from file path
        torrent_path = os.path.dirname(torrent_rel_file_path)

        # construct absolute path to imdb folder name in completed, used to create path to move the largest file to movie file or rename first level directory
        imdb_abs_path = os.path.join(root_save_path, imdb_title_year)
        imdb_abs_file_path = os.path.join(imdb_abs_path, torrent_file_name)

        if not torrent_path:

            # create dir from root save path with name of imdb title and year
            pathlib.Path(imdb_abs_path).mkdir(parents=True, exist_ok=True)

            # move file in root of saved path to imdb named directory
            tools_various.move_files_folders(self.logger_instance, torrent_abs_file_path, imdb_abs_file_path, 'file')

        else:

            # get first level directory name
            torrent_first_path = tools_various.get_first_level_directory(torrent_path)

            # construct new file name based on directory name
            torrent_first_dir_file_name = f"{torrent_first_path}.{torrent_file_ext}"

            # sometimes the filename can be missing information present in the directory name, thus we check and rename the file
            if torrent_file_name != torrent_first_dir_file_name:

                # construct new file path based on directory name
                torrent_abs_path = os.path.join(root_save_path, str(torrent_path))
                torrent_abs_first_dir_file_name = os.path.join(torrent_abs_path, torrent_first_dir_file_name)

                # if the directory name does not match the file name then rename the file to match
                tools_various.rename_files_folders(self.logger_instance, torrent_abs_file_path, torrent_abs_first_dir_file_name)

            # construct partial path to torrent file, using root save path and first level directory name
            torrent_abs_parent_dir_path = os.path.join(root_save_path, torrent_first_path)

            # rename first level folder to imdb name
            tools_various.rename_files_folders(self.logger_instance, torrent_abs_parent_dir_path, imdb_abs_path)

        # return to be used in move_to_library function
        return imdb_abs_path, imdb_title_year

    def move_to_library(self, src_path, imdb_title_year):

        if not self.config_dict['post_process']['move_completed']:
            return False

        move_library_path = self.config_dict['post_process']['move_library_path']
        if not move_library_path:
            return False

        # check destination library path exists
        if not os.path.isdir(move_library_path):

            self.logger_instance.warning(f"Destination library path '{move_library_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container")

        # check source directory exists
        if not os.path.isdir(src_path):

            self.logger_instance.warning(f"Source path '{src_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container")

        absolute_dst_path = os.path.join(move_library_path, imdb_title_year)

        # move completed folders to library
        tools_various.move_files_folders(self.logger_instance, src_path, str(absolute_dst_path), 'dir')
