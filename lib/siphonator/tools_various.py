import os
import json
import datetime
import ffmpeg
import yaml
from itertools import chain


def current_time():
    # datetime object containing current date and time
    run_current_date_and_time = datetime.datetime.now()

    # convert to human-readable format dd/mm/YY H:M:S
    run_current_date_and_time_converted = run_current_date_and_time.strftime("%d/%m/%Y %H:%M:%S")
    return run_current_date_and_time_converted


def current_time_datetime_object():
    # Get the current date and time as a datetime object
    return datetime.datetime.now()


def convert_unix_timestamp_datetime_object(timestamp):
    # Function to convert Unix timestamp to human-readable format
    return datetime.datetime.fromtimestamp(timestamp)


def convert_string_into_datetime_object(datetime_string):
    # convert string to same format as datetime.datetime.now
    return datetime.datetime.strptime(datetime_string, '"%Y-%m-%d %H:%M:%S"')


def convert_datetime_object_into_string(datetime_object):
    # convert string to same format as datetime.datetime.now
    return datetime.datetime.strftime(datetime_object, '"%Y-%m-%d %H:%M:%S"')


def pretty_print_yaml(yaml_string):
    print(yaml.dump(yaml_string, allow_unicode=True, default_flow_style=False))


def pretty_print_json(json_string):
    print(json.dumps(json_string, indent=4))


def library_path_walk(library_path_list):

    if not library_path_list:
        return None

    # Combine the generators from os.walk for both paths into a single generator
    # note the use of 'chain' to permit multiple generators to be chained together
    filter_library_path_walk = chain.from_iterable(os.walk(library_path, topdown=False) for library_path in library_path_list)
    return filter_library_path_walk


def resolution_from_ffprobe(library_filepath, ffprobe_filepath):

    try:

        # get resolution of media
        video_streams = (
            ffmpeg
            .probe(library_filepath, cmd=ffprobe_filepath, select_streams="v")
        )

    except FileNotFoundError:
        return None

    stream_width = video_streams['streams'][0]['width']
    stream_height = video_streams['streams'][0]['height']

    if stream_width == 1920:

        # hard set as video height may not be consistent but width should be
        stream_height = '1080'

    elif stream_width == 3840:

        # hard set as video height may not be consistent but width should be
        stream_height = '2160'

    elif stream_width == 1280:

        # hard set as video height may not be consistent but width should be
        stream_height = '720'

    return stream_height
