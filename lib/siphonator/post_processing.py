import os
import pathlib
import re
import lib.siphonator.torrent_clients as torrent_clients
import lib.siphonator.db_sqlite as db_sqlite
import lib.siphonator.tools_various as tools_various


def helper_get_largest_file_path(torrent_completed_dict):

    # get list of files in torrent
    torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')

    # sort the list of dictionaries by 'file_size' in descending order (largest first)
    sorted_file_size_dict_list = sorted(torrent_file_dict_list, key=lambda x: x['file_size'], reverse=True)

    # get first dictionary from the list, as this is the largest file size
    sorted_file_size_dict = sorted_file_size_dict_list[0]

    # get torrent file path
    torrent_rel_file_path = sorted_file_size_dict.get('file_name')

    # get filename from file path
    torrent_file_name = os.path.basename(torrent_rel_file_path)

    # get directory from file path
    torrent_path = os.path.dirname(torrent_rel_file_path)

    return torrent_file_name, torrent_path


def helper_get_largest_parent_dir(logger_instance, torrent_file_name, torrent_path):

    # get first level directory name from source path
    torrent_parent_dir = tools_various.get_first_level_directory(torrent_path)

    # if there is no first level directory (saved to root of save path) then we cannot use the dir name
    if not torrent_parent_dir:
        logger_instance.debug(f"Torrent file path '{torrent_path}' does not contain parent directory")
        return False

    # if the file extension is not a video container then we cannot safely use the dir name for te file name
    if not torrent_file_name.lower().endswith(('.mkv', '.mp4', '.avi')):
        logger_instance.debug(f"Torrent file name '{torrent_file_name}' is not a video container")
        return False

    # get length of parent path and filename for comparison
    char_length_parent_path = len(torrent_parent_dir)
    char_length_torrent_file_name = len(torrent_file_name)

    # if length of parent directory is less than torrent filename then do not use the dir name for the file name
    if int(char_length_parent_path) < int(char_length_torrent_file_name):
        logger_instance.debug(f"Torrent file name '{torrent_file_name}' char length '{char_length_torrent_file_name}' is greater than torrent parent directory '{torrent_parent_dir}' char length '{char_length_parent_path}'")
        return False

    # get extension from filename, as we need this to construct the new file name
    torrent_file_extension = pathlib.Path(torrent_file_name).suffix

    return torrent_parent_dir, torrent_file_extension


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

            # loop over list of files and generate copy files list and delete files list
            src_copy_files_list, src_delete_files_list = self.create_copy_exclude_lists(torrent_completed_dict)

            # copy filtered list of files to imdb title year named destination folder in library
            if not self.copy_files_dst(torrent_completed_dict, src_copy_files_list):
                continue

            # remove stopped queued items from qbittorrent and data
            if not self.delete_torrent_and_data(torrent_completed_dict):
                continue

    def create_copy_exclude_lists(self, torrent_completed_dict):

        torrent_file_dict_list = torrent_completed_dict.get('torrent_file_list')
        torrent_save_path = torrent_completed_dict.get('torrent_save_path')

        exclude_file_regex_list = self.config_dict['post_process']['exclude_file_regex_list']
        exclude_file_min_kb = self.config_dict['post_process']['exclude_file_min_kb']

        src_copy_files_list = []
        src_exclude_files_list = []

        # iterate over list containing dictionary of files in the torrent
        for torrent_file_dict in torrent_file_dict_list:

            torrent_file_name = torrent_file_dict.get('file_name')
            torrent_file_path = os.path.join(torrent_save_path, torrent_file_name)

            if exclude_file_regex_list:

                for delete_unwanted_regex in exclude_file_regex_list:

                    # perform regex search against filename, if match found then append to delete list
                    regex = re.compile(delete_unwanted_regex)
                    delete_unwanted_regex_match = regex.search(torrent_file_name)

                    # check if filename matches regex to delete
                    if delete_unwanted_regex_match:

                        src_exclude_files_list.append(torrent_file_path)
                        self.logger_instance.info(f"Filename '{torrent_file_name}' matches regex '{delete_unwanted_regex}' defined in config file, added to exclude list '{src_exclude_files_list}'")
                        continue

            if exclude_file_min_kb:

                torrent_file_size = torrent_file_dict.get('file_size')

                # use bitwise operation to convert from bytes to kilobytes
                torrent_file_size_kb = torrent_file_size >> 10

                # if torrent file_size is less than minimum size defined in config then delete
                if int(torrent_file_size_kb) < int(exclude_file_min_kb):

                    src_exclude_files_list.append(torrent_file_path)
                    self.logger_instance.info(f"File size {torrent_file_size_kb}KB for torrent completed filepath '{torrent_file_path}' is less than minimum file size {exclude_file_min_kb}KB defined in config file, added to exclude list '{src_exclude_files_list}'")
                    continue

            src_copy_files_list.append(torrent_file_path)
            self.logger_instance.info(f"Filename '{torrent_file_path}' is to be copy to the library, added to copy list '{src_copy_files_list}'")

        return src_copy_files_list, src_exclude_files_list

    def copy_files_dst(self, torrent_completed_dict, src_copy_files_list):

        if not self.config_dict['post_process']['copy_completed']:
            return False

        copy_library_path = self.config_dict['post_process']['copy_library_path']
        if not copy_library_path:
            return False

        # get imdb title and year - used to construct destination path
        imdb_title_year = self.helper_get_imdb_title_year(torrent_completed_dict)

        # if query result from sqlite for imdb title and year is false then return
        if not imdb_title_year:
            return False

        # get the largest torrent file name and path
        torrent_largest_file_name, torrent_path = helper_get_largest_file_path(torrent_completed_dict)

        # construct absolute path to destination
        dst_copy_path = os.path.join(copy_library_path, imdb_title_year)

        # loop over list of files to copy
        for src_copy_file_path in src_copy_files_list:

            # check source file exists
            if not os.path.isfile(src_copy_file_path):
                self.logger_instance.warning(f"Source file path '{src_copy_file_path}' does not exist, file may of been copy in previous run")
                continue

            # get file name from src file path
            src_copy_file = os.path.basename(src_copy_file_path)

            # if source file path does not match the largest file path then use existing file name
            if src_copy_file != torrent_largest_file_name:
                dst_copy_file_path = os.path.join(dst_copy_path, src_copy_file)

            else:

                # if parent dir does not exist, length of parent dir is shorter than filename, or file type is not container (returns False for all) then use existing file name
                if not helper_get_largest_parent_dir(self.logger_instance, torrent_largest_file_name, torrent_path):
                    dst_copy_file_path = os.path.join(dst_copy_path, src_copy_file)

                else:

                    # get the largest parent path name
                    torrent_largest_parent_dir, torrent_file_extension = helper_get_largest_parent_dir(self.logger_instance, torrent_largest_file_name, torrent_path)

                    # construct full file path with new parent path name as the file name
                    dst_copy_file_path = os.path.join(dst_copy_path, f"{torrent_largest_parent_dir}{torrent_file_extension}")

            self.logger_instance.info(f"Moving source file path '{src_copy_file_path}' to destination file path '{dst_copy_file_path}'")
            if not tools_various.copy_files(self.logger_instance, src_copy_file_path, dst_copy_file_path):
                return False

        return True

    def delete_torrent_and_data(self, torrent_completed_dict):

        if not self.config_dict['post_process']['remove_completed']:
            return False

        torrent_hash = torrent_completed_dict.get('torrent_hash')

        # remove torrent from qbittorrent queue with status stopped, as the files have been moved and it will error otherwise
        if not self.torrent_clients_instance.qbittorrent_delete_torrent(torrent_hash, True, 'stopped'):
            return False

        return True
