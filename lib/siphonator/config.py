import yaml
from pydantic.v1.utils import deep_update


def modify_config(config_filepath, config_modify_dict):

    # read in existing config data
    with open(config_filepath, "r") as config_file:
        # convert from yaml to python dict
        config_data = yaml.safe_load(config_file)

        # using pydantic to merge dicts without overwriting existing keys
        config_data = deep_update(config_data, config_modify_dict)

    # write modified data back to the config file
    with open(config_filepath, "w") as config_file:
        # convert from python dict to yaml
        yaml.safe_dump(config_data, config_file, sort_keys=False)


def update_config(index_dict):

    config_filepath = index_dict['config_filepath']
    config_file_version = index_dict['config_file_version']
    config_version = index_dict['config_version']

    if config_version != config_file_version:

        if config_version == '1.0.1':

            config_modify_dict = {
                'general': {
                    'config_version': '1.0.1',
                }
            }

            # write new config option to config.yaml and then bump config_version
            modify_config(config_filepath, config_modify_dict)


def read_config(index_dict):

    # use function to update config if outdated
    update_config(index_dict)

    # get absolute path to config.yml
    config_filepath = index_dict['config_filepath']

    # read in existing config data
    with open(config_filepath, "r") as config_file:
        # convert from yaml to python dict
        config_dict = yaml.safe_load(config_file)
        
    # TODO save to config_dict and then change to key value not var name e.g. change index_dict['torrent_client_host'] to config_dict['torrent_client']['qbittorrent']['host']
    # TODO remove deep_update as we no longer need to merge dicts as saving to config_dict not index_dict
    # TODO rename index_dict to processed_dict
    # TODO add in config_dict to all classes as now not in index_dict
    print(config_dict)

    torrent_client = config_dict['torrent_client']['selected']
    if torrent_client == 'qbittorrent':

        torrent_client_host = config_dict['torrent_client']['qbittorrent']['host']
        torrent_client_port = config_dict['torrent_client']['qbittorrent']['port']
        torrent_client_username = config_dict['torrent_client']['qbittorrent']['username']
        torrent_client_password = config_dict['torrent_client']['qbittorrent']['password']
        torrent_client_add_paused = config_dict['torrent_client']['qbittorrent']['add_paused']
        torrent_client_category = config_dict['torrent_client']['qbittorrent']['category']

    else:

        torrent_client_host = None
        torrent_client_port = None
        torrent_client_username = None
        torrent_client_password = None
        torrent_client_add_paused = None
        torrent_client_category = None

    index_proxy = config_dict['index_proxy']['selected']
    if index_proxy == 'jackett':

        index_proxy_host = config_dict['index_proxy']['jackett']['host']
        index_proxy_port = config_dict['index_proxy']['jackett']['port']
        index_proxy_api_key = config_dict['index_proxy']['jackett']['api_key']
        index_proxy_read_timeout = config_dict['index_proxy']['jackett']['read_timeout']
        index_proxy_limit = config_dict['index_proxy']['jackett']['limit']
        index_proxy_url = f'http://{index_proxy_host}:{index_proxy_port}/api/v2.0/indexers/all/results/torznab/api?configured=true&apikey={index_proxy_api_key}&t=indexers&q='

    else:

        index_proxy_host = None
        index_proxy_port = None
        index_proxy_api_key = None
        index_proxy_read_timeout = None
        index_proxy_limit = None
        index_proxy_url = None

    notification_email_enabled = config_dict['notification']['email']['enabled']
    if notification_email_enabled:

        notification_email_host = config_dict['notification']['email']['host']
        notification_email_port = config_dict['notification']['email']['port']
        notification_email_enable_tls = config_dict['notification']['email']['enable_tls']
        notification_email_enable_ssl = config_dict['notification']['email']['enable_ssl']
        notification_email_username = config_dict['notification']['email']['username']
        notification_email_password = config_dict['notification']['email']['password']
        notification_email_from_address = config_dict['notification']['email']['from_address']
        notification_email_to_address = config_dict['notification']['email']['to_address']

    else:

        notification_email_host = None
        notification_email_port = None
        notification_email_enable_tls = None
        notification_email_enable_ssl = None
        notification_email_username = None
        notification_email_password = None
        notification_email_from_address = None
        notification_email_to_address = None

    library_path = config_dict['general']['library_path']
    filter_minimum_year = config_dict['filters']['minimum_year']
    filter_minimum_runtime_mins = config_dict['filters']['minimum_runtime_mins']
    filter_genre_minimum_rating_dict = config_dict['filters']['genre_minimum_rating_dict']
    filter_minimum_rating = config_dict['filters']['minimum_rating']
    filter_minimum_votes = config_dict['filters']['minimum_votes']
    filter_minimum_seeders = config_dict['filters']['minimum_seeders']
    filter_bad_index_title_list = config_dict["filters"]['bad_index_title_list']
    filter_preferred_index_group_list = config_dict["filters"]['preferred_index_group_list']
    filter_override_character_list = config_dict["filters"]['override_character_list']

    filter_good_country_list = config_dict["filters"]['good_country_list']
    filter_good_language_list = config_dict["filters"]['good_language_list']
    filter_bad_movie_title_list = config_dict["filters"]['bad_movie_title_list']
    filter_bad_genre_list = config_dict["filters"]['bad_genre_list']
    filter_override_cast_list = config_dict["filters"]['override_cast_list']
    filter_override_writer_list = config_dict["filters"]['override_writer_list']
    filter_override_director_list = config_dict["filters"]['override_director_list']
    filter_override_movie_title_list = config_dict["filters"]['override_movie_title_list']
    filter_preferred_index_quality_list = config_dict["filters"]['preferred_index_quality_list']

    search_tmdb_api_key = config_dict["credentials"]['tmdb']['api_key']
    search_omdb_api_key = config_dict["credentials"]['omdb']['api_key']

    index_site_search_dict_list = config_dict["index_site"]['search_dict_list']
    index_site_ignore_list = config_dict["index_site"]['ignore_list']
    index_site_ignore_list_lower = [x.lower() for x in index_site_ignore_list]

    # add in additional info to pass around as dict
    index_dict.update({
        'library_path': library_path,
        'index_site_search_dict_list': index_site_search_dict_list,
        'index_site_ignore_list_lower': index_site_ignore_list_lower,
        'index_proxy': index_proxy,
        'index_proxy_host': index_proxy_host,
        'index_proxy_port': index_proxy_port,
        'index_proxy_api_key': index_proxy_api_key,
        'index_proxy_limit': index_proxy_limit,
        'index_proxy_read_timeout': index_proxy_read_timeout,
        'index_proxy_url': index_proxy_url,
        'torrent_client': torrent_client,
        'torrent_client_host': torrent_client_host,
        'torrent_client_port': torrent_client_port,
        'torrent_client_username': torrent_client_username,
        'torrent_client_password': torrent_client_password,
        'torrent_client_add_paused': torrent_client_add_paused,
        'torrent_client_category': torrent_client_category,
        'notification_email_enabled': notification_email_enabled,
        'notification_email_host': notification_email_host,
        'notification_email_port': notification_email_port,
        'notification_email_enable_tls': notification_email_enable_tls,
        'notification_email_enable_ssl': notification_email_enable_ssl,
        'notification_email_username': notification_email_username,
        'notification_email_password': notification_email_password,
        'notification_email_from_address': notification_email_from_address,
        'notification_email_to_address': notification_email_to_address,
        'filter_minimum_year': filter_minimum_year,
        'filter_minimum_runtime_mins': filter_minimum_runtime_mins,
        'filter_genre_minimum_rating_dict': filter_genre_minimum_rating_dict,
        'filter_minimum_rating': filter_minimum_rating,
        'filter_minimum_votes': filter_minimum_votes,
        'filter_minimum_seeders': filter_minimum_seeders,
        'filter_bad_genre_list': filter_bad_genre_list,
        'filter_bad_index_title_list': filter_bad_index_title_list,
        'filter_good_language_list': filter_good_language_list,
        'filter_override_character_list': filter_override_character_list,
        'filter_override_director_list': filter_override_director_list,
        'filter_override_writer_list': filter_override_writer_list,
        'filter_override_cast_list': filter_override_cast_list,
        'filter_override_movie_title_list': filter_override_movie_title_list,
        'filter_bad_movie_title_list': filter_bad_movie_title_list,
        'filter_good_country_list': filter_good_country_list,
        'filter_preferred_index_group_list': filter_preferred_index_group_list,
        'filter_preferred_index_quality_list': filter_preferred_index_quality_list,
        'search_tmdb_api_key': search_tmdb_api_key,
        'search_omdb_api_key': search_omdb_api_key,
    })

    return index_dict
