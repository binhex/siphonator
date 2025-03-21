import os
import json
import datetime
import ffmpeg
import yaml
import shutil
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


def helper_get_directory_size(path):

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size


def remove_directory_with_safety_check(logger_instance, src_path, max_path_size_gb=150):

    # calculate the size of the directory
    path_size = helper_get_directory_size(src_path) / (1024 * 1024 * 1024)  # Convert to GB

    # check if the size exceeds the threshold
    if path_size < max_path_size_gb:

        try:
            shutil.rmtree(src_path)
            logger_instance.info(f"Successfully removed source path '{src_path}'")
        except FileNotFoundError as e:
            logger_instance.warning(
                f"The source file path '{src_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        except PermissionError as e:
            logger_instance.warning(f"Permission denied while deleting '{src_path}', error is '{e}'")
        except OSError as e:
            logger_instance.warning(f"General OS error, error is '{e}'")

    else:

        logger_instance.warning(f"Refusing to remove source path '{src_path}', as path size '{path_size}GB' exceeds maximum size safety threshold of '{max_path_size_gb}GB'")


def move_files_folders(logger_instance, config_dict, src_path, dst_path, dst_type):

    # if the destination type is a directory then ensure we append seperator to force destination move to be a directory
    if dst_type is 'dir':
        if not dst_path.endswith(os.sep):
            dst_path += os.sep

    # check if the destination exists, if yes use shutil.copytree, if noy use shutil.move
    if os.path.isdir(dst_path):

        # shutil.copytree will NOT create the destination path (use shutil.move instead), but does permit copying files/directories into an existing destination
        try:
            shutil.copytree(str(src_path), str(dst_path), dirs_exist_ok=True)
            logger_instance.info(f"Successfully copied source path '{src_path}' to destination path '{dst_path}'")
        except FileNotFoundError as e:
            logger_instance.warning(f"The source file path '{src_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        except PermissionError as e:
            logger_instance.warning(f"Permission denied while moving '{src_path}' to '{dst_path}', error is '{e}'")
        except OSError as e:
            logger_instance.warning(f"General OS error, error is '{e}'")

        # get max path size and pass to deletion function
        delete_max_path_size_gb = config_dict['post_process']['delete_max_path_size_gb']

        # once copytree has successfully copied the data across we now need to delete the source path (with checks)
        remove_directory_with_safety_check(logger_instance, src_path, max_path_size_gb=delete_max_path_size_gb)

    else:

        # shutil.move will create the destination path, but will error if the destination already exists (use shutil.copytree instead)
        try:
            shutil.move(str(src_path), str(dst_path))
            logger_instance.info(f"Successfully moved source path '{src_path}' to destination path '{dst_path}'")
        except FileNotFoundError as e:
            logger_instance.warning(f"The source file path '{src_path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
        except PermissionError as e:
            logger_instance.warning(f"Permission denied while moving '{src_path}' to '{dst_path}', error is '{e}'")
        except shutil.Error as e:
            logger_instance.warning(f"General error, error is '{e}'")
        except OSError as e:
            logger_instance.warning(f"General OS error, error is '{e}'")


def delete_files(logger_instance, path):

    # this is a non-recursive deletion of files only, this will not delete directories
    try:
        os.remove(path)
        logger_instance.info(f"Successfully deleted file '{path}'")
    except FileNotFoundError as e:
        logger_instance.warning(f"The file path '{path}' does not exist, if running Siphonator in a Docker container ensure the Docker bind mounts for qBittorrent 'Default save path' match for this container, error is '{e}'")
    except PermissionError as e:
        logger_instance.warning(f"Permission denied while trying to delete '{path}', error is '{e}'")
    except IsADirectoryError as e:
        logger_instance.warning(f"'{path}' is a directory, not a file, error is '{e}'")
    except OSError as e:
        logger_instance.warning(f"General OS error, error is '{e}'")


def rename_files_folders(logger_instance, src_path, dst_path):

    try:
        os.rename(src_path, dst_path)
        logger_instance.info(f"Successfully renamed file/folder from '{src_path}' to '{dst_path}'")
    except FileNotFoundError as e:
        logger_instance.info(f"The folder '{src_path}' does not exist, error is '{e}'")
    except PermissionError as e:
        logger_instance.info(f"Permission denied while renaming '{src_path}' to '{dst_path}'. error is '{e}'")
    except OSError as e:
        logger_instance.info(f"General OS error, error is {e}")


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
