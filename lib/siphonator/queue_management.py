import lib.siphonator.torrent_clients as torrent_clients


class QueueManagement(object):

    def __init__(self, logger_instance, config_dict):
        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.torrent_clients_instance = torrent_clients.TorrentClients(logger_instance, config_dict)

    # feature - check qbittorrent status, if incoming port working (internet connection ok) and if torrent not stopped then look at whether stalled, if stalled for X minutes (defined in config) then delete (torrent or torrent + data, defined in config)
    def delete_stalled_torrents(self):

        # if monitoring not enabled then return
        if not self.config_dict['queue_management']['stalled_monitor_enabled']:
            return False

        # if ul/dl speed is 0 then assume internet down, this is to prevent torrents being incorrectly marked as stalled
        if not self.torrent_clients_instance.qbittorrent_check_global_speed():
            return False

        # get list of torrents added by siphonator (category set)
        qbittorrent_identify_torrents_with_category_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_with_category()

        # if returned dict is empty then we cannot identify any torrents with category set
        if not qbittorrent_identify_torrents_with_category_dict:
            return False

        # check if torrents are in stalled state, if so include in dict
        qbittorrent_identify_torrents_for_deletion_dict = self.torrent_clients_instance.qbittorrent_identify_torrents_for_deletion(qbittorrent_identify_torrents_with_category_dict)

        # if returned dict is empty then we cannot identify any torrents for deletion
        if not qbittorrent_identify_torrents_for_deletion_dict:
            return False

        # if torrent is in stalled state then delete torrent (check config to decide whether we delete data as well)
        self.torrent_clients_instance.qbittorrent_delete_torrents(qbittorrent_identify_torrents_for_deletion_dict)
