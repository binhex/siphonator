import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_filters as siphonator_tools_filters
import re


class SearchOMDb(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.movie_title_and_year_search = result_dict.get('movie_title_and_year_search', None)
        self.movie_title = result_dict.get('movie_title', None)
        self.index_title_compare = result_dict.get('index_title_compare', None)
        self.movie_title_year = result_dict.get('movie_title_year', None)
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance

    def find_imdb_id_omdb(self):

        search_omdb_api_key = self.config_dict["credentials"]['omdb']['api_key']
        movie_title_encoded = urllib.parse.quote(self.movie_title)

        # generate url to find imdb id number
        omdb_find_id_json_url = f"http://www.omdbapi.com/?apikey={search_omdb_api_key}&t={movie_title_encoded}&y={self.movie_title_year}"
        self.logger_instance.info(f"Find id URL is {omdb_find_id_json_url}")

        # download omdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=omdb_find_id_json_url, request_type='get')

        if return_code != 0:

            result_details = f"Failed: Site feed download failed for OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            omdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            result_details = f"Failed: Site feed parse failed for OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        # if resulting omdb json page is blank then continue
        if omdb_find_id_json is None or omdb_find_id_json == {}:

            result_details = f"Failed: Empty json returned from OMDb for index title search '{self.movie_title_and_year_search}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            omdb_title = omdb_find_id_json["Title"]

        except (IndexError, KeyError, TypeError):

            result_details = f"Failed: No title key in json for OMDb for index title search '{self.movie_title_and_year_search}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            omdb_release_year = omdb_find_id_json["Year"]

        except (IndexError, KeyError, TypeError):

            result_details = f"Failed: No year key in json for OMDb for index title search '{self.movie_title_and_year_search}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        # get comparison dictionary for omdb_title
        tools_filters_instance = siphonator_tools_filters.ToolsFilters(self.logger_instance)
        omdb_title_compare = tools_filters_instance.sanitise_compare(omdb_title)

        if omdb_title_compare is None or omdb_title_compare not in self.index_title_compare:
            result_details = f"Failed: Cannot identify movie title '{self.movie_title_and_year_search}' using OMDb search"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.debug(f"OMDb title compare '{omdb_title_compare}' matches index title compare '{self.index_title_compare}'")

        # strip out non-numeric characters
        omdb_release_year = re.sub(r'\D+', '', omdb_release_year)

        if not omdb_release_year:
            result_details = f"Failed: Cannot identify movie year from TMDb '{omdb_release_year}' using OMDb search"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        if int(omdb_release_year) != int(self.movie_title_year):

            result_details = f"Failed: OMDb release year '{omdb_release_year}' does not match index title year '{self.movie_title_year}' using OMDb search"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.debug(f"OMDb year compare '{omdb_release_year}' equals index year compare '{self.movie_title_year}'")

        try:

            imdb_id = omdb_find_id_json["imdbID"]
            self.logger_instance.info(f"IMDb id is '{imdb_id}'")

        except (IndexError, KeyError, TypeError):

            result_details = f"Failed: Cannot find IMDbID for movie using OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        if imdb_id is None or imdb_id == "":

            result_details = f"Failed: IMDb ID is None, unable to identify valid value using OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.info(f"IMDb ID URL is 'https://www.imdb.com/title/{imdb_id}/'")
        self.result_dict.update({'imdb_id': imdb_id})

        result_details = f"Passed: Found IMDb ID '{imdb_id}' for movie '{self.movie_title_and_year_search}' using OMDb search"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})

        return self.result_dict
