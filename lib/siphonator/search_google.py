from googlesearch import search
import lib.siphonator.tools_various as siphonator_tools_various


class SearchGoogle(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title_search = kwargs.get('index_title_search', None)
        self.index_title_compare = kwargs.get('index_title_compare', None)
        self.index_year_compare = kwargs.get('index_year_compare', None)
        self.logger_instance = logger_instance

    def find_imdb_id_google(self):

        # TODO note the timeout does not seem to work well and the search can get stuck, see https://github.com/Nv7-GitHub/googlesearch/issues/34
        google_find_id_gen = search(f"imdb {self.index_title_search} ({self.index_year_compare})", advanced=True, sleep_interval=5, num_results=1, timeout=10)

        if not google_find_id_gen:

            self.index_dict.update({'result': 'failed', 'result_details': u"Failed to search Google for index title compare '%s'" % self.index_title_compare})
            return self.index_dict

        # get first item from generator object
        google_find_id_dict = next(google_find_id_gen)

        imdb_title = google_find_id_dict.title
        imdb_url = google_find_id_dict.url

        # if title or url is none then return
        if not imdb_title or not imdb_url:

            self.index_dict.update({'result': 'failed', 'result_details': u"Failed to return results from Google for index title compare '%s'" % self.index_title_compare})
            return self.index_dict

        # find imdb title
        self.logger_instance.info(u"IMDb title is '%s'" % imdb_title)
        self.logger_instance.info(u"IMDb URL is '%s'" % imdb_url)

        # get comparison dictionary for imdb_title
        tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)
        imdb_title_compare = tools_various_instance.custom_title_compare(imdb_title)

        if imdb_title_compare not in self.index_title_compare:

            self.logger_instance.debug(u"IMDb title compare '%s' not in index title compare '%s'" % (imdb_title_compare, self.index_title_compare))
            self.index_dict.update({'result': 'failed', 'result_details': u"Failed to identify movie '%s' using Google search" % self.index_title_search})
            return self.index_dict

        self.logger_instance.debug(u"IMDb title compare '%s' matches index title compare '%s'" % (imdb_title_compare, self.index_title_compare))

        if self.index_year_compare not in imdb_title:

            self.logger_instance.debug(u"IMDb title '%s' does not contain index year compare '%s'" % (imdb_title, self.index_year_compare))
            self.index_dict.update({'result': 'failed', 'result_details': u"Failed to identify movie '%s' using Google search" % self.index_title_search})
            return self.index_dict

        self.logger_instance.debug(u"IMDb title '%s' does contain index year compare '%s'" % (imdb_title, self.index_year_compare))

        self.logger_instance.info(f"IMDb URL is '{imdb_url}'")

        self.index_dict.update({'imdb_id': imdb_id})

        self.index_dict.update({'result': 'success', 'result_details': u"Found IMDb ID for movie '%s' using Google search" % self.index_title_search})
        return self.index_dict
