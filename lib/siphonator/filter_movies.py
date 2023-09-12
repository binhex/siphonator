import os
import re
from decimal import Decimal
import lib.siphonator.tools_various as siphonator_tools_various

# TODO bad group list, start with SLOT?


class FilterMovies(object):

    def __init__(self, logger_instance, init_dict, result_dict, config_dict):

        self.init_dict = init_dict
        self.result_dict = result_dict
        self.config_dict = config_dict
        self.logger_instance = logger_instance
        self.tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)

    def filter_index_movies(self):

        self.result_dict.update({'result': 'failed'})
        # Local/Index filters
        filter_size_result = self.filter_size('minimum')
        if not filter_size_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_size' (minimum)")
            self.result_dict.update({'result_details': u"Failed index filter 'filter_size' (minimum)"})
            return self.result_dict

        filter_size_result = self.filter_size('maximum')
        if not filter_size_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_size' (maximum)")
            self.result_dict.update({'result_details': u"Failed index filter 'filter_size' (maximum)"})
            return self.result_dict

        filter_bad_index_title = self.filter_bad_index_title()
        if not filter_bad_index_title:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_bad_index_title'")
            self.result_dict.update({'result_details': u"Failed index filter 'filter_bad_index_title'"})
            return self.result_dict

        filter_bad_index_type = self.filter_bad_index_type()
        if not filter_bad_index_type:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_bad_index_type'")
            self.result_dict.update({'result_details': u"Failed index filter 'filter_bad_index_type'"})
            return self.result_dict

        filter_bad_movie_title = self.filter_bad_movie_title()
        if not filter_bad_movie_title:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_bad_movie_title'")
            self.result_dict.update({'result_details': u"Failed index filter 'filter_bad_movie_title'"})
            return self.result_dict

        # if library file returns false then file exists in library
        filter_downloaded_file_result = self.filter_downloaded_file()
        if not filter_downloaded_file_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_downloaded_file'")
            self.result_dict.update({'result_details': u"Failed index filter 'filter_downloaded_file'"})
            return self.result_dict
        # if library file looks to be missing then get movie title from directory name and get resolution using ffprobe (if resolution missing from filename)
        else:
            filter_downloaded_dir_result = self.filter_downloaded_dir()
            if not filter_downloaded_dir_result:
                self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_downloaded_dir'")
                self.result_dict.update({'result_details': u"Failed index filter 'filter_downloaded_dir'"})
                return self.result_dict

        self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' passed all index filters")
        self.result_dict.update({'result': 'index passed'})

        return self.result_dict

    def filter_imdb_movies(self):

        self.result_dict.update({'result': 'failed'})

        filter_bad_genre_result = self.filter_bad_genre()
        if not filter_bad_genre_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_bad_genre'")
            self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_bad_genre'"})
            return self.result_dict

        filter_bitrate_result = self.filter_bitrate()
        if not filter_bitrate_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_bitrate'")
            self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_bitrate'"})
            return self.result_dict

        filter_year_result = self.filter_year()
        if not filter_year_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_year'")
            self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_year'"})
            return self.result_dict

        filter_runtime_result = self.filter_runtime()
        if not filter_runtime_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_runtime'")
            self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_runtime'"})
            return self.result_dict

        filter_good_language_result = self.filter_good_language_country('language')
        if not filter_good_language_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_good_language_country' for filter type 'language'")
            self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_good_language_country' for filter type 'language'"})
            return self.result_dict

        filter_good_country_result = self.filter_good_language_country('country')
        if not filter_good_country_result:
            self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_good_language_country' for filter type 'country'")
            self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_good_language_country' for filter type 'country'"})
            return self.result_dict

        filter_override_character = self.filter_override_person('character')

        if not filter_override_character:
            filter_override_director = self.filter_override_person('director')

            if not filter_override_director:
                filter_override_writer = self.filter_override_person('writer')

                if not filter_override_writer:
                    filter_override_cast = self.filter_override_person('cast')

                    if not filter_override_cast:
                        filter_override_movie_title = self.filter_override_movie_title()

                        if not filter_override_movie_title:

                            filter_rating_result = self.filter_rating()
                            if not filter_rating_result:
                                self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_rating'")
                                self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_rating'"})
                                return self.result_dict

                            filter_votes_result = self.filter_votes()
                            if not filter_votes_result:
                                self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' failed filter 'filter_votes'")
                                self.result_dict.update({'result_details': u"Failed IMDb filter 'filter_votes'"})
                                return self.result_dict

        self.logger_instance.debug(f"Index title '{self.result_dict.get('index_title')}' passed all IMDb filters")
        self.result_dict.update({'result': 'imdb passed'})

        return self.result_dict

    def filter_genre_rating(self):

        imdb_genres_list = self.result_dict.get('imdb_genres_list')
        filter_genre_minimum_rating_dict = self.config_dict['filters']['genre_minimum_rating_dict']

        if imdb_genres_list is None:

            self.logger_instance.debug(u"IMDb genre not found, skipping filter genre rating")
            return None

        if filter_genre_minimum_rating_dict is None:

            self.logger_instance.debug(u"No genre minimum rating defined, skipping filter genre rating")
            return None

        # sort by rating, lowest rating first
        filter_genre_minimum_rating_sorted = sorted(filter_genre_minimum_rating_dict.items(), key=lambda x: x[1])
        filter_genre_minimum_rating_sorted_dict = dict(filter_genre_minimum_rating_sorted)

        # loop over user defined dictionary of genre minimum ratings
        for genre_minimum_rating in filter_genre_minimum_rating_sorted_dict.keys():

            # loop over imdb genre list
            for imdb_genre in imdb_genres_list:

                if genre_minimum_rating.lower() == imdb_genre.lower():

                    filter_genre_minimum_rating = filter_genre_minimum_rating_dict.get(genre_minimum_rating)
                    self.logger_instance.debug(f"Genre '{genre_minimum_rating.lower()}' matches IMDb genre '{imdb_genre.lower()}', setting minimum IMDb rating to '{filter_genre_minimum_rating}'")
                    return filter_genre_minimum_rating

    def filter_rating(self):

        imdb_rating = self.result_dict.get('imdb_rating')
        filter_minimum_rating = self.config_dict['filters']['minimum_rating']
        filter_genre_minimum_rating = self.filter_genre_rating()

        if filter_minimum_rating is None:

            self.logger_instance.debug(u"No IMDb minimum rating defined, assuming above threshold")
            return True

        filter_minimum_rating_dec = Decimal(filter_minimum_rating)
        if filter_minimum_rating_dec > Decimal('10.0'):

            self.logger_instance.debug(f"IMDb rating defined as '{filter_minimum_rating}' is greater than the maximum value of 10.0, assuming above threshold")
            return True

        if imdb_rating is None:

            self.logger_instance.debug(u"No IMDb rating available to filter on, assuming below threshold")
            return False

        # if override rating for genre found then specify as minimum rating
        if filter_genre_minimum_rating is not None:

            filter_minimum_rating = filter_genre_minimum_rating

        filter_minimum_rating_dec = Decimal(filter_minimum_rating)
        if imdb_rating >= filter_minimum_rating_dec:

            self.logger_instance.info(f"IMDb rating '{imdb_rating}' equal to/above threshold '{filter_minimum_rating}'")
            return True

        else:

            self.logger_instance.warning(f"IMDb rating '{imdb_rating}' below threshold '{filter_minimum_rating}'")
            return False

    def filter_votes(self):

        imdb_votes = self.result_dict.get('imdb_votes')
        filter_minimum_votes = self.config_dict['filters']['minimum_votes']

        if filter_minimum_votes is None:

            self.logger_instance.info(u"No IMDb minimum votes defined, skipping votes check")
            return True

        if imdb_votes is None:

            self.logger_instance.warning(u"No IMDb votes available to filter on, assuming below threshold")
            return False

        imdb_votes_int = int(imdb_votes)

        minimum_votes_int = int(filter_minimum_votes)

        if imdb_votes_int >= minimum_votes_int:

            self.logger_instance.info(f"IMDb votes '{imdb_votes}' equal to/above threshold '{filter_minimum_votes}'")
            return True

        else:

            self.logger_instance.warning(f"IMDb votes '{imdb_votes}' below threshold '{filter_minimum_votes}'")
            return False

    def filter_size(self, size):

        index_size = self.result_dict.get('index_size')
        filter_size_mb = self.result_dict.get(f'filter_{size}_size_mb')

        if filter_size_mb is None:

            self.logger_instance.info(f"'{size.capitalize()}' size not defined, skipping maximum size check")
            return True

        if index_size is None:

            self.logger_instance.warning(u"No Index size available to filter on, assuming below threshold")
            return False

        imdb_size_int_mb = int(index_size) // 1000000

        if size == "minimum":

            if imdb_size_int_mb >= filter_size_mb:

                self.logger_instance.info(f"Index size '{imdb_size_int_mb}' (MB) is within '{size}' size threshold '{filter_size_mb}' (MB)")
                return True

            else:

                self.logger_instance.info(f"Index size '{imdb_size_int_mb}' (MB) not within '{size}' size threshold '{filter_size_mb}' (MB)")
                return False

        if size == "maximum":

            if imdb_size_int_mb <= filter_size_mb:

                self.logger_instance.info(f"Index size '{imdb_size_int_mb}' (MB) is within '{size}' size threshold '{filter_size_mb}' (MB)")
                return True

            else:

                self.logger_instance.info(f"Index size '{imdb_size_int_mb}' (MB) not within '{size}' size threshold '{filter_size_mb}' (MB)")
                return False

    def filter_bitrate(self):

        index_size = self.result_dict.get('index_size')
        imdb_runtime_in_minutes = self.result_dict.get('imdb_running_time_in_minutes')
        filter_minimum_bitrate_mb = self.result_dict.get('filter_minimum_bitrate_mb')

        if filter_minimum_bitrate_mb is None:

            self.logger_instance.warning(u"No minimum bitrate defined, assuming above threshold")
            return True

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

            self.logger_instance.info(f"Index bitrate '{imdb_bitrate_int_mb}' (MB/min) equal to/above minimum bitrate threshold '{filter_minimum_bitrate_mb}' (MB/min)")
            return True

        else:

            self.logger_instance.warning(f"Index bitrate '{imdb_bitrate_int_mb}' (MB/min) below minimum bitrate threshold '{filter_minimum_bitrate_mb}' (MB/min)")
            return False

    def filter_year(self):

        index_year_compare = self.result_dict.get('index_year_compare')
        filter_minimum_year = self.config_dict['filters']['minimum_year']

        if filter_minimum_year is None:

            self.logger_instance.warning(u"No minimum movie year defined, assuming above threshold")
            return True

        if index_year_compare is None:

            self.logger_instance.warning(u"No movie year available to filter on, assuming below threshold")
            return False

        index_year_compare_int = int(index_year_compare)
        filter_minimum_year_int = int(filter_minimum_year)

        if index_year_compare_int >= filter_minimum_year_int:

            self.logger_instance.info(f"Movie year '{index_year_compare}' equal to/above minimum year threshold '{filter_minimum_year}'")
            return True

        else:

            self.logger_instance.warning(f"Movie year '{index_year_compare}' below minimum year threshold '{filter_minimum_year}'")
            return False

    def filter_runtime(self):

        imdb_runtime_in_minutes = self.result_dict.get('imdb_running_time_in_minutes')
        filter_minimum_runtime_mins = self.config_dict['filters']['minimum_runtime_mins']

        if filter_minimum_runtime_mins is None:

            self.logger_instance.warning(u"No minimum runtime defined, assuming above threshold")
            return True

        if imdb_runtime_in_minutes is None:

            self.logger_instance.warning(u"No movie runtime available to filter on, assuming below threshold")
            return False

        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        filter_minimum_runtime_mins_int = int(filter_minimum_runtime_mins)

        if imdb_runtime_int_mins >= filter_minimum_runtime_mins_int:

            self.logger_instance.info(f"Movie runtime '{imdb_runtime_int_mins}' (mins) equal to/above minimum runtime threshold '{filter_minimum_runtime_mins_int}' (mins)")
            return True

        else:

            self.logger_instance.warning(f"Movie runtime '{imdb_runtime_int_mins}' (mins) below minimum runtime threshold '{filter_minimum_runtime_mins_int}' (mins)")
            return False

    def filter_downloaded_file(self):

        filter_library_path_walk = self.result_dict.get('filter_library_path_walk')
        library_path = self.config_dict['general']['library_path']
        index_title = self.result_dict.get('index_title')
        index_title_compare = self.result_dict.get('index_title_compare')
        index_year_compare = self.result_dict.get('index_year_compare')
        index_site_search = self.result_dict.get('index_site_search')
        index_site_search_list = index_site_search.split()

        if filter_library_path_walk is None:

            self.logger_instance.warning(u"No library path defined, assuming movie is not present in library")
            return True

        self.logger_instance.debug(f"Index title compare is '{index_title_compare}'")
        self.logger_instance.debug(f"Index year compare is '{index_year_compare}'")

        for root, dirs, files in filter_library_path_walk:

            for library_filename in files:

                # TODO this is a kludge, can we do better?
                # if the file format is not video then go to next iter
                if not library_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
                    continue

                # get library filename compare strings using tools various
                library_filename_title_compare = self.tools_various_instance.custom_title_compare(library_filename)
                library_filename_title_full_compare = self.tools_various_instance.custom_title_full_compare(library_filename)
                library_filename_year_compare = self.tools_various_instance.custom_title_year_compare(library_filename)

                # if we cannot determine the year then go to next iter
                if library_filename_year_compare is None:
                    continue

                # if library filename title compare in index title compare then continue towards false (already downloaded)
                if library_filename_title_compare in index_title_compare:

                    # if library filename title compare in index title year compare then continue towards false (already downloaded)
                    if library_filename_year_compare in index_year_compare:

                        # if all index site search items are in the library filename then continue towards false (already downloaded)
                        if all(index_site_search_item in library_filename_title_full_compare for index_site_search_item in index_site_search_list):

                            # if preferred group is not present in index title or library file already exists with preferred group then continue towards false (already downloaded)
                            if not self.filter_preferred_index_group(library_filename, index_title):

                                # if preferred index quality is not present in index title or library file already exists with preferred index quality then continue towards false (already downloaded)
                                if not self.filter_preferred_index_quality(library_filename, index_title):

                                    self.logger_instance.info(f"Index title '{index_title}' already exists in library file '{library_filename}', skipping movie")
                                    return False

        self.logger_instance.debug(f"Index title '{index_title}' not found in library filenames for library path '{library_path}', continue processing...")
        return True

    def filter_downloaded_file_search_criteria(self, library_filename, library_filepath):

        index_site_search = self.result_dict.get('index_site_search')
        ffprobe_filepath = self.init_dict.get('ffprobe_filepath')
        index_site_search_list = index_site_search.split()
        library_filename_title_full_compare = self.tools_various_instance.custom_title_full_compare(library_filename)

        for index_site_search_item in index_site_search_list:

            if index_site_search_item not in library_filename_title_full_compare:

                index_site_search_item_resolution, index_site_search_item_resolution_numeric = self.tools_various_instance.resolution_from_string(index_site_search_item)

                # check if missing index site search item from library filename is resolution e.g. '1080p' (only item we can calculate, else assume file is missing from library)
                if index_site_search_item_resolution is not None:

                    # get resolution of library file by analysing file using ffprobe
                    library_filepath_height_resolution_numeric = self.tools_various_instance.resolution_from_ffprobe(library_filepath, ffprobe_filepath)

                    if library_filepath_height_resolution_numeric is None:

                        self.logger_instance.debug(f"Unable to determine resolution from ffprobe for library file '{library_filename}', continue processing...")
                        return True

                    self.logger_instance.debug(f"Library file resolution identified as '{library_filepath_height_resolution_numeric}' for library file '{library_filename}'")

                    # if integer of library filename resolution numeric is less than integer of index title resolution numeric then continue
                    if int(library_filepath_height_resolution_numeric) < int(index_site_search_item_resolution_numeric):

                        self.logger_instance.debug(f"Library file resolution '{library_filepath_height_resolution_numeric}' is less than resolution for index title '{index_site_search_item_resolution_numeric}', continue processing...")
                        return True

                else:

                    self.logger_instance.debug(f"Unable to determine missing index site search item '{index_site_search_item}' from library filename '{library_filename}', continue processing...")
                    return True

        self.logger_instance.debug(f"Index site search criteria '{index_site_search_list}' found in library filename '{library_filename}', skipping movie")
        return False

    def filter_downloaded_dir(self):

        # check index title against existing library directories, if match found then analyze library file to
        # determine the resolution to see if it matches the search criteria, if it does match ALL the search
        # criteria then return false (movies already downloaded)

        filter_library_path_walk = self.result_dict.get('filter_library_path_walk')
        library_path = self.config_dict['general']['library_path']
        index_title = self.result_dict.get('index_title')
        index_title_compare = self.result_dict.get('index_title_compare')
        index_year_compare = self.result_dict.get('index_year_compare')

        if filter_library_path_walk is None:

            self.logger_instance.warning(u"No library path defined, assuming movie is not present in library")
            return True

        self.logger_instance.debug(f"Index title compare is '{index_title_compare}'")
        self.logger_instance.debug(f"Index year compare is '{index_year_compare}'")

        for root, dirs, files in filter_library_path_walk:

            for library_dirs in dirs:

                # get library directory compare strings using tools various
                library_dirs_title_compare = self.tools_various_instance.custom_title_compare(library_dirs)
                library_dir_year_compare = self.tools_various_instance.custom_title_year_compare(library_dirs)

                # if we cannot determine the year then go to next iter
                if library_dir_year_compare is None:
                    continue

                # if library directory title compare in index title compare then continue towards false (already downloaded)
                if library_dirs_title_compare in index_title_compare:

                    # if library directory year compare in index title year compare then continue towards false (already downloaded)
                    if library_dir_year_compare in index_year_compare:

                        # if index title and index year in directory name then look at filename for search criteria

                        # construct absolute library path
                        library_dirs_abs_path = os.path.join(root, library_dirs)

                        # walk absolute path
                        library_dirs_abs_path_gen = self.tools_various_instance.library_path_walk(library_dirs_abs_path)

                        # loop over generator absolute path
                        for sub_root, sub_dirs, sub_files in library_dirs_abs_path_gen:

                            for library_sub_file in sub_files:

                                # TODO this is a kludge, can we do better?
                                # only check video container formats
                                if library_sub_file.lower().endswith(('.mkv', '.mp4', '.avi')):

                                    # get full path to filename
                                    library_dirs_abs_filepath = os.path.join(library_dirs_abs_path, library_sub_file)

                                    # if library file contains all search criteria then mark as already in library
                                    if not self.filter_downloaded_file_search_criteria(library_sub_file, library_dirs_abs_filepath):

                                        self.logger_instance.debug(f"Index title '{index_title}' already exists in library directory '{library_dirs}', skipping movie")
                                        return False

        self.logger_instance.debug(f"Index title '{index_title}' not found in library directories for library path '{library_path}'")
        return True

    def filter_bad_genre(self):

        imdb_genres_list = self.result_dict.get('imdb_genres_list')
        filter_bad_genre_list = self.config_dict["filters"]['bad_genre_list']

        if filter_bad_genre_list is None:

            self.logger_instance.debug(u"No bad genre(s) defined, skipping bad genre check")
            return True

        if imdb_genres_list is None:

            self.logger_instance.debug(u"No IMDb genre(s) found, skipping bad genre check")
            return True

        imdb_genres_list_lower = [x.lower() for x in imdb_genres_list]
        filter_bad_genre_list_lower = [x.lower() for x in filter_bad_genre_list]

        for filter_bad_genre in filter_bad_genre_list_lower:

            if filter_bad_genre in imdb_genres_list_lower:

                self.logger_instance.info(f"IMDb genre(s) '{imdb_genres_list_lower}' match bad genre(s) list '{filter_bad_genre_list_lower}', skipping movie")
                return False

        self.logger_instance.info(f"IMDb genre(s) '{imdb_genres_list_lower}' does NOT match any of the bad genre(s) '{filter_bad_genre_list_lower}'")
        return True

    def filter_bad_index_title(self):

        index_title = self.result_dict.get('index_title')
        filter_bad_title_list = self.config_dict["filters"]['bad_index_title_list']

        if filter_bad_title_list is None:

            self.logger_instance.debug(u"No bad index title keywords defined, skipping bad index title keyword check")
            return True

        # get bad index title compare using tools various
        index_title_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(index_title)

        self.logger_instance.debug(f"Index title for bad keyword comparison is '{index_title_year_to_end_compare}'")

        for filter_bad_title in filter_bad_title_list:

            filter_bad_title_lower_search = self.tools_various_instance.custom_bad_keyword_search(index_title_year_to_end_compare, filter_bad_title)

            if filter_bad_title_lower_search:

                self.logger_instance.warning(f"Index title '{index_title_year_to_end_compare}' contains bad title keyword '{filter_bad_title}', skipping movie")
                return False

        self.logger_instance.info(f"Index title '{index_title_year_to_end_compare}' does NOT contain bad title keyword(s) '{filter_bad_title_list}'")
        return True

    def filter_bad_movie_title(self):

        index_title_and_year_compare = self.result_dict.get('index_title_and_year_compare')
        filter_bad_movie_title_list = self.config_dict["filters"]['bad_movie_title_list']

        if filter_bad_movie_title_list is None:

            self.logger_instance.warning(u"No bad movie titles defined, skipping bad movie title check")
            return True

        for filter_bad_movie_title in filter_bad_movie_title_list:

            # get bad movie title compare using tools various
            filter_bad_movie_title_full_compare = self.tools_various_instance.custom_title_full_compare(filter_bad_movie_title)

            if filter_bad_movie_title_full_compare in index_title_and_year_compare:

                self.logger_instance.warning(f"Index title '{index_title_and_year_compare}' contains bad movie title '{filter_bad_movie_title_full_compare}', skipping movie")
                return False

        self.logger_instance.info(f"Index title '{index_title_and_year_compare}' does NOT match any bad movie titles in list")
        return True

    def filter_bad_index_type(self):

        index_title = self.result_dict.get('index_title')
        index_title_tv_season_episode = self.tools_various_instance.custom_title_tv_season_episode(index_title)

        if not index_title_tv_season_episode:

            self.logger_instance.warning(f"Index title '{index_title}' contains tv season or episode string match for regex, skipping movie")
            return False

        return True

    def filter_good_language_country(self, filter_type):

        imdb_list = self.result_dict.get(f'imdb_{filter_type}_list')
        filter_list = self.config_dict["filters"][f"good_{filter_type}_list"]

        if filter_list is None:

            self.logger_instance.debug(f"Filter for '{filter_type}' not defined, skipping '{filter_type}' checks")
            return True

        if imdb_list is None:

            self.logger_instance.warning(f"IMDb '{filter_type}' not found, assuming '{filter_type}' is OK")
            return True

        imdb_lower_list = [x.lower() for x in imdb_list]
        filter_lower_list = [x.lower() for x in filter_list]

        for filter_lower_item in filter_lower_list:

            if filter_lower_item in imdb_lower_list:

                self.logger_instance.info(f"IMDb '{filter_type}' list '{imdb_lower_list}' is in good '{filter_type}' list '{filter_lower_list}'")
                return True

        self.logger_instance.debug(f"IMDb '{filter_type}' list '{imdb_lower_list}' is not in good '{filter_type}' list '{filter_lower_list}'")
        return False

    def filter_preferred_index_group(self, library_filename, index_title):

        filter_preferred_index_group_list = self.config_dict["filters"]['preferred_index_group_list']

        if filter_preferred_index_group_list is None:

            self.logger_instance.info(u"No preferred index groups defined, skipping preferred index group check")
            return False

        filter_preferred_index_group_lower_list = [x.lower() for x in filter_preferred_index_group_list]

        library_filename_group = self.tools_various_instance.custom_title_group_compare(library_filename)
        index_title_group = self.tools_various_instance.custom_title_group_compare(index_title)

        self.logger_instance.debug(f"Filter preferred index group list is '{filter_preferred_index_group_lower_list}'")
        self.logger_instance.debug(f"Library filename group is '{library_filename_group}'")
        self.logger_instance.debug(f"Index title group is '{index_title_group}'")

        # if library filename already matches one of the preferred index groups then return False (no need to dl again)
        if library_filename_group in filter_preferred_index_group_lower_list:

            self.logger_instance.info(f"Library filename group '{library_filename_group}' is in preferred index group list '{filter_preferred_index_group_lower_list}'")
            return False

        # if index title group is not in preferred index group list then return False (not preferred group)
        if index_title_group not in filter_preferred_index_group_lower_list:

            self.logger_instance.info(f"Index title group '{index_title_group}' is not in preferred index group list '{filter_preferred_index_group_lower_list}'")
            return False

        self.logger_instance.info(f"Index title group '{index_title_group}' is in preferred index group list '{filter_preferred_index_group_lower_list}' and library filename group '{library_filename_group}' is not preferred, ignoring existing library file,")
        return True

    def filter_preferred_index_quality(self, library_filename, index_title):

        filter_preferred_index_quality_list = self.config_dict["filters"]['preferred_index_quality_list']

        if not filter_preferred_index_quality_list:

            self.logger_instance.info(u"No preferred index quality defined, skipping preferred index quality check")
            return False

        library_filename_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(library_filename)
        library_filename_year_to_end_compare_convert_separators_to_spaces = self.tools_various_instance.custom_title_search(library_filename_year_to_end_compare)

        index_title_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(index_title)
        index_title_year_to_end_compare_convert_separators_to_spaces = self.tools_various_instance.custom_title_search(index_title_year_to_end_compare)

        self.logger_instance.debug(f"Filter preferred index quality list is '{filter_preferred_index_quality_list}'")

        for filter_preferred_index_quality in filter_preferred_index_quality_list:

            filter_preferred_index_quality_lower = filter_preferred_index_quality.lower()
            filter_preferred_index_quality_lower_convert_separators_to_spaces = self.tools_various_instance.custom_title_search(filter_preferred_index_quality_lower)
            filter_preferred_index_quality_lower_convert_separators_to_spaces_search = re.search(rf'[\s._-]{filter_preferred_index_quality_lower_convert_separators_to_spaces}[\s._-]', index_title_year_to_end_compare_convert_separators_to_spaces)

            if filter_preferred_index_quality_lower_convert_separators_to_spaces_search:

                self.logger_instance.info(f"Index title '{index_title}' does contain preferred quality keyword '{filter_preferred_index_quality}'")

                filter_preferred_index_quality_lower_search = re.search(rf'[\s._-]{filter_preferred_index_quality_lower_convert_separators_to_spaces}[\s._-]', library_filename_year_to_end_compare_convert_separators_to_spaces)

                if filter_preferred_index_quality_lower_search:

                    self.logger_instance.info(f"Library filename '{library_filename}' contains preferred quality keyword '{filter_preferred_index_quality}'")
                    return False

                else:

                    self.logger_instance.info(f"Index title '{index_title}' does include keyword from preferred index quality list '{filter_preferred_index_quality_list}' and library filename '{library_filename}' does not contain keyword from preferred quality list, ignoring existing library file,")
                    return True

        self.logger_instance.info(f"Index title '{index_title}' does not contain any keywords from the preferred quality list '{filter_preferred_index_quality_list}'")
        return False

    def filter_override_person(self, filter_type):

        imdb_list = self.result_dict.get(f'imdb_credits_{filter_type}_list' % filter_type)
        filter_list = self.config_dict["filters"][f"override_{filter_type}_list"]

        if filter_list is None:

            self.logger_instance.debug(f"Filter for '{filter_type}' not defined, skipping '{filter_type}' checks")
            return False

        if imdb_list is None:

            self.logger_instance.warning(f"IMDb '{filter_type}' not found, assuming '{filter_type}' is OK")
            return False

        imdb_lower_list = [x.lower() for x in imdb_list]
        filter_lower_list = [x.lower() for x in filter_list]

        for filter_lower_item in filter_lower_list:

            if filter_lower_item in imdb_lower_list:

                self.logger_instance.info(f"IMDb '{filter_type}' list '{imdb_list}' is in good '{filter_type}' list '{filter_list}', skipping votes and rating checks")
                return True

        self.logger_instance.debug(f"IMDb '{filter_type}' list '{imdb_list}' is not in good '{filter_type}' list '{filter_list}'")
        return False

    def filter_override_movie_title(self):

        index_title_and_year_compare = self.result_dict.get('index_title_and_year_compare')
        filter_override_movie_title_list = self.config_dict["filters"]['override_movie_title_list']

        if filter_override_movie_title_list is None:

            self.logger_instance.debug(u"Override movie title not defined, assuming movie title is not in override list")
            return False

        if index_title_and_year_compare is None:

            self.logger_instance.debug(u"Index title and year for comparison not found, assuming movie title is not in override list")
            return False

        for filter_override_movie_title in filter_override_movie_title_list:

            # get bad movie title compare using tools various
            filter_override_movie_title_compare = self.tools_various_instance.custom_title_compare(filter_override_movie_title)

            if filter_override_movie_title_compare in index_title_and_year_compare:

                self.logger_instance.info(f"Index title '{index_title_and_year_compare}' contains override movie title '{filter_override_movie_title_compare}'")
                return True

        self.logger_instance.debug(f"Index title '{index_title_and_year_compare}' does NOT match any override movie titles in list")
        return False

    # TODO WIP - multiple filters, fix up or delete!!
    def filter_year_runtime(self, process_dict_key, filter_dict_key):

        log_message = 'movie year'
        process_dict_key = 'index_year_compare'
        filter_dict_key = 'filter_minimum_year'

        log_message = 'movie runtime'
        process_dict_key = 'imdb_running_time_in_minutes'
        filter_dict_key = 'filter_minimum_runtime_mins'

        process_compare = self.result_dict.get(process_dict_key)
        filter_compare = self.result_dict.get(filter_dict_key)

        if filter_compare is None:

            self.logger_instance.warning(f"No minimum '{log_message}' defined, assuming above threshold")
            return True

        if process_compare is None:

            self.logger_instance.warning(f"No '{log_message}' available to filter on, assuming below threshold")
            return False

        process_compare_int = int(process_compare)
        filter_compare_int = int(filter_compare)

        if process_compare_int >= filter_compare_int:

            self.logger_instance.info(f"'{log_message}' '{process_compare}' equal to/above minimum threshold '{filter_compare}'")
            return True

        else:

            self.logger_instance.warning(f"'{log_message}' '{process_compare}' below minimum threshold '{filter_compare}'")
            return False
