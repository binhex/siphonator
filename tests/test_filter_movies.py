import os
import configobj
import validate
import pytest
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.tools_logging as siphonator_tools_logging

# to run tests from command line use 'python -m pytest --verbose'

@pytest.fixture
def create_logger():

    # get current path for this script, then split to move up directory to root
    app_root_path = os.path.dirname(os.path.realpath(__file__))
    app_root_path, current_directory = os.path.split(app_root_path)

    # set folder path for config files
    configs_path = os.path.join(app_root_path, u"configs")
    configs_path = os.path.normpath(configs_path)
    configs_filepath = os.path.join(configs_path, u"test_config.ini")

    # set path for configspec.ini file
    configspec_filepath = os.path.join(configs_path, u"configspec.ini")

    # set folder path for log files
    logs_path = os.path.join(app_root_path, u"logs")
    logs_path = os.path.normpath(logs_path)
    logs_filepath = os.path.join(logs_path, u"test_siphonator.log")

    # set folder path for db files
    db_path = os.path.join(app_root_path, u"db")
    db_path = os.path.normpath(db_path)
    db_filepath = os.path.join(db_path, u"test_siphonator.db")

    # create configobj instance, set config.ini file, set encoding and set configspec.ini file
    config_obj = configobj.ConfigObj(configs_filepath, list_values=False, write_empty_values=True, encoding='UTF-8',
                                     default_encoding='UTF-8', configspec=configspec_filepath, unrepr=True)

    # create config.ini
    validator = validate.Validator()
    config_obj.validate(validator, copy=True)
    config_obj.filename = configs_filepath
    config_obj.write()

    logger_instance = siphonator_tools_logging.app_logging(config_obj, logs_filepath)
    logger = logger_instance.get('logger')

    # yield used instead of return to allow us to do cleanup afterward
    yield logger

@pytest.fixture
def filter_rating(create_logger, imdb_rating):

    logger = create_logger

    # Arrange
    test_data = {
        'imdb_rating': imdb_rating,
        'filter_minimum_rating': 6.0,
        'filter_genre_minimum_rating': None
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_rating()

    # yield used instead of return to allow us to do cleanup afterward
    yield response

@pytest.fixture
def filter_bad_index_title(create_logger, filter_bad_index_title_list):

    logger = create_logger

    # Arrange
    test_data = {
        'index_title': 'my bad movie title',
        'filter_bad_index_title_list': filter_bad_index_title_list
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_bad_index_title()

    # yield used instead of return to allow us to do cleanup afterward
    yield response

@pytest.fixture
def filter_genre_rating(create_logger, filter_genre_minimum_rating_dict):

    logger = create_logger

    # Arrange
    test_data = {
        'imdb_genres_list': ['sci-fi', 'comedy'],
        'filter_genre_minimum_rating_dict': filter_genre_minimum_rating_dict
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_genre_rating()

    # yield used instead of return to allow us to do cleanup afterward
    yield response

# tests
###

@pytest.mark.parametrize('filter_bad_index_title_list, exp_assert', [
    (['bad'], False),   # keyword found in index title
    (['good'], True),   # keyword good not found in index title
])
def test_filter_bad_index_title(filter_bad_index_title, filter_bad_index_title_list, exp_assert):

    response = filter_bad_index_title

    # Assert
    assert response == exp_assert

@pytest.mark.parametrize('filter_genre_minimum_rating_dict, exp_assert', [
    (({'sci-fi': 6.5, 'comedy': 8.5}), 6.5),    # genres both match, set to the lowest rating value
    (({'sci-fi': 8.5, 'music': 6.5}), 8.5),     # single genre matches
    (({'music': 8.5, 'romance': 6.5}), None),   # neither genre match
])
def test_filter_genre_rating(filter_genre_rating, filter_genre_minimum_rating_dict, exp_assert):

    response = filter_genre_rating

    # Assert
    assert response == exp_assert

@pytest.mark.parametrize('imdb_rating, exp_assert', [
    (100.0, True),  # rating is bad value
    (0.0, False),   # rating is lowest
    (10.0, True),   # rating is highest
    (6.0, True),    # rating is equal to threshold
    (7.0, True),    # rating is above to threshold
])
def test_filter_rating(filter_rating, imdb_rating, exp_assert):

    response = filter_rating

    # Assert
    assert response == exp_assert
