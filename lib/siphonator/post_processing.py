import os
import re
import lib.siphonator.torrent_clients as torrent_clients
import lib.siphonator.db_sqlite as db_sqlite
import lib.siphonator.tools_various as tools_various


def helper_get_src_parent_path(torrent_completed_dict):

    # get list of files in torrent
    torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')

    # sort the list of dictionaries by 'file_size' in descending order (largest first)
    sorted_file_size_dict_list = sorted(torrent_file_dict_list, key=lambda x: x['file_size'], reverse=True)

    # get first dictionary from the list, as this is the largest file size
    sorted_file_size_dict = sorted_file_size_dict_list[0]

    # get torrent file path
    torrent_rel_file_path = sorted_file_size_dict.get('file_name')

    # get directory from file path
    torrent_path = os.path.dirname(torrent_rel_file_path)

    # get first level directory name from source path
    torrent_parent_path = tools_various.get_first_level_directory(torrent_path)

    # if there is no first level directory (saved to root of save path) then nothing to delete
    if not torrent_parent_path:
        return False

    return torrent_parent_path


class PostProcess(object):

    def __init__(self, logger_instance, config_dict, init_dict, qbt_client):

        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict, qbt_client)
        self.db_sqlite_instance = db_sqlite.DbSqlite(self.logger_instance, init_dict)
        self.qbt_client = qbt_client

    def helper_get_imdb_title_year(self, torrent_completed_dict):

        # send torrent_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return here
        read_database_simple_bool, query_result = self.db_sqlite_instance.read_database_simple('history', 'torrent_tag', torrent_completed_dict.get('torrent_tag'))

        # get imdb title ad year, used for rename
        if not query_result:
            return False

        imdb_title = query_result.get('imdb_title')
        imdb_year = query_result.get('imdb_year')
        imdb_title_year = f"{imdb_title} ({imdb_year})"

        return imdb_title_year

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

            # loop over list of files and generate move files list and delete files list
            src_move_files_list, src_delete_files_list = self.create_move_delete_lists(torrent_completed_dict)

            # move filtered list of files to imdb title year named destination folder in library
            if not self.move_files_dst(torrent_completed_dict, src_move_files_list):
                continue

            # delete completed files in the delete files list
            if not self.delete_files_src(src_delete_files_list):
                continue

            # delete completed parent folder and subfolders
            if not self.delete_dir_src(torrent_completed_dict):
                continue

            # remove stopped queued items from qbittorrent
            if not self.delete_torrents_stopped(torrent_completed_dict):
                continue

    def create_move_delete_lists(self, torrent_completed_dict):

        torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')
        torrent_save_path = torrent_completed_dict.get('torrent_save_path')

        delete_unwanted_regex_list = self.config_dict['post_process']['delete_unwanted_regex_list']
        delete_unwanted_min_kb = self.config_dict['post_process']['delete_unwanted_min_kb']

        src_move_files_list = []
        src_delete_files_list = []

        # iterate over list containing dictionary of files in the torrent
        for torrent_file_dict in torrent_file_dict_list:

            torrent_file_name = torrent_file_dict.get('file_name')
            torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

            if delete_unwanted_regex_list:

                for delete_unwanted_regex in delete_unwanted_regex_list:

                    # perform regex search against filename, if match found then append to delete list
                    regex = re.compile(delete_unwanted_regex)
                    delete_unwanted_regex_match = regex.search(torrent_file_name)

                    # check if filename matches regex to delete
                    if delete_unwanted_regex_match:

                        src_delete_files_list.append(torrent_file_path)
                        self.logger_instance.info(f"Filename '{torrent_file_name}' matches regex '{delete_unwanted_regex}' for deletion defined in config file, added to delete list '{src_delete_files_list}'")
                        continue

            if delete_unwanted_min_kb:

                torrent_file_size = torrent_file_dict.get('file_size')

                # use bitwise operation to convert from bytes to kilobytes
                torrent_file_size_kb = torrent_file_size >> 10

                # if torrent file_size is less than minimum size defined in config then delete
                if int(torrent_file_size_kb) < int(delete_unwanted_min_kb):

                    src_delete_files_list.append(torrent_file_path)
                    self.logger_instance.info(f"File size {torrent_file_size_kb}KB for torrent completed filepath '{torrent_file_path}' is less than minimum file size {delete_unwanted_min_kb}KB defined in config file, added to delete list '{src_delete_files_list}'")
                    continue

            src_move_files_list.append(torrent_file_path)
            self.logger_instance.info(f"Filename '{torrent_file_path}' is to be moved to the library, added to move list '{src_move_files_list}'")

        return src_move_files_list, src_delete_files_list

    def move_files_dst(self, torrent_completed_dict, src_move_files_list):

        if not self.config_dict['post_process']['move_completed']:
            return False

        move_library_path = self.config_dict['post_process']['move_library_path']
        if not move_library_path:
            return False

        # get imdb title and year - used to construct destination path
        imdb_title_year = self.helper_get_imdb_title_year(torrent_completed_dict)

        # if query result from sqlite for imdb title and year is false then return
        if not imdb_title_year:
            return False

        # construct absolute path to destination
        dst_move_path = os.path.join(move_library_path, imdb_title_year)

        # loop over list of files to move
        for src_move_file_path in src_move_files_list:

            # get file name from src file path
            src_move_file = os.path.basename(src_move_file_path)

            # check source file exists
            if not os.path.isfile(src_move_file_path):
                self.logger_instance.warning(f"Source file path '{src_move_file_path}' does not exist, file may of been moved in previous run")
                continue

            dst_move_file_path = os.path.join(dst_move_path, src_move_file)
            self.logger_instance.info(f"Moving source file path '{src_move_file_path}' to destination file path '{dst_move_file_path}'")
            if not tools_various.move_files(self.logger_instance, src_move_file_path, dst_move_file_path):
                return False

        return True

    def delete_files_src(self, src_delete_files_list):

        if not self.config_dict['post_process']['delete_unwanted_files']:
            return False

        for src_delete_file in src_delete_files_list:

            self.logger_instance.info(f"Deleting source file path '{src_delete_file}', file is in unwanted list")
            tools_various.delete_files(self.logger_instance, src_delete_file)

        return True

    def delete_dir_src(self, torrent_completed_dict):

        if not self.config_dict['post_process']['delete_unwanted_files']:
            return False

        # get qbittorrent root save path
        torrent_save_path = torrent_completed_dict.get('torrent_save_path')

        # get source parent path
        torrent_parent_path = helper_get_src_parent_path(torrent_completed_dict)

        # if the torrent parent path does not exist then we have nothing to delete
        if not torrent_parent_path:
            return True

        # construct parent path using root save path and first level directory name
        torrent_abs_parent_path = os.path.join(str(torrent_save_path), str(torrent_parent_path))

        # delete recursively with safety
        tools_various.remove_directory_with_safety_check(self.logger_instance, torrent_abs_parent_path)
        return True

    def delete_torrents_stopped(self, torrent_completed_dict):

        if not self.config_dict['post_process']['remove_completed']:
            return False

        torrent_hash = torrent_completed_dict.get('torrent_hash')

        # remove torrent from qbittorrent queue with status stopped, as the files have been moved and it will error otherwise
        self.torrent_clients_instance.qbittorrent_delete_torrent(torrent_hash, False, 'stopped')
        return True
