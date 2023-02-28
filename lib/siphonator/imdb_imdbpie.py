import imdbpie

# TODO set output to unicode,


def imdb_json_api(logger_instance, **kwargs):

    imdb_dict = kwargs
    credits_cast_list = []
    credits_director_list = []
    credits_character_list = []

    imdb_id = imdb_dict.get('imdb_id', None)
    logger_instance.info(u"Getting title attributes for movie with IMDb ID '%s'..." % imdb_id)

    imdb_instance = imdbpie.Imdb()
    imdb_get_title_dict = imdb_instance.get_title(str(imdb_id))
    imdb_get_title_genres_dict = imdb_instance.get_title_genres(str(imdb_id))
    imdb_get_title_credits_dict = imdb_instance.get_title_credits(str(imdb_id))

    try:
        credits_director_json = (imdb_get_title_credits_dict['credits']['director'])
        for i in credits_director_json:
            credits_director_name = i['name']
            credits_director_list.append(credits_director_name)

    except:
        logger_instance.warning(u"Unable to identify IMDb Credits Director")
        credits_director_list = None

    try:
        credits_cast_json = (imdb_get_title_credits_dict['credits']['cast'])
        for i in credits_cast_json:
            credits_cast_name = i['name']
            credits_cast_list.append(credits_cast_name)

    except:
        logger_instance.warning(u"Unable to identify IMDb Credits Cast")
        credits_cast_list = None

    try:
        credits_cast_json = (imdb_get_title_credits_dict['credits']['cast'])
        for i in credits_cast_json:
            credits_character_name = i['characters'][0]
            credits_character_list.append(credits_character_name)

    except:
        logger_instance.warning(u"Unable to identify IMDb Credits Character")
        credits_character_list = None

    try:
        genres_list = (imdb_get_title_genres_dict['genres'])
    except:
        logger_instance.warning(u"Unable to identify IMDb Genres")
        genres_list = None

    try:
        poster_url = (imdb_get_title_dict['base']['image']['url'])
    except:
        logger_instance.warning(u"Unable to identify IMDb Poster URL")
        poster_url = None

    try:
        title_type = (imdb_get_title_dict['base']['titleType'])
    except:
        logger_instance.warning(u"Unable to identify IMDb Title Type e.g. Movie/TV")
        title_type = None

    try:
        running_time_in_minutes = (imdb_get_title_dict['base']['runningTimeInMinutes'])
    except:
        logger_instance.warning(u"Unable to identify IMDb running time in minutes")
        running_time_in_minutes = None

    try:
        plot_summary = (imdb_get_title_dict['plot']['summaries'][0]['text'])
    except:
        logger_instance.warning(u"Unable to identify IMDb summary")
        plot_summary = None

    try:
        rating = (imdb_get_title_dict['ratings']['rating'])
    except:
        logger_instance.warning(u"Unable to identify IMDb rating")
        rating = None

    try:
        votes = (imdb_get_title_dict['ratings']['ratingCount'])
    except:
        logger_instance.warning(u"Unable to identify IMDb rating count")
        votes = None

    imdb_dict.update({'poster_url': poster_url, 'plot_summary': plot_summary, 'rating': rating, 'votes': votes,
                      'title_type': title_type, 'running_time_in_minutes': running_time_in_minutes,
                      'genres_list': genres_list, 'credits_director_list': credits_director_list,
                      'credits_cast_list': credits_cast_list, 'credits_character_list': credits_character_list})

    return imdb_dict
