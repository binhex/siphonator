import lib.siphonator.torrent_clients as torrent_clients


class PostProcessMove(object):

    def __init__(self, logger_instance, config_dict):

        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.torrent_clients_instance = torrent_clients.TorrentClients(logger_instance, config_dict)

    def move_completed(self):

        # get list of torrents that have completed with tags and save to dict
        post_processing_dict = self.torrent_clients_instance.qbittorrent_identify_completed_tags()

        # TODO take output of function create_dict_of_completed abd perform db query for tag name to get imdb name and year and append to dict

        # TODO delete any non movie related files and folders - note need to identify dvd/bd/uhd raw dumps and not del

        # TODO create folders for all files that do not have folders in the root

        # TODO rename any existing root folders to match imdb title

        # TODO move processed folders and files to storage - need to add path to config.yml
