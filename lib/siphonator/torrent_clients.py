import qbittorrentapi
import lib.siphonator.tools_various as siphonator_tools_various
import uuid


class TorrentClients(object):

    def __init__(self, logger_instance, config_dict, result_dict=None):

        self.logger_instance = logger_instance
        self.config_dict = config_dict
        self.result_dict = result_dict
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

    def qbittorrent_check_global_speed(self):

        # Retrieve transfer information
        transfer_info = self.qbt_client.transfer_info()

        # Get the global download and upload speeds
        global_download_speed = transfer_info['dl_info_speed']
        global_upload_speed = transfer_info['up_info_speed']

        if global_download_speed == 0 and global_upload_speed == 0:

            self.logger_instance.warn(f"qBittorrent global download and upload speed is 0 bytes/sec, assuming internet connectivity issues")
            return False

        self.logger_instance.debug(f"qBittorrent global download speed is '{global_download_speed}' bytes/sec")
        self.logger_instance.debug(f"qBittorrent global upload speed is '{global_upload_speed}' bytes/sec")

        return True

    def qbittorrent_identify_torrents_with_category(self):

        # Retrieve all torrents with the specified category
        torrents_category_filtered = self.qbt_client.torrents_info(category=self.category)

        # Use dictionary comprehension to populate torrent_dict
        torrent_dict = {torrent['hash']: torrent for torrent in torrents_category_filtered}

        return torrent_dict

    def qbittorrent_identify_torrents_for_deletion(self, torrent_dict):

        stalled_delete_torrent_max_mins = self.config_dict['queue_management']['stalled_delete_torrent_max_mins']

        # filter the torrents based on state of stalled download and then get last activity diff from current time
        stalled_torrents_dict = {
            torrent_hash: {
                'name': info['name'],
                'last_activity_diff_mins': int((siphonator_tools_various.current_time_datetime_object() - siphonator_tools_various.convert_unix_timestamp_datetime_object(info['last_activity'])).total_seconds() / 60) if 'last_activity' in info and info['last_activity'] is not None else None,
                'state': info['state'],
            }
            for torrent_hash, info in torrent_dict.items()
            if 'name' in info and 'last_activity_diff_mins' and info.get('state') == 'stalledDL'
        }

        # filter the torrents based on the comparison with stalled_delete_torrent_max_mins (from config)
        torrents_to_delete_dict = {
            torrent_hash: info
            for torrent_hash, info in stalled_torrents_dict.items()
            # TODO would be nice to log torrent names that are stalled but last activity is not greater than config value for stalled_delete_torrent_max_mins
            if info['last_activity_diff_mins'] is not None and info['last_activity_diff_mins'] > stalled_delete_torrent_max_mins
        }

        return torrents_to_delete_dict

    def qbittorrent_delete_torrents(self, qbittorrent_identify_torrents_for_deletion_dict):

        stalled_delete_torrent_data = self.config_dict['queue_management']['stalled_delete_torrent_data']

        # Delete torrents using dictionary comprehension
        failed_deletions = {
            torrent_hash: info
            for torrent_hash, info in qbittorrent_identify_torrents_for_deletion_dict.items()
            if not self.qbittorrent_delete_torrent(torrent_hash, stalled_delete_torrent_data)
        }

        # Print the failed deletions
        if failed_deletions:
            self.logger_instance.info(f"Failed to delete the following torrents:")
            for torrent_hash, info in failed_deletions.items():
                self.logger_instance.info(f"Hash: {torrent_hash}, Name: {info['name']}")

    def qbittorrent_delete_torrent(self, torrent_hash, stalled_delete_torrent_data):

        try:
            self.qbt_client.torrents_delete(delete_files=stalled_delete_torrent_data, torrent_hashes=torrent_hash)
            # TODO would be nice to see name of torrent as well as hash when logging
            if stalled_delete_torrent_data:
                self.logger_instance.info(f"Successfully deleted torrent hash '{torrent_hash}' and data")
            else:
                self.logger_instance.info(f"Successfully deleted torrent hash '{torrent_hash}'")
            return True
        except qbittorrentapi.APIError as e:
            self.logger_instance.info(f"Failed to delete torrent hash '{torrent_hash}', error was '{e}'")
            return False

    def qbittorrent_identify_completed_tags(self):

        completed_torrent_dict_list = []

        # identify torrents in completed state with tags
        try:
            # Get the list of torrents with status 'completed'
            completed_torrents = self.qbt_client.torrents_info(status_filter='completed')

            for torrent in completed_torrents:
                tag = torrent.tags
                if tag:

                    # Get the list of files for the torrent
                    files = self.qbt_client.torrents_files(torrent.hash)

                    torrent_file_list = []

                    for file in files:

                        # filter dict to only filenames
                        torrent_file_dict = {'file_name': file.name}

                        # append dict of filenames to list
                        torrent_file_list.append(torrent_file_dict)

                    # filter dict to torrent name, torrent tag, and torrent  filenames (list)
                    completed_torrent_dict = {'torrent_name': torrent.name, 'torrent_tag': tag, 'torrent_file_list': torrent_file_list}

                    # append dict of torrent name, torrent tag and torrent files to list
                    completed_torrent_dict_list.append(completed_torrent_dict)

        except qbittorrentapi.APIError as e:
            print(f"API error: {e}")

        print(completed_torrent_dict_list)

    def qbittorrent_identify_done(self):

        # identify if torrent is in done state, if done then mark for possible deletion of torrent (not data)
        pass

    def qbittorrent_add(self):

        download_url = self.result_dict['magnet_url']
        if download_url is None:

            self.logger_instance.info(f"No magnet link present for index title '{self.result_dict['index_title']}', trying torrent file...")

            download_url = self.result_dict['torrent_url']
            if download_url is None:

                self.logger_instance.info(f"No torrent/magnet present, cannot download index title '{self.result_dict['index_title']}'")
                return None

        # Generate a unique label and set for the torrent to be added, this unique identifier
        # is then added to the result_dict where it will be saved to the database. This can
        # then be used to post process by creating/renaming folder to match imdb title for
        # that unique id
        torrent_tag = str(uuid.uuid4())

        try:

            # Add the torrent with the unique label as a 'tag'
            self.qbt_client.torrents_add(
                urls=download_url,
                category=self.category,
                is_paused=self.add_paused_bool,
                tags=torrent_tag,
            )
            self.logger_instance.debug(f"Added magnet/torrent URL: {download_url}, Category: {self.category}, Paused: {self.add_paused_bool}, Tag: '{torrent_tag}'")

        except qbittorrentapi.APIError as e:

            self.logger_instance.debug(f"Failed to add torrent, error is '{e}'")
            return None

        # re-announce
        self.qbt_client.torrents_reannounce(torrent_hashes='all')

        # add unique tag to result_dict
        self.result_dict.update({'torrent_tag': torrent_tag})
        return self.result_dict
