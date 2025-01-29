import lib.siphonator.search_google as siphonator_search_google
import lib.siphonator.search_imdb as siphonator_search_imdb
import lib.siphonator.search_tmdb as siphonator_search_tmdb
import lib.siphonator.search_omdb as siphonator_search_omdb
import lib.siphonator.tools_various as siphonator_tools_various


class SearchAll(object):

    def __init__(self,logger_instance, result_dict, config_dict):

        self.logger_instance = logger_instance
        self.result_dict = result_dict
        self.config_dict = config_dict
        self.index_title_no_year = result_dict.get('index_title_no_year', None)
        self.index_year_regex = result_dict.get('index_year_regex', None)
        self.logger_instance = logger_instance
        self.result_details_list = result_dict.get('result_details', [])

    def search(self):

        function_name = siphonator_tools_various.get_function_name()

        search_imdb_instance = siphonator_search_imdb.SearchIMDB(self.logger_instance, self.result_dict, self.config_dict)
        self.result_dict = search_imdb_instance.find_imdb_id_imdb()

        if self.result_dict.get('result') == 'Failed':

            self.logger_instance.warning(u"Failed to identify ID from IMDb, switching to TMDb...")

            search_tmdb_instance = siphonator_search_tmdb.SearchTMDB(self.logger_instance, self.result_dict, self.config_dict)
            self.result_dict = search_tmdb_instance.find_imdb_id_tmdb()

            if self.result_dict.get('result') == 'Failed':

                self.logger_instance.warning(u"Failed to identify ID from TMDb, switching to OMDb...")

                search_omdb_instance = siphonator_search_omdb.SearchOMDb(self.logger_instance, self.result_dict, self.config_dict)
                self.result_dict = search_omdb_instance.find_imdb_id_omdb()

                if self.result_dict.get('result') == 'Failed':

                    self.logger_instance.warning(u"Failed to identify ID from OMDb, switching to Google...")

                    search_google_instance = siphonator_search_google.SearchGoogle(self.logger_instance, self.result_dict, self.config_dict)
                    self.result_dict = search_google_instance.find_imdb_id_google()

                    if self.result_dict.get('result') == 'Failed':

                        self.logger_instance.warning(u"Failed to identify ID from Google, no other methods currently defined")
                        return self.result_dict

        result_details = f"Passed {function_name} - Identified IMDb ID '{self.result_dict.get('imdb_id')}' using search"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return self.result_dict
