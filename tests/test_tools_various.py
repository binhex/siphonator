import pytest
import test_init
import lib.siphonator.tools_various as siphonator_tools_various
# to run tests from command line use 'python -m pytest --verbose'


#
# test functions


@pytest.fixture
def resolution_from_string(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.resolution_from_string(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_sqlite(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_sqlite(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_search(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_search(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_word_match_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_word_match_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_full_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_full_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_group_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_group_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_year_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_year_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_year_to_end_compare(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_year_to_end_compare(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def custom_title_tv_season_episode(index_title):

    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_various_instance = siphonator_tools_various.ToolsVarious(logger)
    response = siphonator_tools_various_instance.custom_title_tv_season_episode(index_title)

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
    ('movie title (2020) DTS 1080p', 'movietitle'),                                               # index title audio encode before resolution
    ('movie title (2020) BD 1080p', 'movietitle'),                                                # index title source and resolution reversed
    ('movie title (2020) 1080p BluRay DTS', 'movietitle'),                                        # index title has no group
    ('movie title (2020) 1080p BluRay DTS-GROUP', 'movietitle'),                                  # index title lower case and  has spaces
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                                  # index title has periods
    ('Movie.Title.[2020.1080p].BluRay.DTS-GROUP', 'movietitle'),                                  # index title has square brackets around year and resolution
    ('Movie.Title.(2020),1080p.BluRay.DTS-GROUP', 'movietitle'),                                  # index title has periods and comma
    ("Movie'.Title.(2020).1080p.BluRay.DTS-GROUP", 'movietitle'),                                 # index title has single quote
    ('Movie:.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                                 # index title has colon
    ('Movie?<>:"/|*.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                          # index title contains all invalid windows filename characters
    ('Movié.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                                  # index title has french e in title
    ('Movie.&.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                                # index title has ampersand symbol - remove
    ('Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),                              # index title has word 'and' - remove
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),               # index title has junk square brackets at start
    ('Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movietitle'),                 # index title has junk square brackets at end
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movietitle'),  # index title has junk square brackets at start and end
    ('www.Torrenting.com   -    Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle'),    # index title has junk before title
    ('Æon Flux (2005) 1080p BluRay DTS-GROUP', 'aeonflux'),                                       # index title is non ascii english, force to ascii using unidecode
])
def test_custom_title_compare(custom_title_compare, index_title, exp_assert):

    response = custom_title_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p bluray.dts-group', 'movie title (2020) 1080p bluray dts-group'),  # spaces and lower case
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movie title (2020) 1080p bluray dts-group'),  # periods and mixed case
    ('MOVIE_TITLE_(2020)_1080p_BluRay_DTS-GROUP', 'movie title (2020) 1080p bluray dts-group'),  # underscores and upper case
])
def test_custom_title_search(custom_title_search, index_title, exp_assert):

    response = custom_title_search

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p BluRay dts-group', 'movie title 2020 1080p bluray dts group'),    # spaces
    ('[movie title (2020) 1080p BluRay dts-group]', 'movie title 2020 1080p bluray dts group'),  # square brackets
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movie title 2020 1080p bluray dts group'),    # periods
    ('MOVIE_TITLE_(2020)_1080p_BLURAY_DTS-GROUP', 'movie title 2020 1080p bluray dts group'),    # underscores and upper case
])
def test_custom_title_word_match_compare(custom_title_word_match_compare, index_title, exp_assert):

    response = custom_title_word_match_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) 1080p BluRay dts-group', 'movietitle20201080pbluraydtsgroup'),                                  # spaces
    ('Movie.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle20201080pbluraydtsgroup'),                                  # periods
    ('MOVIE_TITLE_(2020)_1080p_BluRay_DTS-GROUP', 'movietitle20201080pbluraydtsgroup'),                                  # underscores and upper case
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP', 'movietitle20201080pbluraydtsgroup'),               # index title has junk square brackets at start
    ('Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movietitle20201080pbluraydtsgroup'),                 # index title has junk square brackets at end
    ('[junk at start]Movie.and.Title.(2020).1080p.BluRay.DTS-GROUP[junk at end]', 'movietitle20201080pbluraydtsgroup'),  # index title has junk square brackets at start and end
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
    ('movie title (2020) 1080p bluray dts-group', '(2020) 1080p bluray dts-group'),                                    # brackets on year
    ('movie.title.2020.1080p.bluray.dts-group', '2020.1080p.bluray.dts-group'),                                        # no brackets on year
    ('2100 movie title 2020 1080p bluray dts-group', '2020 1080p bluray dts-group'),                                   # year at start of title, no brackets
    ('movie.title.2020.REMASTERED.PROPER.1080p.BluRay.x265-GROUP', '2020.remastered.proper.1080p.bluray.x265-group'),  # real world failing case
    ('Movie.Title.[2020.1080p].BluRay.DTS-GROUP', '[2020.1080p].bluray.dts-group'),                                    # index title has square brackets around year and resolution
])
def test_custom_title_year_to_end_compare(custom_title_year_to_end_compare, index_title, exp_assert):

    response = custom_title_year_to_end_compare

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [
    ('movie title (2020) S01 1080p bluray dts-group', False),       # shorthand season
    ('movie title (2020) Season01 1080p bluray dts-group', False),  # longhand season
    ('movie title (2020) S01E01 1080p bluray dts-group', False),    # shorthand season and episode
    ('movie (2300) title 2020 1080p bluray dts-group', True),       # no season or episode
])
def test_custom_title_tv_season_episode(custom_title_tv_season_episode, index_title, exp_assert):

    response = custom_title_tv_season_episode

    # Assert
    assert response == exp_assert
