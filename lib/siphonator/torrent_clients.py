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

    def qbittorrent_connect(self):

        function_name = siphonator_tools_various.get_function_name()

        torrent_client = self.config_dict['torrent_client']['selected']
        if torrent_client == 'qbittorrent':

            host = self.config_dict['torrent_client']['qbittorrent']['host']
            port = self.config_dict['torrent_client']['qbittorrent']['port']
            username = self.config_dict['torrent_client']['qbittorrent']['username']
            password = self.config_dict['torrent_client']['qbittorrent']['password']

            try:

                # instantiate a Client using the appropriate WebUI configuration
                qbt_client = qbittorrentapi.Client(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                )

                qbt_client.auth_log_in()

            except qbittorrentapi.LoginFailed:
                result_details = f"Failed: {function_name}: qBittorrent login failed"
                self.logger_instance.warning(result_details)
                return None

            except qbittorrentapi.APIConnectionError:
                result_details = f"Failed: {function_name}: qBittorrent API connection error"
                self.logger_instance.warning(result_details)
                return None

            except qbittorrentapi.APIError:
                result_details = f"Failed: {function_name}: qBittorrent API error"
                self.logger_instance.warning(result_details)
                return None

            return qbt_client

    def qbittorrent_check_global_speed(self):

        qbt_client = self.qbittorrent_connect()
        if not qbt_client:
            return

        # Retrieve transfer information
        transfer_info = qbt_client.transfer_info()

        # Get the global download and upload speeds
        global_download_speed = transfer_info['dl_info_speed']
        global_upload_speed = transfer_info['up_info_speed']

        if global_download_speed == 0 and global_upload_speed == 0:

            self.logger_instance.warn(f"qBittorrent global download and upload speed is 0 bytes/sec, assuming internet connectivity issues")
            return False

        self.logger_instance.debug(f"qBittorrent global download '{global_download_speed}' bytes/sec and upload speed '{global_upload_speed}' bytes/sec != 0, internet connectivity looks good")
        return True

    def qbittorrent_identify_torrents_with_category(self):

        qbt_client = self.qbittorrent_connect()
        if not qbt_client:
            return

        # Retrieve all torrents with the specified category
        torrents_category_filtered = qbt_client.torrents_info(category=self.category)

        # Use dictionary comprehension to populate torrent_dict
        torrent_dict = {torrent['hash']: torrent for torrent in torrents_category_filtered}

        self.logger_instance.debug(f"Dict of torrents returned from qBittorrent with category '{self.category}' is '{torrent_dict}")

        return torrent_dict

    def qbittorrent_identify_torrents_for_deletion(self, torrent_dict, state, delay_max_mins, filter_type):

        # Get the current time
        current_time = siphonator_tools_various.current_time_datetime_object()

        # Filter the torrents based on state of download and then get the appropriate time diff from current time
        torrents_dict = {
            torrent_hash: {
                'name': info['name'],
                'last_activity_diff_mins': int((current_time - siphonator_tools_various.convert_unix_timestamp_datetime_object(info['last_activity'])).total_seconds() / 60) if 'last_activity' in info and info['last_activity'] is not None else None,
                'added_on_diff_mins': int((current_time - siphonator_tools_various.convert_unix_timestamp_datetime_object(info['added_on'])).total_seconds() / 60) if 'added_on' in info and info['added_on'] is not None else None,
                'state': info['state'],
            }
            for torrent_hash, info in torrent_dict.items()
            if 'name' in info and info.get('state') == state
        }

        # Filter the torrents based on delay_max_mins and filter_type
        if filter_type == 'last_activity':
            torrents_to_delete_dict = {
                torrent_hash: info
                for torrent_hash, info in torrents_dict.items()
                if info['last_activity_diff_mins'] is not None and info['last_activity_diff_mins'] > delay_max_mins
            }
        elif filter_type == 'added_on':
            torrents_to_delete_dict = {
                torrent_hash: info
                for torrent_hash, info in torrents_dict.items()
                if info['added_on_diff_mins'] is not None and info['added_on_diff_mins'] > delay_max_mins
            }
        else:
            raise ValueError("Invalid filter_type. Must be 'last_activity' or 'added_on'.")

        self.logger_instance.debug(f"Torrents from qBittorrent with state '{state}' and {filter_type} >= '{delay_max_mins}' mins is '{torrents_to_delete_dict}'")
        return torrents_to_delete_dict

    def qbittorrent_identify_completed_torrents(self):

        qbt_client = self.qbittorrent_connect()
        if not qbt_client:
            return

        completed_torrent_dict_list = []

        # identify torrents in completed state with tags
        try:
            # Get the list of torrents with status 'completed'
            completed_torrents = qbt_client.torrents_info(status_filter='completed')

            for torrent in completed_torrents:
                tag = torrent.tags
                if tag:

                    # Get the list of files for the torrent
                    files = qbt_client.torrents_files(torrent.hash)

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
            self.logger_instance.warn(f"Failed to connect to qBittorrent API, error was '{e}'")

        return completed_torrent_dict_list

    def qbittorrent_add_torrent(self):

        qbt_client = self.qbittorrent_connect()
        if not qbt_client:
            return

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
        torrent_tag = str(f"siphonator-{uuid.uuid4()}")

        try:

            # Add the torrent with the unique label as a 'tag'
            qbt_client.torrents_add(
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
        qbt_client.torrents_reannounce(torrent_hashes='all')

        # add unique tag to result_dict
        self.result_dict.update({'torrent_tag': torrent_tag})
        return self.result_dict

    def qbittorrent_delete_torrent(self, torrent_hash, delete_torrent_data):

        qbt_client = self.qbittorrent_connect()
        if not qbt_client:
            return

        try:
            qbt_client.torrents_delete(delete_files=delete_torrent_data, torrent_hashes=torrent_hash)
            # TODO would be nice to see name of torrent as well as hash when logging
            if delete_torrent_data:
                self.logger_instance.info(f"Successfully deleted torrent hash '{torrent_hash}' and data")
            else:
                self.logger_instance.info(f"Successfully deleted torrent hash '{torrent_hash}'")
            return True
        except qbittorrentapi.APIError as e:
            self.logger_instance.info(f"Failed to delete torrent hash '{torrent_hash}', error was '{e}'")
            return False

    def qbittorrent_delete_stalled_torrents(self, qbittorrent_identify_torrents_for_deletion_dict):

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
