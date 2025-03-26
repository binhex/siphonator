import os
import yaml


def create_config_file(init_dict):

    config_data = {
        'general': {
            'config_version': '0.0.1',
            'daemon_mode': 'foreground',
            'log_level_console': 'info',
            'log_level_file': 'info',
            'library_path_list': None,
        },
        'schedule': {
            'siphonator_thread': {
                'schedule_mode': 'foreground',
                'schedule_time_units': 'minutes',
                'schedule_time_mins': 30
            },
            'queue_management_thread': {
                'schedule_mode': 'background',
                'schedule_time_units': 'minutes',
                'schedule_time_mins': 5
            },
            'post_processing_thread': {
                'schedule_mode': 'background',
                'schedule_time_units': 'minutes',
                'schedule_time_mins': 10
            }
        },
        'filters': {
            'minimum_year': 1970,
            'minimum_runtime_mins': 60,
            'minimum_rating': 7.0,
            'minimum_votes': 5000,
            'minimum_seeders': 1,
            'override_genre': None,
            'good_imdb_title_type_list': ['movie', 'video', 'tvmovie'],
            'good_country_list': None,
            'good_language_list': None,
            'bad_index_title_list': None,
            'bad_genre_list': None,
            'bad_movie_title_list': None,
            'override_cast_list': None,
            'override_writer_list': None,
            'override_director_list': None,
            'override_movie_title_list': None,
            'override_character_list': None,
            'preferred_index_quality_list': None,
            'preferred_index_group_list': None
        },
        'torrent_client': {
            'selected': 'qbittorrent',
            'qbittorrent': {
                'host': None,
                'port': None,
                'username': None,
                'password': None,
                'add_paused': True,
                'category': 'movies-siphonator'
            }
        },
        'index_proxy': {
            'selected': 'jackett',
            'jackett': {
                'host': None,
                'port': None,
                'api_key': None,
                'read_timeout': 60.0,
                'limit': 500,
                'offset': 0
            }
        },
        'notification': {
            'email': {
                'enabled': False,
                'host': None,
                'port': None,
                'enable_tls': None,
                'enable_ssl': None,
                'username': None,
                'password': None,
                'from_address': None,
                'to_address': None
            }
        },
        'credentials': {
            'tmdb': {
                'api_key': None
            },
            'omdb': {
                'api_key': None
            }
        },
        'index_site': {
            'ignore_list': None,
            'search': [
                {
                    'criteria': '1080p',
                    'category': '2000,5000',
                    'minimum_size_mb': 3000,
                    'maximum_size_mb': 20000,
                    'minimum_bitrate_mb': 50
                },
                {
                    'criteria': '2160p',
                    'category': '2000,5000',
                    'minimum_size_mb': 7000,
                    'maximum_size_mb': 170000,
                    'minimum_bitrate_mb': 115
                }
            ],
            'override_search': None
        },
        'queue_management': {
            'queue_management_enabled': True,
            'metadata_monitor_enabled': True,
            'stalled_monitor_enabled': True,
            'stalled_delete_torrent_data': False,
            'stalled_delete_torrent_max_mins': 120,
            'metadata_delete_torrent_max_mins': 20,
            'connection_down_grace_mins': 30,
            'connection_down_datetime': None,
            'client_startup_grace_mins': 30
        },
        'post_process': {
            'post_process_enabled': True,
            'copy_completed': True,
            'remove_completed': True,
            'exclude_file_min_kb': 10000,
            'exclude_file_regex_list': None,
            'copy_library_path': None,
        }
    }

    # get filepath to config.yml
    config_filepath = init_dict.get('config_filepath')

    # if the config.yml does not exist then create it
    if not os.path.isfile(config_filepath):
        print(f"configuration file '{config_filepath}' does not exist, creating default configuration...")
        # write the configuration data to config.yml
        with open(config_filepath, 'w') as config_file:
            yaml.dump(config_data, config_file, default_flow_style=False, sort_keys=False)
        return True
    else:
        print(f"configuration file '{config_filepath}' already exists, skipping creation")
        return False


# TODO WIP
def update_config(init_dict, config_file_version):

    config_version = init_dict['config_version']

    if config_version != config_file_version:

        if config_version == '1.0.1':

            config_modify_dict = {
                'general': {
                    'config_version': '1.0.1',
                }
            }


# read in init_dict as arg, get location of config.yml and return as dict
def read_config(init_dict):

    # get absolute path to config.yml
    config_filepath = init_dict['config_filepath']

    # read in existing config data
    with open(config_filepath, "r") as config_file:
        # convert from yaml to python dict
        config_dict = yaml.safe_load(config_file)

    return config_dict


# read in config_dict as arg, then write back to config.yml
def write_config(init_dict, config_dict):

    # get absolute path to config.yml
    config_filepath = init_dict['config_filepath']

    # write modified data back to the config file
    with open(config_filepath, "w") as config_file:
        # convert from python dict to yaml
        yaml.safe_dump(config_dict, config_file, sort_keys=False)
