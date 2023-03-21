import os
import sys
import configobj
import validate
import argparse
import datetime

from imdbpie import ImdbAPIError
from apscheduler.schedulers.background import BlockingScheduler

# define path to siphonator root path - required for linux
root_dir = os.path.dirname(os.path.realpath(__file__))

python_version = sys.version_info

# check version of python is 3.x.x
if python_version < (3, 0, 0):

    sys.stderr.write("WARNING - You need Python 3.x.x installed to run Siphonator, your running version %s" % (python_version,))
    sys.exit(1)

# -------------------- siphonator modules -----------------------------

try:

    import lib.siphonator.imdb_imdbpie as siphonator_imdb_imdbpie
    import lib.siphonator.tools_downloader as siphonator_tools_downloader
    import lib.siphonator.index_proxy as siphonator_index_proxy
    import lib.siphonator.post_processing as siphonator_post_rename
    import lib.siphonator.tools_logging as siphonator_tools_logging
    import lib.siphonator.tools_various as siphonator_tools_various
    import lib.siphonator.search_all as siphonator_search_all
    import lib.siphonator.db_sqlite as siphonator_db_sqlite

except ImportError:

    # TODO better solution than this
    # check if app root directory is already on path, if not then append.
    # this is req to allow import of local modules (pex bug):-
    # https://github.com/pantsbuild/pex/issues/340#issuecomment-358775440
    sys.path.append('%s/' % root_dir)

    try:

        import lib.siphonator.imdb_imdbpie as siphonator_imdb_imdbpie
        import lib.siphonator.tools_downloader as siphonator_tools_downloader
        import lib.siphonator.index_proxy as siphonator_index_proxy
        import lib.siphonator.post_processing as siphonator_post_rename
        import lib.siphonator.tools_logging as siphonator_tools_logging
        import lib.siphonator.tools_various as siphonator_tools_various
        import lib.siphonator.search_all as siphonator_search_all
        import lib.siphonator.db_sqlite as siphonator_db_sqlite

    except ImportError:

        print("cannot import Siphonator modules, exiting...")
        sys.exit(1)


class Siphonator(object):

    def __init__(self, logger_instance, **kwargs):

        self.config_dict = kwargs
        self.logger_instance = logger_instance

    def schedule_msg(self):

        schedule_mode = self.config_dict['schedule_mode']
        schedule_time_key = self.config_dict['schedule_time_key']
        schedule_time_value = self.config_dict['schedule_time_value']

        # datetime object containing current date and time
        schedule_current_date_and_time = datetime.datetime.now()

        # add in minutes till next schedule
        next_schedule_run = schedule_current_date_and_time + datetime.timedelta(minutes=int(schedule_time_value))

        # convert to human-readable format dd/mm/YY H:M:S
        schedule_run_converted = next_schedule_run.strftime("%d/%m/%Y %H:%M:%S")

        logger_instance.info(u"Schedule running in '%s' mode every '%s %s', next run at '%s'" % (schedule_mode, schedule_time_value, schedule_time_key, schedule_run_converted))

    def current_time(self):

        # datetime object containing current date and time
        run_current_date_and_time = datetime.datetime.now()

        # convert to human-readable format dd/mm/YY H:M:S
        run_current_date_and_time_converted = run_current_date_and_time.strftime("%d/%m/%Y %H:%M:%S")
        return run_current_date_and_time_converted

    def run(self):

        config_schedule_mode = self.config_dict['config_schedule_mode']

        current_time = self.current_time()
        logger_instance.info(u"Processing started at '%s'" % current_time)

        user_agent = u"Siphonator/%s; https://sourceforge.net/projects/moviegrabber" % current_version

        # begin definition of dictionary to pass around
        index_dict = ({'db_filepath': db_filepath, 'db_version': db_version, 'config_ini': config_ini})

        # create sqlite database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(logger_instance, **index_dict)
        db_sqlite_instance.create_database()

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

        index_proxy_jackett_host = "192.168.1.10"
        index_proxy_jackett_port = "1900"
        index_proxy_jackett_api_key = "o4xte43ftp56m64aknxch4pe7cp3lhaj"
        index_proxy_jackett_read_timeout = 60.0
        index_proxy_jackett_limit = "2000"

        # TODO need different libray path depending on search criteria, e.g. 1080p vs 2160p
        library_path = "/media"
        filter_minimum_year = '1960'
        filter_minimum_runtime_mins = '60'
        filter_genre_minimum_rating_dict = ({'sci-fi': 6.5, 'animation': 5.5, 'romance': 6.5, 'comedy': 6.5})
        filter_minimum_rating = '7.0'
        filter_minimum_votes = int(7500)
        filter_minimum_seeders = int(1)
        filter_bad_index_title_list = [
            '3d', 'cam', 'camrip', 'hdcam', 'hdcamrip', 'iptv', 'hqcam', 'hqcamrip', 'hdts',
            'hdtc', 'hc', 'ts', 'telesync', 'screener', 'mostbet', 'xxx', 'subbed', 'german',
            'foreign', 'danish', 'french', 'spanish', 'italian', 'dutch', 'portuguese',
            'portugues', 'ger', 'fre', 'ita', 'spa', 'lpcm', 'hindi', 'nlsubs', 'xvid',
            'divx', 'japanese', 'chinese', 'ads included', 'multi', 'pl', 'sub', 'dub',
            'dvdscr', 'screener'
        ]
        filter_good_language_list = ['en']
        filter_bad_movie_title_list = []
        filter_override_character_list = ['bridget jones']

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
        tools_various_instance = siphonator_tools_various.ToolsVarious(logger_instance)
        filter_library_path_walk = list(tools_various_instance.library_path_walk(library_path))

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
            'filter_bad_index_title_list': filter_bad_index_title_list,
            'filter_good_language_list': filter_good_language_list,
            'filter_override_character_list': filter_override_character_list,
            'filter_bad_movie_title_list': filter_bad_movie_title_list,
            'search_tmdb_api_key': search_tmdb_api_key,
            'search_omdb_api_key': search_omdb_api_key
        })

        index_site_dict_list_dict = {
            'rarbg': [index_site_search_1080p_dict, index_site_search_2160p_remux_dict],
            'thepiratebay': [index_site_search_1080p_dict],
            'torrentgalaxy': [index_site_search_1080p_dict],
            'knaben': [index_site_search_1080p_dict],
            'solidtorrents': [index_site_search_1080p_dict]
        }

        # loop over top level dict of index sites
        for index_site in index_site_dict_list_dict:

            index_site_list_dict = (index_site_dict_list_dict[index_site])

            # loop over dict containing search criteria
            for index_site_dict in index_site_list_dict:

                index_site_search = (index_site_dict['index_site_search'])
                index_site_category = (index_site_dict['index_site_category'])
                filter_minimum_size_mb = (index_site_dict['filter_minimum_size_mb'])
                filter_maximum_size_mb = (index_site_dict['filter_maximum_size_mb'])
                filter_minimum_bitrate_mb = (index_site_dict['filter_minimum_bitrate_mb'])

                # override category for solidtorrents as it incorrectly uses tv category (5000) for movies
                if index_site == "solidtorrents":

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

                logger_instance.info(u"Processing index site '%s' for search criteria '%s' in category '%s'..." % (index_site, index_site_search, index_site_category))
                index_site_instance = siphonator_index_proxy.IndexProxy(logger_instance, **index_dict)

                try:
                    index_site_instance.jackett()
                except ImdbAPIError:
                    logger_instance.error(u"IMDbPie having issues contacting IMDb")

        # compress (vacuum) database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(logger_instance, **index_dict)
        db_sqlite_instance.vacuum_database()

        # close database
        db_sqlite_instance = siphonator_db_sqlite.DbSqlite(logger_instance, **index_dict)
        db_sqlite_instance.close_database()

        # TODO put in elapsed time
        current_time = self.current_time()
        logger_instance.info(u"Processing finished at '%s'" % current_time)

        if config_schedule_mode == 'foreground':

            self.schedule_msg()

# required to prevent separate process from trying to load parent process
if __name__ == '__main__':

    # set siphonator and db schema version numbers
    current_version = "1.0.0"
    db_version = int(1)

    app_root_path = os.path.dirname(os.path.realpath(__file__))

    # set folder path for config files
    config_path = os.path.join(app_root_path, u"configs")
    config_path = os.path.normpath(config_path)

    # set path for configspec.ini file
    configspec_ini = os.path.join(config_path, u"configspec.ini")

    # set path for config.ini file
    config_ini = os.path.join(config_path, u"config.ini")

    # create configobj instance, set config.ini file, set encoding and set configspec.ini file
    config_obj = configobj.ConfigObj(config_ini, list_values=False, write_empty_values=True, encoding='UTF-8', default_encoding='UTF-8', configspec=configspec_ini, unrepr=True)

    # create config.ini
    validator = validate.Validator()
    config_obj.validate(validator, copy=True)
    config_obj.filename = config_ini
    config_obj.write()

    # set folder path for log files
    logs_path = os.path.join(app_root_path, u"logs")
    logs_path = os.path.normpath(logs_path)

    # set folder path for db files
    db_path = os.path.join(app_root_path, u"db")
    db_path = os.path.normpath(db_path)
    db_filepath = os.path.join(db_path, u"siphonator.db")

    # set path for log file
    log_file = os.path.join(logs_path, u"siphonator.log")

    logger = siphonator_tools_logging.app_logging(config_obj, log_file)
    logger_instance = logger.get('logger')
    logger_handler = logger.get('handler')

    # custom argparse to redirect user to help if unknown argument specified
    class ArgparseCustom(argparse.ArgumentParser):

        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    # setup argparse description and usage, also increase spacing for help to 50
    commandline_parser = ArgparseCustom(prog="Siphonator", description="Welcome to %(prog)s - Coded by binhex." + current_version, usage="%(prog)s [--help] [--config <path>] [--logs <path>] [--pidfile <path>] [--daemon] [--version]", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

    # add argparse command line flags
    commandline_parser.add_argument(u"--config", metavar=u"<path>", help=u"specify path for config file e.g. --config /opt/siphonator/config/")
    commandline_parser.add_argument(u"--logs", metavar=u"<path>", help=u"specify path for log files e.g. --logs /opt/siphonator/logs/")
    commandline_parser.add_argument(u"--pidfile", metavar=u"<path>", help=u"specify path to pidfile e.g. --pid /var/run/siphonator/siphonator.pid")
    commandline_parser.add_argument(u"--daemon", action=u"store_true", help=u"run as daemonized process")
    commandline_parser.add_argument(u"--version", action=u"version", version=current_version)

    # save arguments in dictionary
    args = vars(commandline_parser.parse_args())

    config_schedule_mode = 'foreground'
    config_schedule_time_key = 'minutes'
    config_schedule_time_value = '30'

    # send schedule details
    run_dict = ({
        'schedule_mode': config_schedule_mode,
        'schedule_time_key': config_schedule_time_key,
        'schedule_time_value': config_schedule_time_value,
        'config_schedule_mode': config_schedule_mode
    })

    run_instance = Siphonator(logger_instance, **run_dict)

    logger_instance.info(u"Welcome to Siphonator - Coded by binhex.")

    if config_schedule_mode == 'foreground':

        # run on schedule foreground blocking, note will run on startup
        schedule = BlockingScheduler()
        schedule.add_job(run_instance.run, 'interval', minutes=30, next_run_time = datetime.datetime.now())
        schedule.start()

    #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))