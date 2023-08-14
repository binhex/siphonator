import os
import shutil
import pytest
import pathlib
import lib.siphonator.filter_movies as siphonator_filter_movies
import lib.siphonator.tools_various as siphonator_tools_various
import test_init
# to run tests from command line use 'python -m pytest --verbose'


def setup():

    test_init_instance = test_init.TestsInit()
    logger = test_init_instance.create_logger()
    return logger


@pytest.fixture
def filter_bad_genre(imdb_genres_list):

    logger = setup()

    # Arrange
    test_data = {
        'imdb_genres_list': imdb_genres_list,
        'filter_bad_genre_list': ['Documentary'],
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_bad_genre()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_preferred_index_group(filter_preferred_index_group_list, library_filename, index_title):

    logger = setup()

    # Arrange
    test_data = {
        'filter_preferred_index_group_list': filter_preferred_index_group_list,
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_preferred_index_group(library_filename, index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_preferred_index_quality(filter_preferred_index_quality_list, library_filename, index_title):

    logger = setup()

    # Arrange
    test_data = {
        'filter_preferred_index_quality_list': filter_preferred_index_quality_list,
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_preferred_index_quality(library_filename, index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_rating(imdb_rating):

    logger = setup()

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
def filter_bad_index_title(index_title, filter_bad_index_title_list):

    logger = setup()

    # Arrange
    test_data = {
        'index_title': index_title,
        'filter_bad_index_title_list': filter_bad_index_title_list
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_bad_index_title()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_bad_movie_title(filter_bad_movie_title_list):

    logger = setup()

    # Arrange
    test_data = {
        'index_title_and_year_compare': 'badmovie2020',
        'filter_bad_movie_title_list': filter_bad_movie_title_list
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_bad_movie_title()

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def filter_genre_rating(filter_genre_minimum_rating_dict):

    logger = setup()

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


@pytest.fixture
def filter_downloaded_file(index_title, index_site_search, library_path, filename, filter_preferred_index_group_list, filter_preferred_index_quality_list):

    logger = setup()

    tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    index_title_compare = tools_various_instance.custom_title_compare(index_title)
    index_year_compare = tools_various_instance.custom_title_year_compare(index_title)

    # create test directory structure
    pathlib.Path(library_path).mkdir(parents=True, exist_ok=True)

    # create filepath
    library_filepath = os.path.join(library_path, filename)

    # create test movie file from filepath
    open(library_filepath, mode='a').close()

    # walk path to get test directory and filename
    filter_library_path_walk = os.walk(library_path, topdown=False)

    # Arrange
    test_data = {
        'library_path': library_path,
        'filter_library_path_walk': filter_library_path_walk,
        'index_title': index_title,
        'index_title_compare': index_title_compare,
        'index_year_compare': index_year_compare,
        'index_site_search': index_site_search,
        'filter_preferred_index_group_list': filter_preferred_index_group_list,
        'filter_preferred_index_quality_list': filter_preferred_index_quality_list,
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_downloaded_file()

    # yield used instead of return to allow us to do cleanup afterward
    yield response

    # cleanup test area
    shutil.rmtree(library_path)


@pytest.fixture
def filter_downloaded_dir(library_path, src_filename, dst_filename, dst_directory, index_title, index_site_search):

    logger = setup()

    tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    index_title_compare = tools_various_instance.custom_title_compare(index_title)
    index_year_compare = tools_various_instance.custom_title_year_compare(index_title)

    tests_root_path = os.path.dirname(os.path.realpath(__file__))

    # set path to ffprobe bin
    ffprobe_filepath = os.path.join(tests_root_path, '../tools/ffprobe/static/x64/ffprobe')

    # set src test media filepath
    src_test_media_filepath = os.path.join(tests_root_path, 'media', src_filename)

    # construct dir path
    dst_test_media_library_filepath = os.path.join(library_path, dst_directory, dst_filename)

    # copy test media to test library
    os.makedirs(os.path.dirname(dst_test_media_library_filepath), exist_ok=True)
    shutil.copy(src_test_media_filepath, dst_test_media_library_filepath)

    # walk path to get test directory and filename
    filter_library_path_walk = os.walk(library_path, topdown=False)

    # Arrange
    test_data = {
        'library_path': library_path,
        'ffprobe_filepath': ffprobe_filepath,
        'filter_library_path_walk': filter_library_path_walk,
        'index_title': index_title,
        'index_title_compare': index_title_compare,
        'index_year_compare': index_year_compare,
        'index_site_search': index_site_search,
    }

    # Act
    siphonator_filter_movies_instance = siphonator_filter_movies.FilterMovies(logger, **test_data)
    response = siphonator_filter_movies_instance.filter_downloaded_dir()

    # yield used instead of return to allow us to do cleanup afterward
    yield response

    # cleanup test area
    from pathlib import Path

    def rmdir(pathname):
        pathname = Path(pathname)
        for item in pathname.iterdir():
            if item.is_dir():
                rmdir(item)
            else:
                item.unlink()
        pathname.rmdir()

    rmdir(Path(library_path))

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
    ([], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP', False),                                    # no defined preferred group list does not result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1', True),             # match for preferred group list and no existing library filename does result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1.mkv', True),         # match for preferred group list and no existing library filename does result in true for index group with file ext
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1[RARBG]', True),      # match for preferred group list and no existing library filename does result in true for index group with tag
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1[RARBG].mkv', True),  # match for preferred group list and no existing library filename does result in true for index group with tag and file ext
    (['GrOuP1', 'GrOuP1'], 'Library.Filename.2023.1080p.WEBRip.x264-oThErGrOuP', 'Index.title.2023.1080p.WEBRip.x264-GrOuP1', True),             # case check for preferred group list does result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-GROUP1', 'Index.title.2023.1080p.WEBRip.x264-OTHERGROUP', False),            # existing preferred group in library filename does not result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-ANOTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-OTHERGROUP', False),      # library and index title groups that do not match does not result in true
    (['group1', 'group2'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-OTHERGROUP', False),        # library and index title groups matches does not result in true
    (['group11', 'group22'], 'Library.Filename.2023.1080p.WEBRip.x264-OTHERGROUP', 'Index.title.2023.1080p.WEBRip.x264-GROUP1', False),          # no partial matches for preferred groups does not result in true
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


@pytest.mark.parametrize('index_title, index_site_search, library_path, filename, filter_preferred_index_group_list, filter_preferred_index_quality_list, exp_assert', [
    ('movie title (2020) 1080p bluray dts-group', '1080p', '/tmp/tests/test_filter_downloaded_file', 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], False),            # movie does exist in library
    ('movie title (2020) 1080p bluray dts-group', '720p', '/tmp/tests/test_filter_downloaded_file', 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),              # movie does exist in library, but search criteria are not found in filename
    ('movie title (2030) 1080p bluray dts-group', '1080p', '/tmp/tests/test_filter_downloaded_file', 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),             # movie does not exist in library, index title year different
    ('movie title (2020) 1080p bluray dts-preferredgroup', '1080p', '/tmp/tests/test_filter_downloaded_file', 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),    # movie does exist in library, but preferred index group found
    ('movie title (2020) 1080p bluray remastered dts-group', '1080p', '/tmp/tests/test_filter_downloaded_file', 'movie title (2020) 1080p bluray dts-group.mkv', ['preferredgroup'], ['remastered'], True),  # movie does exist in library, but preferred index quality found
])
def test_filter_downloaded_file(filter_downloaded_file, index_title, index_site_search, library_path, filename, filter_preferred_index_group_list, filter_preferred_index_quality_list, exp_assert):

    response = filter_downloaded_file

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('library_path, src_filename, dst_filename, dst_directory, index_title, index_site_search, exp_assert', [
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2020) 1080p bluray dts-group.mkv', 'movie title (2020)', 'movie title (2020) 1080p bluray dts-group', '1080p bluray', False),    # index title resolution matches existing library file resolution, skip
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2020) 1080p bluray dts-group.mkv', 'movie title (2020)', 'movie title (2020) 720p bluray dts-group', '720p bluray', False),      # index title resolution less than existing library file resolution, skip
    ('/tmp/tests/test_filter_downloaded_dir', 'test-720p.mkv', 'movie title (2020) 720p bluray dts-group.mkv', 'movie title (2020)', 'movie title (2020) 1080p bluray dts-group', '1080p bluray', True),       # index title resolution more than existing library file resolution, continue
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2020) 1080p dts-group.mkv', 'movie title (2020)', 'movie title (2020) 1080p bluray dts-group.mkv', '1080p bluray', True),        # index site search criteria 'bluray' cannot be found in library filename, continue
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2020) bluray dts-group.mkv', 'movie title (2020)', 'movie title (2020) 1080p bluray dts-group.mkv', '1080p bluray', False),      # index site search criteria '1080p' not in library filename, but we identify it from ffprobe as 1080p (matches index site search criteria), skip
    ('/tmp/tests/test_filter_downloaded_dir', 'test-720p.mkv', 'movie title (2020) bluray dts-group.mkv', 'movie title (2020)', 'movie title (2020) 1080p bluray dts-group.mkv', '1080p bluray', True),        # index site search criteria '1080p' not in library filename, but we identify it from ffprobe as 720p (does not match index site search criteria), continue
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2020) 1080p bluray dts-group.mkv', 'movie title2 (2022)', 'movie title (2020) 720p bluray dts-group', '1080p bluray', True),     # index title name does not match directory name, continue
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2022) 1080p bluray dts-group.mkv', "movie title's (2022)", 'movie titles (2022) 720p bluray dts-group', '1080p bluray', False),  # directory name contains apostrophe but should match index title, skip
    ('/tmp/tests/test_filter_downloaded_dir', 'test-1080p.mkv', 'movie title (2022) 1080p bluray dts-group.mkv', 'movie titles (2022)', "movie title's (2022) 720p bluray dts-group", '1080p bluray', False),  # index name contains apostrophe but should match directory name, skip
])
def test_filter_downloaded_dir(filter_downloaded_dir, library_path, src_filename, dst_filename, dst_directory, index_title, index_site_search, exp_assert):

    response = filter_downloaded_dir

    # Assert
    assert response == exp_assert
