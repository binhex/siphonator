import os
import json
import datetime
import ffmpeg
import yaml
import shutil
import hashlib
import pathlib
from itertools import chain
from pathvalidate import sanitize_filepath


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


def resolution_from_ffprobe(logger_instance, library_filepath, ffprobe_filepath):

    try:

        # get resolution of media
        video_streams = (
            ffmpeg.probe(library_filepath, cmd=ffprobe_filepath, select_streams="v")
        )

    except ffmpeg.Error as e:

        logger_instance.warning(f"Failed to identify resolution using ffmpeg probe '{ffprobe_filepath}' on file '{library_filepath}', error is '{e}'")
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


def helper_generate_file_checksum(file_path, algorithm='sha256'):

    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def copy_files(logger_instance, src_path, dst_file_paths, db_sqlite_instance, torrent_tag):

    # get verified status from database
    read_verified = db_sqlite_instance.read_database_value('history', 'verified', 'torrent_tag', torrent_tag)

    if read_verified:

        logger_instance.info(f"Torrent tag '{torrent_tag}' is verified, skipping copy operation")
        return True

    # sanitise destination file and path
    dst_file_path_sanitised_os = sanitize_filepath(dst_file_paths)

    # if the destination path does not exist then sanitise it and create it (shutil.copy does not create path)
    dst_path_sanitised_os = os.path.dirname(dst_file_path_sanitised_os)
    if not make_path(logger_instance, dst_path_sanitised_os):
        return False

    if os.path.isfile(dst_file_path_sanitised_os):

        logger_instance.info(f"Existing destination file found, performing sha256 comparison to verify source file '{src_path}' and destination file '{dst_file_path_sanitised_os}' match....")
        src_sha256 = helper_generate_file_checksum(src_path)
        dst_sha256 = helper_generate_file_checksum(dst_file_path_sanitised_os)

        # if the destination file path does exist and the checksums do match then mark as verified and skip the copy
        if str(src_sha256) == str(dst_sha256):
            logger_instance.info(f"Source path '{src_path}' with checksum '{src_sha256}' matches existing destination path '{dst_file_path_sanitised_os}' with checksum '{dst_sha256}', skipping copy to destination")
            return True

        # if the destination file path does exist but the checksums do not match then delete the destination file.
        logger_instance.warning(f"Source path '{src_path}' with checksum '{src_sha256}' does not match existing destination path '{dst_file_path_sanitised_os}' with checksum '{dst_sha256}', deleting partially copied destination file..")
        if not delete_files(logger_instance, dst_file_path_sanitised_os):
            return False

    # shutil.copy will NOT create the destination path, but does permit copying files/directories into an existing destination
    try:
        shutil.copy(str(src_path), str(dst_file_path_sanitised_os))
        logger_instance.info(f"Successfully copied source path '{src_path}' to destination path '{dst_file_path_sanitised_os}'")
    except FileNotFoundError as e:
        logger_instance.warning(f"The source file path '{src_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        return False
    except PermissionError as e:
        logger_instance.warning(f"Permission denied while moving '{src_path}' to '{dst_file_path_sanitised_os}', error is '{e}'")
        return False
    except OSError as e:
        logger_instance.warning(f"General OS error, error is '{e}'")
        return False

    logger_instance.info(f"Copy complete, performing sha256 checksum comparison to verify source file '{src_path}' and destination file '{dst_file_path_sanitised_os}' match...")
    src_sha256 = helper_generate_file_checksum(src_path)
    dst_sha256 = helper_generate_file_checksum(dst_file_path_sanitised_os)

    if str(src_sha256) != str(dst_sha256):
        logger_instance.warning(f"Source path '{src_path}' with sha256 checksum '{src_sha256}' does not match destination path '{dst_file_path_sanitised_os}' with sha256 checksum '{dst_sha256}' after copy operation, copy failure")
        return False

    logger_instance.info(f"Source path '{src_path}' with sha256 checksum '{src_sha256}' does match destination path '{dst_file_path_sanitised_os}' with sha256 checksum '{dst_sha256}' after copy operation. copy success")
    return True


def make_path(logger_instance, path):

    path = pathlib.Path(path)

    # create destination path
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger_instance.info(f"Successfully created path '{path}'")
    except FileNotFoundError as e:
        logger_instance.warning(f"The parent directory for path '{path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        return False
    except PermissionError as e:
        logger_instance.warning(f"Permission denied while trying to create '{path}', error is '{e}'")
        return False
    except FileExistsError as e:
        logger_instance.warning(f"'{path}' already exists, error is '{e}'")
        return False
    except OSError as e:
        logger_instance.warning(f"General OS error, error is '{e}'")
        return False

    return True


def delete_files(logger_instance, filepath):

    # if the file has already been deleted then return true
    if not os.path.isfile(filepath):
        logger_instance.debug(f"File '{filepath}' does not exist, assuming already deleted")
        return True

    # this is a non-recursive deletion of files only, this will not delete directories
    try:
        os.remove(filepath)
        logger_instance.info(f"Successfully deleted file '{filepath}'")
    except FileNotFoundError as e:
        logger_instance.warning(f"The file path '{filepath}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        return False
    except PermissionError as e:
        logger_instance.warning(f"Permission denied while trying to delete '{filepath}', error is '{e}'")
        return False
    except IsADirectoryError as e:
        logger_instance.warning(f"'{filepath}' is a directory, not a file, error is '{e}'")
        return False
    except OSError as e:
        logger_instance.warning(f"General OS error, error is '{e}'")
        return False

    return True


def get_first_level_directory(path):

    # Normalize the path to handle different OS path separators
    normalized_path = os.path.normpath(path)

    # Split the path into its components
    path_components = normalized_path.split(os.sep)

    # Return the first-level directory name
    if len(path_components) > 1:
        return path_components[1]
    else:
        return path_components[0]
