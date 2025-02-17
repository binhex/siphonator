import lib.siphonator.torrent_clients as torrent_clients


class PostProcessMove(object):

    def __init__(self, logger_instance, config_dict):

        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.torrent_clients_instance = torrent_clients.TorrentClients(logger_instance, config_dict)

    def move_completed(self):

        # get list of torrents that have completed with tags and save to dict
        post_processing_dict = self.torrent_clients_instance.qbittorrent_identify_completed_tags()

        # send post_processing_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return

        # use dict from previous function to loop over list of files to delete (chec config to see if enabled)

        # TODO create folders for all files that do not have folders in the root

        # TODO rename any existing root folders to match imdb title

        # TODO move processed folders and files to storage - need to add path to config.yml
