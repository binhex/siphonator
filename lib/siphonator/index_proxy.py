import xmltodict
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_filters as siphonator_tools_filters
import lib.siphonator.search_all as siphonator_search_all
import lib.siphonator.imdb_imdbpie as siphonator_imdb_imdbpie
import lib.siphonator.imdb_omdb as siphonator_imdb_omdb
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.torrent_clients as siphonator_torrent_clients
import lib.siphonator.notification_email as siphonator_notification_email
import lib.siphonator.db_sqlite as siphonator_db_sqlite


class IndexProxy(object):

    def __init__(self, logger_instance, init_dict, config_dict, index_site_dict, library_path_walk, qbt_client):

        self.init_dict = init_dict
        self.config_dict = config_dict
        self.index_site_dict = index_site_dict
        self.logger_instance = logger_instance
        self.library_path_walk = library_path_walk
        self.qbt_client = qbt_client

    def jackett(self):

        self.logger_instance.info(f"Processing index site '{self.index_site_dict['index_site']}' for search criteria '{self.index_site_dict['criteria']}' in category '{self.index_site_dict['category']}'...")

        index_proxy = self.config_dict['index_proxy']['selected']
        if index_proxy == 'jackett':
            try:
                host = self.config_dict['index_proxy']['jackett']['host']
            except KeyError:
                self.logger_instance.warning(u'No jackett hostname sent to function, exiting function...')
                return 1, None

            try:
                port = self.config_dict['index_proxy']['jackett']['port']
            except KeyError:
                self.logger_instance.warning(u'No jackett port sent to function, exiting function...')
                return 1, None

            try:
                api_key = self.config_dict['index_proxy']['jackett']['api_key']
            except KeyError:
                self.logger_instance.warning(u'No jackett api_key sent to function, exiting function...')
                return 1, None

            try:
                read_timeout = self.config_dict['index_proxy']['jackett']['read_timeout']
            except KeyError:
                read_timeout = 30.0
                self.logger_instance.info(f"No jackett read timeout sent to function, defaulting to '{read_timeout}' seconds")

            try:
                limit = self.config_dict['index_proxy']['jackett']['limit']
            except KeyError:
                limit = 500
                self.logger_instance.warning(f"No jackett limit sent to function, defaulting to '{limit}'")

            try:
                max_offset = self.config_dict['index_proxy']['jackett']['offset']
            except KeyError:
                max_offset = 0
                self.logger_instance.warning(f"No jackett offset sent to function, defaulting to '{max_offset}'")

        else:

            self.logger_instance.warning(f"Index proxy of '{index_proxy}' not valid, exiting function...")
            return 1

        if "category" in self.index_site_dict:
            category = self.index_site_dict['category']
        else:
            self.logger_instance.warning(u'No category sent to function, exiting function...')
            return 1, None

        if "index_site" in self.index_site_dict:
            index_site = self.index_site_dict['index_site']
        else:
            self.logger_instance.warning(u"No index site sent to function, defaulting to 'all'")
            index_site = "all"

        if "criteria" in self.index_site_dict:
            search = self.index_site_dict['criteria']
            search = search.replace(",", " ")
            # url encode search string
            search = urllib.parse.quote_plus(search)
        else:
            self.logger_instance.warning(u'No search sent to function, exiting function...')
            return 1, None

        try:
            user_agent = self.init_dict['user_agent']
        except KeyError:
            self.logger_instance.warning(u'No user_agent sent to function, exiting function...')
            return 1, None

        # define offset so we can loop over more results
        offset = int(0)
        while offset <= int(max_offset):

            # construct url for api
            url = f"http://{host}:{port}/api/v2.0/indexers/{index_site}/results/torznab/api?apikey={api_key}&t=search&cat={category}&q={search}&extended=1&limit={limit}&offset={offset}"

            # download torznab results using requests
            return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=url, user_agent=user_agent, request_type="get", read_timeout=read_timeout)

            try:

                # parse xml formatted feed
                site_feed_parse = xmltodict.parse(content, process_namespaces=True)
                site_feed_parse = site_feed_parse["rss"]["channel"]["item"]

            except (ValueError, TypeError, KeyError):

                self.logger_instance.warning(f"Unable to process feed from index site '{index_site}'")
                return 1

            # this breaks down the rss feed page into tag sections
            for node in site_feed_parse:

                # reset dictionary on iteration
                result_dict = {}

                try:

                    title = node["title"]

                except (KeyError, TypeError, IndexError, AttributeError):

                    self.logger_instance.warning(f"Unable to identify title from index site '{index_site}'")
                    continue

                self.logger_instance.debug(f"Checking if index title '{title}' is already in the sqlite database...")

                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                read_database_simple_bool, query_result = db_sqlite_instance.read_database_simple('history', 'index_title', title)

                if read_database_simple_bool:

                    self.logger_instance.info(f"Index title '{title}' found in sqlite database using simple match, skipping movie")
                    continue

                else:

                    self.logger_instance.info(f"Index title '{title}' not found in sqlite database using simple match, performing adv sqlite match...")
                    read_database_adv_bool, query_result = db_sqlite_instance.read_database_adv('history', 'index_title', title)

                    if read_database_adv_bool is False:

                        self.logger_instance.warning(f"Index title '{title}' is empty when sanitised (badly formed index title), skipping movie")
                        continue

                    if read_database_adv_bool:

                        self.logger_instance.info(f"Index title '{title}' found in sqlite database using adv match, skipping movie")
                        continue

                self.logger_instance.info(f"Index title '{title}' not in Sqlite database, continuing...")

                try:

                    torrent_url = node['enclosure']['@url']

                    # if torrent url looks like a magnet then raise error
                    if torrent_url.startswith('magnet'):
                        raise TypeError

                except (KeyError, TypeError, IndexError, AttributeError):

                    self.logger_instance.debug(f"Unable to determine torrent url from index site '{index_site}'")
                    torrent_url = None

                try:

                    list_named_attributes = node['http://torznab.com/schemas/2015/feed:attr']

                except TypeError:

                    self.logger_instance.info(f"Unable to process attributes from index site '{index_site}'")
                    continue

                seeders = None
                peers = None
                magnet_url = None
                imdbid = None

                for i in list_named_attributes:

                    attribute_name = i['@name']

                    if "seeders" in attribute_name:

                        seeders = i['@value']

                    if "peers" in attribute_name:

                        peers = i['@value']

                    if "magnet" in attribute_name:

                        magnet_url = i['@value']

                    if "imdb" in attribute_name:

                        imdbid = i['@value']

                if magnet_url is None and torrent_url is None:

                    self.logger_instance.info(f"No magnet or torrent url available, skipping processing for index title '{title}'...")
                    continue

                try:

                    size = node["size"]
                    size_mb = int(size) // 1000000

                except (KeyError, TypeError, IndexError, AttributeError):

                    size = None
                    size_mb = None

                try:

                    comments = node["comments"]

                except (KeyError, TypeError, IndexError, AttributeError):

                    comments = None

                try:

                    pubdate = node["pubDate"]

                except (KeyError, TypeError, IndexError, AttributeError):

                    pubdate = None

                self.logger_instance.debug(f"Saving index details to dict for index title '{title}'...")
                result_dict.update({
                    'index_title': title,
                    'torrent_url': torrent_url,
                    'index_size': size,
                    'index_size_mb': size_mb,
                    'index_details': comments,
                    'index_pubdate': pubdate,
                    'index_seeders': seeders,
                    'index_peers': peers,
                    'imdb_id': imdbid,
                    'magnet_url': magnet_url,
                    'category': category
                })

                # identify index title information using regex, append to regex and return
                tools_various_instance = siphonator_tools_filters.ToolsFilters(self.logger_instance)
                result_dict = tools_various_instance.index_name(result_dict)

                # if we cannot identify the movie title then write to db and continue
                if not result_dict.get('movie_title'):
                    # write to database
                    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                    db_sqlite_instance.write_database()
                    continue

                # if we cannot identify the movie year then write to db and continue
                if not result_dict.get('movie_title_year'):
                    # write to database
                    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                    db_sqlite_instance.write_database()
                    continue

                if result_dict.get('result') == 'Passed':

                    self.logger_instance.info(u"Filtering movie based on index details...")
                    filter_movies_instance = siphonator_filter_movies.FilterMovies(self.logger_instance, self.init_dict, result_dict, self.config_dict, self.index_site_dict, self.library_path_walk)
                    result_dict = filter_movies_instance.filter_index_movies()

                else:

                    # write to database, need repeated instance due to changing result_dict
                    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                    db_sqlite_instance.write_database()
                    continue

                if result_dict.get('result') == 'Passed':

                    # if imdbid is not found from index site (rarbg supplies tt number) then lookup
                    if imdbid is None:

                        self.logger_instance.info(u"Searching for IMDb ID..")
                        get_imdb_tt_number_instance = siphonator_search_all.SearchAll(self.logger_instance, result_dict, self.config_dict)
                        result_dict = get_imdb_tt_number_instance.search()

                else:

                    # write to database
                    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                    db_sqlite_instance.write_database()
                    continue

                if result_dict.get('result') == 'Passed':

                    self.logger_instance.info(u"Getting movie details from IMDb using OMDb...")
                    result_dict = siphonator_imdb_omdb.omdb_json_api(self.logger_instance, self.config_dict, result_dict)

                    if result_dict.get('result') == 'Failed':

                        self.logger_instance.info(u"Getting movie details from IMDb using IMDBPie...")
                        result_dict = siphonator_imdb_imdbpie.imdb_json_api(self.logger_instance, result_dict)

                else:

                    # write to database
                    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                    db_sqlite_instance.write_database()
                    continue

                if result_dict.get('result') == 'Passed':

                    self.logger_instance.info(u"Filtering movie based on IMDb details...")
                    filter_movies_instance = siphonator_filter_movies.FilterMovies(self.logger_instance, self.init_dict, result_dict, self.config_dict, self.index_site_dict, self.library_path_walk)
                    result_dict = filter_movies_instance.filter_imdb_movies()

                else:

                    # write to database
                    db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                    db_sqlite_instance.write_database()
                    continue

                if result_dict.get('result') == 'Passed':

                    result_details = f"Passed: Passed all Index and IMDb filters"
                    self.logger_instance.info(result_details)
                    result_details_list = result_dict.get('result_details')
                    result_dict.update({'result': u'Passed'})
                    result_details_list.append(result_details)
                    result_dict.update({'result_details': result_details_list})

                    if self.config_dict['notification']['email']['enabled']:

                        self.logger_instance.info(u"E-mail notification enabled, sending E-mail...")
                        notification_email_instance = siphonator_notification_email.NotificationEmail(self.logger_instance, result_dict, self.config_dict)
                        notification_email_instance.email_send()

                    torrent_client_instance = siphonator_torrent_clients.TorrentClients(self.logger_instance, self.config_dict, self.qbt_client, result_dict)
                    result_dict = torrent_client_instance.qbittorrent_add_torrent()

                # write to database
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, self.init_dict, result_dict)
                db_sqlite_instance.write_database()
                continue

            # increment offset by 100 (default number of results from jackett)
            offset = offset+100
