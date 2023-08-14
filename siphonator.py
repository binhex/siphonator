import os
import platform
import sys
import argparse
import datetime
import pytest
import yaml
import xml.etree.ElementTree as elementTree
from imdbpie import ImdbAPIError
from daemonize import Daemonize
from apscheduler.schedulers.background import BlockingScheduler

# check version of python is 3.x.x
python_version = sys.version_info
if python_version < (3, 10, 0):

    sys.stderr.write(f"WARNING - You need Python 3.10.x or later installed to run Siphonator, your running version '{python_version,}'")
    sys.exit(1)

# define path to siphonator root path - required for linux
root_dir = os.path.dirname(os.path.realpath(__file__))

# -------------------- siphonator modules -----------------------------
# this is req to allow import of local modules (pex bug):-
# https://github.com/pantsbuild/pex/issues/340#issuecomment-358775440
sys.path.append('%s/' % root_dir)

import lib.siphonator.index_proxy as siphonator_index_proxy
import lib.siphonator.tools_logging as siphonator_tools_logging
import lib.siphonator.tools_various as siphonator_tools_various
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.db_sqlite as siphonator_db_sqlite


def set_paths(config_param, config_path):

    full_path = os.path.join(app_root_path, config_path)

    if args[config_param]:

        if not os.path.exists(args[config_path]):

            try:
                os.makedirs(args[config_path])
            except OSError as e:
                print(f"Error setting '--{config_param}' path to '{args[config_path]}', error is '{e}', using default location '{full_path}'")
            else:
                full_path = args[config_param]

        else:

            full_path = args[config_param]

    return full_path


class Siphonator(object):

    def __init__(self, logger_instance, **kwargs):

        self.logger_instance = logger_instance
        self.config_dict = kwargs
        self.logs_path = self.config_dict['logs_path']
        self.app_root_path = self.config_dict['app_root_path']
        self.schedule_mode = self.config_dict['schedule_mode']
        self.schedule_time_key = self.config_dict['schedule_time_key']
        self.schedule_time_value = self.config_dict['schedule_time_value']
        self.log_file = self.config_dict['log_file']
        self.db_path = self.config_dict['db_path']
        self.db_filepath = self.config_dict['db_filepath']
        self.config_yaml = self.config_dict['config_yaml']

    def schedule_run(self):

        schedule = BlockingScheduler()
        self.logger_instance.info(f"Running schedule in '{config_schedule_mode}' mode")

        try:

            schedule.add_job(siphonator_instance.run, 'interval', minutes=config_schedule_time_value, next_run_time=datetime.datetime.now())
            schedule.start()

        except (KeyboardInterrupt, SystemExit):

            self.logger_instance.info(u"Keyboard interrupt or system exit detected, shutting down...")
            schedule.shutdown()

    def schedule_msg(self):

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(self.schedule_time_value))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        self.logger_instance.info(u"Schedule running in '%s' mode every '%s %s', next run at '%s'" % (self.schedule_mode, self.schedule_time_value, self.schedule_time_key, schedule_run_converted))

    def run(self):

        current_time = siphonator_tools_various.current_time()
        self.logger_instance.info(f"Processing started at '{current_time}'")

        user_agent = f"Siphonator/{current_version}; https://github.com/binhex/siphonator"

        torrent_client = config_yaml['torrent_client']['selected']
        if torrent_client == 'qbittorrent':

            torrent_client_host = config_yaml['torrent_client']['qbittorrent']['host']
            torrent_client_port = config_yaml['torrent_client']['qbittorrent']['port']
            torrent_client_username = config_yaml['torrent_client']['qbittorrent']['username']
            torrent_client_password = config_yaml['torrent_client']['qbittorrent']['password']
            torrent_client_add_paused = config_yaml['torrent_client']['qbittorrent']['add_paused']
            torrent_client_category = config_yaml['torrent_client']['qbittorrent']['category']

        else:

            torrent_client_host = None
            torrent_client_port = None
            torrent_client_username = None
            torrent_client_password = None
            torrent_client_add_paused = None
            torrent_client_category = None

        index_proxy = config_yaml['index_proxy']['selected']
        if index_proxy == 'jackett':

            index_proxy_host = config_yaml['index_proxy']['jackett']['host']
            index_proxy_port = config_yaml['index_proxy']['jackett']['port']
            index_proxy_api_key = config_yaml['index_proxy']['jackett']['api_key']
            index_proxy_read_timeout = config_yaml['index_proxy']['jackett']['read_timeout']
            index_proxy_limit = config_yaml['index_proxy']['jackett']['limit']

        else:

            index_proxy_host = None
            index_proxy_port = None
            index_proxy_api_key = None
            index_proxy_read_timeout = None
            index_proxy_limit = None

        notification_email_enabled = config_yaml['notification']['email']['enabled']
        if notification_email_enabled:

            notification_email_host = config_yaml['notification']['email']['host']
            notification_email_port = config_yaml['notification']['email']['port']
            notification_email_enable_tls = config_yaml['notification']['email']['enable_tls']
            notification_email_enable_ssl = config_yaml['notification']['email']['enable_ssl']
            notification_email_username = config_yaml['notification']['email']['username']
            notification_email_password = config_yaml['notification']['email']['password']
            notification_email_from_address = config_yaml['notification']['email']['from_address']
            notification_email_to_address = config_yaml['notification']['email']['to_address']

        else:

            notification_email_host = None
            notification_email_port = None
            notification_email_enable_tls = None
            notification_email_enable_ssl = None
            notification_email_username = None
            notification_email_password = None
            notification_email_from_address = None
            notification_email_to_address = None

        library_path = config_yaml['general']['library_path']
        filter_minimum_year = config_yaml['filters']['minimum_year']
        filter_minimum_runtime_mins = config_yaml['filters']['minimum_runtime_mins']
        filter_genre_minimum_rating_dict = config_yaml['filters']['genre_minimum_rating_dict']
        filter_minimum_rating = config_yaml['filters']['minimum_rating']
        filter_minimum_votes = config_yaml['filters']['minimum_votes']
        filter_minimum_seeders = config_yaml['filters']['minimum_seeders']
        filter_bad_index_title_list = config_yaml["filters"]['bad_index_title_list']
        filter_preferred_index_group_list = config_yaml["filters"]['preferred_index_group_list']
        filter_override_character_list = config_yaml["filters"]['override_character_list']

        filter_good_country_list = config_yaml["filters"]['good_country_list']
        filter_good_language_list = config_yaml["filters"]['good_language_list']
        filter_bad_movie_title_list = config_yaml["filters"]['bad_movie_title_list']
        filter_bad_genre_list = config_yaml["filters"]['bad_genre_list']
        filter_override_cast_list = config_yaml["filters"]['override_cast_list']
        filter_override_writer_list = config_yaml["filters"]['override_writer_list']
        filter_override_director_list = config_yaml["filters"]['override_director_list']
        filter_override_movie_title_list = config_yaml["filters"]['override_movie_title_list']
        filter_preferred_index_quality_list = config_yaml["filters"]['preferred_index_quality_list']

        search_tmdb_api_key = config_yaml["credentials"]['tmdb']['api_key']
        search_omdb_api_key = config_yaml["credentials"]['omdb']['api_key']

        index_site_search_dict_list = config_yaml["index_site"]['search_dict_list']
        index_site_ignore_list = config_yaml["index_site"]['ignore_list']
        index_site_ignore_list_lower = [x.lower() for x in index_site_ignore_list]

        # walk library path and store in results dict, note we save it as a list so we can re-use it (costly)
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
        filter_library_path_walk = list(tools_various_instance.library_path_walk(library_path))

        # begin definition of dictionary to pass around
        index_dict = ({'db_filepath': self.db_filepath, 'db_version': db_version, 'config_yaml': self.config_yaml})

        # create sqlite database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **index_dict)
        db_sqlite_instance.create_database()

        # upgrade database if required
        db_sqlite_instance.upgrade_database()

        # add in additional info to pass around as dict
        index_dict.update({
            'user_agent': user_agent,
            'ffprobe_filepath': ffprobe_filepath,
            'library_path': library_path,
            'filter_library_path_walk': filter_library_path_walk,
            'index_proxy': index_proxy,
            'index_proxy_host': index_proxy_host,
            'index_proxy_port': index_proxy_port,
            'index_proxy_api_key': index_proxy_api_key,
            'index_proxy_limit': index_proxy_limit,
            'index_proxy_read_timeout': index_proxy_read_timeout,
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
            'search_omdb_api_key': search_omdb_api_key
        })

        # construct url to jackett api to get list of enabled index sites
        url = f'http://{index_proxy_host}:{index_proxy_port}/api/v2.0/indexers/all/results/torznab/api?configured=true&apikey={index_proxy_api_key}&t=indexers&q='

        # download list of enabled index sites from jackett
        index_sites_return_code, index_sites_status_code, index_sites_content = siphonator_tools_downloader.http_client(
            self.logger_instance, url=url,
            user_agent=user_agent,
            request_type="get",
            read_timeout=index_proxy_read_timeout,
        )

        # ensure jackett is operational by checking for status code 200
        if index_sites_status_code != 200:
            self.logger_instance.warning(f"Unable to access index site '{index_proxy}', retrying in {config_schedule_time_value} minutes")
            return index_sites_status_code

        # parse xml from jackett
        index_sites_xml = elementTree.fromstring(index_sites_content)

        # empty dict to store configured index sites
        index_sites_configured_dict = {}
        for i in index_sites_xml:

            index_site_dict = i.attrib
            index_site_configured = index_site_dict['configured']
            index_site_name = index_site_dict['id']

            if index_site_configured == 'true':

                index_sites_configured_dict.update({index_site_name: index_site_search_dict_list})

        # loop over top level dict of index sites
        for index_site in index_sites_configured_dict:

            index_site_lower = index_site.lower()
            index_site_list_dict = (index_sites_configured_dict[index_site])

            # loop over dict containing search criteria
            for index_site_dict in index_site_list_dict:

                index_site_search = (index_site_dict['index_site_search'])
                index_site_category = (index_site_dict['index_site_category'])
                filter_minimum_size_mb = (index_site_dict['filter_minimum_size_mb'])
                filter_maximum_size_mb = (index_site_dict['filter_maximum_size_mb'])
                filter_minimum_bitrate_mb = (index_site_dict['filter_minimum_bitrate_mb'])

                # we may want to ignore certain index sites
                if index_site_lower in index_site_ignore_list_lower:

                    self.logger_instance.info(f"Index site '{index_site_lower}' is in index site ignore list '{index_site_ignore_list_lower}', skipping processing...")
                    continue

                # override category for solidtorrents as it incorrectly uses tv category (5000) for movies
                if index_site_lower == "solidtorrents":

                    index_site_category = '5000'

                # update dict with index site specific search criteria
                index_dict.update({
                    'index_site': index_site,
                    'index_site_category': index_site_category,
                    'index_site_search': index_site_search,
                    'filter_minimum_size_mb': filter_minimum_size_mb,
                    'filter_maximum_size_mb': filter_maximum_size_mb,
                    'filter_minimum_bitrate_mb': filter_minimum_bitrate_mb
                })

                self.logger_instance.info(u"Processing index site '%s' for search criteria '%s' in category '%s'..." % (index_site, index_site_search, index_site_category))
                index_site_instance = siphonator_index_proxy.IndexProxy(self.logger_instance, **index_dict)

                try:
                    index_site_instance.jackett()
                except ImdbAPIError:
                    self.logger_instance.error(u"IMDbPie having issues contacting IMDb")

        # compress (vacuum) database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **index_dict)
        db_sqlite_instance.vacuum_database()

        # close database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **index_dict)
        db_sqlite_instance.close_database()

        # TODO put in elapsed time
        current_time = siphonator_tools_various.current_time()

        self.logger_instance.info(u"Processing finished at '%s'" % current_time)
        self.schedule_msg()


def read_config(config_filepath):

    with open(config_filepath, "r") as config_file:
        config_yaml_load = yaml.safe_load(config_file)

    return config_yaml_load


# required to prevent separate process from trying to load parent process
if __name__ == '__main__':

    # set siphonator and db schema version numbers
    current_version = "1.0.0"
    db_version = int(4)

    # custom argparse to redirect user to help if unknown argument specified
    class ArgparseCustom(argparse.ArgumentParser):

        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    app_root_path = os.path.dirname(os.path.realpath(__file__))

    # setup argparse description and usage, also increase spacing for help to 50
    commandline_parser = ArgparseCustom(prog="Siphonator", description="Welcome to %(prog)s - Coded by binhex." + current_version, usage="%(prog)s [--help] [--config <path>] [--logs <path>] [--pidfile <path>] [--daemon] [--version]", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

    # add argparse command line flags
    commandline_parser.add_argument(u"--test", action=u"store_true", help=u"run tests")
    commandline_parser.add_argument(u"--logs", metavar=u"<path>", help=u"specify path for log files e.g. --logs /opt/siphonator/logs/")
    commandline_parser.add_argument(u"--configs", metavar=u"<path>", help=u"specify path for config file e.g. --configs /opt/siphonator/config/")
    commandline_parser.add_argument(u"--db", metavar=u"<path>", help=u"specify path for sqlite database e.g. --db /opt/siphonator/db/")
    commandline_parser.add_argument(u"--ffprobe", metavar=u"<path>", help=u"specify path for ffprobe binary e.g. --ffprobe /usr/lib/ffprobe/")
    commandline_parser.add_argument(u"--pid", metavar=u"<path>", help=u"specify path to pidfile e.g. --pid /var/run/siphonator/")
    commandline_parser.add_argument(u"--daemon", action=u"store_true", help=u"run as background daemonized process")
    commandline_parser.add_argument(u"--version", action=u"version", version=current_version)

    # save arguments in dictionary
    args = vars(commandline_parser.parse_args())

    # run tests
    if args['test']:

        return_code = pytest.main(["--verbose"])
        exit(return_code)

    # set path using app location or if specified use argument path
    ffprobe_path = set_paths('ffprobe', 'tools/ffprobe/static/x64')
    ffprobe_filepath = os.path.join(ffprobe_path, 'ffprobe')

    # set path using app location or if specified use argument path
    logs_path = set_paths('logs', 'logs')
    logs_filepath = os.path.join(logs_path, 'siphonator.log')

    # set path using app location or if specified use argument path
    db_path = set_paths('db', 'db')
    db_filepath = os.path.join(db_path, 'siphonator.db')

    # set path using app location or if specified use argument path
    pid_path = set_paths('pid', 'pid')
    pid_filepath = os.path.join(pid_path, 'process.pid')

    # set path using app location or if specified use argument path
    configs_path = set_paths('configs', 'configs')
    configs_filepath = os.path.join(configs_path, 'config.yml')

    # read in config file
    config_yaml = read_config(configs_filepath)

    # setup logging
    log_level = config_yaml['general']['log_level']
    logger = siphonator_tools_logging.app_logging(log_level, logs_filepath)
    logger_create_instance = logger.get('logger')
    logger_handler = logger.get('handler')

    # if daemon cli flag defined
    if args['daemon']:

        if platform.system() == 'Windows':

            # force daemon mode to foreground as windows cannot run daemonized
            config_daemon_mode = 'foreground'

        else:

            config_daemon_mode = 'background'

    else:

        # read daemon mode from config
        config_daemon_mode = config_yaml['general']['daemon_mode']
        config_daemon_mode = config_daemon_mode.lower()

    # setup scheduler
    config_schedule_mode = 'foreground'
    config_schedule_time_key = config_yaml['general']['schedule_time_key']
    config_schedule_time_value = config_yaml['general']['schedule_time_value']

    # define initial settings in dict
    run_dict = ({
        'schedule_mode': config_schedule_mode,
        'schedule_time_key': config_schedule_time_key,
        'schedule_time_value': config_schedule_time_value,
        'config_schedule_mode': config_schedule_mode,
        'app_root_path': app_root_path,
        'logs_path': logs_path,
        'log_file': logs_filepath,
        'db_path': db_path,
        'db_filepath': db_filepath,
        'config_yaml': config_yaml,
    })

    logger_create_instance.info(u"Welcome to Siphonator - Coded by binhex.")
    logger_create_instance.info(f"Starting daemon in '{config_daemon_mode}' mode...")

    siphonator_instance = Siphonator(logger_create_instance, **run_dict)
    if config_daemon_mode == 'background':

        # note when calling method in class for 'action' drop '()'
        # 'keep_fds' prevents daemonize of file descriptors, such as logger, otherwise logging stops
        keep_fds = [logger_handler.stream.fileno()]
        daemon = Daemonize(app="siphonator", pid=pid_filepath, keep_fds=keep_fds, action=siphonator_instance.schedule_run)
        daemon.start()

    else:

        # note when calling method in class for 'action' drop '()'
        daemon = Daemonize(app="siphonator", pid=pid_filepath, foreground=True, action=siphonator_instance.schedule_run)
        try:

            daemon.start()

        except (KeyboardInterrupt, SystemExit):

            # cleanup pid file
            daemon.exit()
