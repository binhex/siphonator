import xmltodict
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_various as siphonator_tools_various
import lib.siphonator.search_all as siphonator_search_all
import lib.siphonator.imdb_imdbpie as siphonator_imdb_imdbpie
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.torrent_clients as siphonator_torrent_clients
import lib.siphonator.notification_email as siphonator_notification_email
import lib.siphonator.db_sqlite as siphonator_db_sqlite

# NOTES yourbittorrent looks like its torrent only but does not download from jackett!!
#limtorrents also looks to be torrent only but wee know it does magnet!!, torrent does not download!! - magnet just not available via jackett!, use raincoat?
#limetorrents magnet links work for prowlarr but not jackett
#1337x works for prowlarr torrent (and magnet?) but not for jackett

class IndexProxy(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.search_site = 'TMDb'
        self.logger_instance = logger_instance

    # in logger_instance,kwargs for construct url (host, port, api_key, category, search, limit, user_agent)
    # out return_code, status_code, content
    def jackett(self):

        if self.index_dict is not None:

            self.index_dict.update({'search_site': self.search_site})

            if "index_proxy_jackett_host" in self.index_dict:
                host = self.index_dict['index_proxy_jackett_host']
            else:
                self.logger_instance.warning(u'No hostname sent to function, exiting function...')
                return 1, None

            if "index_proxy_jackett_port" in self.index_dict:
                port = self.index_dict['index_proxy_jackett_port']
            else:
                self.logger_instance.warning(u'No port sent to function, exiting function...')
                return 1, None

            if "index_proxy_jackett_api_key" in self.index_dict:
                api_key = self.index_dict['index_proxy_jackett_api_key']
            else:
                self.logger_instance.warning(u'No api_key sent to function, exiting function...')
                return 1, None

            if "index_site_category" in self.index_dict:
                category = self.index_dict['index_site_category']
            else:
                self.logger_instance.warning(u'No category sent to function, exiting function...')
                return 1, None

            if "index_site" in self.index_dict:
                index_site = self.index_dict['index_site']
            else:
                self.logger_instance.warning(u'No index site sent to function, defaulting to \'all\'')
                index_site = "all"

            if "index_site_search" in self.index_dict:
                search = self.index_dict['index_site_search']
                search = search.replace(",", " ")
                # url encode search string
                search = urllib.parse.quote_plus(search)
            else:
                self.logger_instance.warning(u'No search sent to function, exiting function...')
                return 1, None

            if "index_proxy_jackett_limit" in self.index_dict:
                limit = self.index_dict['index_proxy_jackett_limit']
            else:
                self.logger_instance.warning(u'No limit sent to function, exiting function...')
                return 1, None

            if "user_agent" in self.index_dict:
                user_agent = self.index_dict['user_agent']
            else:
                self.logger_instance.warning(u'No user_agent sent to function, exiting function...')
                return 1, None

            if "index_proxy_jackett_read_timeout" in self.index_dict:
                read_timeout = self.index_dict['index_proxy_jackett_read_timeout']
            else:
                read_timeout = 30.0
                self.logger_instance.info(u'No read timeout sent to function, defaulting to %s seconds' % read_timeout)

        else:

            self.logger_instance.warning(u'No keyword args sent to function, exiting function...')
            return 1

        # construct url for api
        url = "http://%s:%s/api/v2.0/indexers/%s/results/torznab/api?apikey=%s&t=search&cat=%s&q=%s&extended=1&maxage=%s" % (host, port, index_site, api_key, category, search, limit)

        # download torznab results using requests
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=url, user_agent=user_agent, request_type="get", read_timeout=read_timeout)

        try:

            # parse xml formatted feed
            site_feed_parse = xmltodict.parse(content, process_namespaces=True)
            site_feed_parse = site_feed_parse["rss"]["channel"]["item"]

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"Unable to process feed from index site '%s'" % index_site)
            return 1

        # this breaks down the rss feed page into tag sections
        for node in site_feed_parse:

            self.logger_instance.info(u"Resetting IMDb values for dict from previous run...")
            self.index_dict.update({
                'imdb_title': None,
                'imdb_year': None,
                'imdb_poster_url': None,
                'imdb_plot_summary': None,
                'imdb_plot_outline': None,
                'imdb_rating': None,
                'imdb_votes': None,
                'imdb_title_type': None,
                'imdb_running_time_in_minutes': None,
                'imdb_genre_list': None,
                'imdb_director_list': None,
                'imdb_writer_list': None,
                'imdb_cast_list': None,
                'imdb_languages_list': None,
                'imdb_country_list': None,
                'imdb_character_list': None
            })

            try:

                title = node["title"]

            except (KeyError, TypeError, IndexError, AttributeError):

                self.logger_instance.warning(u"Unable to identify title from index site '%s'" % index_site)
                continue

            self.logger_instance.debug(u"Checking if index title '%s' is already in the sqlite database..." % title)

            db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
            read_database_simple_bool = db_sqlite_instance.read_database_simple('history', 'index_title', title)

            if read_database_simple_bool:

                self.logger_instance.info(u"Index title '%s' found in sqlite database using simple match, skipping movie" % title)
                continue

            else:

                self.logger_instance.info(u"Index title '%s' not found in sqlite database using simple match, performing adv sqlite match..." % title)
                read_database_adv_bool = db_sqlite_instance.read_database_adv('history', 'index_title', title)

                if read_database_adv_bool:

                    self.logger_instance.info(u"Index title '%s' found in sqlite database using adv match, skipping movie" % title)
                    continue

            self.logger_instance.debug(u"Index title '%s' not in sqlite database, continuing..." % title)

            try:

                torrent_url = node['enclosure']['@url']

            except (KeyError, TypeError, IndexError, AttributeError):

                self.logger_instance.debug(u"Unable to determine torrent url from index site '%s'" % index_site)
                torrent_url = None

            try:

                list_named_attributes = node['http://torznab.com/schemas/2015/feed:attr']

            except TypeError:

                self.logger_instance.info(u"Unable to process attributes from index site '%s'" % index_site)
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

                self.logger_instance.info(u"No magnet or torrent url available, skipping processing for index title '%s'..." % title)
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

                details = node["guid"]

            except (KeyError, TypeError, IndexError, AttributeError):

                details = None

            try:

                pubdate = node["pubDate"]

            except (KeyError, TypeError, IndexError, AttributeError):

                pubdate = None

            self.logger_instance.debug(u"Saving index details to dict for index title '%s'..." % title)
            self.index_dict.update({
                'index_title': title,
                'torrent_url': torrent_url,
                'index_size': size,
                'index_size_mb': size_mb,
                'download_link': details,
                'index_details': comments,
                'index_pubdate': pubdate,
                'index_seeders': seeders,
                'index_peers': peers,
                'imdb_id': imdbid,
                'magnet_url': magnet_url,
                'category': category
            })

            tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
            self.index_dict = tools_various_instance.index_title_compare_search(**self.index_dict)

            if self.index_dict.get('result') != 'failed':

                self.logger_instance.info(u"Filtering movie based on index details...")
                filter_movies_instance = siphonator_filter_movies.FilterMovies(self.logger_instance, **self.index_dict)
                self.index_dict = filter_movies_instance.filter_index_movies()

            else:

                # write to database, need repeated instance due to changing self.index_dict
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
                db_sqlite_instance.write_database()
                continue

            if self.index_dict.get('result') != 'failed':

                # if imdbid is not found from index site (rarbg supplies tt number) then lookup
                if imdbid is None:

                    self.logger_instance.info(u"Searching for IMDb ID..")
                    get_imdb_tt_number_instance = siphonator_search_all.SearchAll(self.logger_instance, **self.index_dict)
                    self.index_dict = get_imdb_tt_number_instance.search()

            else:

                # write to database
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
                db_sqlite_instance.write_database()
                continue

            if self.index_dict.get('result') != 'failed':

                self.logger_instance.info(u"Getting movie details from IMDb...")
                self.index_dict = siphonator_imdb_imdbpie.imdb_json_api(self.logger_instance, **self.index_dict)

            else:

                # write to database
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
                db_sqlite_instance.write_database()
                continue

            if self.index_dict.get('result') != 'failed':

                self.logger_instance.info(u"Filtering movie based on IMDb details...")
                filter_movies_instance = siphonator_filter_movies.FilterMovies(self.logger_instance, **self.index_dict)
                self.index_dict = filter_movies_instance.filter_imdb_movies()

            else:

                # write to database
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
                db_sqlite_instance.write_database()
                continue

            if self.index_dict.get('result') != 'failed':

                self.index_dict.update({'result': 'success', 'result_details': u"Passed all Index and IMDb filters"})

                # write to database
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
                db_sqlite_instance.write_database()

                if self.index_dict.get('notification_email_enabled'):

                    self.logger_instance.info(u"E-mail notification enabled, sending E-mail...")
                    notification_email_instance = siphonator_notification_email.NotificationEmail(self.logger_instance, **self.index_dict)
                    notification_email_instance.email_send()

                torrent_client_instance = siphonator_torrent_clients.TorrentClients(self.logger_instance, **self.index_dict)
                torrent_client_instance.qbittorrent_add()

            else:

                # write to database
                db_sqlite_instance = siphonator_db_sqlite.DbSqlite(self.logger_instance, **self.index_dict)
                db_sqlite_instance.write_database()
                continue
