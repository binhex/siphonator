import os
import platform
import sys
import argparse
import datetime
import pytest
import xml.etree.ElementTree as elementTree
from imdbpie import ImdbAPIError
from daemonize import Daemonize
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import lib.siphonator.config as siphonator_config
import lib.siphonator.post_processing as post_processing

# check version of python is 3.x.x
python_version = sys.version_info
if python_version < (3, 10, 0):

    sys.stderr.write(f"WARNING - You need Python 3.10.x or later installed to run Siphonator, your running version '{python_version, }'")
    sys.exit(1)

# define path to siphonator root path - required for linux
root_dir = os.path.dirname(os.path.realpath(__file__))

# -------------------- siphonator modules -----------------------------
# this is req to allow import of local modules (pex bug):-
# https://github.com/pantsbuild/pex/issues/340#issuecomment-358775440
sys.path.append(f"{root_dir}/")

import lib.siphonator.index_proxy as siphonator_index_proxy
import lib.siphonator.tools_logging as siphonator_tools_logging
import lib.siphonator.tools_various as siphonator_tools_various
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.db_sqlite as siphonator_db_sqlite


def create_path(path):

    if not os.path.exists(path):

        try:
            os.makedirs(path)
        except OSError as e:
            print(f"Error creating path '{path}', error is '{e}'")
            return False

    return True


class SiphonatorPostProcess(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.init_dict = init_dict
        self.config_dict = config_dict

    def schedule_run(self):

        # set to blocking scheduler if set to foreground
        if post_process_schedule_mode == 'foreground':
            schedule = BlockingScheduler()
        else:
            schedule = BackgroundScheduler()

        self.logger_instance.info(f"Running schedule in '{post_process_schedule_mode}' mode")

        try:

            schedule.add_job(siphonator_post_process_instance.run, 'interval', minutes=self.config_dict['general']['post_process']['schedule_time_value'], next_run_time=datetime.datetime.now())
            schedule.start()

        except (KeyboardInterrupt, SystemExit):

            self.logger_instance.info(u"Keyboard interrupt or system exit detected, shutting down...")
            schedule.shutdown()

    def schedule_msg(self):

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(self.config_dict['general']['post_process']['schedule_time_value']))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        self.logger_instance.info(f"Schedule running in '{self.config_dict['general']['post_process']['schedule_mode']}' mode every '{self.config_dict['general']['post_process']['schedule_time_value']} {self.config_dict['general']['post_process']['schedule_time_key']}', next run at '{schedule_run_converted}'")

    def run(self):

        current_time = siphonator_tools_various.current_time()
        self.logger_instance.info(f"Processing started at '{current_time}'")

        # TODO need to work out if we need this, if we do then how do we get it?
        result_dict = {}

        post_process_instance = post_processing.PostProcessMonitorQueue(self.logger_instance, result_dict, self.config_dict)
        post_process_instance.post_process_monitor_queue()

        # TODO put in elapsed time
        current_time = siphonator_tools_various.current_time()

        self.logger_instance.info(f"Processing finished at '{current_time}'")
        self.schedule_msg()


class SiphonatorMain(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.init_dict = init_dict
        self.config_dict = config_dict

    def schedule_run(self):

        # set to blocking scheduler if set to foreground
        if main_schedule_mode == 'foreground':
            schedule = BlockingScheduler()
        else:
            schedule = BackgroundScheduler()

        self.logger_instance.info(f"Running schedule in '{main_schedule_mode}' mode")

        try:

            schedule.add_job(siphonator_main_instance.run, 'interval', minutes=self.config_dict['general']['main']['schedule_time_value'], next_run_time=datetime.datetime.now())
            schedule.start()

        except (KeyboardInterrupt, SystemExit):

            self.logger_instance.info(u"Keyboard interrupt or system exit detected, shutting down...")
            schedule.shutdown()

    def schedule_msg(self):

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(self.config_dict['general']['main']['schedule_time_value']))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        self.logger_instance.info(f"Schedule running in '{self.config_dict['general']['main']['schedule_mode']}' mode every '{self.config_dict['general']['main']['schedule_time_value']} {self.config_dict['general']['main']['schedule_time_key']}', next run at '{schedule_run_converted}'")

    def run(self):

        current_time = siphonator_tools_various.current_time()
        self.logger_instance.info(f"Processing started at '{current_time}'")

        # walk library path and store in config dict
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)

        # we save it as a list so we can re-use it, as walking is very costly
        library_path_walk = list(tools_various_instance.library_path_walk(self.config_dict['general']['library_path_list']))

        # add library walk to config dict
        self.config_dict.update({
            'library_path_walk': library_path_walk,
        })

        # create sqlite database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict)
        db_sqlite_instance.create_database()

        # upgrade database if required
        db_sqlite_instance.upgrade_database()

        index_proxy = self.config_dict['index_proxy']['selected']
        if index_proxy == 'jackett':

            index_proxy_url = f"http://{self.config_dict['index_proxy']['jackett']['host']}:{self.config_dict['index_proxy']['jackett']['port']}/api/v2.0/indexers/all/results/torznab/api?configured=true&apikey={self.config_dict['index_proxy']['jackett']['api_key']}&t=indexers&q="

            # download list of enabled index sites from jackett
            index_sites_return_code, index_sites_status_code, index_sites_content = siphonator_tools_downloader.http_client(
                self.logger_instance, url=index_proxy_url,
                user_agent=user_agent,
                request_type="get",
                read_timeout=self.config_dict['index_proxy']['jackett']['read_timeout'],
            )

            # ensure jackett is operational by checking for status code 200
            if index_sites_status_code != 200:
                self.logger_instance.warning(f"Unable to access index site '{self.config_dict['index_proxy']['selected']}', retrying in {self.config_dict['general']['schedule_time_value']} minutes")
                return index_sites_status_code

            # parse xml from jackett
            index_sites_xml = elementTree.fromstring(index_sites_content)

        else:

            self.logger_instance.warning(f"Index Proxy option of '{index_proxy}' not supported, exiting...")
            return 1

        # empty dict to store configured index sites
        index_sites_configured_dict = {}
        for i in index_sites_xml:

            index_site_dict = i.attrib
            index_site_configured = index_site_dict['configured']
            index_site_name = index_site_dict['id']

            if index_site_configured == 'true':

                index_sites_configured_dict.update({index_site_name: self.config_dict['index_site']['search']})

        # loop over top level dict of index sites
        for index_site in index_sites_configured_dict:

            index_site_lower = index_site.lower()
            index_site_list_dict = (index_sites_configured_dict[index_site])

            # we may want to ignore certain index sites
            if index_site_lower in self.config_dict['index_site']['ignore_list']:

                self.logger_instance.info(f"Index site '{index_site_lower}' is in index site ignore list '{self.config_dict['index_site']['ignore_list']}'")
                continue

            # loop over dict containing search criteria
            for index_site_dict in index_site_list_dict:

                # add index site to index site dict
                index_site_dict.update({
                    'index_site': index_site,
                })

                # get category overrides for specific index sites
                override_category_dict = self.config_dict.get('index_site', {}).get('override_search', {}).get(index_site_lower, {})

                # if index site is in the override dictionary then proceed
                if override_category_dict:

                    get_index_site_category = override_category_dict.get('category', {})
                    if get_index_site_category:

                        index_site_category = get_index_site_category
                        self.logger_instance.debug(f"Override category found for index site '{index_site_lower}', category set to '{index_site_category}'")

                index_site_instance = siphonator_index_proxy.IndexProxy(self.logger_instance, self.init_dict, self.config_dict, index_site_dict)

                try:
                    index_site_instance.jackett()
                except ImdbAPIError:
                    self.logger_instance.error(u"IMDbPie having issues contacting IMDb")

        # compress (vacuum) database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict)
        db_sqlite_instance.vacuum_database()

        # close database
        db_sqlite_instance.close_database()

        # TODO put in elapsed time
        current_time = siphonator_tools_various.current_time()

        self.logger_instance.info(f"Processing finished at '{current_time}'")
        self.schedule_msg()

    
# required to prevent separate process from trying to load parent process
if __name__ == '__main__':

    # TODO rework readme, out of date config examples now
    # TODO tidy up reading dict currently nasty mash up of .get and dict['key']  - use .get with default of empty dict then do if <var>
    # TODO rename filters with override to preferred so we are consistent
    # TODO rename config.yml genre_minimum_rating_dict to genre_override_dict and allow to override imdb rating AND votes sci-fi should be 6.0, votes should be 4000

    # set versioning for app, config, and db
    app_version = '1.0.0'
    config_version = '1.0.1'
    db_version = int(4)
    user_agent = f"Siphonator/{app_version}; https://github.com/binhex/siphonator"

    app_root_path = os.path.dirname(os.path.realpath(__file__))

    # custom argparse to redirect user to help if unknown argument specified
    class ArgparseCustom(argparse.ArgumentParser):

        def error(self, message):
            sys.stderr.write(f"error: {message}\n")
            self.print_help()
            sys.exit(2)

    parser = ArgparseCustom(
        prog=f"Siphonator v{app_version}",
        description="Welcome to %(prog)s - Coded by binhex.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100)
    )

    parser.add_argument(
        "-lp",
        "--log-path",
        type=str,
        default=os.path.join(app_root_path, 'logs'),
        help="Specify path to store application log files, defaults to '%(default)s'",
    )
    parser.add_argument(
        "-ll",
        "--log-level",
        type=str,
        default='INFO',
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="Specify logging level, defaults to '%(default)s'",
    )
    parser.add_argument(
        "-pp",
        "--pid-path",
        type=str,
        default=os.path.join(app_root_path, 'pid'),
        help="Specify path to store pid file, defaults to '%(default)s'",
    )
    parser.add_argument(
        "-cp",
        "--config-path",
        type=str,
        default=os.path.join(app_root_path, 'configs'),
        help="Specify path to store config file, defaults to '%(default)s'",
    )
    parser.add_argument(
        "-dp",
        "--db-path",
        type=str,
        default=os.path.join(app_root_path, 'db'),
        help="Specify path to store database file, defaults to '%(default)s'",
    )
    parser.add_argument(
        "-fp",
        "--ffprobe-path",
        type=str,
        default=os.path.join(app_root_path, 'tools/ffprobe/static/x64'),
        help="Specify path to ffprobe binary file, defaults to '%(default)s'",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run tests",
    )
    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        help="Run as background daemonized process",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display version",
    )

    # get arguments
    args = parser.parse_args()

    # create path if it doesn't exist and set filepath
    create_path(args.ffprobe_path)
    ffprobe_filepath = os.path.join(args.ffprobe_path, 'ffprobe')

    # create path if it doesn't exist and set filepath
    log_path = args.log_path
    create_path(log_path)
    logs_filepath = os.path.join(log_path, 'siphonator.log')

    # create path if it doesn't exist and set filepath
    db_path = args.db_path
    create_path(db_path)
    db_filepath = os.path.join(db_path, 'siphonator.db')

    # create path if it doesn't exist and set filepath
    pid_path = args.pid_path
    create_path(pid_path)

    # construct pid filepath for main and post processing threads
    pid_main_filepath = os.path.join(pid_path, 'siphonator.pid')
    pid_post_process_filepath = os.path.join(pid_path, 'siphonator-post-process.pid')

    # create path if it doesn't exist and set filepath
    config_path = args.config_path
    create_path(config_path)
    config_filepath = os.path.join(args.config_path, 'config.yml')

    # define initial settings in dict
    init_dict = ({
        'app_version': app_version,
        'app_root_path': app_root_path,
        'log_path': log_path,
        'log_filepath': logs_filepath,
        'pid_path': pid_path,
        'pid_main_filepath': pid_main_filepath,
        'pid_post_process_filepath': pid_post_process_filepath,
        'db_path': db_path,
        'db_filepath': db_filepath,
        'db_version': db_version,
        'config_path': config_path,
        'config_filepath': config_filepath,
        'config_version': config_version,
        'user_agent': user_agent,
        'ffprobe_filepath': ffprobe_filepath,
    })

    # send init_dict and return config_dict read from config.yml
    config_dict = siphonator_config.read_config(init_dict)

    # setup logging
    log_level = config_dict['general']['log_level']
    logger = siphonator_tools_logging.app_logging(log_level, logs_filepath)
    logger_create_instance = logger.get('logger')
    logger_handler = logger.get('handler')

    # read in config version from config file
    config_file_version = config_dict['general']['config_version']

    # update config.yml if required
    siphonator_config.update_config(init_dict, config_file_version)

    # verify config.yml is valid
    # siphonator_config.verify_config(logger_create_instance, init_dict, config_dict)

    # if daemon cli flag defined
    if args.daemon:

        daemon_mode = 'background'

    else:

        # read daemon mode from config
        daemon_mode = config_dict['general']['daemon_mode'].lower()

    if platform.system() == 'Windows':

        # force daemon mode to foreground as windows cannot run daemonized
        daemon_mode = 'foreground'

    # run tests
    if args.test:

        return_code = pytest.main(["--verbose"])
        exit(return_code)

    # setup main scheduler
    main_schedule_mode = config_dict['general']['main']['schedule_mode'].lower()
    main_schedule_time_key = config_dict['general']['main']['schedule_time_key']
    main_schedule_time_value = config_dict['general']['main']['schedule_time_value']

    # setup post process scheduler
    post_process_schedule_mode = config_dict['general']['post_process']['schedule_mode'].lower()
    post_process_schedule_time_key = config_dict['general']['post_process']['schedule_time_key']
    post_process_schedule_time_value = config_dict['general']['post_process']['schedule_time_value']

    logger_create_instance.info(u"Welcome to Siphonator - Coded by binhex.")
    logger_create_instance.info(f"Starting daemon in '{daemon_mode}' mode...")

    # define instances of classes to run
    siphonator_post_process_instance = SiphonatorPostProcess(logger_create_instance)
    siphonator_main_instance = SiphonatorMain(logger_create_instance)

    if daemon_mode == 'background':

        # note when calling method in class for 'action' drop '()'
        # 'keep_fds' prevents daemonize of file descriptors, such as logger, otherwise logging stops
        keep_fds = [logger_handler.stream.fileno()]

        siphonator_post_process = Daemonize(app="siphonator-post-process", pid=pid_post_process_filepath, keep_fds=keep_fds, action=siphonator_post_process_instance.schedule_run)
        siphonator_post_process.start()

        siphonator_main = Daemonize(app="siphonator-main", pid=pid_main_filepath, keep_fds=keep_fds, action=siphonator_main_instance.schedule_run)
        siphonator_main.start()

    else:

        # note when calling method in class for 'action' drop '()'
        siphonator_post_process = Daemonize(app="siphonator-post-process", pid=pid_post_process_filepath, foreground=post_process_schedule_mode, action=siphonator_post_process_instance.schedule_run)
        siphonator_main = Daemonize(app="siphonator-main", pid=pid_main_filepath, foreground=main_schedule_mode, action=siphonator_main_instance.schedule_run)

        try:

            #siphonator_post_process.start()
            siphonator_main.start()

        except (KeyboardInterrupt, SystemExit):

            # cleanup pid file
            siphonator_main.exit()
