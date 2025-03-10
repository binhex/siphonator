import re

# NOTE: We need to filter for 3 types: imdb title, library filename and index title


class ToolsFilters(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance

        # comparison helpers
        self.helper_invalid_windows_filename_chars_regex = r'\?|<|>|:|\"|\/|\\|\||\*'

        # movie_title, year and group helpers
        self.helper_non_ascii_chars_regex = r'[\.\s\-\_]?(\s?\[?[^\x00-\x7F]{2,}).*([^\x00-\x7F]{2,}\]?\s?)[\.\s\-\_]?'
        self.helper_brackets_at_start_regex = r'^([\s\.\-\_]+)?\[.+?\]'
        self.helper_brackets_at_end_regex = r'\[[^\[]+\]([\s\.\-\_]+)?$'
        self.helper_end_tags_regex = r'[\s\.\-\_]\[[a-zA-Z]+\]$|@[a-zA-Z0-9]+$'
        self.helper_round_square_brackets_regex = r'[\[\]\(\)]+'
        self.helper_movie_title_year_and_end_regex = r'^(.+?\d{4}[\s\.\-\+,]?)(.*)'
        self.helper_file_extension_regex = r'\.[a-z0-9]{3}$'
        self.helper_replacement_words_regex = r'&'
        self.helper_spaces_start_and_end = r'^\s+|\s+$'
        self.helper_website_regex = r'([^\s\.\-\_]+[\s\.\-\_]+){1,3}com[\s\.\-\_]+'

        # various regex
        self.compare_movie_title_regex = r'[\s\.\-\_\:\+]+'
        self.seperator_movie_title_regex = r'[\.\-\_,]+'
        self.sqlite_regex = r'\.|_|-|\s|&'
        self.resolution_regex = r'\d{3,4}(?=p)'

        # core regex
        self.tv_season_or_episode_regex = r'(?i)(season([\d]+)?)|s[\d]{2,3}(e[\d]{2,3})|s[\d]{2,3}|ep[\d]{2,3}'
        self.movie_title_regex = r'^(.*?)(?=[\s\.\-\_]\d{4})'
        self.year_regex = r'(?<=[\(\s\.\-\_])\d{4}(?=[\s\.\-\_\)])'
        self.group_regex = r'[a-zA-Z0-9]+$'

    def sqlite_query(self, string):

        if string is None:
            self.logger_instance.warning(f"No string sent to function")
            return None

        movie_title = self.movie_title(string)
        if not movie_title:
            return None

        sqlite_regex = re.compile(self.sqlite_regex)
        sqlite = sqlite_regex.sub('%', movie_title)
        self.logger_instance.debug(f"input '{movie_title}', regex '{self.sqlite_regex}', output '{sqlite}'")

        result = f"%%{sqlite}%%"
        self.logger_instance.debug(f"Sqlite query regex result is input '{string}', output '{result}'")

        return result

    def keyword_search(self, string, keyword):

        if string is None:
            self.logger_instance.warning(f"No string sent to function")
            return None

        index_title_after_year_to_end = self.index_title_after_year_to_end(string)
        if not index_title_after_year_to_end:
            return None

        result = self.regex_search(index_title_after_year_to_end, rf"^{keyword}\s|\s{keyword}\s|\s{keyword}$")
        self.logger_instance.debug(f"Keyword search regex result is input '{string}', keyword '{keyword}', output '{result}'")
        if result:
            return True
        return False

    def tv_search(self, string):

        if string is None:
            self.logger_instance.warning(f"No string sent to function")
            return None

        result = self.regex_search(string, self.tv_season_or_episode_regex)
        self.logger_instance.debug(f"tv search regex result is input '{string}', output '{result}'")

        if result:
            return True
        return False

    def sanitise_subst(self, string):

        helper_non_ascii_chars_regex = re.compile(self.helper_non_ascii_chars_regex)
        result = helper_non_ascii_chars_regex.sub('', string)
        #self.logger_instance.debug(f"Regex is '{self.helper_non_ascii_chars_regex}', output '{result}'")

        helper_file_extension_regex = re.compile(self.helper_file_extension_regex)
        result = helper_file_extension_regex.sub('', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_file_extension_regex}', output '{result}'")

        helper_brackets_at_start_regex = re.compile(self.helper_brackets_at_start_regex)
        result = helper_brackets_at_start_regex.sub('', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_brackets_at_start_regex}', output '{result}'")

        helper_brackets_at_end_regex = re.compile(self.helper_brackets_at_end_regex)
        result = helper_brackets_at_end_regex.sub('', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_brackets_at_end_regex}', output '{result}'")

        helper_invalid_windows_filename_chars_regex = re.compile(self.helper_invalid_windows_filename_chars_regex)
        result = helper_invalid_windows_filename_chars_regex.sub('', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_invalid_windows_filename_chars_regex}', output '{result}'")

        helper_end_tags_regex = re.compile(self.helper_end_tags_regex)
        result = helper_end_tags_regex.sub('', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_end_tags_regex}', output '{result}'")

        helper_round_square_brackets_regex = re.compile(self.helper_round_square_brackets_regex)
        result = helper_round_square_brackets_regex.sub(' ', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_round_square_brackets_regex}', output '{result}'")

        seperator_movie_title_regex = re.compile(self.seperator_movie_title_regex)
        result = seperator_movie_title_regex.sub(' ', result)
        #self.logger_instance.debug(f"Regex is '{self.seperator_movie_title_regex}', output '{result}'")

        helper_website_regex = re.compile(self.helper_website_regex)
        result = helper_website_regex.sub('', result)
        #self.logger_instance.debug(f"Regex is '{self.helper_website_regex}', output '{result}'")

        result = ' '.join(result.split())
        #self.logger_instance.debug(f"Remove multiple whitespaces, output '{result}'")

        helper_spaces_start_and_end = re.compile(self.helper_spaces_start_and_end)
        result = helper_spaces_start_and_end.sub('', result)

        self.logger_instance.debug(f"Sanitised string regex result is input '{string}', output '{result}'")
        return result

    def regex_search(self, string, regex, group=0):

        if string is None:
            self.logger_instance.debug(f'No string sent to function')
            return None

        regex = re.compile(regex)
        result = regex.search(string)

        if result:
            result = result.group(group)

        self.logger_instance.debug(f"Search regex result is input '{string}', regex '{regex}', output '{result}'")
        return result

    def regex_subst(self, string, subst, regex):

        if string is None:
            self.logger_instance.debug(f'No string sent to function')
            return None

        regex = re.compile(regex)
        result = regex.sub(subst, string)

        self.logger_instance.debug(f"Substitution regex result is input '{string}', subst '{subst} output '{result}'")
        if result:
            result = result
        else:
            return None

        self.logger_instance.debug(f"Substitution regex result is input '{string}', regex '{regex}', substitute '{subst}', output '{result}'")
        return result

    def movie_title(self, string, sanitised_string=None):

        if not sanitised_string:
            sanitised_string = self.sanitise_subst(string)

        result = self.regex_search(sanitised_string, self.movie_title_regex)
        self.logger_instance.debug(f"Movie title regex result is input '{string}', output '{result}'")

        return result

    def movie_title_year(self, string):

        helper_movie_title_year_and_end = self.regex_search(string, self.helper_movie_title_year_and_end_regex, group=1)
        result = self.regex_search(helper_movie_title_year_and_end, self.year_regex)
        self.logger_instance.debug(f"Movie title year regex result is input '{string}', output '{result}'")

        return result

    def movie_title_compare(self, string):

        movie_title = self.movie_title(string)
        if not movie_title:
            return None

        movie_title_compare = self.regex_subst(movie_title, '', self.compare_movie_title_regex)
        result = self.regex_subst(movie_title_compare, 'and', self.helper_replacement_words_regex)
        if result:
            result = result.lower()

        self.logger_instance.debug(f"Movie title compare regex result is input '{string}', output '{result}'")

        return result

    def imdb_title_compare(self, string, sanitised_string=None):

        if not string:
            return None

        if not sanitised_string:
            sanitised_string = self.sanitise_subst(string)

        imdb_title_compare = self.regex_subst(sanitised_string, '', self.compare_movie_title_regex)
        result = self.regex_subst(imdb_title_compare, 'and', self.helper_replacement_words_regex)

        if result:
            result = result.lower()

        self.logger_instance.debug(f"IMDb title compare regex result is input '{string}', output '{result}'")

        return result

    def index_title_after_year_to_end(self, string, sanitised_string=None):

        if not sanitised_string:
            sanitised_string = self.sanitise_subst(string)

        result = self.regex_search(sanitised_string, self.helper_movie_title_year_and_end_regex, group=2)
        if result:
            result = result.lower()

        self.logger_instance.debug(f"Index title after year to end regex result is input '{string}', output '{result}'")

        return result

    def index_title_resolution(self, string):

        index_title_after_year_to_end = self.index_title_after_year_to_end(string)
        if not index_title_after_year_to_end:
            return None

        result = self.regex_search(index_title_after_year_to_end, self.resolution_regex)
        self.logger_instance.debug(f"Index title resolution regex result is input '{string}', output '{result}'")

        return result

    def index_title_group(self, string):

        index_title_after_year_to_end = self.index_title_after_year_to_end(string)
        if not index_title_after_year_to_end:
            return None

        result = self.regex_search(index_title_after_year_to_end, self.group_regex)
        self.logger_instance.debug(f"Index title group regex result is input '{string}', output '{result}'")

        return result

    def index_title_compare(self, string):

        index_title_compare = self.sanitise_subst(string)
        index_title_compare = self.regex_subst(index_title_compare, '', self.compare_movie_title_regex)
        result = self.regex_subst(index_title_compare, 'and', self.helper_replacement_words_regex)
        if result:
            result = result.lower()
        self.logger_instance.debug(f"Index title compare regex result is input '{string}', output '{result}'")

        return result

    def index_name(self, result_dict):

        result_details_list = result_dict.get('result_details', [])

        index_title = result_dict.get('index_title', None)

        # required for tests that may not have index_title defined
        if index_title is None:
            return result_dict

        # remove common characters
        sanitised_string = self.sanitise_subst(index_title)
        if not sanitised_string:
            result_details = f"Failed: Unable to determine sanitised string from index title '{index_title}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        # get required strings from functions
        movie_title = self.movie_title(index_title)
        if not movie_title:
            result_details = f"Failed: Unable to determine movie title from index title '{index_title}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        movie_title_year = self.movie_title_year(index_title)
        if not movie_title_year:
            result_details = f"Failed: Unable to determine movie year from index title '{index_title}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        movie_title_and_year = f"{movie_title} {movie_title_year}"
        if not movie_title_and_year:
            result_details = f"Failed: Unable to determine movie title and year from index title '{index_title}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        movie_title_compare = self.movie_title_compare(index_title)
        if not movie_title_compare:
            result_details = f"Failed: Unable to determine movie title compare from index title '{index_title}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        # get optional strings from functions
        index_title_after_year_to_end = self.index_title_after_year_to_end(index_title, sanitised_string)
        index_title_resolution = self.index_title_resolution(index_title)
        index_title_group = self.index_title_group(index_title)

        # construct other strings from existing variables
        movie_title_and_year_search = f"{movie_title} {movie_title_year}"
        movie_title_and_year_compare = f"{movie_title_compare}{movie_title_year}"

        index_title_compare = self.index_title_compare(index_title)

        index_name_dict = {
            'movie_title': movie_title,
            'movie_title_year': movie_title_year,
            'movie_title_compare': movie_title_compare,
            'movie_title_and_year_compare': movie_title_and_year_compare,
            'movie_title_and_year_search': movie_title_and_year_search,
            'index_title_group': index_title_group,
            'index_title_resolution': index_title_resolution,
            'index_title_compare': index_title_compare,
            'index_title_after_year_to_end': index_title_after_year_to_end,
        }
        result_dict.update(index_name_dict)

        result_details = f"Passed: Identified all information from index title '{index_title}' using regex, resulting dict is '{index_name_dict}'"
        self.logger_instance.info(result_details)
        result_dict.update({'result': u'Passed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict
