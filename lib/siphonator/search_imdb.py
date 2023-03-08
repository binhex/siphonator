import imdbpie
import lib.siphonator.tools_various as siphonator_tools_various

class SearchIMDB(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title_search = kwargs.get('index_title_search', None)
        self.index_title_compare = kwargs.get('index_title_compare', None)
        self.index_year_compare = kwargs.get('index_year_compare', None)
        self.logger_instance = logger_instance

    def find_imdb_id_imdb(self):

        imdb_instance = imdbpie.Imdb()
        try:

            imdb_find_id_dict = imdb_instance.search_for_title(self.index_title_compare)

        except AttributeError:

            self.index_dict.update({'result': 'failed', 'result_details': u"Failed to search IMDb for index title compare '%s'" % self.index_title_compare})
            return self.index_dict

        # if resulting imdb json page is blank then continue
        if imdb_find_id_dict == {}:

            self.logger_instance.info(u"No match for movie title '%s' on IMDb json" % self.index_title_search)
            self.index_dict.update({'result': 'failed', 'result_details': u"No match for movie title '%s' on IMDb json" % self.index_title_search})
            return self.index_dict

        for imdb_find_id in imdb_find_id_dict:

            # find imdb title
            try:

                imdb_title = imdb_find_id["title"]
                self.logger_instance.info(u"IMDb title is '%s'" % imdb_title)

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb Title for movie")
                continue

            if imdb_title is None:

                self.logger_instance.debug(u"IMDb title is None, cannot compare")
                continue

            # get comparison dictionary for imdb_title
            tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
            custom_title_compare_dict = tools_various_instance.custom_title_compare(imdb_title)
            imdb_title_compare = custom_title_compare_dict.get('custom_title_compare')

            if imdb_title_compare not in self.index_title_compare:

                self.logger_instance.debug(u"IMDb title compare '%s' not in index title compare '%s'" % (imdb_title_compare, self.index_title_compare))
                continue

            self.logger_instance.debug(u"IMDb title compare '%s' matches index title compare '%s'" % (imdb_title_compare, self.index_title_compare))

            # find imdb year
            try:

                imdb_year = imdb_find_id["year"]
                self.logger_instance.info(u"IMDb year is '%s'" % imdb_year)

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb year for movie")
                continue

            if imdb_year is None:

                self.logger_instance.debug(u"IMDb year is None, cannot compare")
                continue

            if int(imdb_year) != int(self.index_year_compare):

                self.logger_instance.debug(u"IMDb year compare '%s' does not equal index year compare '%s'" % (imdb_year, self.index_year_compare))
                continue

            self.logger_instance.debug(u"IMDb year compare '%s' equals index year compare '%s'" % (imdb_year, self.index_year_compare))

            # find imdb id
            try:

                imdb_id = imdb_find_id["imdb_id"]
                self.logger_instance.info(u"IMDb id is '%s'" % imdb_id)

            except (IndexError, KeyError, TypeError):

                self.logger_instance.info(u"Cannot find IMDb id for movie")
                continue

            self.logger_instance.info(u"IMDb ID URL is 'https://www.imdb.com/title/%s/'" % imdb_id)
            self.index_dict.update({'imdb_id': imdb_id})

            self.index_dict.update({'result': 'success', 'result_details': u"Found IMDb ID for movie '%s' using IMDb search" % self.index_title_search})
            return self.index_dict

        self.index_dict.update({'result': 'failed', 'result_details': u"Failed to identify movie '%s' using IMDb search" % self.index_title_search})
        return self.index_dict
