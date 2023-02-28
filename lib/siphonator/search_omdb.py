import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader


class SearchOMDb(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title_regex = kwargs.get('index_title_regex', None)
        self.index_year_regex = kwargs.get('index_year_regex', None)
        self.search_site = 'OMDb'
        self.logger_instance = logger_instance

    def find_imdb_id_omdb(self):

        omdb_api_key = self.index_dict.get('omdb_api_key')
        index_title_regex_encoded = urllib.parse.quote(self.index_title_regex)

        # generate url to find tmdb id number
        omdb_find_id_json_url = "http://www.omdbapi.com/?apikey=%s&t=%s&y=%s" % (omdb_api_key, index_title_regex_encoded, self.index_year_regex)
        self.logger_instance.info(u"Find id URL is %s" % omdb_find_id_json_url)

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=omdb_find_id_json_url, request_type='get')
        print(content)
        if return_code != 0:

            self.logger_instance.warning(u"Site feed download failed for %s" % self.search_site)
            return None

        try:

            omdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"Site feed parse failed for %s" % self.search_site)
            return None

        # if resulting tmdb json page is blank then continue
        if omdb_find_id_json is None or omdb_find_id_json == {}:

            self.logger_instance.info(u"No match for movie title '%s' on %s json" % (self.index_title_regex, self.search_site))
            return None

        try:

            imdb_id = omdb_find_id_json["imdbID"]
            self.logger_instance.info(u"IMDb id is '%s'" % imdb_id)

        except (IndexError, KeyError):

            self.logger_instance.info(u"Cannot find '%s' ID for movie" % self.search_site)
            return None

        if imdb_id is None or imdb_id == "":

            self.logger_instance.warning(u"%s Index - IMDb ID is None, unable to identify valid value" % self.search_site)
            return None

        self.logger_instance.info(u"IMDb ID URL is 'https://www.imdb.com/title/%s/'" % imdb_id)
        self.index_dict.update({'imdb_id': imdb_id})

        return self.index_dict
