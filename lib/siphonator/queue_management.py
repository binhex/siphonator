import lib.siphonator.torrent_clients as torrent_clients


class QueueManagement(object):

    def __init__(self, logger_instance, config_dict):
        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict)

    def queue_management(self):

        if not self.config_dict['queue_management']['queue_management_enabled']:
            return False

        self.delete_metadata_torrents()
        self.delete_stalled_torrents()

    def prerun_checks(self):

        # if ul/dl speed is 0 then assume internet down, this is to prevent torrents being incorrectly marked as stalled
        if not self.torrent_clients_instance.qbittorrent_check_global_speed():
            return False

        # get list of torrents added by siphonator (category set)
        qbittorrent_identify_torrents_with_category_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_with_category()

        # if returned dict is empty then we cannot identify any torrents with category set
        if not qbittorrent_identify_torrents_with_category_dict:
            return False

        return qbittorrent_identify_torrents_with_category_dict

    def delete_metadata_torrents(self):

        delay_max_mins = self.config_dict['queue_management']['metadata_delete_torrent_max_mins']

        if not self.config_dict['queue_management']['metadata_monitor_enabled']:
            return False

        qbittorrent_identify_torrents_with_category_dict = self.prerun_checks()

        if not qbittorrent_identify_torrents_with_category_dict:
            return False

        # check if torrents are in metadl state, if so include in dict
        qbittorrent_identify_torrents_for_deletion_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_for_deletion(qbittorrent_identify_torrents_with_category_dict, 'metaDL', delay_max_mins, 'added_on')

        # if returned dict is empty then we cannot identify any torrents for deletion
        if not qbittorrent_identify_torrents_for_deletion_dict:
            return False

        # if torrent is in stalled state then delete torrent (check config to decide whether we delete data as well)
        self.torrent_clients_instance.qbittorrent_delete_stalled_torrents(qbittorrent_identify_torrents_for_deletion_dict)

    def delete_stalled_torrents(self):

        delay_max_mins = self.config_dict['queue_management']['stalled_delete_torrent_max_mins']

        if not self.config_dict['queue_management']['stalled_monitor_enabled']:
            return False

        qbittorrent_identify_torrents_with_category_dict = self.prerun_checks()

        if not qbittorrent_identify_torrents_with_category_dict:
            return False

        # check if torrents are in stalled state, if so include in dict
        qbittorrent_identify_torrents_for_deletion_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_for_deletion(qbittorrent_identify_torrents_with_category_dict, 'stalledDL', delay_max_mins, 'last_activity')

        # if returned dict is empty then we cannot identify any torrents for deletion
        if not qbittorrent_identify_torrents_for_deletion_dict:
            return False

        # if torrent is in stalled state then delete torrent (check config to decide whether we delete data as well)
        self.torrent_clients_instance.qbittorrent_delete_stalled_torrents(qbittorrent_identify_torrents_for_deletion_dict)
