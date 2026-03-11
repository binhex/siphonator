import yaml
from pydantic import BaseModel, ValidationError, IPvAnyAddress

# TODO WIP


class GeneralConfig(BaseModel):
    config_version: str
    daemon_mode: str
    log_level_console: str
    log_level_file: str
    library_path_list: list


class ScheduleConfig(BaseModel):
    schedule_mode: str
    schedule_time_units: str
    schedule_time_mins: int


class FiltersConfig(BaseModel):
    minimum_year: int
    minimum_runtime_mins: int
    minimum_rating: float
    minimum_votes: int
    minimum_seeders: int
    override_genre: list = None
    good_imdb_title_type_list: list
    good_country_list: list = None
    good_language_list: list = None
    bad_index_title_list: list = None
    bad_genre_list: list = None
    bad_movie_title_list: list = None
    override_cast_list: list = None
    override_writer_list: list = None
    override_director_list: list = None
    override_movie_title_list: list = None
    override_character_list: list = None
    preferred_index_quality_list: list = None
    preferred_index_group_list: list = None


class QbittorrentConfig(BaseModel):
    host: IPvAnyAddress
    port: int
    username: str
    password: str
    add_paused: bool
    category: str


class TorrentClientConfig(BaseModel):
    selected: str
    qbittorrent: QbittorrentConfig


class JackettConfig(BaseModel):
    host: str
    port: int
    api_key: str
    read_timeout: float
    limit: int
    offset: int


class IndexProxyConfig(BaseModel):
    selected: str
    jackett: JackettConfig


class EmailConfig(BaseModel):
    enabled: bool
    host: str = None
    port: int = None
    enable_tls: bool = None
    enable_ssl: bool = None
    username: str = None
    password: str = None
    from_address: str = None
    to_address: str = None


class NotificationConfig(BaseModel):
    email: EmailConfig


class CredentialsConfig(BaseModel):
    tmdb: dict
    omdb: dict


class SearchConfig(BaseModel):
    criteria: str
    category: str
    minimum_size_mb: int
    maximum_size_mb: int
    minimum_bitrate_mb: int


class IndexSiteConfig(BaseModel):
    ignore_list: list = None
    search: list[SearchConfig]
    override_search: list = None


class QueueManagementConfig(BaseModel):
    queue_management_enabled: bool
    metadata_monitor_enabled: bool
    stalled_monitor_enabled: bool
    stalled_delete_torrent_data: bool
    stalled_delete_torrent_max_mins: int
    metadata_delete_torrent_max_mins: int
    connection_down_grace_mins: int
    connection_down_datetime: str = None
    client_startup_grace_mins: int


class PostProcessConfig(BaseModel):
    post_process_enabled: bool
    rename_completed: bool
    move_completed: bool
    remove_completed: bool
    delete_unwanted_files: bool
    delete_unwanted_min_kb: int
    delete_max_path_size_gb: int
    delete_unwanted_ext_list: list = None
    move_library_path: str = None


class Config(BaseModel):
    general: GeneralConfig
    schedule: dict[str, ScheduleConfig]
    filters: FiltersConfig
    torrent_client: TorrentClientConfig
    index_proxy: IndexProxyConfig
    notification: NotificationConfig
    credentials: CredentialsConfig
    index_site: IndexSiteConfig
    queue_management: QueueManagementConfig
    post_process: PostProcessConfig


def verify_config(config_dict):
    try:
        config = Config(**config_dict)
        print("Configuration is valid.")
    except ValidationError as e:
        print("Configuration validation failed:")
        print(e)


# Example usage
init_dict = {'config_filepath': '/data/siphonator/configs/config-user.yml'}
config_filepath = init_dict['config_filepath']

# Read the existing config data
with open(config_filepath, "r") as config_file:
    config_dict = yaml.safe_load(config_file)

# Verify the configuration
verify_config(config_dict)
