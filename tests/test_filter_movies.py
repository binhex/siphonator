import os
import configobj
import validate
import pytest
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.tools_logging as siphonator_tools_logging

@pytest.fixture
def create_logger():

    # get current path for this script, then split to move up directory to root
    app_root_path = os.path.dirname(os.path.realpath(__file__))
    app_root_path, current_directory = os.path.split(app_root_path)

    # set folder path for config files
    config_path = os.path.join(app_root_path, u"configs")
    config_path = os.path.normpath(config_path)
    config_ini = os.path.join(config_path, u"test_config.ini")

    # set path for configspec.ini file
    configspec_ini = os.path.join(config_path, u"configspec.ini")

    # set folder path for log files
    logs_path = os.path.join(app_root_path, u"logs")
    logs_path = os.path.normpath(logs_path)
    log_file = os.path.join(logs_path, u"test_siphonator.log")

    # set folder path for db files
    db_path = os.path.join(app_root_path, u"db")
    db_path = os.path.normpath(db_path)
    db_filepath = os.path.join(db_path, u"test_siphonator.db")

    # create configobj instance, set config.ini file, set encoding and set configspec.ini file
    config_obj = configobj.ConfigObj(config_ini, list_values=False, write_empty_values=True, encoding='UTF-8',
                                     default_encoding='UTF-8', configspec=configspec_ini, unrepr=True)

    # create config.ini
    validator = validate.Validator()
    config_obj.validate(validator, copy=True)
    config_obj.filename = config_ini
    config_obj.write()

    logger_instance = siphonator_tools_logging.app_logging(config_obj, log_file)
    logger = logger_instance.get('logger')

    # yield used instead of return to allow us to do cleanup afterwards
    yield logger

@pytest.fixture
def filter_rating(create_logger):

    logger = create_logger

    # Arrange
    test_data = {
        'imdb_rating': 4.0,
        'filter_minimum_rating': 6.0,
        'filter_genre_minimum_rating': None
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_rating()

    # yield used instead of return to allow us to do cleanup afterwards
    yield response

@pytest.fixture
def filter_bad_index_title(create_logger):

    logger = create_logger

    # Arrange
    test_data = {
        'index_title': 'my bad movie title',
        'filter_bad_index_title_list': ['bad']
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_bad_index_title()

    # yield used instead of return to allow us to do cleanup afterwards
    yield response

@pytest.fixture
def filter_genre_rating(create_logger):

    logger = create_logger

    # Arrange
    test_data = {
        'imdb_genres_list': ['sci-fi', 'comedy'],
        'filter_genre_minimum_rating_dict': ({'sci-fi': 6.5, 'comedy': 6.5})
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_genre_rating()

    # yield used instead of return to allow us to do cleanup afterwards
    yield response

def test_filter_bad_index_title(filter_bad_index_title):

    response = filter_bad_index_title

    # Assert - check index title with bad keyword matches bad keyword list
    assert response == False

def test_filter_genre_rating(filter_genre_rating):

    response = filter_genre_rating

    # Assert - check genre rating matches index rating and returns rating value (not None)
    assert response is not None

def test_filter_rating(filter_rating):

    response = filter_rating

    # Assert - check imdb rating below minimum threshold and thus returns false
    assert response == False