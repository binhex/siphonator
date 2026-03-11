import os
import platform
import sys
import argparse
import datetime
import pytest
import time
import qbittorrentapi
import xml.etree.ElementTree as elementTree
from daemonize import Daemonize
from apscheduler.schedulers.background import BackgroundScheduler
import src.siphonator.config_manager as siphonator_config_manager
import src.siphonator.post_processing as post_processing
import src.siphonator.queue_management as queue_management
import src.siphonator.index_proxy as siphonator_index_proxy
import src.siphonator.tools_logging as siphonator_tools_logging
import src.siphonator.tools_various as siphonator_tools_various
import src.siphonator.tools_downloader as siphonator_tools_downloader
import src.siphonator.db_sqlite as siphonator_db_sqlite


def check_python():
    # check version of python is 3.x.x
    python_version = sys.version_info
    if python_version < (3, 11, 0):

        sys.stderr.write(f"WARNING - You need Python 3.11.x or later installed to run {app_name}, your running version '{python_version, }'")
        sys.exit(1)


def create_path(path):

    if not os.path.exists(path):

        try:
            os.makedirs(path)
        except OSError as e:
            print(f"Error creating path '{path}', error is '{e}'")
            return False

    return True


def check_jackett():

    index_proxy = config_dict['index_proxy']['selected']
    if index_proxy != 'jackett':
        return False

    # construct url to jackett
    index_proxy_url = f"http://{config_dict['index_proxy']['jackett']['host']}:{config_dict['index_proxy']['jackett']['port']}/api/v2.0/indexers/all/results/torznab/api?configured=true&apikey={config_dict['index_proxy']['jackett']['api_key']}&t=indexers&q="

    # download list of enabled index sites from jackett
    index_sites_return_code, index_sites_status_code, index_sites_content = siphonator_tools_downloader.http_client(
        logger, url=index_proxy_url,
        user_agent=user_agent,
        request_type="get",
        read_timeout=config_dict['index_proxy']['jackett']['read_timeout'],
    )

    # if jackett status code is not 200 then return false
    if index_sites_status_code != 200:
        logger.warning(f"Unable to access index proxy '{index_proxy}', retrying in {config_dict['schedule']['siphonator_thread']['schedule_time_mins']} minutes")
        return False

    else:

        # parse xml from jackett
        return elementTree.fromstring(index_sites_content)


def check_qbittorrent():

    torrent_client = config_dict['torrent_client']['selected']
    if torrent_client != 'qbittorrent':
        return False

    host = config_dict['torrent_client']['qbittorrent']['host']
    port = config_dict['torrent_client']['qbittorrent']['port']
    username = config_dict['torrent_client']['qbittorrent']['username']
    password = config_dict['torrent_client']['qbittorrent']['password']

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
        result_details = f"{torrent_client} login failed, retrying in {config_dict['schedule']['siphonator_thread']['schedule_time_mins']} minutes"
        logger.warning(result_details)
        return False

    except qbittorrentapi.APIConnectionError:
        result_details = f"{torrent_client} API connection error, retrying in {config_dict['schedule']['siphonator_thread']['schedule_time_mins']} minutes"
        logger.warning(result_details)
        return False

    except qbittorrentapi.APIError:
        result_details = f"{torrent_client} API error, retrying in {config_dict['schedule']['siphonator_thread']['schedule_time_mins']} minutes"
        logger.warning(result_details)
        return False

    return qbt_client


def run_scheduler():
    """
    Function to start the scheduler and keep it running.
    """
    scheduler = BackgroundScheduler()

    # Schedule tasks
    if post_processing_enabled:
        post_processing_instance.schedule_run(scheduler)

    if queue_management_enabled:
        queue_management_instance.schedule_run(scheduler)

    if siphonator_enabled:
        siphonator_instance.schedule_run(scheduler)

    # Start the scheduler
    scheduler.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()


def db_checks():

    # create db instance, this must be created in the same thread as its used, otherwise you will see the error
    # 'SQLite objects created in a thread can only be used in that same thread'
    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(logger, init_dict)

    # get db user version
    pragma_user_version = db_sqlite_instance.get_pragma_user_version()

    # if db filepath is a sqlite database but pragma user version is '0' then create initial tables
    if pragma_user_version == int(0):

        db_sqlite_instance.create_tables()

    # else if pragma user version is not equal to db version (version we want) then upgrade
    elif pragma_user_version != db_version:

        db_sqlite_instance.upgrade_database(pragma_user_version)


class SiphonatorPostProcessing(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.init_dict = init_dict
        self.config_dict = config_dict

    def schedule_run(self, scheduler):

        self.logger_instance.info("Scheduling post-processing task...")
        scheduler.add_job(
            self.run,
            'interval',
            minutes=int(self.config_dict['schedule']['post_processing_thread']['schedule_time_mins']),
            next_run_time=datetime.datetime.now(),
            max_instances=1,
            id="post_processing_task"
        )

    def schedule_msg(self):

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(self.config_dict['schedule']['post_processing_thread']['schedule_time_mins']))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        self.logger_instance.info(f"Schedule for post-processing running in background mode every '{self.config_dict['schedule']['post_processing_thread']['schedule_time_mins']} {self.config_dict['schedule']['post_processing_thread']['schedule_time_units']}', next run at '{schedule_run_converted}'")

    def run(self):

        current_time = siphonator_tools_various.current_time()
        self.logger_instance.info(f"Processing for post-processing started at '{current_time}'")

        qbt_client = check_qbittorrent()

        if not qbt_client:
            return False

        post_processing_run_instance = post_processing.PostProcess(self.logger_instance, self.config_dict, self.init_dict, qbt_client)
        post_processing_run_instance.post_process()

        # TODO put in elapsed time
        current_time = siphonator_tools_various.current_time()

        self.logger_instance.info(f"Processing for post-processing finished at '{current_time}'")
        self.schedule_msg()


class SiphonatorQueueManagement(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.init_dict = init_dict
        self.config_dict = config_dict

    def schedule_run(self, scheduler):

        self.logger_instance.info("Scheduling Queue Management task...")
        scheduler.add_job(
            self.run,
            'interval',
            minutes=int(self.config_dict['schedule']['queue_management_thread']['schedule_time_mins']),
            next_run_time=datetime.datetime.now(),
            max_instances=1,
            id="queue_management_task"
        )

    def schedule_msg(self):

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(self.config_dict['schedule']['queue_management_thread']['schedule_time_mins']))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        self.logger_instance.info(f"Schedule for queue management is running in background mode every '{self.config_dict['schedule']['queue_management_thread']['schedule_time_mins']} {self.config_dict['schedule']['queue_management_thread']['schedule_time_units']}', next run at '{schedule_run_converted}'")

    def run(self):

        current_time = siphonator_tools_various.current_time()
        self.logger_instance.info(f"Processing for queue management started at '{current_time}'")

        qbt_client = check_qbittorrent()

        if not qbt_client:
            return False

        queue_management_run_instance = queue_management.QueueManagement(self.logger_instance, self.config_dict, self.init_dict, qbt_client)
        queue_management_run_instance.queue_management()

        # TODO put in elapsed time
        current_time = siphonator_tools_various.current_time()

        self.logger_instance.info(f"Processing for queue management finished at '{current_time}'")
        self.schedule_msg()


class SiphonatorMain(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.init_dict = init_dict
        self.config_dict = config_dict

    def schedule_run(self, scheduler):

        self.logger_instance.info("Scheduling siphonator task...")
        scheduler.add_job(
            self.run,
            'interval',
            minutes=int(self.config_dict['schedule']['siphonator_thread']['schedule_time_mins']),
            next_run_time=datetime.datetime.now(),
            max_instances=1,
            id="siphonator_task"
        )

    def schedule_msg(self):

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(self.config_dict['schedule']['siphonator_thread']['schedule_time_mins']))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        self.logger_instance.info(f"Schedule for siphonator is running in background mode every '{self.config_dict['schedule']['siphonator_thread']['schedule_time_mins']} {self.config_dict['schedule']['siphonator_thread']['schedule_time_units']}', next run at '{schedule_run_converted}'")

    def run(self):

        current_time = siphonator_tools_various.current_time()
        self.logger_instance.info(f"Processing for siphonator started at '{current_time}'")

        # ensure qbittorrent is operational
        qbt_client = check_qbittorrent()

        if not qbt_client:
            return False

        # ensure jackett is operational
        jackett_index_sites_list_xml = check_jackett()

        if not jackett_index_sites_list_xml:
            return False

        library_path_list = self.config_dict['general']['library_path_list']

        if library_path_list:

            # we save it as a list so we can re-use it, as walking is very costly
            library_path_walk = list(siphonator_tools_various.library_path_walk(library_path_list))

        else:

            library_path_walk = None

        # empty dict to store configured index sites
        index_sites_configured_dict = {}

        # loop over sites defined in xml from jackett
        for jackett_index_site in jackett_index_sites_list_xml:

            jackett_index_site_dict = jackett_index_site.attrib
            jackett_index_site_configured = jackett_index_site_dict['configured']
            jackett_index_site_name = jackett_index_site_dict['id']

            # ensure index site from jackett is set as configured
            if jackett_index_site_configured == 'true':

                # add search criteria from config for each index site from jackett to dict
                index_sites_configured_dict.update({jackett_index_site_name: self.config_dict['index_site']['search']})

        # loop over top level dict of index sites
        for index_site in index_sites_configured_dict:

            # ensure index site name is lowercase for comparison
            index_site_lower = index_site.lower()

            index_site_dict_list = (index_sites_configured_dict[index_site])

            # if index site ignore list is defined then process
            if self.config_dict['index_site']['ignore_list']:

                # ensure config index site ignore list is lowercase for comparison
                config_index_site_ignore_list_lower = [x.lower() for x in self.config_dict['index_site']['ignore_list']]

                # if index site name is in ignore list then skip
                if index_site_lower in config_index_site_ignore_list_lower:

                    self.logger_instance.info(f"Index site '{index_site_lower}' is in index site ignore list '{config_index_site_ignore_list_lower}'")
                    continue

            # loop over dict containing search criteria
            for index_site_dict in index_site_dict_list:

                # add index site name to dict
                index_site_dict.update({
                    'index_site': index_site_lower,
                })

                # get search category
                search_category = index_site_dict['category']

                # get list of index sites with override searches
                override_search_dict = self.config_dict['index_site']['override_search']

                # check if the index site exists in the override dictionary
                if any(override_search_site.lower() == index_site_lower for override_search_site in override_search_dict.keys()):

                    override_search_category = self.config_dict['index_site']['override_search'][index_site_lower]['category']

                    # set category to override category for the specific site
                    index_site_dict.update({
                        'category': override_search_category,
                    })

                    self.logger_instance.info(f"Override category found for index site '{index_site_lower}', category set to '{override_search_category}'")

                else:

                    # if no override found for the index site then set category to search criteria value
                    index_site_dict.update({
                        'category': search_category,
                    })

                index_site_instance = siphonator_index_proxy.IndexProxy(self.logger_instance, self.init_dict, self.config_dict, index_site_dict, library_path_walk, qbt_client)
                index_site_instance.jackett()

                # revert back to the original category if it was overridden
                index_site_dict.update({
                    'category': search_category,
                })

        # create db instance, this must be created in the same thread as its used, otherwise you will see the error
        # 'SQLite objects created in a thread can only be used in that same thread'
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(logger, init_dict)

        # compress (vacuum) database
        db_sqlite_instance.vacuum_database()

        # close database
        db_sqlite_instance.close_database()

        # release memory by clearing walked library path
        del library_path_walk

        # TODO put in elapsed time
        current_time = siphonator_tools_various.current_time()

        self.logger_instance.info(f"Processing for siphonator finished at '{current_time}'")
        self.schedule_msg()


# required to prevent separate process from trying to load parent process
if __name__ == '__main__':

    # TODO rework readme, out of date config examples now
    # TODO tidy up reading dict currently nasty mash up of .get and dict['key']  - use .get with default of empty dict then do if <var>
    # TODO rename filters with override to preferred so we are consistent
    # TODO rename config.yml genre_minimum_rating_dict to genre_override_dict and allow to override imdb rating AND votes sci-fi should be 6.0, votes should be 4000

    # set versioning for app, config, and db
    app_name = 'siphonator'
    app_friendly_name = app_name.capitalize()
    app_version = '0.0.2'
    config_version = '0.0.1'
    db_version = int(6)
    user_agent = f"{app_name}/{app_version}; https://github.com/binhex/{app_name}"

    # ensure we are running python 3.11 or later
    check_python()

    # define root path for app
    app_root_path = os.path.dirname(os.path.realpath(__file__))

    # custom argparse to redirect user to help if unknown argument specified
    class ArgparseCustom(argparse.ArgumentParser):

        def error(self, message):
            sys.stderr.write(f"error: {message}\n")
            self.print_help()
            sys.exit(2)

    parser = ArgparseCustom(
        prog=f"{app_friendly_name} v{app_version}",
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
    logs_filepath = os.path.join(log_path, f'{app_name}.log')

    # create path if it doesn't exist and set filepath
    db_path = args.db_path
    create_path(db_path)
    db_filepath = os.path.join(db_path, f'{app_name}.db')

    # create path if it doesn't exist and set filepath
    pid_path = args.pid_path
    create_path(pid_path)

    # construct pid filepath for main and post-processing threads
    pid_filepath = os.path.join(pid_path, f'{app_name}.pid')

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
        'pid_filepath': pid_filepath,
        'db_path': db_path,
        'db_filepath': db_filepath,
        'db_version': db_version,
        'config_path': config_path,
        'config_filepath': config_filepath,
        'config_version': config_version,
        'user_agent': user_agent,
        'ffprobe_filepath': ffprobe_filepath,
    })

    # TODO WIP create config.yml if it doesnt exist
    # siphonator_config_manager.create_config_file(init_dict)

    # TODO WIP update config.yml if required
    # siphonator_config.update_config(init_dict, config_file_version)

    # send init_dict and return config_dict read from config.yml
    config_dict = siphonator_config_manager.read_config(init_dict)

    # get logging level from config
    log_level_file = config_dict['general']['log_level_file']
    log_level_console = config_dict['general']['log_level_console']

    # get logger and handlers
    logger, file_handler, console_handler = siphonator_tools_logging.app_logging(log_level_file, log_level_console, logs_filepath)

    # read in config version from config file
    config_file_version = config_dict['general']['config_version']

    # perform sqlite db checks and upgrades
    db_checks()

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

    # setup siphonator scheduler
    siphonator_enabled = config_dict['schedule']['siphonator_thread']['enabled']
    siphonator_schedule_time_units = config_dict['schedule']['siphonator_thread']['schedule_time_units']
    siphonator_schedule_time_mins = config_dict['schedule']['siphonator_thread']['schedule_time_mins']

    # setup queue management scheduler
    queue_management_enabled = config_dict['schedule']['queue_management_thread']['enabled']
    queue_management_schedule_time_units = config_dict['schedule']['queue_management_thread']['schedule_time_units']
    queue_management_schedule_time_mins = config_dict['schedule']['queue_management_thread']['schedule_time_mins']

    # setup post-processing scheduler
    post_processing_enabled = config_dict['schedule']['post_processing_thread']['enabled']
    post_processing_schedule_time_units = config_dict['schedule']['post_processing_thread']['schedule_time_units']
    post_processing_schedule_time_mins = config_dict['schedule']['post_processing_thread']['schedule_time_mins']

    # define instances of classes to run
    queue_management_instance = SiphonatorQueueManagement(logger)
    post_processing_instance = SiphonatorPostProcessing(logger)
    siphonator_instance = SiphonatorMain(logger)

    logger.info(f"Welcome to {app_friendly_name} v{app_version} - Coded by binhex.")
    logger.info(f"Running in {daemon_mode} mode...")

    if daemon_mode == 'background':

        # keep logger file descriptors open otherwise logging stops
        keep_fds = [file_handler.stream.fileno(), console_handler.stream.fileno()]

        # remove previous pid file if it was there due to crash
        if os.path.exists(pid_filepath):
            os.remove(pid_filepath)

        # note when calling function/method drop '()'
        daemon = Daemonize(app="siphonator-daemon", pid=pid_filepath, action=run_scheduler, keep_fds=keep_fds)

        try:
            # Run in background mode
            daemon.start()

        except (KeyboardInterrupt, SystemExit):

            # cleanup pid file
            if post_processing_enabled:
                daemon.exit()

    else:

        # Run in foreground mode
        run_scheduler()
