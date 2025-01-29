import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import lib.siphonator.tools_various as siphonator_tools_various
import re


class SearchOMDb(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.index_title_search = result_dict.get('index_title_search', None)
        self.index_title_compare = result_dict.get('index_title_compare', None)
        self.index_year_compare = result_dict.get('index_year_compare', None)
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance

    def find_imdb_id_omdb(self):

        search_omdb_api_key = self.config_dict["credentials"]['omdb']['api_key']
        index_title_search_encoded = urllib.parse.quote(self.index_title_search)
        function_name = siphonator_tools_various.get_function_name()

        # generate url to find tmdb id number
        omdb_find_id_json_url = f"http://www.omdbapi.com/?apikey={search_omdb_api_key}&t={index_title_search_encoded}&y={self.index_year_compare}"
        self.logger_instance.info(f"Find id URL is {omdb_find_id_json_url}")

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=omdb_find_id_json_url, request_type='get')

        if return_code != 0:

            result_details = f"Failed {function_name} - Site feed download failed for OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            omdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"Site feed parse failed for OMDb")
            self.result_dict.update({'result': 'Failed', 'result_details': u"Site feed parse failed for OMDb"})
            return self.result_dict

        # if resulting tmdb json page is blank then continue
        if omdb_find_id_json is None or omdb_find_id_json == {}:

            result_details = f"Failed {function_name} - Empty json returned from OMDb for index title search '{self.index_title_search}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            omdb_title = omdb_find_id_json["Title"]

        except (IndexError, KeyError, TypeError):

            result_details = f"Failed {function_name} - No title key in json for OMDb for index title search '{self.index_title_search}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            omdb_release_year = omdb_find_id_json["Year"]

        except (IndexError, KeyError, TypeError):

            result_details = f"Failed {function_name} -No year key in json for OMDb for index title search '{self.index_title_search}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        # get comparison dictionary for omdb_title
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
        omdb_title_compare = tools_various_instance.custom_title_compare(omdb_title)

        if omdb_title_compare not in self.index_title_compare:

            result_details = f"Failed {function_name} - Failed to identify movie title '{self.index_title_search}' using OMDb search"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.debug(f"OMDb title compare '{omdb_title_compare}' matches index title compare '{self.index_title_compare}'")

        # strip out non-numeric characters
        omdb_release_year = re.sub(r'\D+', '', omdb_release_year)

        if int(omdb_release_year) != int(self.index_year_compare):

            result_details = f"Failed {function_name} - Failed to identify movie year '{self.index_title_search}' using OMDb search"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.debug(f"OMDb year compare '{omdb_release_year}' equals index year compare '{self.index_year_compare}'")

        try:

            imdb_id = omdb_find_id_json["imdbID"]
            self.logger_instance.info(f"IMDb id is '{imdb_id}'")

        except (IndexError, KeyError, TypeError):

            result_details = f"Failed {function_name} - Cannot find IMDbID for movie using OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        if imdb_id is None or imdb_id == "":

            result_details = f"Failed {function_name} - IMDb ID is None, unable to identify valid value using OMDb"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.info(f"IMDb ID URL is 'https://www.imdb.com/title/{imdb_id}/'")
        self.result_dict.update({'imdb_id': imdb_id})

        result_details = f"Passed {function_name} - Found IMDb ID for movie '{self.index_title_search}' using OMDb search"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})

        return self.result_dict
