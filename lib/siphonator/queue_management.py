import lib.siphonator.torrent_clients as torrent_clients


class QueueManagement(object):

    def __init__(self, logger_instance, config_dict, init_dict):
        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.init_dict = init_dict
        # note we specify 'init_dict=' here as we want to skip optional argument 'result_dict' but specify optional argument 'init_dict'
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict, init_dict=self.init_dict)

    def prerun_checks(self):

        # if ul/dl speed is 0 then assume internet down, this is to prevent torrents being incorrectly marked as stalled
        if not self.torrent_clients_instance.qbittorrent_check_global_speed():
            return False

        # if internet previous down datetime + grace period is greater than current datetime then skip queue management
        if not self.torrent_clients_instance.qbittorrent_internet_connection_down_grace():
            return False

        # check if qbittorrent is low on disk space, if so then skip queue management as torrents could be in an error
        # or recovering from error state (stalled) and thus incorrectly marked as stalled and deleted
        if not self.torrent_clients_instance.qbittorrent_check_free_space():
            return False

        return True

    def queue_management(self):

        if not self.config_dict['queue_management']['queue_management_enabled']:
            return False

        if not self.prerun_checks():
            return False

        # check and delete any matching torrents in a metadata download stalled state
        self.delete_stalled_torrents('metadata', 'metaDL', 'added_on')

        # check and delete any matching torrents in a data download stalled state
        self.delete_stalled_torrents('stalled', 'stalledDL', 'last_activity')

    def qbittorrent_list_torrents(self):

        # get list of torrents added by siphonator (category set)
        qbittorrent_identify_torrents_with_category_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_with_category()

        # if returned dict is empty then we cannot identify any torrents with category set
        if not qbittorrent_identify_torrents_with_category_dict:
            return False

        return qbittorrent_identify_torrents_with_category_dict

    def delete_stalled_torrents(self, delete_state, state, filter_type):

        if not self.config_dict['queue_management'][f"{delete_state}_monitor_enabled"]:
            return False

        qbittorrent_list_torrents = self.qbittorrent_list_torrents()

        if not qbittorrent_list_torrents:
            return False

        # get config values for metadata and stalled torrent max mins delay before deletion
        delay_max_mins = self.config_dict['queue_management'][f"{delete_state}_delete_torrent_max_mins"]

        # check if torrents are in stalled state, if so include in dict
        qbittorrent_identify_torrents_for_deletion_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_for_deletion(qbittorrent_list_torrents, state, delay_max_mins, filter_type)

        # if returned dict is empty then we cannot identify any torrents for deletion
        if not qbittorrent_identify_torrents_for_deletion_dict:
            return False

        # if torrent is in stalled state then delete torrent (check config to decide whether we delete data as well)
        self.torrent_clients_instance.qbittorrent_delete_stalled_torrents(qbittorrent_identify_torrents_for_deletion_dict, state)
