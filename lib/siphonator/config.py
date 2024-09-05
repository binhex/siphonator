import yaml
from pydantic import BaseModel

# TODO rework, read config.yml to dict, then write back to yaml if file not exist


def update_config(init_dict, config_file_version):

    config_filepath = init_dict['config_filepath']
    config_version = init_dict['config_version']

    if config_version != config_file_version:

        if config_version == '1.0.1':

            config_modify_dict = {
                'general': {
                    'config_version': '1.0.1',
                }
            }

            # write new config option to config.yaml and then bump config_version
            #modify_config(config_filepath, config_modify_dict)


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


def verify_config(logger_instance, init_dict, config_dict):

    class General(BaseModel):

        library_path: str
        daemon_mode: str
        schedule_mode: str
        schedule_time_key: str
        schedule_time_value: int
        log_level: str
        config_version: float

        class Config:

            str_strip_whitespace = True

    class Filters(BaseModel):

        minimum_year: str
        minimum_runtime_mins: str
        minimum_rating: str
        minimum_votes: int
        minimum_seeders: int
        genre_minimum_rating_dict: dict
        good_country_list: list
        good_language_list: list
        bad_index_title_list: list
        bad_movie_title_list: list
        bad_genre_list: list
        override_cast_list: list
        override_writer_list: list
        override_director_list: list
        override_movie_title_list: list
        preferred_index_quality_list: list
        preferred_index_group_list: list
        override_character_list: list

