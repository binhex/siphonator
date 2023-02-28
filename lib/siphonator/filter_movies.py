from decimal import Decimal
import os
import re

# TODO maximum size, year filters
# TODO add in cast, director, writer, char filters
# TODO look for word match not partial for filter_bad_index_title, e.g. 'TS' should NOT match 'DTS'


class FilterMovies(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.logger_instance = logger_instance

    def filter_movies(self):

        self.index_dict.update({'good_movie': 'no'})

        filter_downloaded_result = self.filter_downloaded()
        filter_bad_index_title = self.filter_bad_index_title()
        filter_seeders_result = self.filter_seeders()
        filter_bitrate_result = self.filter_bitrate()

        filter_rating_result = self.filter_rating()
        filter_votes_result = self.filter_votes()
        filter_size_result = self.filter_size()
        filter_year_result = self.filter_year()
        filter_runtime_result = self.filter_runtime()


        filter_bad_movie_title = self.filter_bad_movie_title()

        if filter_rating_result and \
                filter_votes_result and \
                filter_size_result and \
                filter_year_result and \
                filter_runtime_result and \
                filter_seeders_result and \
                filter_bitrate_result and \
                filter_bad_index_title and \
                filter_bad_movie_title and \
                filter_downloaded_result:

            self.index_dict.update({'good_movie': 'yes'})
            self.logger_instance.info(u"SUCCESS! - Movie '%s' passed all filters" % self.index_dict.get('index_title'))

        return self.index_dict

    def filter_rating(self):

        get_rating = self.index_dict.get('rating')

        if get_rating is None:

            self.logger_instance.warning(u"No IMDb rating available to filter on")
            return False

        get_rating_dec = get_rating

        minimum_rating = '6.5'
        minimum_rating_dec = Decimal(minimum_rating)

        if get_rating_dec >= minimum_rating_dec:

            self.logger_instance.info(u"IMDb rating '%s' equal to/above threshold '%s'" % (get_rating, minimum_rating))
            return True

        else:

            self.logger_instance.warning(u"IMDb rating '%s' below threshold '%s'" % (get_rating, minimum_rating))
            return False

    def filter_votes(self):

        get_votes = self.index_dict.get('votes')

        if get_votes is None:

            self.logger_instance.warning(u"No IMDb votes available to filter on")
            return False

        get_votes_int = int(get_votes)

        minimum_votes = 7500
        minimum_votes_int = int(minimum_votes)

        if get_votes_int >= minimum_votes_int:

            self.logger_instance.info(u"IMDb votes '%s' equal to/above threshold '%s'" % (get_votes, minimum_votes))
            return True

        else:

            self.logger_instance.warning(u"IMDb votes '%s' below threshold '%s'" % (get_votes, minimum_votes))
            return False

    def filter_size(self):

        get_size = self.index_dict.get('index_size')

        if get_size is None:

            self.logger_instance.warning(u"No Index size available to filter on")
            return False

        get_size_int_mb = int(get_size)//1000000

        minimum_size_int_mb = int(5000)

        if get_size_int_mb >= minimum_size_int_mb:

            self.logger_instance.info(u"Index size '%s' (MB) equal to/above minimum size threshold '%s' (MB)" % (get_size_int_mb, minimum_size_int_mb))
            return True

        else:

            self.logger_instance.warning(u"Index size '%s' (MB) below minimum size threshold '%s' (MB)" % (get_size_int_mb, minimum_size_int_mb))
            return False

    def filter_bitrate(self):

        get_size = self.index_dict.get('index_size')
        get_runtime_in_minutes = self.index_dict.get('running_time_in_minutes')

        if get_size is None:

            self.logger_instance.warning(u"No Index size available to filter on")
            return False

        if get_runtime_in_minutes is None:

            self.logger_instance.warning(u"No movie runtime available to filter on")
            return False

        get_size_int_mb = int(get_size)//1000000
        get_runtime_int_mins = int(get_runtime_in_minutes)
        get_bitrate_int_mb = get_size_int_mb//get_runtime_int_mins

        minimum_bitrate_int_mb = int(50)

        if get_bitrate_int_mb >= minimum_bitrate_int_mb:

            self.logger_instance.info(u"Index bitrate '%s' (MB/min) equal to/above minimum bitrate threshold '%s' (MB/min)" % (get_bitrate_int_mb, minimum_bitrate_int_mb))
            return True

        else:

            self.logger_instance.warning(u"Index bitrate '%s' (MB/min) below minimum bitrate threshold '%s' (MB/min)" % (get_bitrate_int_mb, minimum_bitrate_int_mb))
            return False

    def filter_year(self):

        get_index_year_regex = self.index_dict.get('index_year_regex')
        get_filter_minimum_year = self.index_dict.get('filter_minimum_year')

        if get_index_year_regex is None:

            self.logger_instance.warning(u"No movie year available to filter on")
            return False

        get_index_year_regex_int = int(get_index_year_regex)
        get_minimum_year_int = int(get_filter_minimum_year)

        if get_index_year_regex_int >= get_minimum_year_int:

            self.logger_instance.info(u"Movie year '%s' equal to/above minimum year threshold '%s'" % (get_index_year_regex, get_filter_minimum_year))
            return True

        else:

            self.logger_instance.warning(u"Movie year '%s' below minimum year threshold '%s'" % (get_index_year_regex, get_filter_minimum_year))
            return False

    def filter_runtime(self):

        get_runtime_in_minutes = self.index_dict.get('running_time_in_minutes')
        get_filter_minimum_runtime_mins = self.index_dict.get('filter_minimum_runtime_mins')

        if get_runtime_in_minutes is None:

            self.logger_instance.warning(u"No movie runtime available to filter on")
            return False

        get_runtime_int_mins = int(get_runtime_in_minutes)
        get_filter_minimum_runtime_mins_int = int(get_filter_minimum_runtime_mins)

        if get_runtime_int_mins >= get_filter_minimum_runtime_mins_int:

            self.logger_instance.info(u"Movie runtime '%s' (mins) equal to/above minimum runtime threshold '%s' (mins)" % (get_runtime_int_mins, get_filter_minimum_runtime_mins_int))
            return True

        else:

            self.logger_instance.warning(u"Movie runtime '%s' (mins) below minimum runtime threshold '%s' (mins)" % (get_runtime_int_mins, get_filter_minimum_runtime_mins_int))
            return False

    def filter_seeders(self):

        get_seeders = self.index_dict.get('index_seeders')

        if get_seeders is None:

            self.logger_instance.warning(u"No Index seeders available to filter on, assuming equal to/above threshold")
            return True

        get_seeders_int = int(get_seeders)

        minimum_seeders_int = int(1)

        if get_seeders_int >= minimum_seeders_int:

            self.logger_instance.info(u"Index seeders '%s' equal to/above minimum seeders threshold '%s'" % (get_seeders_int, minimum_seeders_int))
            return True

        else:

            self.logger_instance.warning(u"Index seeders '%s' below minimum seeders threshold '%s'" % (get_seeders_int, minimum_seeders_int))
            return False

    def filter_downloaded(self):

        get_library_path = self.index_dict.get('library_path')
        get_index_title = self.index_dict.get('index_title')
        get_index_year_regex = self.index_dict.get('index_year_regex')
        get_index_title_regex = self.index_dict.get('index_title_regex')
        index_title_regex_compare = re.sub(r'\s|,|\.|_|-', "", get_index_title_regex).lower()

        # TODO store list of files in sqlite db or memory to speed up subsequent checks
        library_list = []

        for root, dirs, files in os.walk(get_library_path, topdown=False):

            for library_filename in files:

                library_title_compare = re.sub(r'\s|,|\.|_', "", library_filename).lower()

                if index_title_regex_compare in library_title_compare:

                    if get_index_year_regex in library_title_compare:

                        self.logger_instance.warning(u"Index title '%s' already exists in library '%s', skipping movie" % (get_index_title, library_filename))
                        return False

        return True

    def filter_bad_index_title(self):

        regex_compare = r'\.|,|_|-|\(\)|\[\]'
        get_index_title = self.index_dict.get('index_title')
        index_title_compare = re.sub(regex_compare, "", get_index_title).lower()
        get_filter_bad_title_list = self.index_dict.get('filter_bad_index_title_list')

        if get_filter_bad_title_list is None:

            return True

        for get_filter_bad_title in get_filter_bad_title_list:

            get_filter_bad_title = re.sub(regex_compare, "", get_filter_bad_title).lower()

            # use spaces to ensure exact match
            get_filter_bad_title_word_match = " %s " % get_filter_bad_title

            if get_filter_bad_title_word_match in index_title_compare:

                self.logger_instance.warning(u"Index title '%s' contains bad title keyword '%s', skipping movie" % (index_title_compare, get_filter_bad_title))
                return False

        self.logger_instance.info(u"Index title '%s' does NOT contain bad title keyword(s) '%s'" % (index_title_compare, get_filter_bad_title_list))
        return True

    def filter_bad_movie_title(self):

        regex_compare = r'\s|,|\.|_|-|\(\)|\[\]'
        get_index_title_regex = self.index_dict.get('index_title_regex')
        get_index_year_regex = self.index_dict.get('index_year_regex')
        index_title_regex_compare = re.sub(regex_compare, "", get_index_title_regex).lower()
        get_filter_bad_movie_title_list = self.index_dict.get('filter_bad_movie_title_list')

        if get_filter_bad_movie_title_list is None:

            return True

        for get_filter_bad_movie_title in get_filter_bad_movie_title_list:

            get_filter_bad_movie_title = re.sub(regex_compare, "", get_filter_bad_movie_title).lower()

            if index_title_regex_compare in get_filter_bad_movie_title:

                if get_index_year_regex in get_filter_bad_movie_title:

                    self.logger_instance.warning(u"Index movie title '%s' found in bad movie title list, skipping movie" % index_title_regex_compare)
                    return False

        self.logger_instance.info(u"Index movie title '%s (%s)' NOT found in bad movie list" % (get_index_title_regex, get_index_year_regex))
        return True
