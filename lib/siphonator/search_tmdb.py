import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_filters as siphonator_tools_filters
from datetime import datetime


class SearchTMDB(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.movie_title_and_year_search = result_dict.get('movie_title_and_year_search', None)
        self.movie_title = result_dict.get('movie_title', None)
        self.index_title_compare = result_dict.get('index_title_compare', None)
        self.movie_title_year = result_dict.get('movie_title_year', None)
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance

    def find_imdb_id_tmdb(self):

        search_tmdb_api_key = self.config_dict["credentials"]['tmdb']['api_key']
        movie_title_encoded = urllib.parse.quote(self.movie_title)

        # generate url to find tmdb id number
        tmdb_find_id_json_url = f"https://api.themoviedb.org/3/search/movie?query={movie_title_encoded}&year={self.movie_title_year}&api_key={search_tmdb_api_key}"
        self.logger_instance.info(f"Find id URL is {tmdb_find_id_json_url}")

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=tmdb_find_id_json_url, request_type='get')

        if return_code != 0:

            result_details = f"Failed: Site feed download failed for TMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            tmdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"Site feed parse failed for TMDb")
            self.result_dict.update({'result': 'Failed', 'result_details': u"Site feed parse failed for TMDb"})
            return self.result_dict

        # if resulting tmdb json page is blank then continue
        if tmdb_find_id_json == {}:

            result_details = f"Failed: No match for movie title '{self.movie_title_and_year_search}' on TMDb json"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        for tmdb_find_id in tmdb_find_id_json["results"]:

            tmdb_title = tmdb_find_id["title"]
            tmdb_original_title = tmdb_find_id["original_title"]

            # get comparison dictionary for tmdb_title
            tools_filters_instance = siphonator_tools_filters.ToolsFilters(self.logger_instance)
            tmdb_title_compare = tools_filters_instance.sanitise_compare(tmdb_title)
            tmdb_original_title_compare = tools_filters_instance.sanitise_compare(tmdb_original_title)

            if tmdb_title_compare is not None and tmdb_title_compare in self.index_title_compare:
                self.logger_instance.debug(f"TMDb title compare '{tmdb_title_compare}' matches index title compare '{self.index_title_compare}'")

            elif tmdb_original_title_compare is not None and tmdb_original_title_compare in self.index_title_compare:
                self.logger_instance.debug(f"TMDb original title compare '{tmdb_title_compare}' not in index title compare '{self.index_title_compare}'")

            else:
                self.logger_instance.debug(f"TMDb title/original title compare not in index title compare '{self.index_title_compare}', skipping")
                continue

            tmdb_release_date = (tmdb_find_id["release_date"])
            tmdb_release_date_object = datetime.strptime(tmdb_release_date, '%Y-%m-%d')
            tmdb_release_year = tmdb_release_date_object.year

            if not tmdb_release_year:

                self.logger_instance.debug(f"Failed: Cannot identify movie year from TMDb '{tmdb_release_year}' using TMDb search")
                continue

            if int(tmdb_release_year) != int(self.movie_title_year):

                self.logger_instance.debug(f"TMDb year compare '{tmdb_release_year}' does not equal index year compare '{self.movie_title_year}'")
                continue

            self.logger_instance.debug(f"TMDb year compare '{tmdb_release_year}' equals index year compare '{self.movie_title_year}'")

            # find tmdb id
            try:

                tmdb_movie_id = tmdb_find_id["id"]
                self.logger_instance.info(f"TMDb id is {tmdb_movie_id}")

            except (IndexError, KeyError, TypeError):

                result_details = f"Failed: Site feed download failed for TMDb"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return self.result_dict

            # generate url to find imdb tt number using tmdb id number from previous search
            tmdb_find_tt_json_url = f"https://api.themoviedb.org/3/movie/{tmdb_movie_id}?api_key={search_tmdb_api_key}"
            self.logger_instance.info(f"TMDb find tt URL is {tmdb_find_tt_json_url}")

            request_type = "get"

            # download tmdb json (used for iphone/android)
            return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=tmdb_find_tt_json_url, request_type=request_type)

            if return_code != 0:

                result_details = f"Failed: Site feed download failed for TMDb"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return self.result_dict

            try:

                tmdb_find_tt_json = json.loads(content)

            except (ValueError, TypeError, KeyError):

                result_details = f"Failed: Site feed download failed for TMDb"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return self.result_dict

            if tmdb_find_tt_json is None or tmdb_find_tt_json == {}:

                result_details = f"Failed: Site feed download failed for TMDb"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return self.result_dict

            try:

                imdb_id = tmdb_find_tt_json["imdb_id"]
                self.logger_instance.info(f"IMDb ID from TMDb is '{imdb_id}'")

            except (IndexError, KeyError, TypeError):

                result_details = f"Failed: Site feed download failed for TMDb"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return self.result_dict

            if imdb_id is None or imdb_id == "":

                result_details = f"Failed: Site feed download failed for TMDb"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return self.result_dict

            self.logger_instance.info(f"IMDb ID URL is 'https://www.imdb.com/title/{imdb_id}/'")
            self.result_dict.update({'imdb_id': imdb_id})

            result_details = f"Passed: Found IMDb ID '{imdb_id}' for movie '{self.movie_title_and_year_search}' using TMDb search"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        result_details = f"Failed: Failed to identify movie '{self.movie_title_and_year_search}' using TMDb search"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return self.result_dict
