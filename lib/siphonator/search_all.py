import lib.siphonator.search_google as siphonator_search_google
import lib.siphonator.search_imdb as siphonator_search_imdb
import lib.siphonator.search_tmdb as siphonator_search_tmdb
import lib.siphonator.search_omdb as siphonator_search_omdb


class SearchAll(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title_no_year = kwargs.get('index_title_no_year', None)
        self.index_year_regex = kwargs.get('index_year_regex', None)
        self.logger_instance = logger_instance

    def search(self):

        search_imdb_instance = siphonator_search_imdb.SearchIMDB(self.logger_instance, **self.index_dict)
        self.index_dict = search_imdb_instance.find_imdb_id_imdb()

        if self.index_dict.get('result') == 'failed':

            self.logger_instance.warning(u"Failed to identify ID from IMDb, switching to TMDb...")

            search_tmdb_instance = siphonator_search_tmdb.SearchTMDB(self.logger_instance, **self.index_dict)
            self.index_dict = search_tmdb_instance.find_imdb_id_tmdb()

            if self.index_dict.get('result') == 'failed':

                self.logger_instance.warning(u"Failed to identify ID from TMDb, switching to OMDb...")

                search_omdb_instance = siphonator_search_omdb.SearchOMDb(self.logger_instance, **self.index_dict)
                self.index_dict = search_omdb_instance.find_imdb_id_omdb()

                if self.index_dict.get('result') == 'failed':

                    self.logger_instance.warning(u"Failed to identify ID from OMDb, switching to Google...")

                    search_google_instance = siphonator_search_google.SearchGoogle(self.logger_instance, **self.index_dict)
                    self.index_dict = search_google_instance.find_imdb_id_google()

                    if self.index_dict.get('result') == 'failed':

                        self.logger_instance.warning(u"Failed to identify ID from Google, no other methods currently defined")
                        return self.index_dict

        self.index_dict.update({'result': 'success', 'result_details': u"Identified IMDb ID using search"})
        return self.index_dict
