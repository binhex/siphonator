import qbittorrentapi
import lib.siphonator.tools_various as siphonator_tools_various


class TorrentClients(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.add_paused_bool = self.config_dict['torrent_client']['qbittorrent']['add_paused']
        self.category = self.config_dict['torrent_client']['qbittorrent']['category']
        self.torrent_dict = {}

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

    def qbittorrent_check_global_speed(self):

        # Retrieve transfer information
        transfer_info = self.qbt_client.transfer_info()

        # Get the global download and upload speeds
        global_download_speed = transfer_info['dl_info_speed']
        global_upload_speed = transfer_info['up_info_speed']

        self.logger_instance.info(f"qBittorrent global download speed is '{global_download_speed}' bytes/sec")
        self.logger_instance.info(f"qBittorrent global upload speed is '{global_upload_speed}' bytes/sec")

        if global_download_speed is 0 and global_upload_speed is 0:
            self.logger_instance.info(f"qBittorrent global download and upload speed is 0 bytes/sec, assuming internet connectivity issues")
            return False
        return True

    def qbittorrent_identify_torrents_with_category(self):

        # Retrieve all torrents with the specified category
        torrents_category_filtered = self.qbt_client.torrents_info(category=self.category)

        # Use dictionary comprehension to populate torrent_dict
        torrent_dict = {torrent['hash']: torrent for torrent in torrents_category_filtered}

        return torrent_dict

    def qbittorrent_identify_torrents_stalled(self, torrent_dict):

        # identify if torrent is in stalled state, if stalled for longer than xx minutes defined in config then mark for possible deletion

        # Extract 'name', 'last_activity', and 'state' values using dictionary comprehension
        stalled_torrents_dict = {
            torrent_hash: {
                'name': info['name'],
                'last_activity': siphonator_tools_various.convert_unix_timestamp(info['last_activity']),
                'state': info['state'],
            }
            for torrent_hash, info in torrent_dict.items()
            if 'name' in info and 'last_activity' in info and info.get('state') == 'stalledDL'
        }

        # Get last_activity datetime and compare to current time to get difference in minutes
        current_time = siphonator_tools_various.current_time()


        # if time difference in minutes is geater than config value then add to dict, else remove

        return stalled_torrents_dict

    def qbittorrent_identify_slow(self):

        # identify if torrent is slow, so if speed of download is equal to or less than defined speed in config file then mark for possible deletion
        pass

    def qbittorrent_delete_torrent(self):

        # delete specified torrent, also if configured in config then delete data
        pass

    def qbittorrent_identify_done(self):

        # identify if torrent is in done state, if done then mark for possible deletion of torrent (not data)
        pass

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
