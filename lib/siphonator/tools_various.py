import re
import os
import datetime
import ffmpeg
import yaml
from unidecode import unidecode


def current_time():

    # datetime object containing current date and time
    run_current_date_and_time = datetime.datetime.now()

    # convert to human-readable format dd/mm/YY H:M:S
    run_current_date_and_time_converted = run_current_date_and_time.strftime("%d/%m/%Y %H:%M:%S")
    return run_current_date_and_time_converted


def pretty_print_yaml(yaml_string):

    print(yaml.dump(yaml_string, allow_unicode=True, default_flow_style=False))


class ToolsVarious(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.index_title_search_regex = r'\.|_'
        self.index_title_sqlite_regex = r'\.|_|-|\s|&'
        self.index_title_word_match_regex = r'-|\.|_|\[|\]|\(|\)'
        self.index_title_remove_non_ascii_regex = r'[^a-zA-Z0-9]+'
        self.index_title_remove_separators_regex = r'[\.\-_\s\(\):\'\,]+'
        self.index_title_remove_square_brackets_and_content_regex = r'\[[^\]]+\]'
        self.index_title_remove_website_regex = r'www\.[a-zA-Z0-9]+\.[a-zA-Z]{2,4}|[a-zA-Z0-9]+\.com'
        self.index_title_remove_bad_words_regex = r'and|&'
        self.index_title_remove_invalid_windows_filename_chars_regex = r'\?|<|>|:|\"|\/|\\|\||\*'
        self.index_title_resolution_regex = r'\d{3,4}p'
        self.index_title_year_to_end_regex = r'([\s\.\-_\[])(\(?\d{4}\)?)([^pi]).*'
        self.index_title_year_regex = r'^([\.\-_\s\(\):\'\,\[])?(\()?(\d{4})(\))?'
        self.index_title_group_regex = r'([a-zA-Z0-9]+)(\)?)(\[[a-zA-Z0-9]+\])?(\.[a-z0-9]{3})?(\[[a-zA-Z0-9]+\])?$'
        self.index_title_identify_tv_season_or_episode_regex = r'(season([\d]+)?)|s[\d]{2,3}(e[\d]{2,3})?'
        self.index_title_bad_keyword_regex = r'[\s._\-()\[\]]'

    def library_path_walk(self, library_path):

        filter_library_path_walk = os.walk(library_path, topdown=False)

        self.logger_instance.debug(u"Filter library path '%s' walked" % library_path)
        return filter_library_path_walk

    def resolution_from_ffprobe(self, library_filepath, ffprobe_filepath):

        try:

            # get resolution of media
            video_streams = (
                ffmpeg
                .probe(library_filepath, cmd=ffprobe_filepath, select_streams="v")
            )

        except FileNotFoundError:

            self.logger_instance.info(u"ffprobe missing or not on path")
            return None

        stream_width = video_streams['streams'][0]['width']
        stream_height = video_streams['streams'][0]['height']

        if stream_width == 1920:

            # hard set as video height may not be consistent but width should be
            stream_height = '1080'

        elif stream_width == 3840:

            # hard set as video height may not be consistent but width should be
            stream_height = '2160'

        elif stream_width == 1280:

            # hard set as video height may not be consistent but width should be
            stream_height = '720'

        self.logger_instance.debug(u"Resolution from ffmpeg for filepath '%s' is '%s'" % (library_filepath, stream_height))
        return stream_height

    def resolution_from_string(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        resolution_string_search = re.search(self.index_title_resolution_regex, custom_title)
        if resolution_string_search:

            resolution = resolution_string_search.group(0)

            # return numeric value for int comparison
            numeric_filter = filter(str.isdigit, resolution)
            resolution_numeric = "".join(numeric_filter)

        else:

            resolution = None
            resolution_numeric = None

        self.logger_instance.debug(u"Resolution from string '%s' is '%s'" % (custom_title, resolution))
        self.logger_instance.debug(u"Numeric resolution from string '%s' is '%s'" % (custom_title, resolution_numeric))
        return resolution, resolution_numeric

    def custom_title_sqlite(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_sqlite = re.sub(self.index_title_year_to_end_regex, '', custom_title)
        custom_title_sqlite = re.sub(self.index_title_sqlite_regex, '%', custom_title_sqlite)
        custom_title_sqlite = '%%%s%%' % custom_title_sqlite

        return custom_title_sqlite

    def custom_title_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_compare = unidecode(custom_title)
        custom_title_compare = self.custom_title_remove_year_to_end_compare(custom_title_compare)
        custom_title_compare = self.custom_title_strip(custom_title_compare)

        return custom_title_compare

    def custom_title_search(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_search = re.sub(self.index_title_search_regex, ' ', custom_title)

        # remove duplicate whitespaces
        custom_title_search = " ".join(custom_title_search.split()).lower()

        return custom_title_search

    def custom_bad_keyword_search(self, custom_title, filter_bad_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        if filter_bad_title is None:

            self.logger_instance.warning(u'No filter_bad_title sent to function')
            return None

        filter_bad_title_lower = filter_bad_title.lower()
        filter_bad_title_lower_search = re.search(rf'{self.index_title_bad_keyword_regex}{filter_bad_title_lower}{self.index_title_bad_keyword_regex}|{self.index_title_bad_keyword_regex}{filter_bad_title_lower}$', custom_title)

        return filter_bad_title_lower_search

    def custom_title_strip(self, custom_title):

        if custom_title is None:
            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_strip = re.sub(self.index_title_remove_website_regex, '', custom_title).lower()
        custom_title_strip = re.sub(self.index_title_remove_square_brackets_and_content_regex, '', custom_title_strip).lower()
        custom_title_strip = re.sub(self.index_title_remove_separators_regex, '', custom_title_strip).lower()
        custom_title_strip = re.sub(self.index_title_remove_bad_words_regex, '', custom_title_strip).lower()
        custom_title_strip = re.sub(self.index_title_remove_invalid_windows_filename_chars_regex, '', custom_title_strip).lower()
        return custom_title_strip

    def custom_title_word_match_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_word_match_compare = re.sub(self.index_title_word_match_regex, ' ', custom_title)

        # remove duplicate whitespaces
        custom_title_word_match_compare = " ".join(custom_title_word_match_compare.split()).lower()

        return custom_title_word_match_compare

    def custom_title_full_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_full_compare = self.custom_title_strip(custom_title)

        return custom_title_full_compare

    def custom_title_year_to_end_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_year_to_end_compare_search = re.search(self.index_title_year_to_end_regex, custom_title)

        if custom_title_year_to_end_compare_search:

            custom_title_year_to_end_compare = custom_title_year_to_end_compare_search.group(0).lower()
            # remove extra leading character
            custom_title_year_to_end_compare = re.sub(r'^[\s.\-_]+', '', custom_title_year_to_end_compare)

        else:

            return None

        return custom_title_year_to_end_compare

    def custom_title_remove_year_to_end_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_remove_year_to_end_compare = re.sub(self.index_title_year_to_end_regex, '', custom_title).lower()
        return custom_title_remove_year_to_end_compare

    def custom_title_group_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_group_compare_search = re.search(self.index_title_group_regex, custom_title)

        if custom_title_group_compare_search:

            custom_title_group_compare = custom_title_group_compare_search.group(1).lower()

        else:

            return None

        return custom_title_group_compare

    def custom_title_year_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_year_to_end_compare = self.custom_title_year_to_end_compare(custom_title)

        if custom_title_year_to_end_compare is not None:

            custom_title_year_compare_search = re.search(self.index_title_year_regex, custom_title_year_to_end_compare)

            if custom_title_year_compare_search:

                custom_title_year_compare = custom_title_year_compare_search.group(3).lower()

            else:

                return None

        else:

            return None

        return custom_title_year_compare

    def custom_title_and_year_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_compare = self.custom_title_compare(custom_title)
        custom_title_year_compare = self.custom_title_year_compare(custom_title)

        custom_title_and_year_compare = f"{custom_title_compare}{custom_title_year_compare}"
        return custom_title_and_year_compare

    def custom_title_tv_season_episode(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_tv_season_episode_search = bool(re.search(self.index_title_identify_tv_season_or_episode_regex, custom_title.lower()))

        # if search matches regex then return boolean, we do not care about the match only that it did match
        if custom_title_tv_season_episode_search:

            return False

        else:

            return True

    def index_title_process(self, **index_dict):

        if index_dict is None:

            self.logger_instance.warning(u'No kwargs sent to function')
            return None

        index_title = index_dict.get('index_title', None)
        if index_title is None:

            self.logger_instance.warning(u"Index title not found in dictionary '%s'" % index_dict)
            index_dict.update({'result': 'failed', 'result_details': 'Index title not found'})
            return index_dict

        self.logger_instance.debug(u"Index title is '%s'" % index_title)

        index_title_full_compare = self.custom_title_full_compare(index_title)
        if index_title_full_compare is None:

            self.logger_instance.debug(f"Cannot identify index title compare from index title '{index_title}' using regex")
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify index title compare from index title'})
            return index_dict

        self.logger_instance.info(u"Index title full compare is '%s'" % index_title_full_compare)

        index_title_compare = self.custom_title_compare(index_title)
        if index_title_compare is None:

            self.logger_instance.debug(f"Cannot identify compare title from index title '{index_title}' using regex")
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify compare title from index title'})
            return index_dict

        self.logger_instance.info(u"Index title compare is '%s'" % index_title_compare)

        index_title_search = self.custom_title_search(index_title)
        if index_title_search is None:

            self.logger_instance.info(u"Cannot identify search title from index title '%s' using regex '%s'" % (index_title, self.index_title_search_regex))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify search title from index title'})
            return index_dict

        self.logger_instance.info(u"Index title search is '%s'" % index_title_search)

        index_title_year_to_end_compare = self.custom_title_year_to_end_compare(index_title)
        if index_title_year_to_end_compare is None:

            self.logger_instance.info(u"Cannot identify year to end from index title '%s' using regex '%s'" % (index_title, self.index_title_year_to_end_regex))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify year to end from index title'})
            return index_dict

        self.logger_instance.info(u"Index year to end is '%s'" % index_title_year_to_end_compare)

        index_year_compare = self.custom_title_year_compare(index_title)
        if index_year_compare is None:

            self.logger_instance.info(u"Cannot identify year compare from index title '%s' using regex '%s'" % (index_title, self.index_title_year_regex))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify year compare from index title'})
            return index_dict

        self.logger_instance.info(u"Index title year compare is '%s'" % index_year_compare)

        index_title_and_year_compare = self.custom_title_and_year_compare(index_title)
        if index_title_and_year_compare is None:

            self.logger_instance.info(u"Cannot identify index title and year compare from index title '%s'" % index_title)
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify index title and year compare from index title'})
            return index_dict

        self.logger_instance.info(u"Index title and year compare is '%s'" % index_title_and_year_compare)

        index_dict.update({
            'index_title_compare': index_title_compare,
            'index_title_full_compare': index_title_full_compare,
            'index_year_compare': index_year_compare,
            'index_title_search': index_title_search,
            'index_title_year_to_end_compare': index_title_year_to_end_compare,
            'index_title_and_year_compare': index_title_and_year_compare,
            'result': 'success',
            'result_details': 'Identified title and year from index title'
        })

        return index_dict
