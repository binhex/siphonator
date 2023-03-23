from decimal import Decimal
import re

# TODO add in cast, director, writer, bad genre
# TODO filter_override_downloaded - if repack or proper then check for on disk, if there then possible override
# TODO if remastered or extended or directors cut then check for on disk, if there then possible override
# TODO if in completed then do not download, or in qbittorrent queue, or in qbittorrent history (possible?)
# TODO if size of movie is larger on disk compared to index title then ignore, UNLESS its remastered, proper etc.

class FilterMovies(object):

    def __init__(self, logger_instance, **kwargs):

        self.index_dict = kwargs
        self.logger_instance = logger_instance
        self.regex_compare = r'\s|,|\.|_|-|\'|\!|[\(\)]|[\[\]]'

    def filter_index_movies(self):

        # Local/Index filters
        filter_size_result = self.filter_size('minimum')
        if not filter_size_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_size' (minimum)" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_size' (minimum)" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_size_result = self.filter_size('maximum')
        if not filter_size_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_size' (maximum)" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_size' (maximum)" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_bad_index_title = self.filter_bad_index_title()
        if not filter_bad_index_title:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_bad_index_title'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_bad_index_title'" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_bad_index_type = self.filter_bad_index_type()
        if not filter_bad_index_type:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_bad_index_type'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_bad_index_type'" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_bad_movie_title = self.filter_bad_movie_title()
        if not filter_bad_movie_title:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_bad_movie_title'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_bad_movie_title'" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_seeders_result = self.filter_seeders()
        if not filter_seeders_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_seeders'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_seeders'" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_downloaded_result = self.filter_downloaded()
        if not filter_downloaded_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_downloaded'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_downloaded'" % self.index_dict.get('index_title')})
            return self.index_dict

        self.logger_instance.debug(u"Index title '%s' passed index filters" % self.index_dict.get('index_title'))

        self.index_dict.update({'result': 'passed','result_details': u"Index title '%s' passed index filters" % self.index_dict.get('index_title')})
        return self.index_dict

    def filter_imdb_movies(self):

        # IMDb filters
        filter_bitrate_result = self.filter_bitrate()
        if not filter_bitrate_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_bitrate'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_bitrate'" % self.index_dict.get('index_title')})
            return self.index_dict

        # if override character bool is True then skip check for rating and votes
        filter_override_character = self.filter_override_character()
        if not filter_override_character:

            filter_rating_result = self.filter_rating()
            if not filter_rating_result:
                self.logger_instance.debug(u"Index title '%s' failed filter 'filter_rating'" % self.index_dict.get('index_title'))
                self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_rating'" % self.index_dict.get('index_title')})
                return self.index_dict

            filter_votes_result = self.filter_votes()
            if not filter_votes_result:
                self.logger_instance.debug(u"Index title '%s' failed filter 'filter_votes'" % self.index_dict.get('index_title'))
                self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_votes'" % self.index_dict.get('index_title')})
                return self.index_dict

        filter_year_result = self.filter_year()
        if not filter_year_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_year'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_year'" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_runtime_result = self.filter_runtime()
        if not filter_runtime_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_runtime'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_runtime'" % self.index_dict.get('index_title')})
            return self.index_dict

        filter_good_language_result = self.filter_good_language()
        if not filter_good_language_result:
            self.logger_instance.debug(u"Index title '%s' failed filter 'filter_good_language'" % self.index_dict.get('index_title'))
            self.index_dict.update({'result': 'failed', 'result_details': u"Index title '%s' failed filter 'filter_good_language'" % self.index_dict.get('index_title')})
            return self.index_dict

        # all filters passed mark as good movie
        self.index_dict.update({'good_movie': 'yes'})

        self.logger_instance.debug(u"Index title '%s' passed IMDb filters" % self.index_dict.get('index_title'))
        return self.index_dict

    def filter_genre_rating(self):

        imdb_genres_list = self.index_dict.get('imdb_genres_list')
        filter_genre_minimum_rating_dict = self.index_dict.get('filter_genre_minimum_rating_dict')

        # TODO regex to strip any wierd chars from imdb abd filter genre

        if filter_genre_minimum_rating_dict is not None:

            # sort by rating, lowest rating first
            filter_genre_minimum_rating_sorted = sorted(filter_genre_minimum_rating_dict.items(), key=lambda x: x[1])
            filter_genre_minimum_rating_sorted_dict = dict(filter_genre_minimum_rating_sorted)

            # loop over user defined dictionary of genre minimum ratings
            for genre_minimum_rating in filter_genre_minimum_rating_sorted_dict.keys():

                # loop over imdb genre list
                for imdb_genre in imdb_genres_list:

                    if genre_minimum_rating.lower() == imdb_genre.lower():

                        filter_genre_minimum_rating = filter_genre_minimum_rating_dict.get(genre_minimum_rating)
                        self.logger_instance.debug(u"Genre '%s' matches IMDb genre '%s', setting minimum IMDb rating to '%s'" % (genre_minimum_rating.lower(), imdb_genre.lower(), filter_genre_minimum_rating))
                        return filter_genre_minimum_rating

        return None

    def filter_rating(self):

        imdb_rating = self.index_dict.get('imdb_rating')
        filter_minimum_rating = self.index_dict.get('filter_minimum_rating')

        if imdb_rating is None:

            self.logger_instance.warning(u"No IMDb rating available to filter on, assuming below threshold")
            return False

        filter_genre_minimum_rating = self.filter_genre_rating()

        if filter_genre_minimum_rating is not None:

            filter_minimum_rating = filter_genre_minimum_rating

        minimum_rating_dec = Decimal(filter_minimum_rating)

        if imdb_rating >= minimum_rating_dec:

            self.logger_instance.info(u"IMDb rating '%s' equal to/above threshold '%s'" % (imdb_rating, filter_minimum_rating))
            return True

        else:

            self.logger_instance.warning(u"IMDb rating '%s' below threshold '%s'" % (imdb_rating, filter_minimum_rating))
            return False

    def filter_votes(self):

        imdb_votes = self.index_dict.get('imdb_votes')
        filter_minimum_votes = self.index_dict.get('filter_minimum_votes')

        if imdb_votes is None:

            self.logger_instance.warning(u"No IMDb votes available to filter on, assuming below threshold")
            return False

        imdb_votes_int = int(imdb_votes)

        minimum_votes_int = int(filter_minimum_votes)

        if imdb_votes_int >= minimum_votes_int:

            self.logger_instance.info(u"IMDb votes '%s' equal to/above threshold '%s'" % (imdb_votes, filter_minimum_votes))
            return True

        else:

            self.logger_instance.warning(u"IMDb votes '%s' below threshold '%s'" % (imdb_votes, filter_minimum_votes))
            return False

    def filter_size(self, size):

        index_size = self.index_dict.get('index_size')
        filter_size_mb = self.index_dict.get('filter_%s_size_mb' % size)

        if filter_size_mb == 0 or filter_size_mb is None:

            self.logger_instance.info(u"%s size not defined, skipping maximum size check" % size.capitalize())
            return True

        if index_size is None:

            self.logger_instance.warning(u"No Index size available to filter on, assuming below threshold")
            return False

        imdb_size_int_mb = int(index_size) // 1000000

        if size == "minimum":

            if imdb_size_int_mb >= filter_size_mb:

                self.logger_instance.info(u"Index size '%s' (MB) is within %s size threshold '%s' (MB)" % (imdb_size_int_mb, size, filter_size_mb))
                return True

            else:

                self.logger_instance.info(u"Index size '%s' (MB) not within %s size threshold '%s' (MB)" % (imdb_size_int_mb, size, filter_size_mb))
                return False

        if size == "maximum":

            if imdb_size_int_mb <= filter_size_mb:

                self.logger_instance.info(u"Index size '%s' (MB) is within %s size threshold '%s' (MB)" % (imdb_size_int_mb, size, filter_size_mb))
                return True

            else:

                self.logger_instance.info(u"Index size '%s' (MB) not within %s size threshold '%s' (MB)" % (imdb_size_int_mb, size, filter_size_mb))
                return False

    def filter_bitrate(self):

        index_size = self.index_dict.get('index_size')
        imdb_runtime_in_minutes = self.index_dict.get('imdb_running_time_in_minutes')
        filter_minimum_bitrate_mb = self.index_dict.get('filter_minimum_bitrate_mb')

        if index_size is None:

            self.logger_instance.warning(u"No Index size available to filter on, assuming below threshold")
            return False

        if imdb_runtime_in_minutes is None:

            self.logger_instance.warning(u"No movie runtime available to filter on, assuming below threshold")
            return False

        index_size_int_mb = int(index_size)//1000000
        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        imdb_bitrate_int_mb = index_size_int_mb//imdb_runtime_int_mins

        if imdb_bitrate_int_mb >= filter_minimum_bitrate_mb:

            self.logger_instance.info(u"Index bitrate '%s' (MB/min) equal to/above minimum bitrate threshold '%s' (MB/min)" % (imdb_bitrate_int_mb, filter_minimum_bitrate_mb))
            return True

        else:

            self.logger_instance.warning(u"Index bitrate '%s' (MB/min) below minimum bitrate threshold '%s' (MB/min)" % (imdb_bitrate_int_mb, filter_minimum_bitrate_mb))
            return False

    def filter_year(self):

        index_year_compare = self.index_dict.get('index_year_compare')
        filter_minimum_year = self.index_dict.get('filter_minimum_year')

        if index_year_compare is None:

            self.logger_instance.warning(u"No movie year available to filter on, assuming below threshold")
            return False

        index_year_compare_int = int(index_year_compare)
        filter_minimum_year_int = int(filter_minimum_year)

        if index_year_compare_int >= filter_minimum_year_int:

            self.logger_instance.info(u"Movie year '%s' equal to/above minimum year threshold '%s'" % (index_year_compare, filter_minimum_year))
            return True

        else:

            self.logger_instance.warning(u"Movie year '%s' below minimum year threshold '%s'" % (index_year_compare, filter_minimum_year))
            return False

    def filter_runtime(self):

        imdb_runtime_in_minutes = self.index_dict.get('imdb_running_time_in_minutes')
        filter_minimum_runtime_mins = self.index_dict.get('filter_minimum_runtime_mins')

        if imdb_runtime_in_minutes is None:

            self.logger_instance.warning(u"No movie runtime available to filter on, assuming below threshold")
            return False

        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        filter_minimum_runtime_mins_int = int(filter_minimum_runtime_mins)

        if imdb_runtime_int_mins >= filter_minimum_runtime_mins_int:

            self.logger_instance.info(u"Movie runtime '%s' (mins) equal to/above minimum runtime threshold '%s' (mins)" % (imdb_runtime_int_mins, filter_minimum_runtime_mins_int))
            return True

        else:

            self.logger_instance.warning(u"Movie runtime '%s' (mins) below minimum runtime threshold '%s' (mins)" % (imdb_runtime_int_mins, filter_minimum_runtime_mins_int))
            return False

    def filter_seeders(self):

        index_seeders = self.index_dict.get('index_seeders')
        filter_minimum_seeders = self.index_dict.get('filter_minimum_seeders')

        if index_seeders is None:

            self.logger_instance.warning(u"No Index seeders available to filter on, assuming equal to/above threshold")
            return True

        index_seeders_int = int(index_seeders)

        if index_seeders_int >= filter_minimum_seeders:

            self.logger_instance.info(u"Index seeders '%s' equal to/above minimum seeders threshold '%s'" % (index_seeders_int, filter_minimum_seeders))
            return True

        else:

            self.logger_instance.warning(u"Index seeders '%s' below minimum seeders threshold '%s'" % (index_seeders_int, filter_minimum_seeders))
            return False

    def filter_downloaded(self):

        filter_library_path_walk = self.index_dict.get('filter_library_path_walk')
        library_path = self.index_dict.get('library_path')
        index_title = self.index_dict.get('index_title')
        index_title_compare = self.index_dict.get('index_title_compare')
        index_year_compare = self.index_dict.get('index_year_compare')
        index_site_search = self.index_dict.get('index_site_search')
        index_site_search_list = index_site_search.split()

        self.logger_instance.debug(u"Index title compare is '%s'" % index_title_compare)
        self.logger_instance.debug(u"Index year compare is '%s'" % index_year_compare)

        for root, dirs, files in filter_library_path_walk:

            for library_filename in files:

                library_filename_compare_lower = re.sub(self.regex_compare, "", library_filename).lower()

                # check that index title is not in file in library
                if index_title_compare in library_filename_compare_lower:

                    # check that index year is not in file in library
                    if index_year_compare in library_filename_compare_lower:

                        # if all of the search items in the search list are present in the library filename then return false (already downloaded)
                        index_site_search_bool = all(index_site_search_item in library_filename_compare_lower for index_site_search_item in index_site_search_list)

                        if index_site_search_bool:

                            self.logger_instance.warning(u"Index title '%s' already exists in library file '%s', skipping movie" % (index_title, library_filename))
                            return False

        self.logger_instance.debug(u"Index title '%s' not found in library '%s', continue processing..." % (index_title, library_path))
        return True

    def filter_bad_index_title(self):

        index_title_regex = r'\.|_|\[|\]|\(|\)'
        index_title = self.index_dict.get('index_title')
        index_title_strip_lower = re.sub(index_title_regex, ' ', index_title).lower()
        self.logger_instance.debug(u"Index title for bad keyword comparison is '%s'" % index_title_strip_lower)

        filter_bad_title_list = self.index_dict.get('filter_bad_index_title_list')

        if filter_bad_title_list is None:

            return True

        for filter_bad_title in filter_bad_title_list:

            filter_bad_title_lower = re.sub(self.regex_compare, "", filter_bad_title).lower()

            # use spaces to ensure exact match
            filter_bad_title_word_match_lower = " %s " % filter_bad_title_lower

            if filter_bad_title_word_match_lower in index_title_strip_lower:

                self.logger_instance.warning(u"Index title '%s' contains bad title keyword '%s', skipping movie" % (index_title_strip_lower, filter_bad_title))
                return False

        self.logger_instance.info(u"Index title '%s' does NOT contain bad title keyword(s) '%s'" % (index_title_strip_lower, filter_bad_title_list))
        return True

    def filter_bad_movie_title(self):

        index_title_compare_lower = self.index_dict.get('index_title_compare')
        filter_bad_movie_title_list = self.index_dict.get('filter_bad_movie_title_list')

        if filter_bad_movie_title_list is None:

            return True

        for filter_bad_movie_title in filter_bad_movie_title_list:

            filter_bad_movie_title_lower = re.sub(self.regex_compare, "", filter_bad_movie_title).lower()

            if filter_bad_movie_title_lower in index_title_compare_lower:

                self.logger_instance.warning(u"Index title '%s' contains bad movie title '%s', skipping movie" % (index_title_compare_lower, filter_bad_movie_title_lower))
                return False

        self.logger_instance.info(u"Index title '%s' does NOT contain bad movie titles from list '%s'" % (index_title_compare_lower, filter_bad_movie_title_list))
        return True

    def filter_bad_index_type(self):

        index_title_year_to_end_compare = self.index_dict.get('index_title_year_to_end_compare')
        identify_tv_season_or_episode_regex = r'(season([\d]+)?)|s[\d]{2,3}(e[\d]{2,3})?'

        if re.search(identify_tv_season_or_episode_regex, index_title_year_to_end_compare):

            self.logger_instance.warning(u"Index title year to end '%s' contains tv series string match for regex '%s', skipping movie" % (index_title_year_to_end_compare, identify_tv_season_or_episode_regex))
            return False

        return True

    def filter_good_language(self):

        imdb_spoken_languages_list = self.index_dict.get('imdb_spoken_languages_list')
        filter_good_language_list = self.index_dict.get('filter_good_language_list')

        if filter_good_language_list is None:

            self.logger_instance.debug(u"IMDb good language not defined, skipping language checks")
            return True

        if imdb_spoken_languages_list is None:

            self.logger_instance.warning(u"IMDb spoken language not found, assuming language is OK")
            return True

        for filter_good_language in filter_good_language_list:

            if filter_good_language.lower() in imdb_spoken_languages_list:

                self.logger_instance.info(u"IMDb language '%s' is in good language list '%s'" % (imdb_spoken_languages_list, filter_good_language_list))
                return True

        self.logger_instance.debug(u"IMDb language '%s' is not in good language list '%s'" % (imdb_spoken_languages_list, filter_good_language_list))
        return False

    def filter_override_character(self):

        imdb_credits_character_list = self.index_dict.get('imdb_credits_character_list')
        filter_override_character_list = self.index_dict.get('filter_override_character_list')

        if filter_override_character_list is None:

            self.logger_instance.debug(u"Override character not defined, skipping character checks")
            return False

        if imdb_credits_character_list is None:

            self.logger_instance.warning(u"IMDb credits character not found, skipping character checks")
            return False

        imdb_credits_character_lower_list = [x.lower() for x in imdb_credits_character_list]
        filter_override_character_lower_list = [x.lower() for x in filter_override_character_list]

        for filter_override_character_lower in filter_override_character_lower_list:

            if filter_override_character_lower in imdb_credits_character_lower_list:

                self.logger_instance.info(u"Override character '%s' is in IMDb credits character list '%s', skipping votes and rating checks" % (filter_override_character_lower, imdb_credits_character_lower_list))
                return True

        self.logger_instance.debug(u"Override characters in list '%s' are NOT in IMDb credits character list '%s'" % (filter_override_character_lower_list, imdb_credits_character_lower_list))
        return False
