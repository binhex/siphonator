import lib.siphonator.torrent_clients as torrent_clients


class PostProcess(object):

    def __init__(self, logger_instance, config_dict):

        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.torrent_clients_instance = torrent_clients.TorrentClients(self.logger_instance, self.config_dict)

    def post_process(self):

        if not self.config_dict['post_process']['post_process_enabled']:
            return False

        self.identify_completed_torrents()
        self.delete_completed_torrents()
        self.cleanup_completed_files()
        self.rename_completed_files()
        self.move_completed_files()

    def identify_completed_torrents(self):

        # TODO WIP
        # get list of torrents that have completed with tags and save to dict
        torrent_completed_dict = self.torrent_clients_instance.qbittorrent_identify_completed_torrents()

        # send torrent_dict to db_sqlite to query db bsed on tag name for imdb name and year and append to dict and return here

    def delete_completed_torrents(self):

        # if db sqlite commit successful then delete completed torrents WITHOUT data
        pass

    def cleanup_completed_files(self):
        # if db sqlite commit successful then delete completed torrents WITHOUT data

        if not self.config_dict['post_process']['clean_completed']:
            return False

    def rename_completed_files(self):
        # if db sqlite commit successful then delete completed torrents WITHOUT data

        if not self.config_dict['post_process']['rename_completed']:
            return False

    def move_completed_files(self):
        # if db sqlite commit successful then delete completed torrents WITHOUT data

        if not self.config_dict['post_process']['move_completed']:
            return False
