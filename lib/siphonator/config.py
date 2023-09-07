import yaml
# TODO remove deep_update as we no longer need to merge dicts as saving to config_dict not result_dict
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
            modify_config(config_filepath, config_modify_dict)


def read_config(init_dict):

    # get absolute path to config.yml
    config_filepath = init_dict['config_filepath']

    # read in existing config data
    with open(config_filepath, "r") as config_file:
        # convert from yaml to python dict
        config_dict = yaml.safe_load(config_file)

    # TODO work out best way to capture bad keys when calling dict, currently this style 'self.config_dict['notification']['email']['enabled']' will fail wil keyerror is not defined
    # TODO tidy up reading dict currently nasty mash up of .get and dict['key']

    return config_dict


def verify_config(logger_instance, init_dict, config_dict):

    # get absolute path to config.yml
    config_filepath = init_dict['config_filepath']

    # TODO verify options set correctly eg if notification email enabled then ensure we have all options set, see below
    if config_dict['notification']['email']['enabled']:

        if not config_dict['notification']['email']['host']:

            logger_instance.warning(f"E-mail notification enabled but no SMTP host specified in '{config_filepath}', please fix, disabling email notification...")
            config_modify_dict = {
                'notification': {
                    'email': {
                        'enabled': False,
                    }
                }
            }

            # write new config option to config.yaml and then bump config_version
            modify_config(config_filepath, config_modify_dict)

    # check enabled options
    # check values are sane
    # fill in missing values with defaults and write to config
    pass
