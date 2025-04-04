import re


class ToolsFilters(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance

        # comparison helpers
        self.helper_invalid_windows_filename_chars_regex = r'[<>:"/\\|?*]+'

        # movie_title, year and group helpers
        self.helper_non_ascii_chars_regex = r'[\.\s\-\_]?(\s?\[?[^\x00-\x7F]{2,}).*([^\x00-\x7F]{2,}\]?\s?)[\.\s\-\_]?'
        self.helper_brackets_at_start_regex = r'^([\s\.\-\_]+)?\[.+?\]'
        self.helper_brackets_at_end_regex = r'\[[^\[]+\]([\s\.\-\_]+)?$'
        self.helper_braces_at_start_regex = r'^([\s\.\-\_]+)?\{.+?\}'
        self.helper_braces_at_end_regex = r'\{[^\{]+\}([\s\.\-\_]+)?$'
        self.helper_end_tags_regex = r'[\s\.\-\_]\[[a-zA-Z]+\]$|@[a-zA-Z0-9]+$'
        self.helper_round_square_brackets_regex = r'[\[\]\(\)]+'
        self.helper_movie_title_year_and_end_regex = r'^(.+?\d{4}[\s\.\-\+,]?)(.*)'
        self.helper_file_extension_regex = r'\.[a-z0-9]{3}$'
        self.helper_spaces_start_and_end = r'^\s+|\s+$'
        self.helper_website_regex = r'(?i)www[\s\.\-\_][a-zA-Z0-9]+[\s\.\-\_][a-zA-Z0-9]{3,}'
        self.helper_start_date_regex = r'^(\d{2,4}\s){3}'
        self.helper_tt_number_regex = r'(?i)tt\d{7,}'
        self.helper_at_end_regex = r'@.+?$'

        # various regex
        self.compare_movie_title_regex = r'[\s\.\-\_\:\+\'\"\!\,\@\#]+'
        self.seperator_movie_title_regex = r'[\.\-\_,]+'
        self.sqlite_regex = r'\.|_|-|\s|&'
        self.resolution_regex = r'\d{3,4}(?=p)'

        # core regex
        self.tv_season_or_episode_regex = r'(?i)s[\d]{2,3}(e[\d]{2,3})|s[\d]{2,3}|ep[\d]{2,3}'
        self.movie_title_regex = r'^(.*?)(?=[\s\.\-\_]\d{4})'
        self.year_regex = r'(?<=[\(\s\.\-\_])\d{4}(?=[\s\.\-\_\)]|$)'
        self.group_regex = r'[a-zA-Z0-9]+$'

    def sqlite_query(self, string):

        # string can be raw, no pre-processing
        if not string:
            return None

        movie_title = self.movie_title(string)
        if not movie_title:
            return None

        sqlite_regex = re.compile(self.sqlite_regex)
        sqlite = sqlite_regex.sub('%', movie_title)
        self.logger_instance.debug(f"input '{movie_title}', regex '{self.sqlite_regex}', output '{sqlite}'")

        result = f"%%{sqlite}%%"

        return result

    def keyword_search(self, string, keyword):

        # string must have been pre-processed by sanitise_subst
        if not string:
            return None

        index_title_after_year_to_end = self.index_title_after_year_to_end(string)
        if not index_title_after_year_to_end:
            return None

        result = self.regex_search(index_title_after_year_to_end, rf"^{keyword}\s|\s{keyword}\s|\s{keyword}$")

        if result:
            return True
        return False

    def tv_search(self, string):

        # string must have been pre-processed by sanitise_subst and index_title_after_year_to_end functions
        if not string:
            return None

        result = self.regex_search(string, self.tv_season_or_episode_regex)

        if result:
            return True
        return False

    def convert_string_to_integer_string(self, string):

        # string must have been pre-processed by sanitise_subst and index_title_after_year_to_end functions
        if not string:
            return None

        # Define the mapping of words to integers
        word_to_int_dict = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10
        }

        # Define the mapping of roman numerals to integers
        roman_to_int_dict = {
            'i': 1,
            'ii': 2,
            'iii': 3,
            'iv': 4,
            'v': 5,
            'vi': 6,
            'vii': 7,
            'viii': 8,
            'ix': 9,
            'x': 10
        }

        conversion_dict_list = [word_to_int_dict, roman_to_int_dict]

        # iterate over list of conversion dictionaries
        for conversion_dict in conversion_dict_list:

            # iterate over the dictionary and apply re.compile and re.sub
            for key, value in conversion_dict.items():
                regex_pattern = re.compile(fr'(?<=[\s.\-_])({key})(?=[\s.\-_]|$)', re.IGNORECASE)
                string = regex_pattern.sub(str(value), string)

        return string

    def sanitise(self, string):

        # string can be raw, no pre-processing
        if not string:
            return None

        helper_file_extension_regex = re.compile(self.helper_file_extension_regex)
        result = helper_file_extension_regex.sub('', string)

        helper_non_ascii_chars_regex = re.compile(self.helper_non_ascii_chars_regex)
        result = helper_non_ascii_chars_regex.sub('', result)

        helper_brackets_at_start_regex = re.compile(self.helper_brackets_at_start_regex)
        result = helper_brackets_at_start_regex.sub('', result)

        helper_brackets_at_end_regex = re.compile(self.helper_brackets_at_end_regex)
        result = helper_brackets_at_end_regex.sub('', result)

        helper_braces_at_start_regex = re.compile(self.helper_braces_at_start_regex)
        result = helper_braces_at_start_regex.sub('', result)

        helper_braces_at_end_regex = re.compile(self.helper_braces_at_end_regex)
        result = helper_braces_at_end_regex.sub('', result)

        helper_invalid_windows_filename_chars_regex = re.compile(self.helper_invalid_windows_filename_chars_regex)
        result = helper_invalid_windows_filename_chars_regex.sub('', result)

        helper_end_tags_regex = re.compile(self.helper_end_tags_regex)
        result = helper_end_tags_regex.sub('', result)

        helper_round_square_brackets_regex = re.compile(self.helper_round_square_brackets_regex)
        result = helper_round_square_brackets_regex.sub(' ', result)

        seperator_movie_title_regex = re.compile(self.seperator_movie_title_regex)
        result = seperator_movie_title_regex.sub(' ', result)

        helper_website_regex = re.compile(self.helper_website_regex)
        result = helper_website_regex.sub('', result)

        helper_start_date_regex = re.compile(self.helper_start_date_regex)
        result = helper_start_date_regex.sub('', result)

        helper_tt_number_regex = re.compile(self.helper_tt_number_regex)
        result = helper_tt_number_regex.sub('', result)

        helper_at_end_regex = re.compile(self.helper_at_end_regex)
        result = helper_at_end_regex.sub('', result)

        # remove 2+ whitespace
        result = ' '.join(result.split())

        helper_spaces_start_and_end = re.compile(self.helper_spaces_start_and_end)
        result = helper_spaces_start_and_end.sub('', result)

        return result

    # compares imdb title result with movie title from index title
    def compare(self, string):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        string_lower = string.lower()

        # replace & with and
        result = string_lower.replace('&', 'and')

        # remove string imdb from Google search result
        result = result.replace('imdb', '')

        # replace numeric strings or roman numerals with integer values
        result = self.convert_string_to_integer_string(result)

        # remove all separators
        result = self.regex_subst(result, '', self.compare_movie_title_regex)

        return result

    def regex_search(self, string, regex, group=0):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        regex = re.compile(regex)
        result = regex.search(string)

        if result:
            result = result.group(group)

        return result

    def regex_subst(self, string, subst, regex):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        regex = re.compile(regex)
        result = regex.sub(subst, string)

        if result:
            result = result
        else:
            return None

        return result

    def movie_title(self, string):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        result = self.regex_search(string, self.movie_title_regex)

        return result

    def movie_title_year(self, string):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        result = self.regex_search(string, self.year_regex)

        return result

    def index_title_after_year_to_end(self, string):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        result = self.regex_search(string, self.helper_movie_title_year_and_end_regex, group=2)
        if result:
            result = result.lower()

        return result

    def index_title_resolution(self, string):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        index_title_after_year_to_end = self.index_title_after_year_to_end(string)
        if not index_title_after_year_to_end:
            return None

        result = self.regex_search(index_title_after_year_to_end, self.resolution_regex)

        return result

    def index_title_group(self, string):

        # string must have been pre-processed by sanitise_subst function
        if not string:
            return None

        index_title_after_year_to_end = self.index_title_after_year_to_end(string)
        if not index_title_after_year_to_end:
            return None

        result = self.regex_search(index_title_after_year_to_end, self.group_regex)

        return result

    def index_name(self, result_dict):

        result_details_list = result_dict.get('result_details', [])

        index_title = result_dict.get('index_title', None)

        # required for pytest that may not have index_title defined
        if index_title is None:
            return result_dict

        index_title_sanitised = self.sanitise(index_title)
        if not index_title_sanitised:
            result_details = f"Failed: Unable to determine sanitised string from index title '{index_title}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        movie_title = self.movie_title(index_title_sanitised)
        if not movie_title:
            result_details = f"Failed: Unable to determine movie title from index title '{index_title_sanitised}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        movie_title_compare = self.compare(movie_title)
        if not movie_title_compare:
            result_details = f"Failed: Unable to determine movie title compare from index title '{index_title_sanitised}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        movie_title_year = self.movie_title_year(index_title_sanitised)
        if not movie_title_year:
            result_details = f"Failed: Unable to determine movie year from index title '{index_title_sanitised}'"
            self.logger_instance.info(result_details)
            result_dict.update({'result': u'Failed'})
            result_details_list.append(result_details)
            result_dict.update({'result_details': result_details_list})
            return result_dict

        # get optional strings from functions
        index_title_after_year_to_end = self.index_title_after_year_to_end(index_title_sanitised)
        index_title_resolution = self.index_title_resolution(index_title_sanitised)
        index_title_group = self.index_title_group(index_title_sanitised)

        # construct other strings from existing variables
        movie_title_and_year_search = f"{movie_title} {movie_title_year}"
        movie_title_and_year_compare = f"{movie_title_compare}{movie_title_year}"

        index_title_compare = self.compare(index_title_sanitised)

        index_name_dict = {
            'movie_title': movie_title,
            'movie_title_year': movie_title_year,
            'movie_title_compare': movie_title_compare,
            'movie_title_and_year_compare': movie_title_and_year_compare,
            'movie_title_and_year_search': movie_title_and_year_search,
            'index_title_sanitised': index_title_sanitised,
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
