import re
import imdbpie

# fixme need to regex for Blade Runner 2049 (2017) as it is assuming year is 2049


class SearchIMDB(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.index_title = kwargs.get('index_title', None)
        self.search_site = 'IMDb'
        self.logger_instance = logger_instance
        self.index_title_regex = kwargs.get('index_title_regex', None)
        self.index_year_regex = kwargs.get('index_year_regex', None)

    def roman_to_dec(self, title):

        title = re.sub('\sI\s?$', '1', title)
        title = re.sub('\sII\s?$', '2', title)
        title = re.sub('\sIII\s?$', '3', title)
        title = re.sub('\sIV\s?$', '4', title)
        title = re.sub('\sV\s?$', '5', title)
        title = re.sub('\sVI\s?$', '6', title)
        title = re.sub('\sVII\s?$', '7', title)
        title = re.sub('\sVIII\s?$', '8', title)
        title = re.sub('\sIX\s?$', '9', title)
        title = re.sub('\sX\s?$', '10', title)

        return title

    def get_imdb_id(self):

        self.logger_instance.info(u"Searching '%s' for '%s'..." % (self.search_site, self.index_title_regex))

        imdb_instance = imdbpie.Imdb()

        try:
            imdb_title_search_list_dict = imdb_instance.search_for_title(self.index_title_regex)
        except AttributeError:
            self.logger_instance.warning(u"No match found for index title '%s' using search site '%s'" % (self.index_title_regex, self.search_site))
            return None

        if not imdb_title_search_list_dict:

            self.logger_instance.warning(u'%s did not return any results' % self.search_site)
            return None

        else:

            self.logger_instance.info(u'Results returned')

        strip_title_compare_regex = re.compile('[-()/:;*?"<>|.,`~!%_\'\s]+')
        title_clean_regex = re.compile('[/:*?"<>|]+')

        index_title_roman = self.roman_to_dec(self.index_title_regex)
        index_title_regex_compare = re.sub(strip_title_compare_regex, '', index_title_roman)
        index_title_regex_compare = re.sub('and|And', '&', index_title_regex_compare)

        # loop over list of dicts with possible match
        for i in imdb_title_search_list_dict:

            imdb_title = i.get("title")
            imdb_year = i.get("year")

            self.logger_instance.debug(u'%s title possible match is %s %s' % (self.search_site, imdb_title, imdb_year))

            if imdb_year == self.index_year_regex:

                if imdb_title:

                    imdb_title_compare = self.roman_to_dec(imdb_title)
                    imdb_title_compare = re.sub(strip_title_compare_regex, '', imdb_title_compare)
                    imdb_title_compare = re.sub('and|And', '&', imdb_title_compare)
                    imdb_title_clean = re.sub(title_clean_regex, '', imdb_title)

                    if imdb_title_compare.lower() == index_title_regex_compare.lower():

                        imdb_year = i.get("year")
                        imdb_id = i.get("imdb_id")

                        self.index_dict.update({'imdb_title': imdb_title_clean, 'imdb_id': imdb_id, 'imdb_year': imdb_year})
                        self.logger_instance.info(u"%s year '%s' and download year regex '%s' match for %s title '%s'" % (self.search_site, imdb_year, self.index_year_regex, self.search_site, imdb_title))
                        self.logger_instance.info(u"IMDb ID for movie '%s' is '%s'" % (imdb_title, imdb_id))

                        return self.index_dict

                    else:

                        self.logger_instance.info(u'%s title %s and download title regex %s do not match' % (self.search_site, imdb_title_compare, index_title_regex_compare))
                else:

                    # unable to get title - bad data from IMDb site?
                    self.logger_instance.warning(u'No title returned from %s' % self.search_site)
                    return None

            else:

                self.logger_instance.debug(u'%s year %s and download year regex %s do not match' % (self.search_site, imdb_year, self.index_year_regex))

        self.logger_instance.warning(u'No match found using %s search' % self.search_site)
        return None
