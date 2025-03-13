import shutil
import os
import pytest
import pathlib
import test_init
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.tools_filters as siphonator_tools_filters

# to run tests from command line use 'python -m pytest --verbose'


@pytest.fixture
def filter_bad_genre(imdb_genres_list):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'imdb_genres_list': imdb_genres_list,
    }

    # Arrange
    config_dict = {
        'filters': {
            'bad_genre_list': ['Documentary'],
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_imdb_bad_genre()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_preferred_index_group(filter_preferred_index_group_list, library_filename, index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }
    # Arrange
    result_dict = {}

    # Arrange
    config_dict = {
        'filters': {
            'preferred_index_group_list': filter_preferred_index_group_list,
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_index_preferred_group(library_filename, index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_preferred_index_quality(filter_preferred_index_quality_list, library_filename, index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'result_details': [],
    }

    # Arrange
    config_dict = {
        'filters': {
            'preferred_index_quality_list': filter_preferred_index_quality_list,
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_special_editions(library_filename, index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_rating(imdb_rating):

    # get setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'imdb_rating': imdb_rating,
    }

    # Arrange
    config_dict = {
        'filters': {
            'minimum_rating': 6.0,
            'genre_minimum_rating_dict': None,
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Arrange
    override_genre_dict = {}

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_imdb_rating(override_genre_dict)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_bad_index_title(index_title, filter_bad_index_title_list):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'index_title': index_title,
    }

    # Arrange
    config_dict = {
        'filters': {
            'bad_index_title_list': filter_bad_index_title_list
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_index_bad_keyword()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_bad_movie_title(filter_bad_movie_title_list):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'movie_title_and_year_compare': 'badmovie2020',
    }

    # Arrange
    config_dict = {
        'filters': {
            'bad_movie_title_list': filter_bad_movie_title_list
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_imdb_bad_title()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_override_genre(imdb_genres_list, override_genre, override_genre_minimum_rating, override_genre_minimum_votes):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'imdb_genres_list': imdb_genres_list,
    }

    # Arrange
    config_dict = {
        'filters': {
            'minimum_rating': 7.0,
            'minimum_votes': 5000,
            'override_genre': {
                override_genre: {
                    'minimum_rating': override_genre_minimum_rating,
                    'minimum_votes': override_genre_minimum_votes,
                }
            }
        }
    }

    # Arrange
    index_site_dict = {
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict)
    response = siphonator_filter_movies_instance.filter_imdb_override_genre()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_downloaded_iterate_files(index_title, index_site_search, library_path_list, library_filename, filter_preferred_index_group_list, filter_preferred_index_quality_list):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    index_title_compare = tools_filters_instance.sanitise_compare(index_title)
    index_year_compare = tools_filters_instance.movie_title_year(index_title)

    # Arrange
    init_dict = {
        'ffprobe_filepath': ffprobe_filepath,
    }

    # Arrange
    result_dict = {
        'index_title': index_title,
        'index_title_compare': index_title_compare,
        'index_year_compare': index_year_compare,
    }

    # Arrange
    config_dict = {
        'general': {
            'library_path_list': library_path_list,
        },
        'filters': {
            'preferred_index_group_list': filter_preferred_index_group_list,
            'preferred_index_quality_list': filter_preferred_index_quality_list,
        },
    }

    # Arrange
    index_site_dict = {
        'criteria': index_site_search,
    }

    # Arrange
    ####

    for library_path in library_path_list:
        # create test directory structure
        pathlib.Path(library_path).mkdir(parents=True, exist_ok=True)

        # create filepath
        library_filepath = os.path.join(library_path, library_filename)

        # create test movie file from filepath
        open(library_filepath, mode='a').close()

        # walk path to get test directory and filename
        library_path_walk = os.walk(library_path, topdown=False)

        # Act
        siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, init_dict, result_dict, config_dict, index_site_dict, library_path_walk)
        response = siphonator_filter_movies_instance.filter_library_iterate_files()

        # yield used instead of return to allow us to do cleanup afterward
        yield response

        # cleanup test area
        shutil.rmtree(library_path)

# tests
###


@pytest.mark.parametrize('index_title, filter_bad_index_title_list, exp_assert', [
    ('Movie.Title.(2020).1080p.BluRay.ITA.DTS-GROUP', ['ita', 'ts'], False),        # check that index title with ITA does match bad keyword ITA
    ('Movie.Title.(2020).1080p.BluRay TS-GROUP', ['ita', 'ts'], False),             # check that mix of separators still matches bad keyword TS
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', ['ita', 'ts'], True),             # check that partial matches for DTS and TS are not happening
    ('Movie.Title.(2020).1080p.(BluRay)HDTS.DTS-GROUP', ['hdts'], False),           # index title has round brackets near bad keyword, skip
    ('Movie.Title.(2020).1080p.[BluRay]HDTS.DTS-GROUP', ['hdts'], False),           # index title has square brackets near bad keyword, skip
    ('Movie-Title-(2020)-1080p-BluRay-DTS-es-lat', ['es'], False),                  # index title contains bad language les, skip
    ('Movie-Title-(2020)-1080p-BluRay-DTS-es-lat', ['lat'], False),                 # index title contains bad language lat at the end of the index title, skip
    ('Movie Title [2023, WEB-DL 1080p] BluRay DTS Rus, Ukr, Eng', ['ukr'], False),  # index title contains bad language ukr with commas separating languages, skip
])
def test_filter_bad_index_title(filter_bad_index_title, index_title, filter_bad_index_title_list, exp_assert):

    response = filter_bad_index_title

    # Assert
    assert response == exp_assert


# TODO rework so it looks more like the bad_index_title test above
@pytest.mark.parametrize('filter_bad_movie_title_list, exp_assert', [
    (['bad movie (2020)'], False),  # bad movie title found in index title, skip
    (['bad movie'], False),         # bad movie title found in index title, no year, skip
    (['bad.movie.(2020)'], False),  # bad movie title found in index title, period separators, skip
    (['bad_movie_(2020)'], False),  # bad movie title found in index title, underscores separators, skip
    (['good movie (2020)'], True),  # bad movie title not found in index title, continue
])
def test_filter_bad_movie_title(filter_bad_movie_title, filter_bad_movie_title_list, exp_assert):

    response = filter_bad_movie_title

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('imdb_genres_list, override_genre, override_genre_minimum_rating, override_genre_minimum_votes, exp_assert', [
    (['sci-fi'], 'sci-fi', 6.5, 4000, {'minimum_rating': 6.5, 'minimum_votes': 4000}),               # imdb genre matches override genre, return override rating and votes
    (['sci-fi', 'animation'], 'sci-fi', 6.5, 4000, {'minimum_rating': 6.5, 'minimum_votes': 4000}),  # imdb genre matches override genre, return override rating and votes
    (['sci-fi', 'animation'], 'sci-fi', 6.5, None, {'minimum_rating': 6.5}),                         # imdb genre matches override genre, return override rating
    (['sci-fi', 'animation'], 'sci-fi', None, 4000, {'minimum_votes': 4000}),                        # imdb genre matches override genre, return override votes
    (['music'], 'sci-fi', 6.5, 4000, {}),                                                            # imdb genre does not match override genre, return default rating and votes
])
def test_filter_override_genre(filter_override_genre, imdb_genres_list, override_genre, override_genre_minimum_rating, override_genre_minimum_votes, exp_assert):

    response = filter_override_genre

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


@pytest.mark.parametrize('imdb_genres_list, exp_assert', [
    ([], True),                         # genre does not match Documentary
    (['Music'], True),                  # genre does not match Documentary
    (['documentary'], False),           # genre does match Documentary
    (['Documentary'], False),           # genre does match Documentary
    (['Documentary', 'Music'], False),  # genre does match Documentary
])
def test_filter_bad_genre(filter_bad_genre, imdb_genres_list, exp_assert):

    response = filter_bad_genre

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('filter_preferred_index_group_list, library_filename, index_title, exp_assert', [
    ([], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP', False),                                    # no defined preferred group list does results in false
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1', True),             # match for preferred group list and no existing library filename does result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1.mkv', True),         # match for preferred group list and no existing library filename does result in true for index group with file ext
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1[RARBG]', True),      # match for preferred group list and no existing library filename does result in true for index group with tag
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1[RARBG].mkv', True),  # match for preferred group list and no existing library filename does result in true for index group with tag and file ext
    (['GrOuP1', 'GrOuP1'], 'Library.Filename.2023.1080p.WEBRip.x264-oThErGrOuP', 'Index.title.2023.1080p.WEBRip.x264-GrOuP1', True),             # case check for preferred group list does result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP1', 'Index.title.2023.1080p.WEBRip.x264-OTHERGROUP', False),            # existing preferred group in library filename results in false
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-ANOTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-OTHERGROUP', False),      # library and index title groups that do not match results in false
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-OTHERGROUP', False),        # library and index title groups matches results in false
    (['group11', 'group22'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1', False),          # no partial matches for preferred groups results in false
])
def test_filter_preferred_index_group(filter_preferred_index_group, filter_preferred_index_group_list, library_filename, index_title, exp_assert):

    response = filter_preferred_index_group

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('filter_preferred_index_quality_list, library_filename, index_title, exp_assert', [
    ([], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP', False),                                         # no defined preferred quality list does not result in true
    (['remastered'], 'Library.Filename.2023.1080p.remastered.WEBRip.x264-GROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP', False),                  # library filename already contains keyword remastered, do not re-download (False)
    (['directors.cut'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index title 2023 1080p directors WEBRip x264-GROUP', False),                # partial match for quality keyword in index title, do not re-download (False)
    (['remastered'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index.title.2023.1080p.remastered.WEBRip.x264-GROUP', True),                   # index title contains keyword remastered and library filename does not, force download (True)
    (['directors cut'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index.title.2023.1080p.directors.cut.WEBRip.x264-GROUP', True),             # quality keyword contains space, check that index title quality keyword matches, force download (True)
    (['directors.cut'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index title 2023 1080p directors cut.WEBRip x264-GROUP', True),             # use dot for quality keyword and spaces for index title, library filename does not contain quality keyword, force download (True)
    (['directors.cut', 'remastered'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index title 2023 1080p remastered WEBRip x264-GROUP', True),  # more than 1 quality keywords defined, match on second keyword, force download (True)
])
def test_filter_preferred_index_quality(filter_preferred_index_quality, filter_preferred_index_quality_list, library_filename, index_title, exp_assert):

    response = filter_preferred_index_quality

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, index_site_search, library_path_list, library_filename, filter_preferred_index_group_list, filter_preferred_index_quality_list, exp_assert', [
    ('movie title (2020) 1080p bluray dts-group', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], False),                                          # index title matches library file, do not download (False)
    ('movie title (2020) 1080p bluray dts-group', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dtshd-group.mkv', ['preferredgroup'], ['remastered'], False),                                        # index title matches library file, but score is lower for index title, skip
    ('movie title (2020) 1080p bluray dtshd-group', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),                                         # index title matches library file, but score is higher for index title, download
    ('movie title (2020) 1080p bluray dts-group', '720p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], False),                                           # index title found in library, but search criteria does not match library filename
    ('movie title (2030) 1080p bluray dts-group', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),                                           # index title not found in library, index title year different
    ('movie title (2020) 1080p bluray dts-preferredgroup', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),                                  # index title exists in library, but preferred index group found
    ('movie title (2020) 1080p bluray dts-preferredgroup1', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-preferredgroup2.mkv', ['preferredgroup1', 'preferredgroup2'], ['remastered'], False),  # index title contains preferred group and library file contains preferred group, do not download (False)
    ('movie title (2020) 1080p bluray remastered dts-group', '1080p', ['/tmp/tests/test_filter_downloaded_file'], 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),                                # index title found in library, but preferred quality found for index title
])
def test_filter_downloaded_iterate_files(filter_downloaded_iterate_files, index_title, index_site_search, library_path_list, library_filename, filter_preferred_index_group_list, filter_preferred_index_quality_list, exp_assert):

    response = filter_downloaded_iterate_files

    # Assert
    assert response == exp_assert

#
# test functions


@pytest.fixture
def resolution_from_string(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.index_title_resolution(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_sqlite(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.sqlite_query(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.sanitise_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_word_match_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.sanitise_subst(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_full_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.sanitise_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_group_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.index_title_group(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_year_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.movie_title_year(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_year_to_end(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.index_title_after_year_to_end(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_tv_season_episode(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)
    response = siphonator_tools_filters_instance.tv_search(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


# test data


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 48p BluRay DTS-GROUP', None),       # no matching resolution in index title
    ('movie title (2020) 480p BluRay DTS-GROUP', '480'),     # index title with spaces
    ('movie.title.(2020).1080p.BluRay.DTS-GROUP', '1080'),   # index title with periods
    ('Movie_Title_(2020)_2160pp_BluRay_DTS-GROUP', '2160'),  # index title with underscores
])
def test_resolution_from_string(resolution_from_string, index_title, exp_assert):

    response = resolution_from_string

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p bluRay dts-group', '%movie%title%'),         # index title lower case and has spaces
    ('Movie Title (2020) 1080p BluRay DTS-GROUP', '%Movie%Title%'),         # index title mixed case and has spaces
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', '%Movie%Title%'),         # index title mixed case and has periods
    ('Movie_Title_(2020)_1080p_BluRay_DTS-GROUP', '%Movie%Title%'),         # index title mixed case and has underscores
    ('Movie_Title_(2020)_1080p_BluRay_DTS-GROUP[RARBG]', '%Movie%Title%'),  # index title has junk at the end
])
def test_custom_title_sqlite(custom_title_sqlite, index_title, exp_assert):

    response = custom_title_sqlite

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) DTS 1080p', 'movietitle'),                                                  # index title audio encode before resolution
    ('movie title (2020) BD 1080p', 'movietitle'),                                                   # index title source and resolution reversed
    ('movie title (2020) 1080p BluRay DTS', 'movietitle'),                                           # index title has no group
    ('movie title (2020) 1080p BluRay DTS-GROUP', 'movietitle'),                                     # index title lower case and  has spaces
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                                     # index title has periods
    ('Movie.Title.[2020.1080p].BluRay.DTS-GROUP', 'movietitle'),                                     # index title has square brackets around year and resolution
    ('Movie.Title.(2020),1080p.BluRay.DTS-GROUP', 'movietitle'),                                     # index title has periods and comma
    ('Movie:.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                                    # index title has colon
    ('Movie?<>:"/|*.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                             # index title contains all invalid windows filename characters
    ('Movie.&.Title.(2020).1080p.BluRay.DTS-GROUP', 'movieandtitle'),                                # index title has ampersand symbol - replace with 'and'
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movieandtitle'),               # index title has junk square brackets at start
    ('Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movieandtitle'),                 # index title has junk square brackets at end
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movieandtitle'),  # index title has junk square brackets at start and end
    ('www.Torrenting.com   -    Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movieandtitle'),    # index title has junk before title
    ('Æon Flux (2005) 1080p BluRay DTS-GROUP', 'æonflux'),                                           # index title is non ascii english, ensure we permit single non ascii chars
])
def test_custom_title_compare(custom_title_compare, index_title, exp_assert):

    response = custom_title_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p BluRay dts-group', 'movie title 2020 1080p bluray dts group'),    # spaces
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movie title 2020 1080p bluray dts group'),    # periods
    ('MOVIE_TITLE_(2020)_1080p_BLURAY_DTS-GROUP', 'movie title 2020 1080p bluray dts group'),    # underscores and upper case
])
def test_custom_title_word_match_compare(custom_title_word_match_compare, index_title, exp_assert):

    response = custom_title_word_match_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p BluRay dts-group', 'movietitle20201080pbluraydtsgroup'),                                     # spaces
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle20201080pbluraydtsgroup'),                                     # periods
    ('MOVIE_TITLE_(2020)_1080p_BluRay_DTS-GROUP', 'movietitle20201080pbluraydtsgroup'),                                     # underscores and upper case
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movieandtitle20201080pbluraydtsgroup'),               # index title has junk square brackets at start
    ('Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movieandtitle20201080pbluraydtsgroup'),                 # index title has junk square brackets at end
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movieandtitle20201080pbluraydtsgroup'),  # index title has junk square brackets at start and end
])
def test_custom_title_full_compare(custom_title_full_compare, index_title, exp_assert):

    response = custom_title_full_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p bluray dts-group', 'group'),  # hyphen
    ('movie title (2020) 1080p bluray dts-GROUP', 'group'),  # uppercase group name, should vbe lowercase
    ('movie title (2020) 1080p bluray dts group', 'group'),  # space
    ('movie title (2020) 1080p bluray dts_group', 'group'),  # underscore
])
def test_custom_title_group_compare(custom_title_group_compare, index_title, exp_assert):

    response = custom_title_group_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p bluray dts-group', '2020'),       # get year
    ('movie.title.2020.1080p.bluray.dts-group', '2020'),         # periods no brackets for year
    ('2100 movie title 2020 1080p bluray dts_group', '2020'),    # year at start of title, no brackets
    ('Movie.Title.[2020.1080p].BluRay.DTS-GROUP', '2020'),       # index title has square brackets around year and resolution
])
def test_custom_title_year_compare(custom_title_year_compare, index_title, exp_assert):

    response = custom_title_year_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p bluray dts-group', '1080p bluray dts group'),                                      # brackets on year
    ('movie.title.2020.1080p.bluray.dts-group', '1080p bluray dts group'),                                        # no brackets on year
    ('2100 movie title 2020 1080p bluray dts-group', '1080p bluray dts group'),                                   # year at start of title, no brackets
    ('movie.title.2020.REMASTERED.PROPER.1080p.BluRay.x265-GROUP', 'remastered proper 1080p bluray x265 group'),  # real world failing case
    ('Movie.Title.[2020.1080p].BluRay.DTS-GROUP', '1080p bluray dts group'),                                      # index title has square brackets around year and resolution
])
def test_custom_title_year_to_end(custom_title_year_to_end, index_title, exp_assert):

    response = custom_title_year_to_end

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) S01 1080p bluray dts-group', True),       # shorthand season
    ('movie title (2020) Season01 1080p bluray dts-group', True),  # longhand season
    ('movie title (2020) S01E01 1080p bluray dts-group', True),    # shorthand season and episode
    ('movie (2300) title 2020 1080p bluray dts-group', False),     # no season or episode
])
def test_custom_title_tv_season_episode(custom_title_tv_season_episode, index_title, exp_assert):

    response = custom_title_tv_season_episode

    # Assert
    assert response == exp_assert
