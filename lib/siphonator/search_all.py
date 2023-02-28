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
        results_dict = search_imdb_instance.find_imdb_id_imdb()

        if results_dict is None:

            self.logger_instance.warning(u"Failed to identify ID from IMDb, switching to TMDb...")

            search_tmdb_instance = siphonator_search_tmdb.SearchTMDB(self.logger_instance, **self.index_dict)
            results_dict = search_tmdb_instance.find_imdb_id_tmdb()

            if results_dict is None:

                self.logger_instance.warning(u"Failed to identify ID from TMDb, switching to OMDb...")

                search_omdb_instance = siphonator_search_omdb.SearchOMDb(self.logger_instance, **self.index_dict)
                results_dict = search_omdb_instance.find_imdb_id_omdb()

                if results_dict is None:

                    self.logger_instance.warning(u"Failed to identify ID from OMDb, no other methods currently defined")

        return results_dict
