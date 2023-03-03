import re
import os

def get_title_and_year_from_index_title(logger_instance, **index_dict):

    if index_dict is None:

        logger_instance.warning(u'No kwargs sent to function')
        return None


    else:

        index_title = index_dict.get('index_title', None)
        search_site = index_dict.get('search_site', None)

        if index_title is None:

            logger_instance.warning(u"Index title not found in dictionary '%s'" % index_dict)
            index_dict.update({'result': 'failed', 'result_details': 'Index title not found'})
            return index_dict

        if search_site is None:

            logger_instance.warning(u"Search site not found in dictionary '%s'" % index_dict)
            index_dict.update({'result': 'failed', 'result_details': 'Search site not found'})
            return index_dict

    logger_instance.info(u"Index title is '%s'" % index_title)

    index_title_regex_search = r'\.|_'
    index_title_regex_strip = r'[^a-zA-Z0-9]+'
    index_title_remove_year_to_end_regex = r'(\_|\.|\s|\s\()\d{4}(\_|\.|\s|\)\s).*$'
    index_title_year_regex = r'(\_|\.|\s|\s\()\d{4}(\_|\.|\s|\)\s)'

    index_title_strip = re.sub(index_title_remove_year_to_end_regex, '', index_title)
    index_title_compare = re.sub(index_title_regex_strip, '', index_title_strip).lower()
    index_title_year_to_end = re.search(index_title_remove_year_to_end_regex, index_title)
    index_title_search = re.sub(index_title_regex_search, ' ', index_title_strip)
    # remove duplicate whitespaces
    index_title_search = " ".join(index_title_search.split())

    if index_title_compare is None:

        logger_instance.info(u"Cannot identify compare title from index title '%s' using regex '%s'" % (index_title, index_title_regex_strip))
        index_dict.update({'result': 'failed', 'result_details': 'Cannot identify compare title from index title '})
        return index_dict

    logger_instance.info(u"Index title compare is '%s'" % index_title_compare)

    if index_title_search is None:

        logger_instance.info(u"Cannot identify search title from index title '%s' using regex '%s'" % (index_title, index_title_regex_search))
        index_dict.update({'result': 'failed', 'result_details': 'Cannot identify search title from index title'})
        return index_dict

    logger_instance.info(u"Index title search is '%s'" % index_title_search)

    # identify matching string from search of regex against index name
    if index_title_year_to_end:

        index_title_year_to_end = index_title_year_to_end.group(0)

    else:

        logger_instance.info(u"Cannot identify year to end from index title '%s' using regex '%s'" % (index_title, index_title_remove_year_to_end_regex))
        index_dict.update({'result': 'failed', 'result_details': 'Cannot identify year to end from index title'})
        return index_dict

    index_year_compare = re.search(index_title_year_regex, index_title_year_to_end)
    if index_year_compare:

        index_year_compare = index_year_compare.group(0)

    else:

        logger_instance.info(u"Cannot identify search year from index title '%s' using regex '%s'" % (index_title, index_title_year_regex))
        index_dict.update({'result': 'failed', 'result_details': 'Cannot identify search year from index title'})
        return index_dict

    index_year_compare = re.sub(r'[._\s()]+', '', index_year_compare)

    logger_instance.info (u"Index year compare is '%s'" % index_year_compare)
    index_dict.update({'index_title_compare': index_title_compare, 'index_year_compare': index_year_compare, 'index_title_search': index_title_search})
    index_dict.update({'result': 'success', 'result_details': u'Identified title and year from index title'})
    return index_dict

def library_path_walk(logger_instance, library_path):

    filter_library_path_walk = os.walk(library_path, topdown=False)

    logger_instance.info (u"Filter library path '%s' walked" % library_path)
    return filter_library_path_walk
