import imdbpie
import re
import lib.siphonator.tools_various as siphonator_tools_various

# TODO once we have all imdb details in the database then any index title that matches an existing processed title can use the same imdb details without the need to contact imdb


def imdb_json_api(logger_instance, result_dict, config_dict):

    result_dict = result_dict
    result_details_list = result_dict.get('result_details', [])
    credits_cast_list = []
    credits_director_list = []
    credits_writer_list = []
    credits_character_list = []
    spoken_languages_list = []
    country_origins_list = []
    genres_list = []

    imdb_id = result_dict.get('imdb_id')
    logger_instance.info(f"Getting title attributes for movie with IMDb ID '{imdb_id}'...")
    function_name = siphonator_tools_various.get_function_name()

    try:
        imdb_instance = imdbpie.Imdb()

    except OSError:
        result_details = f"Failed {function_name} - Cannot connect to IMDb"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict

    try:
        imdb_get_title_dict = imdb_instance.get_title(str(imdb_id))

    except ValueError:
        result_details = f"Failed {function_name} - Invalid IMDb id '{imdb_id}'"
        logger_instance.warning(result_details)
        result_dict.update({'result': u'Failed'})
        result_details_list.append(result_details)
        result_dict.update({'result_details': result_details_list})
        return result_dict

    imdb_get_title_genres_dict = imdb_instance.get_title_genres(str(imdb_id))
    imdb_get_title_credits_dict = imdb_instance.get_title_credits(str(imdb_id))
    imdb_get_title_auxiliary_dict = imdb_instance.get_title_auxiliary(str(imdb_id))

    try:
        credits_director_json = (imdb_get_title_credits_dict['credits']['director'])
        for i in credits_director_json:
            credits_director_name = i['name']
            if credits_director_name not in credits_director_list and len(credits_director_list) < 20:
                credits_director_list.append(credits_director_name)

    except (IndexError, KeyError, TypeError):
        if not credits_director_list:
            logger_instance.warning(u"Unable to identify IMDb Credits Director")
            credits_director_list = None

    try:
        credits_writer_json = (imdb_get_title_credits_dict['credits']['writer'])
        for i in credits_writer_json:
            credits_writer_name = i['name']
            if credits_writer_name not in credits_writer_list and len(credits_writer_list) < 20:
                credits_writer_list.append(credits_writer_name)

    except (IndexError, KeyError, TypeError):
        if not credits_writer_list:
            logger_instance.warning(u"Unable to identify IMDb Credits Writer")
            credits_writer_list = None

    try:
        credits_cast_json = (imdb_get_title_credits_dict['credits']['cast'])
        for i in credits_cast_json:
            credits_cast_name = i['name']
            if credits_cast_name not in credits_cast_list and len(credits_cast_list) < 20:
                credits_cast_list.append(credits_cast_name)

    except (IndexError, KeyError, TypeError):
        if not credits_cast_list:
            logger_instance.warning(u"Unable to identify IMDb Credits Cast")
            credits_cast_list = None

    try:
        credits_cast_json = (imdb_get_title_credits_dict['credits']['cast'])
        for i in credits_cast_json:
            for credits_character_name in i['characters']:
                if credits_character_name not in credits_character_list and len(credits_character_list) < 20:
                    credits_character_list.append(credits_character_name)

    except (IndexError, KeyError, TypeError):
        if not credits_character_list:
            logger_instance.warning(u"Unable to identify IMDb Credits Characters")
            credits_character_list = None

    try:
        spoken_languages_list = imdb_get_title_auxiliary_dict['spokenLanguages']

    except (IndexError, KeyError, TypeError):
        if not spoken_languages_list:
            logger_instance.warning(u"Unable to identify IMDb Spoken Languages")
            spoken_languages_list = None

    try:
        country_origins_list = imdb_get_title_auxiliary_dict['origins']

    except (IndexError, KeyError, TypeError):
        if not spoken_languages_list:
            logger_instance.warning(u"Unable to identify IMDb Country Origins")
            country_origins_list = None

    try:
        genres_list = (imdb_get_title_genres_dict['genres'])

    except (IndexError, KeyError, TypeError):
        if not genres_list:
            logger_instance.warning(u"Unable to identify IMDb Genres")
            genres_list = None

    try:
        imdb_title = (imdb_get_title_dict['base']['title'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb Title")
        imdb_title = None

    try:
        imdb_year = (imdb_get_title_dict['base']['year'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb Year")
        imdb_year = None

    try:
        imdb_trailer_id = (imdb_get_title_auxiliary_dict['videos']['mainTrailer']['id'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb Trailer")
        imdb_trailer_id = None

    trailer_url = None
    if imdb_trailer_id:

        imdb_trailer_vi_search = re.search('vi[0-9]+', imdb_trailer_id)

        if imdb_trailer_vi_search:

            imdb_trailer_vi = imdb_trailer_vi_search.group()
            trailer_url = f'https://imdb.com/video/{imdb_trailer_vi}'

    try:
        poster_url = (imdb_get_title_dict['base']['image']['url'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb Poster URL")
        poster_url = None

    try:
        title_type = (imdb_get_title_dict['base']['titleType'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb Title Type e.g. Movie/TV")
        title_type = None

    try:
        running_time_in_minutes = (imdb_get_title_dict['base']['runningTimeInMinutes'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb running time in minutes")
        running_time_in_minutes = None

    try:
        plot_summary = (imdb_get_title_dict['plot']['summaries'][0]['text'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb plot summary")
        plot_summary = None

    try:
        plot_outline = (imdb_get_title_dict['plot']['outline']['text'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb plot outline")
        plot_outline = None

    try:
        rating = (imdb_get_title_dict['ratings']['rating'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb rating")
        rating = None

    try:
        votes = (imdb_get_title_dict['ratings']['ratingCount'])

    except (IndexError, KeyError, TypeError):
        logger_instance.warning(u"Unable to identify IMDb rating count")
        votes = None

    result_dict.update({
        'imdb_title': imdb_title,
        'imdb_year': imdb_year,
        'imdb_poster_url': poster_url,
        'imdb_trailer_url': trailer_url,
        'imdb_plot_summary': plot_summary,
        'imdb_plot_outline': plot_outline,
        'imdb_rating': rating,
        'imdb_votes': votes,
        'imdb_title_type': title_type,
        'imdb_running_time_in_minutes': running_time_in_minutes,
        'imdb_genres_list': genres_list,
        'imdb_credits_character_list': credits_character_list,
        'imdb_credits_director_list': credits_director_list,
        'imdb_credits_writer_list': credits_writer_list,
        'imdb_credits_cast_list': credits_cast_list,
        'imdb_language_list': spoken_languages_list,
        'imdb_country_list': country_origins_list,
    })

    result_details = f"Passed {function_name} - Identified IMDb metadata using IMDbPie"
    logger_instance.warning(result_details)
    result_dict.update({'result': u'Passed'})
    result_details_list.append(result_details)
    result_dict.update({'result_details': result_details_list})

    return result_dict
