import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_various as siphonator_tools_various
import lib.siphonator.search_all as siphonator_search_all
import lib.siphonator.imdb_imdbpie as siphonator_imdb_imdbpie
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.torrent_clients as siphonator_torrent_clients
import lib.siphonator.notification_email as siphonator_notification_email
import xmltodict
import urllib.parse
#
# example with keyword filter (1080p)
# http://192.168.1.10:1900/api/v2.0/indexers/all/results/torznab/api?apikey=o4xte43ftp56m64aknxch4pe7cp3lhaj&t=search&cat=&q=1080p&
#
# example with cat filtering
# http://192.168.1.10:1900/api/v2.0/indexers/all/results/torznab/api?apikey=o4xte43ftp56m64aknxch4pe7cp3lhaj&t=search&cat=5050&q=1080p&
#
# example with movie category and 1080p and bluray query filter
# http://192.168.1.10:1900/api/v2.0/indexers/all/results/torznab/api?apikey=o4xte43ftp56m64aknxch4pe7cp3lhaj&t=search&cat=2000&q=1080p%20bluray&extended=1
#
# example with limit of 10 results
# http://192.168.1.10:1900/api/v2.0/indexers/all/results/torznab/api?apikey=o4xte43ftp56m64aknxch4pe7cp3lhaj&t=search&cat=&extended=1&seeders=10000&q=&limit=10&maxage=10
#
# list of categories:-
# 2000	Movies
# 2010	Movies/Foreign
# 2020	Movies/Other
# 2030	Movies/SD
# 2040	Movies/HD
# 2045	Movies/UHD
# 2050	Movies/BluRay
# 2060	Movies/3D
#
# note looks like you cannot specify output as json thus use xml2dict
#
# input will be logger, host ip, post port, apikey, pos keyword filters, categories, limit
# output will be list containing dict, value of dict can be list also
#
# MG calls
#   torznab_download calls
#   torznab_result returns items will be:- title, *magnet, *torrent, *nzb, *details, *seeders, *peers, *imdb_tt, size, date, *nfo, *id
#
#   * = optional
#
#   e.g. return from torznab_result would look like:- [[{"title" : "ghostbusters"}, {"magnet" : "dfgsdfgdfdfgsdf"}], [{"title" : "ghostbusters2"}, {"magnet" : "eqweqweqweqwe"}]]
#
# MG processes list of dicts for each group against the filters


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

            seeders = None
            peers = None
            magnet_url = None
            torrent_url = None

            results_dict = self.index_dict

            try:

                list_named_attributes = node['http://torznab.com/schemas/2015/feed:attr']

            except TypeError:

                self.logger_instance.warning(u"Unable to process attributes from index site '%s'" % index_site)
                return 1

            for i in list_named_attributes:

                attribute_name = i['@name']

                if attribute_name == "seeders":

                    seeders = i['@value']

                if attribute_name == "peers":

                    peers = i['@value']

                if attribute_name == "magnet_url":

                    magnet_url = i['@value']

            try:

                title = node["title"]

            except (KeyError, TypeError, IndexError, AttributeError):

                title = None

            try:

                link = node["link"]

            except (KeyError, TypeError, IndexError, AttributeError):

                link = None

            if link != magnet_url:

                torrent_url = link

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

            self.logger_instance.info(u"Starting processing index title '%s'..." % title)
            results_dict.update({'index_title': title, 'torrent_url': torrent_url, 'index_size': size, 'index_size_mb': size_mb, 'download_link': details, 'index_comments': comments, 'index_pubdate': pubdate, 'index_seeders': seeders, 'index_peers': peers, 'magnet_url': magnet_url})
            results_dict = siphonator_tools_various.get_title_and_year_from_index_title(self.logger_instance, **results_dict)

            if results_dict is not None:

                self.logger_instance.info(u"Filtering movie based on index details...")
                filter_movies_instance = siphonator_filter_movies.FilterMovies(self.logger_instance, **results_dict)
                results_dict = filter_movies_instance.filter_index_movies()

            else:

                continue

            if results_dict is not None:

                self.logger_instance.info(u"Searching for IMDb ID..")
                get_imdb_tt_number_instance = siphonator_search_all.SearchAll(self.logger_instance, **results_dict)
                results_dict = get_imdb_tt_number_instance.search()

            else:

                continue

            #self.logger_instance.debug(u"Results dict is '%s'" % results_dict)

            if results_dict is not None:

                self.logger_instance.info(u"Getting movie details from IMDb...")
                results_dict = siphonator_imdb_imdbpie.imdb_json_api(self.logger_instance, **results_dict)

            else:

                continue

            if results_dict is not None:

                self.logger_instance.info(u"Filtering movie based on IMDb details...")
                filter_movies_instance = siphonator_filter_movies.FilterMovies(self.logger_instance, **results_dict)
                results_dict = filter_movies_instance.filter_imdb_movies()

            else:

                continue

            if results_dict is not None:

                self.logger_instance.debug(u"woot")

                if self.index_dict.get('notification_email_enabled'):

                    self.logger_instance.info(u"E-mail notification enabled, sending E-mail...")
                    notification_email_instance = siphonator_notification_email.NotificationEmail(self.logger_instance, **results_dict)
                    notification_email_instance.email_send()

                torrent_client_instance = siphonator_torrent_clients.TorrentClients(self.logger_instance, **results_dict)
                torrent_client_instance.qbittorrent_add()