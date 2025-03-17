import os
import shutil
import lib.siphonator.torrent_clients as torrent_clients
import lib.siphonator.db_sqlite as db_sqlite


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
            self.remove_completed_torrents(torrent_completed_dict)

            # get the list of files for the torrent
            self.delete_unwanted_files(torrent_completed_dict)

            # rename completed files
            self.rename_completed_files(torrent_completed_dict)

    def remove_completed_torrents(self, torrent_completed_dict):

        if not self.config_dict['post_process']['remove_completed']:
            return False

        torrent_hash = torrent_completed_dict.get('torrent_hash')

        # remove torrent from completed, this is required otherwise errors will show up as missing files once moved
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

            try:
                os.remove(path)
                self.logger_instance.info(f"Successfully deleted file '{path}'")
            except FileNotFoundError as e:
                self.logger_instance.warning(f"The file '{path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
            except PermissionError as e:
                self.logger_instance.warning(f"Permission denied while trying to delete '{path}', error is '{e}'")
            except IsADirectoryError as e:
                self.logger_instance.warning(f"'{path}' is a directory, not a file, error is '{e}'")
            except OSError as e:
                self.logger_instance.warning(f"General OS error, error is '{e}'")

        # iterate over list containing dictionary of files in the torrent
        for torrent_file_dict in torrent_file_dict_list:

            torrent_file_name = torrent_file_dict.get('file_name')
            torrent_completed_dict.get('torrent_file_list')

            torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

            # get torrent file extension, [1:] removes period
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

        if not self.config_dict['post_process']['rename_completed']:
            return False

        # send torrent_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return here
        read_database_simple_bool, query_result = self.db_sqlite_instance.read_database_simple('history', 'torrent_tag', torrent_completed_dict.get('torrent_tag'))

        # get imdb title ad year, used for rename
        if query_result:

            imdb_title = query_result.get('imdb_title')
            imdb_year = query_result.get('imdb_year')
            imdb_title_year = f"{imdb_title} ({imdb_year})"

        # TODO WIP
        # get parent folder for largest file in the torrent

        # if parent folder is /data/completed then create imdb folder and move all files for torrent into folder (some may fail as they have been deleted).

        # create folder imdb_title_year if the torrent main video file is not in a folder and movie it there

        # if folder does exist and main video file is in there then rename it to imdb_title_year

        # call move function, passing in paths
        # TODO WIP
        #self.move_completed_directory(torrent_completed_dict)

    def move_completed_directory(self, absolute_completed_path, movie_directory):

        if not self.config_dict['post_process']['move_completed']:
            return False

        move_dest_path = self.config_dict['post_process']['move_dest_path']
        if not move_dest_path:
            return False

        # check move destination path exists
        if not os.path.isdir(move_dest_path):

            self.logger_instance.warning(f"Destination path '{move_dest_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container")

        absolute_dst_path = os.path.join(move_dest_path, movie_directory)

        try:
            shutil.move(absolute_completed_path, str(absolute_dst_path))
            self.logger_instance.info(f"Successfully moved source path '{absolute_completed_path}' to destination path '{absolute_dst_path}'")
        except FileNotFoundError as e:
            self.logger_instance.warning(f"The source directory '{absolute_completed_path}' does not exist if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        except PermissionError as e:
            self.logger_instance.warning(f"Permission denied while moving '{absolute_completed_path}' to '{absolute_dst_path}', error is '{e}'")
        except shutil.Error as e:
            self.logger_instance.warning(f"General error, error is '{e}'")
        except OSError as e:
            self.logger_instance.warning(f"OS error, error is '{e}'")
