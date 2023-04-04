import re
import os
import datetime
import ffmpeg

def current_time():

    # datetime object containing current date and time
    run_current_date_and_time = datetime.datetime.now()

    # convert to human-readable format dd/mm/YY H:M:S
    run_current_date_and_time_converted = run_current_date_and_time.strftime("%d/%m/%Y %H:%M:%S")
    return run_current_date_and_time_converted

def ffmpeg_resolution(media_filepath):

    # get resolution of media
    video_streams = ffmpeg.probe(media_filepath, select_streams="v")
    stream_width = video_streams['streams'][0]['width']
    stream_height = video_streams['streams'][0]['height']

    if stream_width == '1920':

        # hard set as video height may not be consistent but width should be
        stream_height = '1080'

    elif stream_width == '3840':

        # hard set as video height may not be consistent but width should be
        stream_height = '2160'

    return stream_height

class ToolsVarious(object):

    def __init__(self, logger_instance):

        self.logger_instance = logger_instance
        self.index_title_regex_search = r'\.|_'
        self.index_title_regex_sqlite = r'\.|_|-|\s'
        self.index_title_regex_word_match =  r'\.|_|\[|\]|\(|\)'
        self.index_title_regex_strip = r'\s|,|\.|_|-|\'|\!|[\(\)]|[\[\]]'
        self.index_title_remove_year_to_end_regex = r'(\_|\.|\s|\s\()\d{4}(\_|\.|\s|\)\s).*$'
        # TODO bug, incorrectly identifies year as 2013 for title 'Cloudy with a Chance of Meatballs (2009, 2013) BDRip 1080p H.265 [UKR_ENG] [Hurtom]'
        self.index_title_year_regex = r'(\_|\.|\s|\s\()\d{4}(\_|\.|\s|\)\s)'

    def custom_title_sqlite(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_strip = re.sub(self.index_title_remove_year_to_end_regex, '', custom_title)
        custom_title_search = re.sub(self.index_title_regex_search, ' ', custom_title_strip)
        custom_title_sqlite = re.sub(self.index_title_regex_sqlite, '%', custom_title_search)
        custom_title_sqlite = '%%%s%%' % custom_title_sqlite
        return custom_title_sqlite

    def custom_title_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_compare = re.sub(self.index_title_regex_strip, '', custom_title).lower()
        return custom_title_compare

    def custom_title_word_match_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_word_match_compare = re.sub(self.index_title_regex_word_match, ' ', custom_title).lower()
        return custom_title_word_match_compare

    def custom_title_full_compare(self, custom_title):

        if custom_title is None:

            self.logger_instance.warning(u'No custom_title sent to function')
            return None

        custom_title_full_compare = re.sub(self.index_title_regex_strip, '', custom_title).lower()
        return custom_title_full_compare

    def index_title_compare_search(self, **index_dict):

        if index_dict is None:

            self.logger_instance.warning(u'No kwargs sent to function')
            return None

        index_title = index_dict.get('index_title', None)

        if index_title is None:

            self.logger_instance.warning(u"Index title not found in dictionary '%s'" % index_dict)
            index_dict.update({'result': 'failed', 'result_details': 'Index title not found'})
            return index_dict

        self.logger_instance.debug(u"Index title is '%s'" % index_title)

        index_title_strip = re.sub(self.index_title_remove_year_to_end_regex, '', index_title)
        index_title_compare = re.sub(self.index_title_regex_strip, '', index_title_strip).lower()
        index_title_full_compare = re.sub(self.index_title_regex_strip, '', index_title).lower()
        index_title_year_to_end = re.search(self.index_title_remove_year_to_end_regex, index_title)
        index_title_search = re.sub(self.index_title_regex_search, ' ', index_title_strip)

        # remove duplicate whitespaces
        index_title_search = " ".join(index_title_search.split())

        if index_title_compare is None:

            self.logger_instance.debug(u"Cannot identify compare title from index title '%s' using regex '%s'" % (index_title, self.index_title_regex_strip))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify compare title from index title'})
            return index_dict

        self.logger_instance.info(u"Index title compare is '%s'" % index_title_compare)

        if index_title_search is None:

            self.logger_instance.info(u"Cannot identify search title from index title '%s' using regex '%s'" % (index_title, self.index_title_regex_search))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify search title from index title'})
            return index_dict

        self.logger_instance.info(u"Index title search is '%s'" % index_title_search)

        # identify matching string from search of regex against index name
        if index_title_year_to_end:

            index_title_year_to_end = index_title_year_to_end.group(0)
            index_title_year_to_end_compare = re.sub(self.index_title_regex_strip, '', index_title_year_to_end).lower()

        else:

            self.logger_instance.info(u"Cannot identify year to end from index title '%s' using regex '%s'" % (index_title, self.index_title_remove_year_to_end_regex))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify year to end from index title'})
            return index_dict

        index_year_compare = re.search(self.index_title_year_regex, index_title_year_to_end)
        if index_year_compare:

            index_year_compare = index_year_compare.group(0)

        else:

            self.logger_instance.info(u"Cannot identify search year from index title '%s' using regex '%s'" % (index_title, self.index_title_year_regex))
            index_dict.update({'result': 'failed', 'result_details': 'Cannot identify search year from index title'})
            return index_dict

        index_year_compare = re.sub(r'[._\s()]+', '', index_year_compare)
        self.logger_instance.info (u"Index year compare is '%s'" % index_year_compare)

        index_title_and_year_compare = "%s%s" % (index_title_compare, index_year_compare)

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

    def library_path_walk(self, library_path):

        filter_library_path_walk = os.walk(library_path, topdown=False)

        self.logger_instance.info (u"Filter library path '%s' walked" % library_path)
        return filter_library_path_walk
