import os
import yaml
import pathlib
import lib.siphonator.tools_logging as siphonator_tools_logging


def read_config(config_filepath):

    with open(config_filepath, "r") as config_file:
        config_yaml_load = yaml.safe_load(config_file)

    return config_yaml_load


class TestsInit(object):
    # prevents pytest from assuming this is a test due to the class name including the word 'test'
    __test__ = False

    def __init__(self):

        # get current path for this script, then split to move up directory to root
        app_root_path = os.path.dirname(os.path.realpath(__file__))

        # set folder path for config files
        configs_path = os.path.join(app_root_path, u"configs")
        configs_path = os.path.normpath(configs_path)
        configs_filepath = os.path.join(configs_path, 'config.yml')

        # read in config file
        self.config_yaml = read_config(configs_filepath)

        # set folder path for db files
        db_path = os.path.join(app_root_path, u"db")
        db_path = os.path.normpath(db_path)
        self.db_filepath = os.path.join(db_path, u"siphonator.db")

        # set folder path for ffprobe files
        ffprobe_path = os.path.join(app_root_path, 'tools/ffprobe/static/x64')
        self.ffprobe_filepath = os.path.join(ffprobe_path, 'ffprobe')

        # set folder path for log files
        logs_path = os.path.join(app_root_path, u"logs")
        logs_path = os.path.normpath(logs_path)
        self.logs_filepath = os.path.join(logs_path, u"siphonator.log")

    def setup(self):

        ffprobe_filepath = self.ffprobe_filepath

        # setup logging
        log_level = self.config_yaml['general']['log_level_console']
        logger, file_handler, console_handler = siphonator_tools_logging.app_logging(log_level, self.logs_filepath, self.logs_filepath)

        return ffprobe_filepath, logger
