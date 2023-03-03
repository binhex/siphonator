import json
import urllib.parse
import lib.siphonator.tools_downloader as siphonator_tools_downloader
import re


class SearchOMDb(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title_search = kwargs.get('index_title_search', None)
        self.index_title_compare = kwargs.get('index_title_compare', None)
        self.index_year_compare = kwargs.get('index_year_compare', None)
        self.search_site = 'OMDb'
        self.logger_instance = logger_instance

    def find_imdb_id_omdb(self):

        search_omdb_api_key = self.index_dict.get('search_omdb_api_key')
        index_title_search_encoded = urllib.parse.quote(self.index_title_search)
        omdb_title_regex_strip = r'[^a-zA-Z0-9]+'

        # generate url to find tmdb id number
        omdb_find_id_json_url = "http://www.omdbapi.com/?apikey=%s&t=%s&y=%s" % (search_omdb_api_key, index_title_search_encoded, self.index_year_compare)
        self.logger_instance.info(u"Find id URL is %s" % omdb_find_id_json_url)

        # download tmdb json (used for iphone/android)
        return_code, status_code, content = siphonator_tools_downloader.http_client(self.logger_instance, url=omdb_find_id_json_url, request_type='get')

        if return_code != 0:

            self.logger_instance.warning(u"Site feed download failed for %s" % self.search_site)
            self.index_dict.update({'result': 'failed', 'result_details': u"Site feed download failed for %s" % self.search_site})
            return self.index_dict

        try:

            omdb_find_id_json = json.loads(content)

        except (ValueError, TypeError, KeyError):

            self.logger_instance.warning(u"Site feed parse failed for %s" % self.search_site)
            self.index_dict.update({'result': 'failed', 'result_details': u"Site feed parse failed for %s" % self.search_site})
            return self.index_dict

        # if resulting tmdb json page is blank then continue
        if omdb_find_id_json is None or omdb_find_id_json == {}:

            self.logger_instance.info(u"Empty json returned from OMDb for index title search '%s'" % self.index_title_search)
            self.index_dict.update({'result': 'failed', 'result_details': u"Empty json returned from OMDb for index title search '%s'" % self.index_title_search})
            return self.index_dict

        try:

            omdb_title = omdb_find_id_json["Title"]

        except (IndexError, KeyError, TypeError):

            self.logger_instance.info(u"No title key in json for OMDb for index title search '%s'" % self.index_title_search)
            self.index_dict.update({'result': 'failed', 'result_details': u"No title key in json for OMDb for index title search '%s'" % self.index_title_search})
            return self.index_dict

        try:

            omdb_release_year = omdb_find_id_json["Year"]

        except (IndexError, KeyError, TypeError):

            self.logger_instance.info(u"No year key in json for OMDb for index title search '%s'" % self.index_title_search)
            self.index_dict.update({'result': 'failed', 'result_details': u"No year key in json for OMDb for index title search '%s'" % self.index_title_search})
            return self.index_dict

        omdb_title_compare = re.sub(omdb_title_regex_strip, '', omdb_title).lower()

        if omdb_title_compare not in self.index_title_compare:

            self.logger_instance.debug(u"OMDb title compare '%s' not in index title compare '%s', trying original title..." % (omdb_title_compare, self.index_title_compare))
            self.index_dict.update({'result': 'failed', 'result_details': u"OMDb title compare '%s' not in index title compare '%s', trying original title..." % (omdb_title_compare, self.index_title_compare)})
            return self.index_dict

        self.logger_instance.debug(u"OMDb title compare '%s' matches index title compare '%s'" % (omdb_title_compare, self.index_title_compare))

        # strip out non-numeric characters
        omdb_release_year = re.sub('\D+', '', omdb_release_year)

        if int(omdb_release_year) != int(self.index_year_compare):

            self.logger_instance.debug(u"OMDb year compare '%s' does not equal index year compare '%s'" % (omdb_release_year, self.index_year_compare))
            self.index_dict.update({'result': 'failed', 'result_details': u"OMDb year compare '%s' does not equal index year compare '%s'" % (omdb_release_year, self.index_year_compare)})
            return self.index_dict

        self.logger_instance.debug(u"OMDb year compare '%s' equals index year compare '%s'" % (omdb_release_year, self.index_year_compare))

        try:

            imdb_id = omdb_find_id_json["imdbID"]
            self.logger_instance.info(u"IMDb id is '%s'" % imdb_id)

        except (IndexError, KeyError, TypeError):

            self.logger_instance.info(u"Cannot find '%s' ID for movie" % self.search_site)
            self.index_dict.update({'result': 'failed', 'result_details': u"Cannot find '%s' ID for movie" % self.search_site})
            return self.index_dict

        if imdb_id is None or imdb_id == "":

            self.logger_instance.warning(u"%s index - IMDb ID is None, unable to identify valid value" % self.search_site)
            self.index_dict.update({'result': 'failed', 'result_details': u"%s index - IMDb ID is None, unable to identify valid value" % self.search_site})
            return self.index_dict

        self.logger_instance.info(u"IMDb ID URL is 'https://www.imdb.com/title/%s/'" % imdb_id)
        self.index_dict.update({'imdb_id': imdb_id})

        self.index_dict.update({'result': 'success', 'result_details': u"Found IMDb ID for movie '%s' using OMDb search" % self.index_title_search})
        return self.index_dict
