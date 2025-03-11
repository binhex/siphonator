import os
import re
from decimal import Decimal
import lib.siphonator.tools_various as siphonator_tools_various
import lib.siphonator.tools_filters as siphonator_tools_filters

# TODO bad group list, start with SLOT?


class FilterMovies(object):

    def __init__(self, logger_instance, init_dict, result_dict, config_dict, index_site_dict, library_path_walk=None):

        self.init_dict = init_dict
        self.config_dict = config_dict
        self.result_dict = result_dict
        self.index_site_dict = index_site_dict
        self.tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger_instance)
        self.result_details_list = result_dict.get('result_details', [])
        self.logger_instance = logger_instance
        self.library_path_walk = library_path_walk

    def filter_index_movies(self):

        filter_movie_title_and_year_search_result = self.filter_index_search_criteria()
        if not filter_movie_title_and_year_search_result:
            return self.result_dict

        filter_size_min_result = self.filter_index_size('minimum')
        if not filter_size_min_result:
            return self.result_dict

        filter_size_max_result = self.filter_index_size('maximum')
        if not filter_size_max_result:
            return self.result_dict

        filter_bad_index_title_result = self.filter_index_bad_keyword()
        if not filter_bad_index_title_result:
            return self.result_dict

        filter_bad_index_type_result = self.filter_index_bad_type()
        if not filter_bad_index_type_result:
            return self.result_dict

        filter_bad_movie_title_result = self.filter_imdb_bad_title()
        if not filter_bad_movie_title_result:
            return self.result_dict

        filter_downloaded_iterate_files_result = self.filter_library_iterate_files()
        if not filter_downloaded_iterate_files_result:
            return self.result_dict

        return self.result_dict

    def filter_imdb_movies(self):

        filter_good_imdb_title_type_result = self.filter_imdb_good_type()
        if not filter_good_imdb_title_type_result:
            return self.result_dict

        filter_bad_genre_result = self.filter_imdb_bad_genre()
        if not filter_bad_genre_result:
            return self.result_dict

        filter_bitrate_result = self.filter_index_bitrate()
        if not filter_bitrate_result:
            return self.result_dict

        filter_year_result = self.filter_imdb_year()
        if not filter_year_result:
            return self.result_dict

        filter_runtime_result = self.filter_imdb_runtime()
        if not filter_runtime_result:
            return self.result_dict

        filter_good_language_result = self.filter_imdb_good_language_country('language')
        if not filter_good_language_result:
            return self.result_dict

        filter_good_country_result = self.filter_imdb_good_language_country('country')
        if not filter_good_country_result:
            return self.result_dict

        filter_override_character = self.filter_imdb_override_person('character')
        if not filter_override_character:

            filter_override_director = self.filter_imdb_override_person('director')
            if not filter_override_director:

                filter_override_writer = self.filter_imdb_override_person('writer')
                if not filter_override_writer:

                    filter_override_cast = self.filter_imdb_override_person('cast')
                    if not filter_override_cast:

                        filter_override_movie_title = self.filter_index_override_title()
                        if not filter_override_movie_title:

                            override_genre_dict = self.filter_imdb_override_genre()

                            filter_rating_result = self.filter_imdb_rating(override_genre_dict)
                            if not filter_rating_result:
                                return self.result_dict

                            filter_votes_result = self.filter_imdb_votes(override_genre_dict)
                            if not filter_votes_result:
                                return self.result_dict

        return self.result_dict

    def filter_index_override_title(self):

        movie_title_and_year_compare = self.result_dict.get('movie_title_and_year_compare')
        filter_override_movie_title_list = self.config_dict["filters"]['override_movie_title_list']

        if not filter_override_movie_title_list:

            result_details = f"Failed: Override movie title not defined, assuming movie title is not in override list"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        if not movie_title_and_year_compare:

            result_details = f"Failed: Index title and year for comparison not found, assuming movie title is not in override list"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        for filter_override_movie_title in filter_override_movie_title_list:

            # get bad movie title compare using tools various
            filter_override_movie_title_compare = self.tools_filters_instance.imdb_title_compare(filter_override_movie_title)

            if filter_override_movie_title_compare in movie_title_and_year_compare:

                result_details = f"Passed: Index title '{movie_title_and_year_compare}' contains override movie titles in '{filter_override_movie_title_compare}'"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed: Index title '{movie_title_and_year_compare}' does NOT match any override movie titles in '{filter_override_movie_title_list}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_index_search_criteria(self):

        index_title = self.result_dict.get('index_title')
        index_site_search_result_dict = self.index_site_dict.get('criteria').lower()
        index_site_search_list = index_site_search_result_dict.split()

        for index_site_search in index_site_search_list:

            if index_site_search not in index_title:
                result_details = f"Failed: Index title '{index_title}' does not contain search criteria keyword '{index_site_search}', skipping movie"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed: Index title '{index_title}' does contain all search criteria keyword(s) '{index_site_search_result_dict}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_index_bad_type(self):

        index_title = self.result_dict.get('index_title')

        index_title_after_year_to_end = self.result_dict.get('index_title_after_year_to_end')
        index_title_tv_season_episode = self.tools_filters_instance.tv_search(index_title_after_year_to_end)

        if index_title_tv_season_episode:

            result_details = f"Failed: Index title '{index_title}' contains tv season or episode string match for regex, skipping movie"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        result_details = f"Passed: Index title '{index_title}' does NOT contain tv season or episode string match"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_index_bad_keyword(self):

        filter_bad_index_title_list = self.config_dict["filters"]['bad_index_title_list']

        if not filter_bad_index_title_list:

            result_details = f"Passed: No bad index title keywords defined, skipping bad index title keyword check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        # get bad index title compare using tools various
        index_title = self.result_dict.get('index_title')

        # get sanitised index title from result dict
        index_title_sanitised = self.result_dict.get('index_title_sanitised')

        for filter_bad_index_title in filter_bad_index_title_list:

            if self.tools_filters_instance.keyword_search(index_title_sanitised, filter_bad_index_title):

                result_details = f"Failed: Index title '{index_title}' contains bad title keyword '{filter_bad_index_title}', skipping movie"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed: Index title '{index_title}' does NOT contain bad title keyword(s) '{filter_bad_index_title_list}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_index_preferred_group(self, library_filename_sanitised):

        filter_preferred_index_group_list = self.config_dict["filters"]['preferred_index_group_list']

        if not filter_preferred_index_group_list:

            result_details = f"Failed: No preferred index groups defined, skipping preferred index group check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        filter_preferred_index_group_list_lower = [x.lower() for x in filter_preferred_index_group_list]

        library_filename_group = self.tools_filters_instance.index_title_group(library_filename_sanitised)
        index_title_group = self.result_dict.get('index_title_group')

        self.logger_instance.debug(f"Filter preferred index group list is '{filter_preferred_index_group_list_lower}'")
        self.logger_instance.debug(f"Library filename group is '{library_filename_group}'")
        self.logger_instance.debug(f"Index title group is '{index_title_group}'")

        # if library filename already matches one of the preferred index groups then return False (no need to dl again)
        if library_filename_group in filter_preferred_index_group_list_lower:

            result_details = f"Failed: Library filename group '{library_filename_group}' is in preferred index group list '{filter_preferred_index_group_list_lower}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        # if index title group is not in preferred index group list then return False (not preferred group)
        if index_title_group not in filter_preferred_index_group_list_lower:

            result_details = f"Failed: Index title group '{index_title_group}' is not in preferred index group list '{filter_preferred_index_group_list_lower}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        result_details = f"Passed: Index title group '{index_title_group}' is in preferred index group list '{filter_preferred_index_group_list_lower}' and library filename group '{library_filename_group}' is not preferred, ignoring existing library file."
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_special_editions(self, library_filename_sanitised, index_title_sanitised):

        filter_preferred_index_quality_list = self.config_dict["filters"]['preferred_index_quality_list']

        if not filter_preferred_index_quality_list:

            result_details = f"Failed: No preferred index quality defined, skipping preferred index quality check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        # ensure config filters preferred_index_quality_list is lower case
        filter_preferred_index_quality_list_lower = [x.lower() for x in filter_preferred_index_quality_list]

        self.logger_instance.debug(f"Filter preferred index quality list is '{filter_preferred_index_quality_list_lower}'")

        for filter_preferred_index_quality in filter_preferred_index_quality_list_lower:

            if self.tools_filters_instance.keyword_search(library_filename_sanitised, filter_preferred_index_quality):

                result_details = f"Failed: Library filename '{library_filename_sanitised}' contains preferred quality keyword '{filter_preferred_index_quality}'"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

            if self.tools_filters_instance.keyword_search(index_title_sanitised, filter_preferred_index_quality):

                result_details = f"Passed: Index title '{index_title_sanitised}' does include keyword from preferred index quality list '{filter_preferred_index_quality_list_lower}' and library filename '{library_filename_sanitised}' does not contain keyword from preferred quality list, ignoring existing library file."
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed: Index title '{index_title_sanitised}' does not contain any keywords from the preferred quality list '{filter_preferred_index_quality_list_lower}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_index_size(self, size):

        index_size = self.result_dict.get('index_size')
        filter_size_mb = self.index_site_dict.get(f'{size}_size_mb')

        if not filter_size_mb:

            result_details = f"Passed: '{size.capitalize()}' size not defined, skipping maximum size check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not index_size:

            result_details = f"Failed: No Index size available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        imdb_size_int_mb = int(index_size) // 1000000

        if size == "minimum":

            if imdb_size_int_mb >= filter_size_mb:

                result_details = f"Passed: Index size '{imdb_size_int_mb}' (MB) is within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

            else:

                result_details = f"Failed: Index size '{imdb_size_int_mb}' (MB) not within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        if size == "maximum":

            if imdb_size_int_mb <= filter_size_mb:

                result_details = f"Passed: Index size '{imdb_size_int_mb}' (MB) is within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

            else:

                result_details = f"Failed: Index size '{imdb_size_int_mb}' (MB) not within '{size}' size threshold '{filter_size_mb}' (MB)"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

    def filter_index_bitrate(self):

        index_size = self.result_dict.get('index_size')
        imdb_runtime_in_minutes = self.result_dict.get('imdb_running_time_in_minutes')
        filter_minimum_bitrate_mb = self.index_site_dict.get('minimum_bitrate_mb')

        if not filter_minimum_bitrate_mb:

            result_details = f"Passed: No minimum bitrate defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not index_size:

            result_details = f"Failed: No Index size available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        if not imdb_runtime_in_minutes:

            result_details = f"Failed: No movie runtime available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        index_size_int_mb = int(index_size)//1000000
        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        imdb_bitrate_int_mb = index_size_int_mb//imdb_runtime_int_mins

        if imdb_bitrate_int_mb >= filter_minimum_bitrate_mb:

            result_details = f"Passed: Index bitrate '{imdb_bitrate_int_mb}' (MB/min) equal to/above minimum bitrate threshold '{filter_minimum_bitrate_mb}' (MB/min)"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed: Index bitrate '{imdb_bitrate_int_mb}' (MB/min) below minimum bitrate threshold '{filter_minimum_bitrate_mb}' (MB/min)"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_library_file(self):

        identify_walk_files_filepath_list = []

        for root, dirs, files in self.library_path_walk:

            for library_filename in files:

                # TODO this is a kludge, can we do better?
                # only check video container formats
                if not library_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
                    continue

                # if index year and title does not exist in library filename then continue
                if self.filter_library_year_and_title(library_filename):
                    continue

                # get full path to library filename
                library_files_abs_filepath = os.path.join(root, library_filename)

                identify_walk_files_filepath_list.append(library_files_abs_filepath)

        return {'identify_walk_files_filepath_list': identify_walk_files_filepath_list}

    def filter_library_dir(self):

        movie_title_compare = self.result_dict.get('movie_title_compare')
        movie_title_year = self.result_dict.get('movie_title_year')
        identify_walk_files_filepath_list = []

        for root, dirs, files in self.library_path_walk:

            for library_dirs in dirs:

                library_dirs_sanitised = self.tools_filters_instance.sanitise_subst(library_dirs)

                # get library directory compare strings using tools various
                library_dirs_title_compare = self.tools_filters_instance.movie_title_compare(library_dirs_sanitised)
                library_dir_year_compare = self.tools_filters_instance.movie_title_year(library_dirs_sanitised)

                # if we cannot determine the year from the directory then continue
                if not library_dir_year_compare:
                    continue

                # if library directory year compare not in index title then continue
                if library_dir_year_compare not in movie_title_year:
                    continue

                # if library directory title compare not in index title then continue
                if library_dirs_title_compare not in movie_title_compare:
                    continue

                # construct absolute library path
                library_abs_path = os.path.join(root, library_dirs)

                # note this must be a list as the library_path_walk function takes a list
                # in case multiple root folders need to be walked
                library_abs_path_list = [library_abs_path]

                # walk absolute path to get filename
                library_abs_path_gen = siphonator_tools_various.library_path_walk(library_abs_path_list)

                # loop over generator absolute path
                for sub_root, sub_dirs, sub_files in library_abs_path_gen:

                    for library_filename in sub_files:

                        # TODO this is a kludge, can we do better?
                        # only check video container formats
                        if not library_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
                            continue

                        # get full path to library filename
                        library_files_abs_filepath = os.path.join(sub_root, library_filename)

                        identify_walk_files_filepath_list.append(library_files_abs_filepath)

        return {'identify_walk_dirs_filepath_list': identify_walk_files_filepath_list}

    def filter_library_year_and_title(self, library_filename):

        movie_title_year = self.result_dict.get('movie_title_year')

        library_filename_sanitised = self.tools_filters_instance.sanitise_subst(library_filename)

        library_year_compare = self.tools_filters_instance.movie_title_year(library_filename_sanitised)
        if not library_year_compare:
            return True

        library_title_compare = self.tools_filters_instance.movie_title_compare(library_filename_sanitised)
        if not library_title_compare:
            return True

        movie_title_compare = self.result_dict.get('movie_title_compare')

        # if index title not in library title then movie does not exist, download
        if library_title_compare not in movie_title_compare:
            return True

        # if index year not in library title then movie does not exist, download
        if library_year_compare not in movie_title_year:
            return True

        # index title in library, skip download
        return False

    def filter_quality_score(self, after_year_to_end_string):

        # define scores for resolution, score increases as resolution increases
        resolution_score_dict = {
            r'(480p?|540p?)': int(10),
            r'(720p?)': int(20),
            r'(1080p?)': int(30),
            r'(2160p?)': int(40),
            r'(4320p?)': int(50)
        }

        # define score for source type, score increases as source type improves (higher bitrate)
        source_score_dict = {
            r'(dvdrip|webrip)': int(10),
            r'(hdtv)': int(20),
            r'(web\sdl|webdl|hdrip)': int(30),
            r'(bd|bdrip|bluray|blu-ray)': int(40),
            r'(bdremux|remux)': int(80)
        }

        # define scores for audio quality, score increases as audio quality increases
        audio_score_dict = {
            r'(dts)': int(10),
            r'(dts-hd|dtshd|true-hd|truehd|ddp)': int(20),
            r'(dts-x|dtsx|atmos)': int(30)
        }

        score = 0
        score_dicts = [resolution_score_dict, audio_score_dict, source_score_dict]

        # iterate over dicts
        for score_dict in score_dicts:

            # Iterate over the key-value pairs
            for key, value in score_dict.items():

                # search for key names, if found add value to score
                if re.search(fr'^{key}\s|\s{key}\s|\s{key}$', after_year_to_end_string, re.IGNORECASE):
                    score += value

        self.logger_instance.debug(f"Index/library title after year to end string '{after_year_to_end_string}' has a total score of '{score}'")

        # return final score
        return score

    def filter_quality_check(self, library_file):

        index_title_sanitised = self.result_dict.get('index_title_sanitised')
        library_file_sanitised = self.tools_filters_instance.sanitise_subst(library_file)

        index_title_after_year_to_end = self.tools_filters_instance.index_title_after_year_to_end(index_title_sanitised)

        # if index title year to end is not none (maybe mangled) then return
        if index_title_after_year_to_end is None:

            result_details = f"Failed: Cannot identify after year to end for index title '{index_title_sanitised}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        library_filename_after_year_to_end = self.tools_filters_instance.index_title_after_year_to_end(library_file_sanitised)

        # if library filename year to end is not none (maybe mangled) then return
        if library_filename_after_year_to_end is None:

            result_details = f"Failed: Cannot identify after year to end for library filename '{library_file_sanitised}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        # calculate scores for index title and library filename
        index_title_score = self.filter_quality_score(index_title_after_year_to_end)
        library_filename_score = self.filter_quality_score(library_filename_after_year_to_end)

        # check if index/library filename contain preferred group
        if self.filter_index_preferred_group(library_file_sanitised):

            index_title_score += 10
            result_details = f"Index title '{index_title_after_year_to_end}' does contain preferred index group, and library filename '{library_filename_after_year_to_end}' does not contain preferred index group, adding to score"
            self.logger_instance.info(result_details)

        else:

            library_filename_score += 10
            result_details = f"Library title '{library_filename_after_year_to_end}' does contain preferred index group, and index title '{index_title_after_year_to_end}' does not contain preferred index group, adding to score"
            self.logger_instance.info(result_details)

        # check if index/library filename contain special edition
        if self.filter_special_editions(library_file_sanitised, index_title_sanitised):

            index_title_score += 10
            result_details = f"Passed: Index title '{index_title_after_year_to_end}' does contain special edition, and library filename '{library_filename_after_year_to_end}' does not contain special edition, adding to score"
            self.logger_instance.info(result_details)

        else:

            library_filename_score += 10
            result_details = f"Library title '{library_filename_after_year_to_end}' does contain special edition, and index title '{index_title_after_year_to_end}' does not contain special edition, adding to score"
            self.logger_instance.info(result_details)

        # if library filename score is less than index title score then mark as passed (download)
        if library_filename_score < index_title_score:

            result_details = f"Passed: Index title year to end '{index_title_after_year_to_end}' score '{index_title_score}' is greater than library filename year to end '{library_filename_after_year_to_end}' score '{library_filename_score}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed: Index title year to end '{index_title_after_year_to_end}' score '{index_title_score}' is less than library filename year to end '{library_filename_after_year_to_end}' score '{library_filename_score}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_library_file_resolution(self, library_filename, library_filepath):

        ffprobe_filepath = self.init_dict.get('ffprobe_filepath')

        library_filename_sanitised = self.tools_filters_instance.sanitise_subst(library_filename)

        # attempt to identify resolution from library filename
        library_filename_resolution_string = self.tools_filters_instance.index_title_resolution(library_filename_sanitised)

        # if we cannot identify resolution from library filename then use ffprobe
        if not library_filename_resolution_string:

            # get resolution of library file by analysing file using ffprobe
            library_filename_resolution_string = siphonator_tools_various.resolution_from_ffprobe(library_filepath, ffprobe_filepath)

            if not library_filename_resolution_string:

                result_details = f"Passed: Unable to determine resolution from filename or ffprobe for library file '{library_filename_sanitised}'"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return None

        self.logger_instance.debug(f"Library filename resolution identified as '{str(library_filename_resolution_string)}' using filename/ffprobe for library file '{library_filename_sanitised}'")
        return library_filename_resolution_string

    def filter_library_iterate_files(self):

        index_title = self.result_dict.get('index_title')

        # get index title resolution from index title
        index_title_resolution_string = self.result_dict.get('index_title_resolution')

        # if the index title resolution cannot be identified from index title then skip
        if not index_title_resolution_string:

            result_details = f"Failed: Index title '{index_title}' does not contain resolution"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        library_path = self.config_dict['general']['library_path_list']

        # if the library is not defined then return true
        if not self.library_path_walk:
            result_details = f"Passed: No library paths defined, assuming movie does not exist in library"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        # constructs a list of library filenames that match the index title and year
        identify_walk_files_filepath_dict = self.filter_library_file()

        library_filepath_list = identify_walk_files_filepath_dict['identify_walk_files_filepath_list']

        # if libray path is defined (not None) then process, else return True
        if self.library_path_walk is not None:

            # if identify_walk_files_filepath_dict value is not empty then get filepaths from files
            if library_filepath_list:

                for library_filepath in library_filepath_list:

                    # get filename and path from filepath
                    library_filename = os.path.basename(library_filepath)

                    # get library filename resolution from filename or ffprobe
                    library_file_resolution_string = self.filter_library_file_resolution(library_filename, library_filepath)

                    # if the library file resolution cannot be identified via filename or ffprobe then continue
                    if not library_file_resolution_string:
                        continue

                    # if the resolution in index title matches library file then check for overrides
                    if int(index_title_resolution_string) == int(library_file_resolution_string):

                        # if index title does not contain any overrides (special editions, higher quality or preferred group) then return False (skip)
                        if not self.filter_quality_check(library_filename):

                            result_details = f"Failed: Index title '{index_title}' does not contain overrides for library filename '{library_filename}'"
                            self.logger_instance.info(result_details)
                            self.result_dict.update({'result': u'Failed'})
                            self.result_details_list.append(result_details)
                            self.result_dict.update({'result_details': self.result_details_list})
                            return False

                    # if index resolution is less than library file then skip
                    if int(index_title_resolution_string) < int(library_file_resolution_string):

                        result_details = f"Failed: Index title '{index_title}' resolution {index_title_resolution_string} is less than library filename '{library_filename}' resolution {library_file_resolution_string}"
                        self.logger_instance.info(result_details)
                        self.result_dict.update({'result': u'Failed'})
                        self.result_details_list.append(result_details)
                        self.result_dict.update({'result_details': self.result_details_list})
                        return False

            else:

                # constructs a list of library filenames that exist in a directory, NO matching of index and year
                identify_walk_dirs_filepath_dict = self.filter_library_dir()
                library_filepath_list = identify_walk_dirs_filepath_dict['identify_walk_dirs_filepath_list']

                # if identify_walk_dirs_filepath_dict value is not empty then get filepaths from dirs
                if library_filepath_list:

                    for library_filepath in library_filepath_list:

                        # get filename and path from filepath
                        library_filename = os.path.basename(library_filepath)

                        # get library filename resolution from filename or ffprobe
                        library_file_resolution_string = self.filter_library_file_resolution(library_filename, library_filepath)

                        # if the library file resolution cannot be identified via filename or ffprobe then continue
                        if not library_file_resolution_string:
                            continue

                        # if the resolution in index title matches library file then check for overrides
                        if int(index_title_resolution_string) == int(library_file_resolution_string):

                            # if index title does not contain any overrides (special editions, higher quality or preferred group) then return False (skip)
                            if not self.filter_quality_check(library_filename):

                                result_details = f"Failed: Index title '{index_title}' does not contain overrides for library filename '{library_filename}'"
                                self.logger_instance.info(result_details)
                                self.result_dict.update({'result': u'Failed'})
                                self.result_details_list.append(result_details)
                                self.result_dict.update({'result_details': self.result_details_list})
                                return False

                        # if index resolution is less than library file then skip
                        if int(index_title_resolution_string) < int(library_file_resolution_string):

                            result_details = f"Failed: Index title '{index_title}' resolution {index_title_resolution_string} is less than library filename '{library_filename}' resolution {library_file_resolution_string}"
                            self.logger_instance.info(result_details)
                            self.result_dict.update({'result': u'Failed'})
                            self.result_details_list.append(result_details)
                            self.result_dict.update({'result_details': self.result_details_list})
                            return False

        result_details = f"Passed: Index title '{index_title}' contains overrides, is higher resolution or does not exist in library path '{library_path}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_imdb_override_genre(self):

        imdb_genres_list = self.result_dict.get('imdb_genres_list', [])

        if not imdb_genres_list:

            result_details = f"Failed: IMDb genre not found, skipping filter genre rating"
            self.logger_instance.info(result_details)
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

    def filter_imdb_rating(self, override_genre_dict):

        imdb_rating = self.result_dict.get('imdb_rating')
        filter_minimum_rating = self.config_dict['filters']['minimum_rating']

        if not filter_minimum_rating:

            result_details = f"Passed: No IMDb minimum rating defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not imdb_rating:

            result_details = f"Failed: No IMDb rating available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
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

            result_details = f"Passed: IMDb rating defined as '{filter_minimum_rating}' is greater than the maximum value of 10.0, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        imdb_rating_dec = Decimal(imdb_rating)
        if imdb_rating_dec >= filter_minimum_rating_dec:

            result_details = f"Passed: IMDb rating '{imdb_rating}' equal to/above threshold '{filter_minimum_rating}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed: IMDb rating '{imdb_rating}' below threshold '{filter_minimum_rating}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_imdb_votes(self, override_genre_dict):

        imdb_votes = self.result_dict.get('imdb_votes')
        filter_minimum_votes = self.config_dict['filters']['minimum_votes']

        if not filter_minimum_votes:

            result_details = f"Passed: No IMDb minimum votes defined, skipping votes check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not imdb_votes:

            result_details = f"Failed: No IMDb votes available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
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

            result_details = f"Passed: IMDb votes '{imdb_votes}' equal to/above threshold '{filter_minimum_votes}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed: IMDb votes '{imdb_votes}' below threshold '{filter_minimum_votes}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_imdb_year(self):

        movie_title_year = self.result_dict.get('movie_title_year')
        filter_minimum_year = self.config_dict['filters']['minimum_year']

        if not filter_minimum_year:

            result_details = f"Passed: No minimum movie year defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not movie_title_year:

            result_details = f"Failed: No movie year available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        movie_title_year_int = int(movie_title_year)
        filter_minimum_year_int = int(filter_minimum_year)

        if movie_title_year_int >= filter_minimum_year_int:

            result_details = f"Passed: Movie year '{movie_title_year}' equal to/above minimum year threshold '{filter_minimum_year}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed: Movie year '{movie_title_year}' below minimum year threshold '{filter_minimum_year}'"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_imdb_runtime(self):

        imdb_runtime_in_minutes = self.result_dict.get('imdb_running_time_in_minutes')
        filter_minimum_runtime_mins = self.config_dict['filters']['minimum_runtime_mins']

        if not filter_minimum_runtime_mins:

            result_details = f"Passed: No minimum runtime defined, assuming above threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not imdb_runtime_in_minutes:

            result_details = f"Failed: No movie runtime available to filter on, assuming below threshold"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        imdb_runtime_int_mins = int(imdb_runtime_in_minutes)
        filter_minimum_runtime_mins_int = int(filter_minimum_runtime_mins)

        if imdb_runtime_int_mins >= filter_minimum_runtime_mins_int:

            result_details = f"Passed: Movie runtime '{imdb_runtime_int_mins}' (mins) equal to/above minimum runtime threshold '{filter_minimum_runtime_mins_int}' (mins)"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        else:

            result_details = f"Failed: Movie runtime '{imdb_runtime_int_mins}' (mins) below minimum runtime threshold '{filter_minimum_runtime_mins_int}' (mins)"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

    def filter_imdb_bad_genre(self):

        imdb_genres_list = self.result_dict.get('imdb_genres_list')
        filter_bad_genre_list = self.config_dict["filters"]['bad_genre_list']

        if not filter_bad_genre_list:

            result_details = f"Passed: No bad genre(s) defined, skipping bad genre check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not imdb_genres_list:

            result_details = f"Passed: No IMDb genre(s) found, skipping bad genre check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        imdb_genres_list_lower = [x.lower() for x in imdb_genres_list]
        filter_bad_genre_list_lower = [x.lower() for x in filter_bad_genre_list]

        for filter_bad_genre in filter_bad_genre_list_lower:

            if filter_bad_genre in imdb_genres_list_lower:

                result_details = f"Failed: IMDb genre(s) '{imdb_genres_list_lower}' match bad genre(s) list '{filter_bad_genre_list_lower}', skipping movie"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed: IMDb genre(s) '{imdb_genres_list_lower}' does NOT match any of the bad genre(s) '{filter_bad_genre_list_lower}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_imdb_bad_title(self):

        filter_bad_movie_title_list = self.config_dict["filters"]['bad_movie_title_list']

        if not filter_bad_movie_title_list:

            result_details = f"Passed: No bad movie titles defined, skipping bad movie title check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        movie_title_and_year_compare = self.result_dict.get('movie_title_and_year_compare')

        for filter_bad_movie_title in filter_bad_movie_title_list:

            # get bad movie title compare using tools various
            filter_bad_movie_title_full_compare = self.tools_filters_instance.index_title_compare(filter_bad_movie_title)

            if filter_bad_movie_title_full_compare in movie_title_and_year_compare:

                result_details = f"Failed: Index title '{movie_title_and_year_compare}' contains bad movie title '{filter_bad_movie_title_full_compare}', skipping movie"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Failed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return False

        result_details = f"Passed: Index title '{movie_title_and_year_compare}' does NOT match any bad movie titles in list"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_imdb_good_type(self):

        imdb_title_type_lower = self.result_dict.get('imdb_title_type').lower()
        filter_good_imdb_title_type_list = self.config_dict["filters"][f"good_imdb_title_type_list"]

        if not filter_good_imdb_title_type_list:

            result_details = f"Passed: No good IMDb types defined, skipping good IMDb type check"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        # convert list from config to lowercase
        filter_good_imdb_title_type_list_lower = [element.lower() for element in filter_good_imdb_title_type_list]

        if imdb_title_type_lower not in filter_good_imdb_title_type_list_lower:

            result_details = f"Failed: IMDb title type '{imdb_title_type_lower}' is not in IMDb good title type '{filter_good_imdb_title_type_list_lower}', skipping movie"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        result_details = f"Passed: IMDb title type '{imdb_title_type_lower}' is in IMDb good title type '{filter_good_imdb_title_type_list_lower}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Passed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return True

    def filter_imdb_good_language_country(self, filter_type):

        imdb_list = self.result_dict.get(f'imdb_{filter_type}_list')
        filter_list = self.config_dict["filters"][f"good_{filter_type}_list"]

        if not filter_list:

            result_details = f"Passed: Filter for '{filter_type}' not defined, skipping '{filter_type}' checks"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        if not imdb_list:

            result_details = f"Passed: IMDb '{filter_type}' not found, assuming '{filter_type}' is OK"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Passed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return True

        imdb_lower_list = [x.lower() for x in imdb_list]
        filter_lower_list = [x.lower() for x in filter_list]

        for filter_lower_item in filter_lower_list:

            if filter_lower_item in imdb_lower_list:

                result_details = f"Passed: IMDb '{filter_type}' list '{imdb_lower_list}' is in good '{filter_type}' list '{filter_lower_list}'"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed: IMDb '{filter_type}' list '{imdb_lower_list}' is not in good '{filter_type}' list '{filter_lower_list}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False

    def filter_imdb_override_person(self, filter_type):

        imdb_list = self.result_dict.get(f'imdb_credits_{filter_type}_list')
        filter_list = self.config_dict["filters"][f"override_{filter_type}_list"]

        if not filter_list:

            result_details = f"Failed: No {filter_type} defined in config, skipping IMDb override {filter_type} checks"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        if not imdb_list:

            result_details = f"Failed: IMDb {filter_type} not found, skipping IMDb override {filter_type} checks"
            self.logger_instance.info(result_details)
            self.result_dict.update({'result': u'Failed'})
            self.result_details_list.append(result_details)
            self.result_dict.update({'result_details': self.result_details_list})
            return False

        imdb_lower_list = [x.lower() for x in imdb_list]
        filter_lower_list = [x.lower() for x in filter_list]

        for filter_lower_item in filter_lower_list:

            if filter_lower_item in imdb_lower_list:

                result_details = f"Passed: IMDb {filter_type} list '{imdb_lower_list}' is in filter override_{filter_type}_list '{filter_lower_list}', skipping votes and rating checks"
                self.logger_instance.info(result_details)
                self.result_dict.update({'result': u'Passed'})
                self.result_details_list.append(result_details)
                self.result_dict.update({'result_details': self.result_details_list})
                return True

        result_details = f"Failed: IMDb {filter_type} list '{imdb_lower_list}' is not in override_{filter_type}_list '{filter_lower_list}'"
        self.logger_instance.info(result_details)
        self.result_dict.update({'result': u'Failed'})
        self.result_details_list.append(result_details)
        self.result_dict.update({'result_details': self.result_details_list})
        return False
