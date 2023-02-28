import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader


class SearchTMDB(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title_regex = kwargs.get('index_title_regex', None)
        self.index_year_regex = kwargs.get('index_year_regex', None)
        self.search_site = 'TMDb'
        self.logger_instance = logger_instance

    def find_imdb_id_tmdb(self):

        tmdb_api_key = self.index_dict.get('tmdb_api_key')
        index_title_regex_encoded = urllib.parse.quote(self.index_title_regex)

        # generate url to find tmdb id number
        tmdb_find_id_json_url = "https://api.themoviedb.org/3/search/movie?query=%s&year=%s&api_key=%s" % (index_title_regex_encoded, self.index_year_regex, tmdb_api_key)
        self.logger_instance.info(u"Find id URL is %s" % tmdb_find_id_json_url)

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=tmdb_find_id_json_url, request_type='get')

        if return_code != 0:
            self.logger_instance.warning(u"Site feed download failed for %s" % self.search_site)
            return None

        try:

            tmdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"%s Index - Site feed parse failed for TMDb" % self.search_site)
            return None

        # if resulting tmdb json page is blank then continue
        if tmdb_find_id_json == {}:
            self.logger_instance.info(u"%s Index - No match for movie title %s on TMDb json" % (self.search_site, self.index_title_regex))
            return None

        # find tmdb id
        try:

            tmdb_movie_id = tmdb_find_id_json["id"]
            self.logger_instance.info(u"%s Index - TMDb id is %s" % (self.search_site, tmdb_movie_id))

        except (IndexError, KeyError):

            try:

                tmdb_movie_id = tmdb_find_id_json["results"][0]["id"]
                self.logger_instance.info(u"%s Index - TMDb id is %s" % (self.search_site, tmdb_movie_id))

            except (IndexError, KeyError):

                self.logger_instance.info(u"%s Index - Cannot find TMDb ID for movie" % self.search_site)
                return None

        # generate url to find imdb tt number using tmdb id number from previous search
        tmdb_find_tt_json_url = "https://api.themoviedb.org/3/movie/%s?api_key=%s" % (tmdb_movie_id, tmdb_api_key)
        self.logger_instance.info(u"%s Index - TMDb find tt URL is %s" % (self.search_site, tmdb_find_tt_json_url))

        request_type = "get"

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=tmdb_find_tt_json_url, request_type=request_type)

        if return_code != 0:
            self.logger_instance.warning(u"%s Index - Site feed download failed for TMDb" % self.search_site)
            return None

        try:

            tmdb_find_tt_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"%s Index - Site feed parse failed for TMDb" % self.search_site)
            return None

        if tmdb_find_tt_json is None or tmdb_find_tt_json == {}:
            self.logger_instance.info(u"%s Index - No IMDb ID for movie title %s on TMDb json" % (self.search_site, self.index_title_regex))
            return None

        try:

            imdb_id = tmdb_find_tt_json["imdb_id"]
            self.logger_instance.info(u"%s Index - IMDb ID from TMDb is '%s'" % (self.search_site, imdb_id))

        except KeyError:

            self.logger_instance.info(u"%s Index - Cannot find IMDb ID for movie" % self.search_site)
            return None

        if imdb_id is None or imdb_id == "":

            self.logger_instance.warning(u"%s Index - IMDb ID is None, unable to identify valid value" % self.search_site)
            return None

        self.logger_instance.info(u"IMDb ID URL is 'https://www.imdb.com/title/%s/'" % imdb_id)
        self.index_dict.update({'imdb_id': imdb_id})

        return self.index_dict
