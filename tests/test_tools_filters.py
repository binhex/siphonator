import pytest
import test_init
import lib.siphonator.tools_filters as siphonator_tools_filters


# to run tests from command line use 'python -m pytest --verbose'

#
# test functions

@pytest.fixture
def index_name(index_title):
    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Arrange
    result_dict = {
        'index_title': index_title,
    }

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)

    response = siphonator_tools_filters_instance.index_name(result_dict)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


@pytest.fixture
def sqlite_query(index_title):
    # Setup
    test_init_instance = test_init.TestsInit()
    ffprobe_filepath, logger = test_init_instance.setup()

    # Act
    siphonator_tools_filters_instance = siphonator_tools_filters.ToolsFilters(logger)

    response = siphonator_tools_filters_instance.sqlite_query(index_title)

    # yield used instead of return to allow us to do cleanup afterward
    yield response


# test data

@pytest.mark.parametrize('index_title, exp_assert', [
    # check index title with spaces returns expected dict
    ('movie title (2020) 480p BluRay DTS-GROUP',
        {
            'movie_title': 'movie title',
            'movie_title_and_year_compare': 'movietitle2020',
            'movie_title_and_year_search': 'movie title 2020',
            'movie_title_compare': 'movietitle',
            'movie_title_year': '2020',
            'index_title': 'movie title (2020) 480p BluRay DTS-GROUP',
            'index_title_after_year_to_end': '480p bluray dts group',
            'index_title_compare': 'movietitle2020480pbluraydtsgroup',
            'index_title_group': 'group',
            'index_title_resolution': '480',
        }
     ),
    # check index title with periods returns expected dict
    ('movie.title.(2020).480p.BluRay.DTS-GROUP',
        {
            'movie_title': 'movie title',
            'movie_title_and_year_compare': 'movietitle2020',
            'movie_title_and_year_search': 'movie title 2020',
            'movie_title_compare': 'movietitle',
            'movie_title_year': '2020',
            'index_title': 'movie.title.(2020).480p.BluRay.DTS-GROUP',
            'index_title_after_year_to_end': '480p bluray dts group',
            'index_title_compare': 'movietitle2020480pbluraydtsgroup',
            'index_title_group': 'group',
            'index_title_resolution': '480',
        }
     ),
    # check index title with underscores returns expected dict
    ('movie_title_(2020)_480p_BluRay_DTS-GROUP',
        {
            'movie_title': 'movie title',
            'movie_title_and_year_compare': 'movietitle2020',
            'movie_title_and_year_search': 'movie title 2020',
            'movie_title_compare': 'movietitle',
            'movie_title_year': '2020',
            'index_title': 'movie_title_(2020)_480p_BluRay_DTS-GROUP',
            'index_title_after_year_to_end': '480p bluray dts group',
            'index_title_compare': 'movietitle2020480pbluraydtsgroup',
            'index_title_group': 'group',
            'index_title_resolution': '480',
        }
     ),
    # check index title with non ascii chars gets removed
    ('【高清影视之家发布 www.HDBTHD.com】魔发精灵3[国英多音轨+简繁英字幕].Trolls.Band.Together.2023.1080p.BluRay.x264.Atmos.TrueHD7.1-CTRLHD',
        {
            'movie_title': 'Trolls Band Together',
            'movie_title_and_year_compare': 'trollsbandtogether2023',
            'movie_title_and_year_search': 'Trolls Band Together 2023',
            'movie_title_compare': 'trollsbandtogether',
            'movie_title_year': '2023',
            'index_title': '【高清影视之家发布 www.HDBTHD.com】魔发精灵3[国英多音轨+简繁英字幕].Trolls.Band.Together.2023.1080p.BluRay.x264.Atmos.TrueHD7.1-CTRLHD',
            'index_title_after_year_to_end': '1080p bluray x264 atmos truehd7 1 ctrlhd',
            'index_title_compare': 'trollsbandtogether20231080pblurayx264atmostruehd71ctrlhd',
            'index_title_group': 'ctrlhd',
            'index_title_resolution': '1080',
        }
     ),
    # check index title that includes lots of square brackets
    ('Gracie And Pedro Pets To The Rescue (2024) [1080p] [WEBRip] [5.1] YTS',
        {
            'movie_title': 'Gracie And Pedro Pets To The Rescue',
            'movie_title_year': '2024',
            'movie_title_and_year_compare': 'gracieandpedropetstotherescue2024',
            'movie_title_and_year_search': 'Gracie And Pedro Pets To The Rescue 2024',
            'movie_title_compare': 'gracieandpedropetstotherescue',
            'index_title': 'Gracie And Pedro Pets To The Rescue (2024) [1080p] [WEBRip] [5.1] YTS',
            'index_title_after_year_to_end': '1080p webrip 5 1 yts',
            'index_title_compare': 'gracieandpedropetstotherescue20241080pwebrip51yts',
            'index_title_group': 'yts',
            'index_title_resolution': '1080',
        }
     ),
    # check index title strip site tag
    ('Gracie And Pedro Pets To The Rescue (2024) [1080p] [WEBRip] [5.1] YTS [RARBG]',
        {
            'movie_title': 'Gracie And Pedro Pets To The Rescue',
            'movie_title_year': '2024',
            'movie_title_and_year_compare': 'gracieandpedropetstotherescue2024',
            'movie_title_and_year_search': 'Gracie And Pedro Pets To The Rescue 2024',
            'movie_title_compare': 'gracieandpedropetstotherescue',
            'index_title': 'Gracie And Pedro Pets To The Rescue (2024) [1080p] [WEBRip] [5.1] YTS [RARBG]',
            'index_title_after_year_to_end': '1080p webrip 5 1 yts',
            'index_title_compare': 'gracieandpedropetstotherescue20241080pwebrip51yts',
            'index_title_group': 'yts',
            'index_title_resolution': '1080',
        }
     ),
    # check index title strip site tag
    ('Gracie And Pedro Pets To The Rescue (2024) [1080p] [WEBRip] [5.1] YTS@RARBG',
        {
            'movie_title': 'Gracie And Pedro Pets To The Rescue',
            'movie_title_year': '2024',
            'movie_title_and_year_compare': 'gracieandpedropetstotherescue2024',
            'movie_title_and_year_search': 'Gracie And Pedro Pets To The Rescue 2024',
            'movie_title_compare': 'gracieandpedropetstotherescue',
            'index_title': 'Gracie And Pedro Pets To The Rescue (2024) [1080p] [WEBRip] [5.1] YTS@RARBG',
            'index_title_after_year_to_end': '1080p webrip 5 1 yts',
            'index_title_compare': 'gracieandpedropetstotherescue20241080pwebrip51yts',
            'index_title_group': 'yts',
            'index_title_resolution': '1080',
        }
     ),
])
def test_index_name(index_name, index_title, exp_assert):
    response = index_name

    # Assert
    assert response == exp_assert


@pytest.mark.parametrize('index_title, exp_assert', [

    ('movie title (2020) 480p BluRay DTS-GROUP', '%%movie%title%%'),     # check sqlite query is as expected
])
def test_sqlite_query(sqlite_query, index_title, exp_assert):
    response = sqlite_query

    # Assert
    assert response == exp_assert
