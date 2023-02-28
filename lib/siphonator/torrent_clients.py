import qbittorrentapi

# TODO search and identify if existing movie already paused/downloading/downloaded
# TODO read in user defined option to add torrent/magnet in paused or started state, currently hard set to paused

class TorrentClients(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.logger_instance = logger_instance
        self.add_paused_bool = self.index_dict['torrent_client_qbittorrent_add_paused'].lower()

        host = self.index_dict['torrent_client_qbittorrent_host']
        port = self.index_dict['torrent_client_qbittorrent_port']
        username = self.index_dict['torrent_client_qbittorrent_username']
        password = self.index_dict['torrent_client_qbittorrent_password']


        # instantiate a Client using the appropriate WebUI configuration
        self.qbt_client = qbittorrentapi.Client(
            host = host,
            port = port,
            username = username,
            password = password,
        )

        # the Client will automatically acquire/maintain a logged-in state
        # in line with any request. therefore, this is not strictly necessary;
        # however, you may want to test the provided login credentials.
        try:

            self.qbt_client.auth_log_in()

        except qbittorrentapi.LoginFailed as e:

            self.logger_instance.warning(u"qBittorrent login failed for username '%s' with error '%s'" % (username, e))

    def qbittorrent_search(self):

        # display qBittorrent info
        print(f'qBittorrent: {self.qbt_client.app.version}')
        print(f'qBittorrent Web API: {self.qbt_client.app.web_api_version}')
        for k,v in self.qbt_client.app.build_info.items(): print(f'{k}: {v}')

        # retrieve and show torrents tagged as added by siphonator
        for torrent in self.qbt_client.torrents_info(tag='siphonator'):
            print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

    def qbittorrent_queue(self):

        # pause all torrents
        self.qbt_client.torrents.pause.all()

    def qbittorrent_add(self):

        # TODO seems to be a bug in getting torrent_url, seems to be magnet or empty?
        download_url = self.index_dict['magnet_url']
        if download_url is None:

            self.logger_instance.info(u"No magnet link present for index title '%s', trying torrent file..." % self.index_dict['index_title'])

            download_url = self.index_dict['torrent_url']
            if download_url is None:

                self.logger_instance.info(u"No torrent file present, cannot download index title '%s'" % self.index_dict['index_title'])
                return None

        self.logger_instance.debug(u"Magnet/Torrent link is '%s'" % download_url)

        # add torrent/magnet to quue
        self.qbt_client.torrents_add(urls=download_url, category='movies-siphonator', is_paused=self.add_paused_bool)
        self.qbt_client.torrents_reannounce(torrent_hashes='all')
