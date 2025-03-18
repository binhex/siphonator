import re
import pycountry
import omdb
import requests


def get_json_value(logger_instance, omdb_json, key):

    try:
        omdb_value = omdb_json[key]

    except (IndexError, KeyError, TypeError) as e:
        logger_instance.warning(f"Failed: Unable to get IMDb '{key}' from OMDb json, error is '{e}'")
        return None

    return omdb_value


def omdb_get_movie(logger_instance, config_dict, result_dict):

    search_omdb_api_key = config_dict["credentials"]['omdb']['api_key']
    result_details_list = result_dict.get('result_details', [])
    imdb_id = result_dict.get('imdb_id')

    try:
        omdb_instance = omdb.OMDB(api_key=search_omdb_api_key, timeout=30.0)
        omdb_json = omdb_instance.get_movie(imdbid=imdb_id)

    except omdb.exceptions.OMDBTooManyResults:
        result_details = f"Failed: Too many results returned from OMDb"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict, None

    except omdb.exceptions.OMDBNoResults:
        result_details = f"Failed: No results returned from OMDb"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict, None

    except omdb.exceptions.OMDBLimitReached:
        result_details = f"Failed: OMDb API limit reached"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict, None

    except omdb.exceptions.OMDBInvalidAPIKey:
        result_details = f"Failed: Invalid API key for OMDb"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict, None

    except omdb.exceptions.OMDBException as e:
        result_details = f"Failed: Base exception for OMDb, error is '{e}'"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict, None

    except requests.exceptions.ReadTimeout as e:
        result_details = f"Failed: Requests module read timeout exception for OMDb, error is '{e}'"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict, None

    return result_dict, omdb_json


def omdb_json_api(logger_instance, config_dict, result_dict):

    result_details_list = result_dict.get('result_details', [])

    # get omdb json, in a function of it's as we share this function with search_omdb
    result_dict, omdb_json = omdb_get_movie(logger_instance, config_dict, result_dict)

    # if omdb json is None (failed) then return result_dict (contains failure details)
    if not omdb_json:
        return result_dict

    omdb_plot = get_json_value(logger_instance, omdb_json, 'plot')
    if omdb_plot == 'N/A':
        omdb_plot = None

    omdb_type = get_json_value(logger_instance, omdb_json, 'type')
    if omdb_type == 'N/A':
        omdb_type = None

    omdb_poster = get_json_value(logger_instance, omdb_json, 'poster')
    if omdb_poster == 'N/A':
        omdb_poster = None

    omdb_title = get_json_value(logger_instance, omdb_json, 'title')
    if omdb_title == 'N/A':
        omdb_title = None

    omdb_year = get_json_value(logger_instance, omdb_json, 'year')
    if omdb_year == 'N/A':
        omdb_year = None

    omdb_rating = get_json_value(logger_instance, omdb_json, 'imdb_rating')
    if omdb_rating == 'N/A':
        omdb_rating = None

    # strip out commas from votes
    omdb_votes = get_json_value(logger_instance, omdb_json, 'imdb_votes')
    if omdb_votes is not None and omdb_votes != 'N/A':
        omdb_votes_digits_list = re.findall(r'\d+', omdb_votes)
        omdb_votes = ''.join(omdb_votes_digits_list)
    else:
        omdb_votes = None

    # strip out 'mins' from runtime
    omdb_runtime = get_json_value(logger_instance, omdb_json, 'runtime')
    if omdb_runtime is not None and omdb_runtime != 'N/A':
        omdb_runtime_digits_list = re.findall(r'\d+', omdb_runtime)
        omdb_runtime = ''.join(omdb_runtime_digits_list)
    else:
        omdb_runtime = None

    omdb_actors_list = get_json_value(logger_instance, omdb_json, 'actors')
    if omdb_actors_list is not None and omdb_actors_list != 'N/A':
        omdb_actors_list = omdb_actors_list.split(',')
    else:
        omdb_actors_list = None

    omdb_director_list = get_json_value(logger_instance, omdb_json, 'director')
    if omdb_director_list is not None and omdb_director_list != 'N/A':
        omdb_director_list = omdb_director_list.split(',')
    else:
        omdb_director_list = None

    omdb_writer_list = get_json_value(logger_instance, omdb_json, 'writer')
    if omdb_writer_list is not None and omdb_writer_list != 'N/A':
        omdb_writer_list = omdb_writer_list.split(',')
    else:
        omdb_writer_list = None

    omdb_genre_list = get_json_value(logger_instance, omdb_json, 'genre')
    if omdb_genre_list is not None and omdb_genre_list != 'N/A':
        omdb_genre_list = omdb_genre_list.split(',')
    else:
        omdb_genre_list = None

    omdb_country_list = get_json_value(logger_instance, omdb_json, 'country')
    if omdb_country_list is not None and omdb_country_list != 'N/A':
        omdb_country_list = omdb_country_list.split(',')

        # country returned is long name e.g. 'United States' we need to covert to 'us'
        omdb_country_short_list = []
        for omdb_country in omdb_country_list:

            _pycountry = pycountry.countries.get(name=omdb_country)
            if _pycountry is not None:
                short_country = _pycountry.alpha_2.lower()
                omdb_country_short_list.append(short_country)
        omdb_country_list = omdb_country_short_list

    else:
        omdb_country_list = None

    omdb_language_list = get_json_value(logger_instance, omdb_json, 'language')
    if omdb_language_list is not None and omdb_language_list != 'N/A':
        omdb_language_list = omdb_language_list.split(',')

        # language returned is long name e.g. 'english' we need to covert to 'en'
        omdb_language_short_list = []
        for omdb_language in omdb_language_list:

            _pycountry = pycountry.languages.get(name=omdb_language)
            if _pycountry is not None:
                try:
                    omdb_language = _pycountry.alpha_2
                except AttributeError as e:
                    logger_instance.debug(f"Unable to get 2 character country code, error is '{e}'")
                    continue

                omdb_language_short_list.append(omdb_language.lower())
        omdb_language_list = omdb_language_short_list

    else:
        omdb_language_list = None

    result_dict.update({
        'imdb_title': omdb_title,
        'imdb_year': omdb_year,
        'imdb_poster_url': omdb_poster,
        'imdb_trailer_url': None,
        'imdb_plot_summary': omdb_plot,
        'imdb_plot_outline': None,
        'imdb_rating': omdb_rating,
        'imdb_votes': omdb_votes,
        'imdb_title_type': omdb_type,
        'imdb_running_time_in_minutes': omdb_runtime,
        'imdb_genres_list': omdb_genre_list,
        'imdb_credits_character_list': None,
        'imdb_credits_director_list': omdb_director_list,
        'imdb_credits_writer_list': omdb_writer_list,
        'imdb_credits_cast_list': omdb_actors_list,
        'imdb_language_list': omdb_language_list,
        'imdb_country_list': omdb_country_list,
    })

    result_details = f"Passed: Identified IMDb metadata using OMDb"
    logger_instance.info(result_details)
    result_dict.update({'result': u'Passed'})
    result_details_list.append(result_details)
    result_dict.update({'result_details': result_details_list})

    return result_dict
