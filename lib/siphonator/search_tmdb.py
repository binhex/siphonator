import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_various as siphonator_tools_various
from datetime import datetime


class SearchTMDB(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.index_title_search = result_dict.get('index_title_search', None)
        self.index_title_compare = result_dict.get('index_title_compare', None)
        self.index_year_compare = result_dict.get('index_year_compare', None)
        self.logger_instance = logger_instance

    def find_imdb_id_tmdb(self):

        search_tmdb_api_key = self.config_dict["credentials"]['tmdb']['api_key']
        index_title_search_encoded = urllib.parse.quote(self.index_title_search)

        # generate url to find tmdb id number
        tmdb_find_id_json_url = "https://api.themoviedb.org/3/search/movie?query=%s&year=%s&api_key=%s" % (index_title_search_encoded, self.index_year_compare, search_tmdb_api_key)
        self.logger_instance.info(u"Find id URL is %s" % tmdb_find_id_json_url)

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=tmdb_find_id_json_url, request_type='get')

        if return_code != 0:

            self.logger_instance.warning(u"Site feed download failed for TMDb")
            self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
            return self.result_dict

        try:

            tmdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"Site feed parse failed for TMDb")
            self.result_dict.update({'result': 'failed', 'result_details': u"Site feed parse failed for TMDb"})
            return self.result_dict

        # if resulting tmdb json page is blank then continue
        if tmdb_find_id_json == {}:

            self.logger_instance.info(u"No match for movie title '%s' on TMDb json" % self.index_title_search)
            self.result_dict.update({'result': 'failed', 'result_details': u"No match for movie title '%s' on TMDb json" % self.index_title_search})
            return self.result_dict

        for tmdb_find_id in tmdb_find_id_json["results"]:

            tmdb_title = tmdb_find_id["title"]
            tmdb_original_title = tmdb_find_id["original_title"]

            # get comparison dictionary for tmdb_title
            tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
            tmdb_title_compare = tools_various_instance.custom_title_compare(tmdb_title)

            tmdb_original_title_compare = tools_various_instance.custom_title_compare(tmdb_original_title)

            if tmdb_title_compare not in self.index_title_compare:

                self.logger_instance.debug(u"TMDb title compare '%s' not in index title compare '%s', attempting comparison of original title..." % (tmdb_title_compare, self.index_title_compare))

                if tmdb_original_title_compare not in self.index_title_compare:

                    self.logger_instance.debug(u"TMDb original title compare '%s' not in index title compare '%s'" % (tmdb_title_compare, self.index_title_compare))
                    continue

                else:

                    self.logger_instance.debug(u"TMDb original title compare '%s' matches index title compare '%s'" % (tmdb_title_compare, self.index_title_compare))

            else:

                self.logger_instance.debug(u"TMDb title compare '%s' matches index title compare '%s'" % (tmdb_title_compare, self.index_title_compare))

            tmdb_release_date = (tmdb_find_id["release_date"])
            tmdb_release_date_object = datetime.strptime(tmdb_release_date, '%Y-%m-%d')
            tmdb_release_year = tmdb_release_date_object.year

            if int(tmdb_release_year) != int(self.index_year_compare):

                self.logger_instance.debug(u"TMDb year compare '%s' does not equal index year compare '%s'" % (tmdb_release_year, self.index_year_compare))
                continue

            self.logger_instance.debug(u"TMDb year compare '%s' equals index year compare '%s'" % (tmdb_release_year, self.index_year_compare))

            # find tmdb id
            try:

                tmdb_movie_id = tmdb_find_id["id"]
                self.logger_instance.info(u"TMDb id is %s" % tmdb_movie_id)

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find TMDb ID for movie")
                self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
                return self.result_dict

            # generate url to find imdb tt number using tmdb id number from previous search
            tmdb_find_tt_json_url = "https://api.themoviedb.org/3/movie/%s?api_key=%s" % (tmdb_movie_id, search_tmdb_api_key)
            self.logger_instance.info(u"TMDb find tt URL is %s" % tmdb_find_tt_json_url)

            request_type = "get"

            # download tmdb json (used for iphone/android)
            return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=tmdb_find_tt_json_url, request_type=request_type)

            if return_code != 0:

                self.logger_instance.warning(u"Site feed download failed for TMDb")
                self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
                return self.result_dict

            try:

                tmdb_find_tt_json = json.loads(content)

            except (ValueError, TypeError, KeyError):

                self.logger_instance.warning(u"Site feed parse failed for TMDb")
                self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
                return self.result_dict

            if tmdb_find_tt_json is None or tmdb_find_tt_json == {}:
                self.logger_instance.info(u"No IMDb ID for movie title %s on TMDb json" % self.index_title_search)
                self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
                return self.result_dict

            try:

                imdb_id = tmdb_find_tt_json["imdb_id"]
                self.logger_instance.info(u"IMDb ID from TMDb is '%s'" % imdb_id)

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb ID for movie")
                self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
                return self.result_dict

            if imdb_id is None or imdb_id == "":

                self.logger_instance.warning(u"IMDb ID is None, unable to identify valid value")
                self.result_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for TMDb"})
                return self.result_dict

            self.logger_instance.info(u"IMDb ID URL is 'https://www.imdb.com/title/%s/'" % imdb_id)
            self.result_dict.update({'imdb_id': imdb_id})

            self.result_dict.update({'result': 'success', 'result_details': u"Found IMDb ID for movie '%s' using TMDb search" % self.index_title_search})
            return self.result_dict

        self.result_dict.update({'result': 'failed', 'result_details': u"Failed to identify movie '%s' using TMDb search" % self.index_title_search})
        return self.result_dict
