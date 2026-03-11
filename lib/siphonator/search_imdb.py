import imdbpie
from imdbpie import ImdbAPIError
import lib.siphonator.tools_filters as siphonator_tools_filters


class SearchIMDB(object):

    def __init__(self, logger_instance, result_dict, config_dict):

        self.result_dict = result_dict
        self.config_dict = config_dict
        self.movie_title_and_year_search = result_dict.get('movie_title_and_year_search', None)
        self.movie_title_compare = result_dict.get('movie_title_compare', None)
        self.movie_title_year = result_dict.get('movie_title_year', None)
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance

    def find_imdb_id_imdb(self):

        imdb_instance = imdbpie.Imdb()
        try:

            imdb_find_id_dict = imdb_instance.search_for_title(self.movie_title_and_year_search)

        except (AttributeError, ValueError, ImdbAPIError) as e:

            result_details = f"Failed: Failed to search IMDb for index title search '{self.movie_title_and_year_search}' using IMDbPie, error is '{e}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        # if resulting imdb json page is blank then continue
        if imdb_find_id_dict == {}:

            result_details = f"Failed: No match for movie title '{self.movie_title_and_year_search}' on IMDb json"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        for imdb_find_id in imdb_find_id_dict:

            # find imdb title
            try:

                imdb_title = imdb_find_id["title"]
                self.logger_instance.info(f"IMDb title is '{imdb_title}'")

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb Title for movie")
                continue

            if imdb_title is None:

                self.logger_instance.debug(u"IMDb title is None, cannot compare")
                continue

            # get comparison dictionary for imdb_title
            tools_filters_instance = siphonator_tools_filters.ToolsFilters(self.logger_instance)
            imdb_title_compare = tools_filters_instance.compare(imdb_title)

            if imdb_title_compare is None or imdb_title_compare not in self.movie_title_compare:
                self.logger_instance.info(f"IMDb title compare '{imdb_title_compare}' not in index title compare '{self.movie_title_compare}'")
                continue

            self.logger_instance.info(f"IMDb title compare '{imdb_title_compare}' matches index title compare '{self.movie_title_compare}'")

            # find imdb year
            try:

                imdb_year = imdb_find_id["year"]
                self.logger_instance.info(f"IMDb year is '{imdb_year}'")

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb year for movie")
                continue

            if imdb_year is None:

                self.logger_instance.debug(u"IMDb year is None, cannot compare")
                continue

            if int(imdb_year) != int(self.movie_title_year):

                self.logger_instance.debug(f"IMDb year compare '{imdb_year}' does not equal index year compare '{self.movie_title_year}'")
                continue

            self.logger_instance.debug(f"IMDb year compare '{imdb_year}' equals index year compare '{self.movie_title_year}'")

            # find imdb id
            try:

                imdb_id = imdb_find_id["imdb_id"]
                self.logger_instance.info(f"IMDb id is '{imdb_id}'")

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb id for movie")
                continue

            self.logger_instance.info(f"IMDb ID URL is 'https://www.imdb.com/title/{imdb_id}/'")
            self.result_dict.update({'imdb_id': imdb_id})

            result_details = f"Passed: Found IMDb ID '{imdb_id}' for movie '{self.movie_title_and_year_search}' using IMDb search"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return self.result_dict

        result_details = f"Failed: Failed to identify movie '{self.movie_title_and_year_search}' using IMDb search"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return self.result_dict
