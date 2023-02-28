import os
import sys
import configobj
import validate
import argparse

from imdbpie import ImdbAPIError

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
    import lib.siphonator.index_torznab as siphonator_index_torznab
    import lib.siphonator.post_rename as siphonator_post_rename
    import lib.siphonator.tools_logging as siphonator_tools_logging
    import lib.siphonator.search_all as siphonator_search_all

except ImportError:

    # check if app root directory is already on path, if not then append.
    # this is req to allow import of local modules (pex bug):-
    # https://github.com/pantsbuild/pex/issues/340#issuecomment-358775440
    sys.path.append('%s/' % root_dir)

    try:

        import lib.siphonator.imdb_imdbpie as siphonator_imdb_imdbpie
        import lib.siphonator.tools_downloader as siphonator_tools_downloader
        import lib.siphonator.index_torznab as siphonator_index_torznab
        import lib.siphonator.post_rename as siphonator_post_rename
        import lib.siphonator.tools_logging as siphonator_tools_logging
        import lib.siphonator.search_all as siphonator_search_all

    except ImportError:

        print("cannot import Siphonator modules, exiting...")
        sys.exit(1)


# required to prevent separate process from trying to load parent process
if __name__ == '__main__':

    # set siphonator and db schema version numbers
    current_version = "1.0.0"
    latest_db_version = "1"

    app_root_dir = os.path.dirname(os.path.realpath(__file__))

    # set folder path for config files
    config_dir = os.path.join(app_root_dir, u"configs")
    config_dir = os.path.normpath(config_dir)

    # set path for configspec.ini file
    configspec_ini = os.path.join(config_dir, u"configspec.ini")

    # set path for config.ini file
    config_ini = os.path.join(config_dir, u"config.ini")

    # set folder path for log files
    logs_dir = os.path.join(app_root_dir, u"logs")
    logs_dir = os.path.normpath(logs_dir)

    # set path for log file
    log_file = os.path.join(logs_dir, u"siphonator.log")

    # create configobj instance, set config.ini file, set encoding and set configspec.ini file
    config_obj = configobj.ConfigObj(config_ini, list_values=False, write_empty_values=True, encoding='UTF-8', default_encoding='UTF-8', configspec=configspec_ini, unrepr=True)

    # create config.ini
    validator = validate.Validator()
    config_obj.validate(validator, copy=True)
    config_obj.filename = config_ini
    config_obj.write()

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
    commandline_parser = ArgparseCustom(prog="Siphonator", description="%(prog)s " + current_version, usage="%(prog)s [--help] [--config <path>] [--logs <path>] [--pidfile <path>] [--daemon] [--version]", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50))

    # add argparse command line flags
    commandline_parser.add_argument(u"--config", metavar=u"<path>", help=u"specify path for config file e.g. --config /opt/siphonator/config/")
    commandline_parser.add_argument(u"--logs", metavar=u"<path>", help=u"specify path for log files e.g. --logs /opt/siphonator/logs/")
    commandline_parser.add_argument(u"--pidfile", metavar=u"<path>", help=u"specify path to pidfile e.g. --pid /var/run/siphonator/siphonator.pid")
    commandline_parser.add_argument(u"--daemon", action=u"store_true", help=u"run as daemonized process")
    commandline_parser.add_argument(u"--version", action=u"version", version=current_version)

    # save arguments in dictionary
    args = vars(commandline_parser.parse_args())

    # -----------

    logger_instance.info(u"Running...")

    index_site_host = "192.168.1.10"
    index_site_port = "1900"
    index_site_api_key = "o4xte43ftp56m64aknxch4pe7cp3lhaj"
    index_site_read_timeout = 60.0
    index_site_limit = "2000"

    user_agent = u"Siphonator/%s; https://sourceforge.net/projects/moviegrabber" % current_version
    library_path = "/media"

    torrent_client_qbittorrent_host = '192.168.1.10'
    torrent_client_qbittorrent_port = 2100
    torrent_client_qbittorrent_username = 'admin'
    torrent_client_qbittorrent_password = 'adminadmin'

    rarbg_category = '2000'
    rarbg_search = '1080p'

    limetorrents_category = '2000'
    limetorrents_search = '1080p'

    thepiratebay_category = '2000'
    thepiratebay_search = '1080p'

    torrentgalaxy_category = '2000'
    torrentgalaxy_search = '1080p'

    index_site_list = ['rarbg', 'limetorrents', 'thepiratebay', 'torrentgalaxy']

    filter_minimum_year = '2021'
    filter_minimum_runtime_mins = '60'
    filter_bad_index_title_list = ['3d', 'cam', 'hdcam', 'camrip', 'hqcam', 'hdts', 'hc', 'ts', 'telesync', 'german', 'foreign', 'french', 'dutch', 'ger', 'fre', 'ita', 'truehd', 'aac', 'lpcm', 'avc', 'hindi', 'nlsubs', 'season']
    filter_bad_movie_title_list = []

    tmdb_api_key = "1d93addd6def495cec493845cd3b2788"
    omdb_api_key = "bc61f97e"

    for index_site in index_site_list:

        category = '%s_category' % index_site
        search = '%s_search' % index_site

        logger_instance.info(u"Processing index site '%s'..." % index_site)
        index_site_instance = siphonator_index_torznab.IndexTorznab(logger_instance, host=index_site_host, port=index_site_port, api_key=index_site_api_key, category=eval(category), index_site=index_site, search=eval(search), limit=index_site_limit, user_agent=user_agent, read_timeout=index_site_read_timeout, library_path=library_path, torrent_client_qbittorrent_host=torrent_client_qbittorrent_host, torrent_client_qbittorrent_port=torrent_client_qbittorrent_port, torrent_client_qbittorrent_username=torrent_client_qbittorrent_username, torrent_client_qbittorrent_password=torrent_client_qbittorrent_password, filter_minimum_year=filter_minimum_year, tmdb_api_key=tmdb_api_key, omdb_api_key=omdb_api_key, filter_minimum_runtime_mins=filter_minimum_runtime_mins, filter_bad_index_title_list=filter_bad_index_title_list, filter_bad_movie_title_list=filter_bad_movie_title_list)

        try:

            index_site_instance.torznab_download()

        except ImdbAPIError:

            logger_instance.error(u"IMDbPie having issues contacting IMDb")
