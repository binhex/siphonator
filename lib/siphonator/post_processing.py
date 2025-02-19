import lib.siphonator.torrent_clients as torrent_clients


class PostProcess(object):

    def __init__(self, logger_instance, config_dict):

        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict)

    def post_process(self):

        if not self.config_dict['post_process']['post_process_enabled']:
            return False

        self.torrents_completed_dict()

        # send torrent_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return

        # if db sqlite commit successful then delete completed torrents WITHOUT data

        # use dict to loop over list of files to delete (chec config to see if enabled)

        # TODO create folders for all files that do not have folders in the root

        # TODO rename any existing root folders to match imdb title

        # TODO move processed folders and files to storage - need to add path to config.yml

    def torrents_completed_dict(self):

        # TODO WIP
        # get list of torrents that have completed with tags and save to dict
        torrent_completed_dict = self.torrent_clients_instance.qbittorrent_identify_completed_torrents()
