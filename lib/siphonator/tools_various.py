import re


def get_title_and_year_from_index_title(logger_instance, **search_dict):

    if search_dict is None:

        logger_instance.warning(u'No kwargs sent to function')
        return None

    else:

        index_title = search_dict.get('index_title', None)
        search_site = search_dict.get('search_site', None)

        if index_title is None:

            logger_instance.warning(u"Index title not found in dictionary '%s'" % search_dict)
            return None

        if search_site is None:

            logger_instance.warning(u"Search site not found in dictionary '%s'" % search_dict)
            return None

    logger_instance.info(u"Index title is '%s'" % index_title)
    index_title_regex_remove_year_to_end_regex = re.compile('\.?\s?\(?\d{4}.*$')

    index_title_no_year = re.sub(index_title_regex_remove_year_to_end_regex, '', index_title)
    index_title_no_year = re.sub('[._]+', ' ', index_title_no_year)

    if index_title_no_year is None:

        logger_instance.warning(u"Cannot identify search title from index title '%s'" % index_title)
        return None

    index_year_regex = re.compile('(?<!^)[\s._\-()][\d]{4}([\s._\-()]|$)')
    index_year_regex_clean = re.compile('[^\d]+')

    index_year_regex = re.search(index_year_regex, index_title)

    if index_year_regex is None:

        logger_instance.warning(u"Cannot identify search year from index title '%s'" % index_title)
        return None

    else:

        index_year_regex = index_year_regex.group(0)
        index_year_regex = re.sub(index_year_regex_clean, '', index_year_regex)

    logger_instance.info (u"Search title '%s' and search year '%s' identified, looking up details on '%s'..." % (index_title_no_year, index_year_regex, search_site))
    search_dict.update({'index_title_regex': index_title_no_year, 'index_year_regex': index_year_regex})
    return search_dict
