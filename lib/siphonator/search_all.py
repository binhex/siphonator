import lib.siphonator.search_google as siphonator_search_google
import lib.siphonator.search_imdb as siphonator_search_imdb
import lib.siphonator.search_tmdb as siphonator_search_tmdb
import lib.siphonator.search_omdb as siphonator_search_omdb


class SearchAll(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.index_title_no_year = result_dict.get('index_title_no_year', None)
        self.index_year_regex = result_dict.get('index_year_regex', None)
        self.result_details_list = result_dict.get('result_details', [])

    def search(self):

        search_imdb_instance = siphonator_search_imdb.SearchIMDB(self.logger_instance, self.result_dict, self.config_dict)
        self.result_dict = search_imdb_instance.find_imdb_id_imdb()

        if self.result_dict.get('result') == 'Passed':
            return self.result_dict

        search_tmdb_instance = siphonator_search_tmdb.SearchTMDB(self.logger_instance, self.result_dict, self.config_dict)
        self.result_dict = search_tmdb_instance.find_imdb_id_tmdb()

        if self.result_dict.get('result') == 'Passed':
            return self.result_dict

        search_omdb_instance = siphonator_search_omdb.SearchOMDb(self.logger_instance, self.result_dict, self.config_dict)
        self.result_dict = search_omdb_instance.find_imdb_id_omdb()

        if self.result_dict.get('result') == 'Passed':
            return self.result_dict

        search_google_instance = siphonator_search_google.SearchGoogle(self.logger_instance, self.result_dict, self.config_dict)
        self.result_dict = search_google_instance.find_imdb_id_google()

        if self.result_dict.get('result') == 'Passed':
            return self.result_dict

        self.logger_instance.warning(u"Failed to identify ID, no other methods currently defined")
        return self.result_dict
