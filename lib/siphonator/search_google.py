import googlesearch
import lib.siphonator.tools_various as siphonator_tools_various
import re


class SearchGoogle(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.index_title_search = result_dict.get('index_title_search', None)
        self.index_title_compare = result_dict.get('index_title_compare', None)
        self.index_title_full_compare = result_dict.get('index_title_full_compare', None)
        self.index_year_compare = result_dict.get('index_year_compare', None)
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance

    def find_imdb_id_google(self):

        # TODO note the timeout does not seem to work well and the search can get stuck, see https://github.com/Nv7-GitHub/googlesearch/issues/34
        google_find_id_gen = googlesearch.search(f"imdb {self.index_title_search} ({self.index_year_compare})", advanced=True, sleep_interval=5, num_results=1, timeout=10)

        function_name = siphonator_tools_various.get_function_name()

        if not google_find_id_gen:

            result_details = f"Failed {function_name} - Failed to search Google for index title compare '{self.index_title_compare}'"
            self.logger_instance.debug(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        try:

            # get first item from generator object
            google_find_id_dict = next(google_find_id_gen)

        except StopIteration:

            result_details = f"Failed {function_name} - Failed to return results from Google for index title compare '{self.index_title_compare}'"
            self.logger_instance.debug(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        imdb_title = google_find_id_dict.title
        imdb_url = google_find_id_dict.url

        # if title or url is none then return
        if not imdb_title or not imdb_url:

            result_details = f"Failed {function_name} - Failed to return IMDb title or URL from Google for index title compare '{self.index_title_compare}'"
            self.logger_instance.debug(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        # find imdb title
        self.logger_instance.info(f"IMDb title is '{imdb_title}'")
        self.logger_instance.info(f"IMDb URL is '{imdb_url}'")

        # create imdb_title to compare
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
        imdb_title_remove_year_to_end = tools_various_instance.custom_title_remove_year_to_end_compare(imdb_title)
        imdb_title_compare = tools_various_instance.custom_title_compare(imdb_title_remove_year_to_end)

        # check imdb title match index title
        if imdb_title_compare not in self.index_title_compare:

            result_details = f"Failed {function_name} - IMDb title compare '{imdb_title_compare}' not in index title compare '{self.index_title_compare}'"
            self.logger_instance.debug(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.debug(f"IMDb title compare '{imdb_title_compare}' matches index title compare '{self.index_title_compare}'")

        # check imdb title year matches index title year
        if self.index_year_compare not in imdb_title:

            result_details = f"Failed {function_name} - IMDb title '{imdb_title}' does not contain index year compare '{self.index_year_compare}'"
            self.logger_instance.debug(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        self.logger_instance.debug(f"IMDb title '{imdb_title}' does contain index year compare '{self.index_year_compare}'")

        # regex for tt number as we get full url returned from Google search
        imdb_id_search = re.search('tt[0-9]+', imdb_url)

        if not imdb_id_search:

            result_details = f"Failed {function_name} - IMDb URL '{imdb_url}' from Google search does not contain IMDb ID"
            self.logger_instance.debug(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        imdb_id = imdb_id_search.group()
        self.logger_instance.debug(f"IMDb ID is '{imdb_id}'")
        self.logger_instance.debug(f"IMDb URL is '{imdb_url}'")
        self.result_dict.update({'imdb_id': imdb_id})

        result_details = f"Passed {function_name} - Found IMDb ID for movie '{self.index_title_search}' using Google search"
        self.logger_instance.debug(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return self.result_dict
