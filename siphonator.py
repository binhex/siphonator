import os
import sys
import configobj
import validate
import argparse
import datetime
import pytest
import xml.etree.ElementTree as elementTree
from imdbpie import ImdbAPIError
from pathlib import Path
from apscheduler.schedulers.background import BlockingScheduler

# check version of python is 3.x.x
python_version = sys.version_info
if python_version < (3, 10, 0):

    sys.stderr.write(f"WARNING - You need Python 3.10.x or later installed to run Siphonator, your running version '{python_version,}'")
    sys.exit(1)

# define path to siphonator root path - required for linux
root_dir = os.path.dirname(os.path.realpath(__file__))

# -------------------- siphonator modules -----------------------------

# check if app root directory is already on path, if not then append.
# this is req to allow import of local modules (pex bug):-
# https://github.com/pantsbuild/pex/issues/340#issuecomment-358775440
sys.path.append('%s/' % root_dir)

import lib.siphonator.index_proxy as siphonator_index_proxy
import lib.siphonator.tools_logging as siphonator_tools_logging
import lib.siphonator.tools_various as siphonator_tools_various
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.db_sqlite as siphonator_db_sqlite

def set_paths(config_arg, config_filename):
    if args[config_arg]:

        pathname = args[config_arg]
        pathname = os.path.normpath(pathname)

    else:

        pathname = os.path.join(app_root_path, config_arg)
        pathname = os.path.normpath(pathname)

    Path(pathname).mkdir(parents=True, exist_ok=True)
    config_filepath = os.path.join(pathname, config_filename)

    return pathname, config_filepath

class Siphonator(object):

    def __init__(self, logger_instance, **kwargs):

        self.logger_instance = logger_instance
        self.config_dict = kwargs
        self.config_ini = self.config_dict['config_ini']
        self.configs_path = self.config_dict['configs_path']
        self.logs_path = self.config_dict['logs_path']
        self.app_root_path = self.config_dict['app_root_path']
        self.schedule_mode = self.config_dict['schedule_mode']
        self.schedule_time_key = self.config_dict['schedule_time_key']
        self.schedule_time_value = self.config_dict['schedule_time_value']
        self.configspec_ini = self.config_dict['configspec_ini']
        self.log_file = self.config_dict['log_file']
        self.db_path = self.config_dict['db_path']
        self.db_filepath = self.config_dict['db_filepath']

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
        self.logger_instance.info(u"Processing started at '%s'" % current_time)

        user_agent = u"Siphonator/%s; https://sourceforge.net/projects/moviegrabber" % current_version

        torrent_client = 'qbittorrent'
        torrent_client_qbittorrent_host = '192.168.1.10'
        torrent_client_qbittorrent_port = 2100
        torrent_client_qbittorrent_username = 'admin'
        torrent_client_qbittorrent_password = 'adminadmin'
        torrent_client_qbittorrent_add_paused = bool(True)

        notification_email_enabled = True
        notification_email_host = 'smtp.gmail.com'
        notification_email_port = 587
        notification_email_enable_tls = True
        notification_email_enable_ssl = False
        notification_email_username = 'paul.eccleston1@gmail.com'
        notification_email_password= 'quzpugkhxvimjwwv'
        notification_email_from_address = 'paul.eccleston1@gmail.com'
        notification_email_to_address= 'paul.eccleston1@gmail.com'

        index_proxy = 'jackett'
        index_proxy_jackett_host = "192.168.1.10"
        index_proxy_jackett_port = "1900"
        index_proxy_jackett_api_key = "o4xte43ftp56m64aknxch4pe7cp3lhaj"
        index_proxy_jackett_read_timeout = 60.0
        index_proxy_jackett_limit = "2000"

        library_path = "/media"
        filter_minimum_year = '1960'
        filter_minimum_runtime_mins = '60'
        filter_genre_minimum_rating_dict = ({'sci-fi': 6.5, 'animation': 5.0})
        filter_minimum_rating = '7.0'
        filter_minimum_votes = int(5000)
        filter_minimum_seeders = int(1)
        filter_bad_index_title_list = [
            '3d', 'cam', 'camrip', 'hdcam', 'hdcamrip', 'iptv', 'hqcam', 'hqcamrip', 'hdts',
            'hdtc', 'hc', 'ts', 'telesync', 'screener', 'mostbet', 'xxx', 'subbed', 'german',
            'foreign', 'danish', 'french', 'spanish', 'italian', 'dutch', 'portuguese',
            'portugues', 'ger', 'fre', 'ita', 'spa', 'lpcm', 'hindi', 'nlsubs', 'xvid',
            'divx', 'japanese', 'chinese', 'ads included', 'multi', 'pl', 'sub', 'dub',
            'dvdscr', 'screener', 'spa', 'dual', 'protected', 'www'
        ]
        filter_good_country_list = ['gb', 'us', 'ca', 'au', 'ie', 'nz']
        filter_good_language_list = ['en']
        filter_bad_movie_title_list = []
        filter_bad_genre_list = ['Musical', 'Music', 'Documentary']
        filter_override_character_list = ['Bridget Jones', 'Shazam', 'James Bond', 'Jack Sparrow', 'Superman']
        filter_override_cast_list = ['Jason Statham']
        filter_override_writer_list = []
        filter_override_director_list = ['Steven Spielberg', 'Stanley Kubrick', 'James Cameron', 'Quentin Tarantino']
        filter_override_movie_title_list = ['Star Trek']

        index_site_ignore_list = ['showrss']
        index_site_ignore_list_lower = [x.lower() for x in index_site_ignore_list]

        index_site_search_1080p_dict = {
            'index_site_search': '1080p',
            'index_site_category': '2000',
            'filter_minimum_size_mb': int(3000),
            'filter_maximum_size_mb': int(20000),
            'filter_minimum_bitrate_mb': int(42)
        }

        index_site_search_2160p_remux_dict = {
            'index_site_search': '2160p remux',
            'index_site_category': '2000',
            'filter_minimum_size_mb': int(30000),
            'filter_maximum_size_mb': int(170000),
            'filter_minimum_bitrate_mb': int(415)
        }

        search_tmdb_api_key = "1d93addd6def495cec493845cd3b2788"
        search_omdb_api_key = "bc61f97e"

        # walk library path and store in results dict, note we save it as a list so we can re-use it (costly)
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
        filter_library_path_walk = list(tools_various_instance.library_path_walk(library_path))

        # begin definition of dictionary to pass around
        index_dict = ({'db_filepath': self.db_filepath, 'db_version': db_version, 'config_ini': self.config_ini})

        # create sqlite database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **index_dict)
        db_sqlite_instance.create_database()

        # upgrade database if required
        db_sqlite_instance.upgrade_database()

        # add in additional info to pass around as dict
        index_dict.update({
            'user_agent': user_agent,
            'library_path': library_path,
            'filter_library_path_walk': filter_library_path_walk,
            'index_proxy_jackett_host': index_proxy_jackett_host,
            'index_proxy_jackett_port': index_proxy_jackett_port,
            'index_proxy_jackett_api_key': index_proxy_jackett_api_key,
            'index_proxy_jackett_limit': index_proxy_jackett_limit,
            'index_proxy_jackett_read_timeout': index_proxy_jackett_read_timeout,
            'torrent_client': torrent_client,
            'torrent_client_qbittorrent_host': torrent_client_qbittorrent_host,
            'torrent_client_qbittorrent_port': torrent_client_qbittorrent_port,
            'torrent_client_qbittorrent_username': torrent_client_qbittorrent_username,
            'torrent_client_qbittorrent_password': torrent_client_qbittorrent_password,
            'torrent_client_qbittorrent_add_paused': torrent_client_qbittorrent_add_paused,
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
            'search_tmdb_api_key': search_tmdb_api_key,
            'search_omdb_api_key': search_omdb_api_key
        })

        # construct url to jackett api to get list of enabled index sites
        url = f'http://{index_proxy_jackett_host}:{index_proxy_jackett_port}/api/v2.0/indexers/all/results/torznab/api?configured=true&apikey={index_proxy_jackett_api_key}&t=indexers&q='

        # download list of enabled index sites from jackett
        index_sites_return_code, index_sites_status_code, index_sites_content = siphonator_tools_downloader.http_client(
            self.logger_instance, url=url,
            user_agent=user_agent,
            request_type="get",
            read_timeout=index_proxy_jackett_read_timeout,
        )

        # ensure jackett is operational by checking for status code 200
        if index_sites_status_code != 200:
            self.logger_instance.warning(f"Unable to access index site '{index_proxy}', retrying in {config_schedule_time_mins} minutes")
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
                index_sites_configured_dict.update({index_site_name: [index_site_search_1080p_dict, index_site_search_2160p_remux_dict]})

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

        if self.schedule_mode == 'foreground':

            self.schedule_msg()

# required to prevent separate process from trying to load parent process
if __name__ == '__main__':

    # set siphonator and db schema version numbers
    current_version = "1.0.0"
    db_version = int(3)

    # custom argparse to redirect user to help if unknown argument specified
    class ArgparseCustom(argparse.ArgumentParser):

        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    # setup argparse description and usage, also increase spacing for help to 50
    commandline_parser = ArgparseCustom(prog="Siphonator", description="Welcome to %(prog)s - Coded by binhex." + current_version, usage="%(prog)s [--help] [--config <path>] [--logs <path>] [--pidfile <path>] [--daemon] [--version]", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

    # add argparse command line flags
    commandline_parser.add_argument(u"--test", action=u"store_true", help=u"run tests")
    commandline_parser.add_argument(u"--configs", metavar=u"<path>", help=u"specify path for config file e.g. --configs /opt/siphonator/config/")
    commandline_parser.add_argument(u"--logs", metavar=u"<path>", help=u"specify path for log files e.g. --logs /opt/siphonator/logs/")
    commandline_parser.add_argument(u"--db", metavar=u"<path>", help=u"specify path for sqlite database e.g. --db /opt/siphonator/db/")
    commandline_parser.add_argument(u"--pidfile", metavar=u"<path>", help=u"specify path to pidfile e.g. --pid /var/run/siphonator/siphonator.pid")
    commandline_parser.add_argument(u"--daemon", action=u"store_true", help=u"run as daemonized process")
    commandline_parser.add_argument(u"--version", action=u"version", version=current_version)

    # save arguments in dictionary
    args = vars(commandline_parser.parse_args())

    if args['test']:

        return_code = pytest.main(["--verbose"])
        exit(return_code)

    config_schedule_mode = 'foreground'
    config_schedule_time_key = 'minutes'
    config_schedule_time_mins = 30

    app_root_path = os.path.dirname(os.path.realpath(__file__))

    # set folder paths and filepaths
    configs_path, configs_filepath = set_paths('configs', 'config.ini')
    logs_path, logs_filepath = set_paths('logs', 'siphonator.log')
    db_path, db_filepath = set_paths('db', 'siphonator.db')

    configspec_filepath = os.path.join(configs_path, u"configspec.ini")

    # create configobj instance, set config.ini file, set encoding and set configspec.ini file
    config_obj = configobj.ConfigObj(configs_filepath, list_values=False, write_empty_values=True, encoding='UTF-8',
                                     default_encoding='UTF-8', configspec=configspec_filepath, unrepr=True)

    # create config.ini
    validator = validate.Validator()
    config_obj.validate(validator, copy=True)
    config_obj.filename = configs_filepath
    config_obj.write()

    logger = siphonator_tools_logging.app_logging(config_obj, logs_filepath)
    logger_create_instance = logger.get('logger')
    logger_handler = logger.get('handler')

    # send schedule details
    run_dict = ({
        'schedule_mode': config_schedule_mode,
        'schedule_time_key': config_schedule_time_key,
        'schedule_time_value': config_schedule_time_mins,
        'config_schedule_mode': config_schedule_mode,
        'config_ini': configs_filepath,
        'configs_path': configs_path,
        'app_root_path': app_root_path,
        'logs_path': logs_path,
        'configspec_ini': configspec_filepath,
        'log_file': logs_filepath,
        'db_path': db_path,
        'db_filepath': db_filepath
    })

    logger_create_instance.info(u"Welcome to Siphonator - Coded by binhex.")

    siphonator_instance = Siphonator(logger_create_instance, **run_dict)
    if config_schedule_mode == 'foreground':
        # run on schedule foreground blocking, note ext run is now
        schedule = BlockingScheduler()
        schedule.add_job(siphonator_instance.run, 'interval', minutes=config_schedule_time_mins, next_run_time=datetime.datetime.now())
        schedule.start()
