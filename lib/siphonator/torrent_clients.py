import qbittorrentapi


class TorrentClients(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.add_paused_bool = self.config_dict['torrent_client']['qbittorrent']['add_paused']
        self.category = self.config_dict['torrent_client']['qbittorrent']['category']

        torrent_client = self.config_dict['torrent_client']['selected']
        if torrent_client == 'qbittorrent':

            host = self.config_dict['torrent_client']['qbittorrent']['host']
            port = self.config_dict['torrent_client']['qbittorrent']['port']
            username = self.config_dict['torrent_client']['qbittorrent']['username']
            password = self.config_dict['torrent_client']['qbittorrent']['password']

            # instantiate a Client using the appropriate WebUI configuration
            self.qbt_client = qbittorrentapi.Client(
                host=host,
                port=port,
                username=username,
                password=password,
            )

            # the Client will automatically acquire/maintain a logged-in state
            # in line with any request. therefore, this is not strictly necessary;
            # however, you may want to test the provided login credentials.
            try:

                self.qbt_client.auth_log_in()

            except qbittorrentapi.LoginFailed as e:

                self.logger_instance.warning(f"qBittorrent login failed for username '{username}' with error '{e}'")

    # TODO search and identify if existing movie already paused/downloading/downloaded
    def qbittorrent_search(self):

        # display qBittorrent info
        print(f'qBittorrent: {self.qbt_client.app.version}')
        print(f'qBittorrent Web API: {self.qbt_client.app.web_api_version}')
        for k, v in self.qbt_client.app.build_info.items():
            print(f'{k}: {v}')

        # retrieve and show torrents tagged as added by siphonator
        for torrent in self.qbt_client.torrents_info(tag='siphonator'):
            print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

    def qbittorrent_queue(self):

        # pause all torrents
        self.qbt_client.torrents.pause.all()

    def qbittorrent_add(self):

        download_url = self.result_dict['magnet_url']
        if download_url is None:

            self.logger_instance.info(f"No magnet link present for index title '{self.result_dict['index_title']}', trying torrent file...")

            download_url = self.result_dict['torrent_url']
            if download_url is None:

                self.logger_instance.info(f"No torrent/magnet present, cannot download index title '{self.result_dict['index_title']}'")
                return None

        self.logger_instance.debug(f"Magnet/Torrent link is '{download_url}'")

        # add torrent/magnet to queue
        self.qbt_client.torrents_add(urls=download_url, category=self.category, is_paused=self.add_paused_bool)
        self.qbt_client.torrents_reannounce(torrent_hashes='all')
