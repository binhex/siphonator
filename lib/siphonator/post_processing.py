import lib.siphonator.torrent_clients as torrent_clients


class PostProcessMoveCompleted(object):

    def __init__(self,logger_instance, result_dict, config_dict):

        self.logger_instance = logger_instance
        self.result_dict = result_dict
        self.config_dict = config_dict
        self.index_title_no_year = result_dict.get('index_title_no_year', None)
        self.index_year_regex = result_dict.get('index_year_regex', None)
        self.logger_instance = logger_instance

    # TODO this calls the other functions below in this class
    def post_process_move_completed(self):
        pass

    # TODO take output of function get_file_list and perform db query, looking for column result value = 'Passed'
    def compare_files_to_db_success(self ):
        pass

    # TODO read in completed folder path from qbittorrent
    def get_completed_folder_from_bittorrent_client(self):
        pass

    # TODO get all files located in root of completed, including only video files, also exclude tv series regex patterns, exclude samples
    def get_file_list(self):
        pass

    # TODO get a list of all top level root folders (non recursive) in completed
    def get_folder_list(self):
        pass

    # TODO create folders for all files that do not have folders in the root
    def create_folder(self):
        pass

    # TODO rename any existing root folders to match imdb title
    def rename_folder(self):
        pass

    # TODO delete any non movie related files and folders - note need to identify dvd/bd/uhd raw dumps and not del
    def delete_files(self):
        pass

    # TODO move processed folders and files to storage - need to add path to config.yml
    def move_folder(self):
        pass


class PostProcessMonitorQueue(object):

    def __init__(self, logger_instance, result_dict, config_dict):
        self.logger_instance = logger_instance
        self.result_dict = result_dict
        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.torrent_clients_instance = torrent_clients.TorrentClients(logger_instance, result_dict, config_dict)

    # feature - check qbittorrent status, if incoming port working (internet connection ok) and if torrent not stopped then look at whether stalled, if stalled for X minutes (defined in config) then delete (torrent or torrent + data, defined in config)
    def post_process_monitor_queue(self):

        # check global ul and dl speeds
        qbittorrent_check_global_speed = self.torrent_clients_instance.qbittorrent_check_global_speed()

        # if speed is 0 then return False and exit this function
        if not qbittorrent_check_global_speed:
            return False

        # # get list of torrents added by siphonator (tagged)
        # self.torrent_clients_instance.qbittorrent_identify_torrents_tagged()
        #
        # # check if torrent is in stalled state
        # self.torrent_clients_instance.qbittorrent_identify_stalled()
        #
        # # check if torrent is downloading slow (check config for definition of slow, less than 100 KB?)
        # self.torrent_clients_instance.qbittorrent_identify_slow()
        #
        # # if torrent is in stalled state then delete torrent (check config to decide whether we delete data as well)
        # self.torrent_clients_instance.qbittorrent_delete_torrent()
