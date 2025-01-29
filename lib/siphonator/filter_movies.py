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
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance
        self.tools_various_instance = siphonator_tools_various.ToolsVarious(self.logger_instance)

    def filter_index_movies(self):

        self.result_dict.update({'result': 'Failed'})

        function_name = siphonator_tools_various.get_function_name()

        filter_index_title_search_result = self.filter_index_title_search_check()
        if not filter_index_title_search_result:
            return self.result_dict

        filter_size_min_result = self.filter_size('minimum')
        if not filter_size_min_result:
            return self.result_dict

        filter_size_max_result = self.filter_size('maximum')
        if not filter_size_max_result:
            return self.result_dict

        filter_bad_index_title_result = self.filter_bad_index_title()
        if not filter_bad_index_title_result:
            return self.result_dict

        filter_bad_index_type_result = self.filter_bad_index_type()
        if not filter_bad_index_type_result:
            return self.result_dict

        filter_bad_movie_title_result = self.filter_bad_movie_title()
        if not filter_bad_movie_title_result:
            return self.result_dict

        filter_downloaded_file_result = self.filter_downloaded_file()
        # if true (file does not exist in library) then check directory
        if filter_downloaded_file_result:
            filter_downloaded_dir_result = self.filter_downloaded_dir()
            # if false (file does exist in library) then return (failed)
            if not filter_downloaded_dir_result:
                return self.result_dict
        # if false (file does exist in library) then return (failed)
        else:
            return self.result_dict

        self.logger_instance.debug(f"Passed {function_name} - Index title '{self.result_dict.get('index_title')}'")
        self.result_dict.update({'result': 'Passed'})

        return self.result_dict

    def filter_imdb_movies(self):

        self.result_dict.update({'result': 'Failed'})
        function_name = siphonator_tools_various.get_function_name()

        filter_bad_genre_result = self.filter_bad_genre()
        if not filter_bad_genre_result:
            return self.result_dict

        filter_bitrate_result = self.filter_bitrate()
        if not filter_bitrate_result:
            return self.result_dict

        filter_year_result = self.filter_year()
        if not filter_year_result:
            return self.result_dict

        filter_runtime_result = self.filter_runtime()
        if not filter_runtime_result:
            return self.result_dict

        filter_good_language_result = self.filter_good_language_country('language')
        if not filter_good_language_result:
            return self.result_dict

        filter_good_country_result = self.filter_good_language_country('country')
        if not filter_good_country_result:
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

                            override_genre_dict = self.filter_override_genre()

                            filter_rating_result = self.filter_rating(override_genre_dict)
                            if not filter_rating_result:
                                return self.result_dict

                            filter_votes_result = self.filter_votes(override_genre_dict)
                            if not filter_votes_result:
                                return self.result_dict

        self.logger_instance.debug(f"Passed {function_name} - Index title '{self.result_dict.get('index_title')}'")
        self.result_dict.update({'result': 'Passed'})

        return self.result_dict

    def filter_override_genre(self):

        imdb_genres_list = self.result_dict.get('imdb_genres_list', [])
        function_name = siphonator_tools_various.get_function_name()

        if not imdb_genres_list:

            result_details = f"Failed {function_name} - IMDb genre not found, skipping filter genre rating"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return None

        override_genre_dict = {}

        # loop over imdb genre list
        for imdb_genre in imdb_genres_list:

            filter_override_genre_dict = self.config_dict.get('filters', {}).get('override_genre', {}).get(imdb_genre.lower(), {})

            if filter_override_genre_dict:

                filter_override_minimum_rating = filter_override_genre_dict.get('minimum_rating', {})
                if filter_override_minimum_rating:

                    self.logger_instance.debug(f"Override genre '{imdb_genre.lower()}' found, setting minimum IMDb rating to '{filter_override_minimum_rating}'")
                    override_genre_dict['minimum_rating'] = filter_override_minimum_rating

                filter_override_minimum_votes = filter_override_genre_dict.get('minimum_votes', {})
                if filter_override_minimum_votes:

                    self.logger_instance.debug(f"Override genre '{imdb_genre.lower()}' found, setting minimum IMDb votes to '{filter_override_minimum_votes}'")
                    override_genre_dict['minimum_votes'] = filter_override_minimum_votes

        return override_genre_dict

    def filter_rating(self, override_genre_dict):

        imdb_rating = self.result_dict.get('imdb_rating')
        filter_minimum_rating = self.config_dict['filters']['minimum_rating']
        function_name = siphonator_tools_various.get_function_name()

        if filter_minimum_rating is None:

            result_details = f"Passed {function_name} - No IMDb minimum rating defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if imdb_rating is None:

            result_details = f"Failed {function_name} - No IMDb rating available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        # if override genre dict is not empty then proceed
        if override_genre_dict:

            # if minimum_rating defined in override dict then use
            if override_genre_dict.get('minimum_rating', {}):

                filter_minimum_rating = override_genre_dict.get('minimum_rating', {})

        filter_minimum_rating_dec = Decimal(filter_minimum_rating)
        if filter_minimum_rating_dec > Decimal('10.0'):

            result_details = f"Passed {function_name} - IMDb rating defined as '{filter_minimum_rating}' is greater than the maximum value of 10.0, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        filter_minimum_rating_dec = Decimal(filter_minimum_rating)
        if imdb_rating >= filter_minimum_rating_dec:

            result_details = f"Passed {function_name} - IMDb rating '{imdb_rating}' equal to/above threshold '{filter_minimum_rating}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed {function_name} - IMDb rating '{imdb_rating}' below threshold '{filter_minimum_rating}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_votes(self, override_genre_dict):

        imdb_votes = self.result_dict.get('imdb_votes')
        filter_minimum_votes = self.config_dict['filters']['minimum_votes']
        function_name = siphonator_tools_various.get_function_name()

        if filter_minimum_votes is None:

            result_details = f"Passed {function_name} - No IMDb minimum votes defined, skipping votes check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if imdb_votes is None:

            result_details = f"Failed {function_name} - No IMDb votes available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        # if override genre dict is not empty then proceed
        if override_genre_dict:

            # if minimum_votes defined in override dict then use
            if override_genre_dict.get('minimum_votes', {}):

                filter_minimum_votes = override_genre_dict.get('minimum_votes', {})

        imdb_votes_int = int(imdb_votes)

        minimum_votes_int = int(filter_minimum_votes)

        if imdb_votes_int >= minimum_votes_int:

            result_details = f"Passed {function_name} - IMDb votes '{imdb_votes}' equal to/above threshold '{filter_minimum_votes}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed {function_name} - IMDb votes '{imdb_votes}' below threshold '{filter_minimum_votes}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_size(self, size):

        index_size = self.result_dict.get('index_size')
        filter_size_mb = self.result_dict.get(f'filter_{size}_size_mb')
        function_name = siphonator_tools_various.get_function_name()

        if filter_size_mb is None:

            result_details = f"Passed {function_name} - '{size.capitalize()}' size not defined, skipping maximum size check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if index_size is None:

            result_details = f"Failed {function_name} - No Index size available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        imdb_size_int_mb = int(index_size) // 1000000

        if size == "minimum":

            if imdb_size_int_mb >= filter_size_mb:

                result_details = f"Passed {function_name} - Index size '{imdb_size_int_mb}' (MB) is within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

            else:

                result_details = f"Failed {function_name} - Index size '{imdb_size_int_mb}' (MB) not within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        if size == "maximum":

            if imdb_size_int_mb <= filter_size_mb:

                result_details = f"Passed {function_name} - Index size '{imdb_size_int_mb}' (MB) is within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

            else:

                result_details = f"Failed {function_name} - Index size '{imdb_size_int_mb}' (MB) not within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

    def filter_bitrate(self):

        index_size = self.result_dict.get('index_size')
        imdb_runtime_in_minutes = self.result_dict.get('imdb_running_time_in_minutes')
        filter_minimum_bitrate_mb = self.result_dict.get('filter_minimum_bitrate_mb')
        function_name = siphonator_tools_various.get_function_name()

        if filter_minimum_bitrate_mb is None:

            result_details = f"Passed {function_name} - No minimum bitrate defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if index_size is None:

            result_details = f"Failed {function_name} - No Index size available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        if imdb_runtime_in_minutes is None:

            result_details = f"Failed {function_name} - No movie runtime available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        index_size_int_mb = int(index_size)//1000000
        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        imdb_bitrate_int_mb = index_size_int_mb//imdb_runtime_int_mins

        if imdb_bitrate_int_mb >= filter_minimum_bitrate_mb:

            result_details = f"Passed {function_name} - Index bitrate '{imdb_bitrate_int_mb}' (MB/min) equal to/above minimum bitrate threshold '{filter_minimum_bitrate_mb}' (MB/min)"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed {function_name} - Index bitrate '{imdb_bitrate_int_mb}' (MB/min) below minimum bitrate threshold '{filter_minimum_bitrate_mb}' (MB/min)"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_year(self):

        index_year_compare = self.result_dict.get('index_year_compare')
        filter_minimum_year = self.config_dict['filters']['minimum_year']
        function_name = siphonator_tools_various.get_function_name()

        if filter_minimum_year is None:

            result_details = f"Passed {function_name} - No minimum movie year defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if index_year_compare is None:

            result_details = f"Failed {function_name} - No movie year available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        index_year_compare_int = int(index_year_compare)
        filter_minimum_year_int = int(filter_minimum_year)

        if index_year_compare_int >= filter_minimum_year_int:

            result_details = f"Passed {function_name} - Movie year '{index_year_compare}' equal to/above minimum year threshold '{filter_minimum_year}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed {function_name} - Movie year '{index_year_compare}' below minimum year threshold '{filter_minimum_year}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_runtime(self):

        imdb_runtime_in_minutes = self.result_dict.get('imdb_running_time_in_minutes')
        filter_minimum_runtime_mins = self.config_dict['filters']['minimum_runtime_mins']
        function_name = siphonator_tools_various.get_function_name()

        if filter_minimum_runtime_mins is None:

            result_details = f"Passed {function_name} - No minimum runtime defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if imdb_runtime_in_minutes is None:

            result_details = f"Failed {function_name} - No movie runtime available to filter on, assuming below threshold"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        filter_minimum_runtime_mins_int = int(filter_minimum_runtime_mins)

        if imdb_runtime_int_mins >= filter_minimum_runtime_mins_int:

            result_details = f"Passed {function_name} - Movie runtime '{imdb_runtime_int_mins}' (mins) equal to/above minimum runtime threshold '{filter_minimum_runtime_mins_int}' (mins)"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed {function_name} - Movie runtime '{imdb_runtime_int_mins}' (mins) below minimum runtime threshold '{filter_minimum_runtime_mins_int}' (mins)"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_downloaded_file(self):

        filter_library_path_walk = self.result_dict.get('filter_library_path_walk')
        library_path = self.config_dict['general']['library_path']
        index_title = self.result_dict.get('index_title')
        index_title_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(index_title)
        index_title_compare = self.result_dict.get('index_title_compare')
        index_year_compare = self.result_dict.get('index_year_compare')
        function_name = siphonator_tools_various.get_function_name()

        if filter_library_path_walk is None:

            result_details = f"Passed {function_name} - No library path defined, assuming movie is not present in library"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
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
                library_filename_year_compare = self.tools_various_instance.custom_title_year_compare(library_filename)
                library_filename_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(library_filename)
                library_filename_abs_path = os.path.join(root, library_filename)

                # if we cannot determine the year then go to top of loop
                if library_filename_year_compare is None:
                    continue

                # if library filename title compare not in index title compare then go to top of loop
                if library_filename_title_compare not in index_title_compare:
                    continue

                # if the library filename year cannot be found then continue
                if library_filename_year_compare is None:
                    continue

                # if library filename title compare not in index title year compare then skip
                if library_filename_year_compare not in index_year_compare:
                    continue

                # if library filename does not contain all search criteria then skip
                if not self.filter_downloaded_file_search_criteria(library_filename, library_filename_abs_path):
                    continue

                # calculate scores for index title and library filename
                library_filename_score = siphonator_tools_various.quality_score(library_filename_year_to_end_compare)
                index_title_score = siphonator_tools_various.quality_score(index_title_year_to_end_compare)

                # library filename maybe mangled and thus cannot identify year to end for comparison
                if library_filename_year_to_end_compare is not None:

                    self.logger_instance.debug(f"Library filename quality score is '{library_filename_score}'")
                    self.logger_instance.debug(f"Index title quality score is '{index_title_score}'")

                    # if index title score is greater than library filename score then continue
                    if library_filename_score < index_title_score:
                        result_details = f"Passed {function_name} - Index title '{index_title}' score {index_title_score} is greater than library filename score {library_filename_score}, continue processing..."
                        self.logger_instance.info(result_details)
                        self.result_dict.update({'result': u'Passed'})
                        self.result_details_list.append(result_details)
                        self.result_dict.update({'result_details': self.result_details_list})
                        return True

                # if preferred index group is not present in library file then continue
                if self.filter_preferred_index_group(library_filename, index_title):
                    result_details = f"Passed {function_name} - Index title '{index_title}' contains preferred group and library filename {library_filename} does not, continue processing..."
                    self.logger_instance.info(result_details)
                    self.result_dict.update({'result': u'Passed'})
                    self.result_details_list.append(result_details)
                    self.result_dict.update({'result_details': self.result_details_list})
                    return True

                # if preferred index quality is not present in library file then continue
                if self.filter_preferred_index_quality(library_filename, index_title):
                    result_details = f"Passed {function_name} - Index title '{index_title}' contains preferred index quality and library filename {library_filename} does not, continue processing..."
                    self.logger_instance.info(result_details)
                    self.result_dict.update({'result': u'Passed'})
                    self.result_details_list.append(result_details)
                    self.result_dict.update({'result_details': self.result_details_list})
                    return True

                # if index title found in library path then skip
                result_details = f"Failed {function_name} - Index title '{index_title}' already exists in library file '{library_filename}', skipping movie"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        # if index title not found in library path then continue
        result_details = f"Passed {function_name} - Index title '{index_title}' does not exist in library path '{library_path}', continue processing..."
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_downloaded_dir(self):

        filter_library_path_walk = self.result_dict.get('filter_library_path_walk')
        library_path = self.config_dict['general']['library_path']
        index_title = self.result_dict.get('index_title')
        index_title_compare = self.result_dict.get('index_title_compare')
        index_year_compare = self.result_dict.get('index_year_compare')
        index_title_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(index_title)
        function_name = siphonator_tools_various.get_function_name()

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
                if library_dirs_title_compare not in index_title_compare:
                    continue

                # if library directory year compare in index title year compare then continue towards false (already downloaded)
                if library_dir_year_compare not in index_year_compare:
                    continue

                # construct absolute library path
                library_dirs_abs_path = os.path.join(root, library_dirs)

                # walk absolute path
                library_dirs_abs_path_gen = self.tools_various_instance.library_path_walk(library_dirs_abs_path)

                # loop over generator absolute path
                for sub_root, sub_dirs, sub_files in library_dirs_abs_path_gen:

                    for library_sub_file in sub_files:

                        # TODO this is a kludge, can we do better?
                        # only check video container formats
                        if not library_sub_file.lower().endswith(('.mkv', '.mp4', '.avi')):
                            continue

                        # get full path to filename
                        library_dirs_abs_filepath = os.path.join(sub_root, library_sub_file)

                        # if library filename does not contain all search criteria then continue
                        if not self.filter_downloaded_file_search_criteria(library_sub_file, library_dirs_abs_filepath):
                            continue

                        library_filename_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(library_sub_file)

                        # library filename maybe mangled and thus cannot identify year to end for comparison
                        if library_filename_year_to_end_compare is not None:

                            # calculate scores for index title and library filename
                            library_filename_score = siphonator_tools_various.quality_score(library_filename_year_to_end_compare)
                            index_title_score = siphonator_tools_various.quality_score(index_title_year_to_end_compare)
                            self.logger_instance.debug(f"Library filename quality score is '{library_filename_score}'")
                            self.logger_instance.debug(f"Index title quality score is '{index_title_score}'")

                            # if library filename title quality score is less than the index title then continue
                            if library_filename_score < index_title_score:
                                result_details = f"Passed {function_name} - Index title '{index_title}' score {index_title_score} is greater than library filename {library_sub_file} score {library_filename_score}, continue processing..."
                                self.logger_instance.info(result_details)
                                self.result_dict.update({'result': u'Passed'})
                                self.result_details_list.append(result_details)
                                self.result_dict.update({'result_details': self.result_details_list})
                                return True

                        # if preferred group is present in index title or library file already exists with preferred group then continue
                        if self.filter_preferred_index_group(library_sub_file, index_title):
                            result_details = f"Passed {function_name} - Index title '{index_title}' contains preferred index quality and library filename {library_sub_file} does not, continue processing..."
                            self.logger_instance.info(result_details)
                            self.result_dict.update({'result': u'Passed'})
                            self.result_details_list.append(result_details)
                            self.result_dict.update({'result_details': self.result_details_list})
                            return True

                        # if preferred index quality is present in index title or library file then continue
                        if self.filter_preferred_index_quality(library_sub_file, index_title):
                            result_details = f"Passed {function_name} - Index title '{index_title}' contains preferred index quality and library filename {library_sub_file} does not, continue processing..."
                            self.logger_instance.info(result_details)
                            self.result_dict.update({'result': u'Passed'})
                            self.result_details_list.append(result_details)
                            self.result_dict.update({'result_details': self.result_details_list})
                            return True

                        result_details = f"Failed {function_name} - Index title '{index_title}' already exists in library file '{library_sub_file}', skipping movie"
                        self.logger_instance.warning(result_details)
                        self.result_dict.update({'result': u'Failed'})
                        self.result_details_list.append(result_details)
                        self.result_dict.update({'result_details': self.result_details_list})
                        return False

        result_details = f"Passed {function_name} - Index title '{index_title}' does not exist in library path '{library_path}', continue processing..."
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_downloaded_file_search_criteria(self, library_filename, library_filepath):

        index_site_search = self.result_dict.get('index_site_search')
        ffprobe_filepath = self.init_dict.get('ffprobe_filepath')
        index_site_search_list = index_site_search.split()
        library_filename_title_full_compare = self.tools_various_instance.custom_title_full_compare(library_filename)
        function_name = siphonator_tools_various.get_function_name()

        for index_site_search_item in index_site_search_list:

            if index_site_search_item not in library_filename_title_full_compare:

                index_site_search_item_resolution, index_site_search_item_resolution_numeric = self.tools_various_instance.resolution_from_string(index_site_search_item)

                # check if missing index site search item from library filename is resolution e.g. '1080p' (only item we can calculate, else assume file is missing from library)
                if index_site_search_item_resolution is not None:

                    # get resolution of library file by analysing file using ffprobe
                    library_filepath_height_resolution_numeric = self.tools_various_instance.resolution_from_ffprobe(library_filepath, ffprobe_filepath)

                    if library_filepath_height_resolution_numeric is None:

                        result_details = f"Failed {function_name} - Unable to determine resolution from ffprobe for library file '{library_filename}'"
                        self.logger_instance.info(result_details)
                        self.result_dict.update({'result': u'Failed'})
                        self.result_details_list.append(result_details)
                        self.result_dict.update({'result_details': self.result_details_list})
                        return False

                    self.logger_instance.debug(f"Library file resolution identified as '{library_filepath_height_resolution_numeric}' for library file '{library_filename}'")

                    # if integer of library filename resolution numeric is less than integer of index title resolution numeric then continue
                    if int(library_filepath_height_resolution_numeric) < int(index_site_search_item_resolution_numeric):

                        result_details = f"Failed {function_name} - Library file resolution '{library_filepath_height_resolution_numeric}' is less than resolution for index title '{index_site_search_item_resolution_numeric}'"
                        self.logger_instance.info(result_details)
                        self.result_dict.update({'result': u'Failed'})
                        self.result_details_list.append(result_details)
                        self.result_dict.update({'result_details': self.result_details_list})
                        return False

                else:

                    result_details = f"Failed {function_name} - Unable to determine missing index site search item '{index_site_search_item}' from library filename '{library_filename}'"
                    self.logger_instance.info(result_details)
                    self.result_dict.update({'result': u'Failed'})
                    self.result_details_list.append(result_details)
                    self.result_dict.update({'result_details': self.result_details_list})
                    return False

        result_details = f"Passed {function_name} - Index site search criteria '{index_site_search_list}' found in library filename '{library_filename}'"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_bad_genre(self):

        imdb_genres_list = self.result_dict.get('imdb_genres_list')
        filter_bad_genre_list = self.config_dict["filters"]['bad_genre_list']
        function_name = siphonator_tools_various.get_function_name()

        if filter_bad_genre_list is None:

            result_details = f"Passed {function_name} - No bad genre(s) defined, skipping bad genre check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if imdb_genres_list is None:

            result_details = f"Passed {function_name} - No IMDb genre(s) found, skipping bad genre check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        imdb_genres_list_lower = [x.lower() for x in imdb_genres_list]
        filter_bad_genre_list_lower = [x.lower() for x in filter_bad_genre_list]

        for filter_bad_genre in filter_bad_genre_list_lower:

            if filter_bad_genre in imdb_genres_list_lower:

                result_details = f"Failed {function_name} - IMDb genre(s) '{imdb_genres_list_lower}' match bad genre(s) list '{filter_bad_genre_list_lower}', skipping movie"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed {function_name} - IMDb genre(s) '{imdb_genres_list_lower}' does NOT match any of the bad genre(s) '{filter_bad_genre_list_lower}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_bad_index_title(self):

        filter_bad_title_list = self.config_dict["filters"]['bad_index_title_list']
        function_name = siphonator_tools_various.get_function_name()

        if filter_bad_title_list is None:

            result_details = f"Passed {function_name} - No bad index title keywords defined, skipping bad index title keyword check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        # get bad index title compare using tools various
        index_title = self.result_dict.get('index_title')
        index_title_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(index_title)

        self.logger_instance.debug(f"Index title for bad keyword comparison is '{index_title_year_to_end_compare}'")

        for filter_bad_title in filter_bad_title_list:

            filter_bad_title_lower_search = self.tools_various_instance.custom_bad_keyword_search(index_title_year_to_end_compare, filter_bad_title)

            if filter_bad_title_lower_search:

                result_details = f"Failed {function_name} - Index title '{index_title_year_to_end_compare}' contains bad title keyword '{filter_bad_title}', skipping movie"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed {function_name} - Index title '{index_title_year_to_end_compare}' does NOT contain bad title keyword(s) '{filter_bad_title_list}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_bad_movie_title(self):

        filter_bad_movie_title_list = self.config_dict["filters"]['bad_movie_title_list']
        function_name = siphonator_tools_various.get_function_name()

        if filter_bad_movie_title_list is None:

            result_details = f"Passed {function_name} - No bad movie titles defined, skipping bad movie title check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        index_title_and_year_compare = self.result_dict.get('index_title_and_year_compare')

        for filter_bad_movie_title in filter_bad_movie_title_list:

            # get bad movie title compare using tools various
            filter_bad_movie_title_full_compare = self.tools_various_instance.custom_title_full_compare(filter_bad_movie_title)

            if filter_bad_movie_title_full_compare in index_title_and_year_compare:

                result_details = f"Failed {function_name} - Index title '{index_title_and_year_compare}' contains bad movie title '{filter_bad_movie_title_full_compare}', skipping movie"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Index title '{index_title_and_year_compare}' does NOT match any bad movie titles in list"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_bad_index_type(self):

        index_title = self.result_dict.get('index_title')
        index_title_tv_season_episode = self.tools_various_instance.custom_title_tv_season_episode(index_title)
        function_name = siphonator_tools_various.get_function_name()

        if not index_title_tv_season_episode:

            result_details = f"Failed {function_name} - Index title '{index_title}' contains tv season or episode string match for regex, skipping movie"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        result_details = f"Passed {function_name} - Index title '{index_title}' does NOT contains tv season or episode string match"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_good_language_country(self, filter_type):

        imdb_list = self.result_dict.get(f'imdb_{filter_type}_list')
        filter_list = self.config_dict["filters"][f"good_{filter_type}_list"]
        function_name = siphonator_tools_various.get_function_name()

        if filter_list is None:

            result_details = f"Passed {function_name} - Filter for '{filter_type}' not defined, skipping '{filter_type}' checks"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if imdb_list is None:

            result_details = f"Passed {function_name} - IMDb '{filter_type}' not found, assuming '{filter_type}' is OK"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        imdb_lower_list = [x.lower() for x in imdb_list]
        filter_lower_list = [x.lower() for x in filter_list]

        for filter_lower_item in filter_lower_list:

            if filter_lower_item in imdb_lower_list:

                result_details = f"Passed {function_name} - IMDb '{filter_type}' list '{imdb_lower_list}' is in good '{filter_type}' list '{filter_lower_list}'"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed {function_name} - IMDb '{filter_type}' list '{imdb_lower_list}' is not in good '{filter_type}' list '{filter_lower_list}'"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_preferred_index_group(self, library_filename, index_title):

        filter_preferred_index_group_list = self.config_dict["filters"]['preferred_index_group_list']
        function_name = siphonator_tools_various.get_function_name()

        if filter_preferred_index_group_list is None:

            result_details = f"Failed {function_name} - No preferred index groups defined, skipping preferred index group check"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        filter_preferred_index_group_lower_list = [x.lower() for x in filter_preferred_index_group_list]

        library_filename_group = self.tools_various_instance.custom_title_group_compare(library_filename)
        index_title_group = self.tools_various_instance.custom_title_group_compare(index_title)

        self.logger_instance.debug(f"Filter preferred index group list is '{filter_preferred_index_group_lower_list}'")
        self.logger_instance.debug(f"Library filename group is '{library_filename_group}'")
        self.logger_instance.debug(f"Index title group is '{index_title_group}'")

        # if library filename already matches one of the preferred index groups then return False (no need to dl again)
        if library_filename_group in filter_preferred_index_group_lower_list:

            result_details = f"Failed {function_name} - Library filename group '{library_filename_group}' is in preferred index group list '{filter_preferred_index_group_lower_list}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        # if index title group is not in preferred index group list then return False (not preferred group)
        if index_title_group not in filter_preferred_index_group_lower_list:

            result_details = f"Failed {function_name} - Index title group '{index_title_group}' is not in preferred index group list '{filter_preferred_index_group_lower_list}'"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        result_details = f"Passed {function_name} - Index title group '{index_title_group}' is in preferred index group list '{filter_preferred_index_group_lower_list}' and library filename group '{library_filename_group}' is not preferred, ignoring existing library file."
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_preferred_index_quality(self, library_filename, index_title):

        filter_preferred_index_quality_list = self.config_dict["filters"]['preferred_index_quality_list']
        function_name = siphonator_tools_various.get_function_name()

        if not filter_preferred_index_quality_list:

            result_details = f"Failed {function_name} - No preferred index quality defined, skipping preferred index quality check"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
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

                    result_details = f"Failed {function_name} - Library filename '{library_filename}' contains preferred quality keyword '{filter_preferred_index_quality}'"
                    self.logger_instance.warning(result_details)
                    self.result_dict.update({'result': u'Failed'})
                    self.result_details_list.append(result_details)
                    self.result_dict.update({'result_details': self.result_details_list})
                    return False

                else:

                    result_details = f"Passed {function_name} - Index title '{index_title}' does include keyword from preferred index quality list '{filter_preferred_index_quality_list}' and library filename '{library_filename}' does not contain keyword from preferred quality list, ignoring existing library file,"
                    self.logger_instance.info(result_details)
                    self.result_dict.update({'result': u'Passed'})
                    self.result_details_list.append(result_details)
                    self.result_dict.update({'result_details': self.result_details_list})
                    return True

        result_details = f"Failed {function_name} - Index title '{index_title}' does not contain any keywords from the preferred quality list '{filter_preferred_index_quality_list}'"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_override_person(self, filter_type):

        imdb_list = self.result_dict.get(f'imdb_credits_{filter_type}_list')
        filter_list = self.config_dict["filters"][f"override_{filter_type}_list"]
        function_name = siphonator_tools_various.get_function_name()

        if filter_list is None:

            result_details = f"Failed {function_name} - Filter for '{filter_type}' not defined, skipping '{filter_type}' checks"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        if imdb_list is None:

            result_details = f"Failed {function_name} - IMDb '{filter_type}' not found, assuming '{filter_type}' is OK"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        imdb_lower_list = [x.lower() for x in imdb_list]
        filter_lower_list = [x.lower() for x in filter_list]

        for filter_lower_item in filter_lower_list:

            if filter_lower_item in imdb_lower_list:

                result_details = f"Passed {function_name} - IMDb '{filter_type}' list '{imdb_list}' is in good '{filter_type}' list '{filter_list}', skipping votes and rating checks"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed {function_name} - IMDb '{filter_type}' list '{imdb_list}' is not in good '{filter_type}' list '{filter_list}'"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_override_movie_title(self):

        index_title_and_year_compare = self.result_dict.get('index_title_and_year_compare')
        filter_override_movie_title_list = self.config_dict["filters"]['override_movie_title_list']
        function_name = siphonator_tools_various.get_function_name()

        if filter_override_movie_title_list is None:

            result_details = f"Failed {function_name} - Override movie title not defined, assuming movie title is not in override list"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        if index_title_and_year_compare is None:

            result_details = f"Failed {function_name} - Index title and year for comparison not found, assuming movie title is not in override list"
            self.logger_instance.warning(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        for filter_override_movie_title in filter_override_movie_title_list:

            # get bad movie title compare using tools various
            filter_override_movie_title_compare = self.tools_various_instance.custom_title_compare(filter_override_movie_title)

            if filter_override_movie_title_compare in index_title_and_year_compare:

                result_details = f"Passed {function_name} - Index title '{index_title_and_year_compare}' contains override movie title '{filter_override_movie_title_compare}'"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed {function_name} - Index title '{index_title_and_year_compare}' does NOT match any override movie titles in list"
        self.logger_instance.warning(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_index_title_search_check(self):

        index_title = self.result_dict.get('index_title')
        index_title_year_to_end_compare = self.tools_various_instance.custom_title_year_to_end_compare(index_title)
        index_title_year_to_end_search_compare = self.tools_various_instance.custom_title_word_match_compare(index_title_year_to_end_compare)
        index_site_search_result_dict = self.result_dict.get('index_site_search').lower()
        index_site_search_list = index_site_search_result_dict.split()
        function_name = siphonator_tools_various.get_function_name()

        self.logger_instance.debug(f"Index title search criteria check is '{index_title_year_to_end_compare}'")

        for index_site_search in index_site_search_list:

            if index_site_search not in index_title_year_to_end_search_compare:
                result_details = f"Failed {function_name} - Index title '{index_title_year_to_end_compare}' does not contain search criteria keyword '{index_site_search}', skipping movie"
                self.logger_instance.warning(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed {function_name} - Index title '{index_title_year_to_end_compare}' does contain all search criteria keyword(s) '{index_site_search_result_dict}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True
