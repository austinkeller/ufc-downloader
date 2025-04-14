#!/usr/bin/env python3
import os
import re
import difflib
import logging
from typing import Optional

from .indexer import read_index_events_by_titles

logger = logging.getLogger(__name__)

# Configuration
SOURCE_DIR = "/volume1/data/sabnzbd/completed/"
DEST_DIR = "/volume1/data/media/movies"
# RENAME_FILE_FORMAT = (
#     "{movie_title} ({release_year}) {quality_full} {{edition-{edition_tag}}}"
# )
RENAME_FILE_FORMAT = "{movie_title} {{edition-{edition_tag}}}"


def find_closest_match(
    movie_title: str, titles_to_events_map: dict[str, dict]
) -> Optional[str]:
    # Find the closest match
    closest_matches = difflib.get_close_matches(
        movie_title, titles_to_events_map.keys(), n=1, cutoff=0.6
    )

    if closest_matches:
        closest_match = closest_matches[0]
        logger.info(f"Closest match found: {closest_match}")
        return closest_match
    else:
        logger.error(f"No close match found for the movie title {movie_title}")
        return None


def handle_empty_source_dir(
    source_path: str,
    interactive: bool,
    auto_delete_empty_source_dir: bool,
) -> bool:
    """
    Handle the case where the source directory is empty.

    Args:
        source_path (str): The path to the source directory.
        interactive (bool): Whether to prompt the user interactively.
        auto_delete_empty_source_dir (bool): Whether to automatically delete the empty source directory.

    Returns:
        bool: True if the directory was deleted, False otherwise.
    """
    if interactive:
        user_input = input(f"{source_path} is empty. Delete? (y/n): ")
        if user_input.lower() == "y":
            os.rmdir(source_path)
            print(f"Deleted empty directory: {source_path}")
            return True
    elif auto_delete_empty_source_dir:
        os.rmdir(source_path)
        print(f"Deleted empty directory: {source_path}")
        return True
    return False


def import_downloads(
    auto_delete_empty_source_dir: bool = False,
    auto_overwrite_destination_file: bool = False,
    interactive: bool = False,
) -> bool:
    titles_to_events_map = read_index_events_by_titles()
    if not titles_to_events_map:
        logger.error("No events found in the index.")
        return False
    try:
        # Scan for UFC files by looking for the "UFC." prefix
        for src_root, src_dirs, src_files in os.walk(SOURCE_DIR):
            for dir_name in src_dirs:
                if dir_name.upper().startswith("UFC."):
                    # Found one.
                    source_path = os.path.join(src_root, dir_name)

                    # Check if the source path is empty. If so, delete the directory and continue.
                    if not os.listdir(source_path):
                        handle_empty_source_dir(
                            source_path, interactive, auto_delete_empty_source_dir
                        )
                        continue

                    # For the destination path, rename the directory replacing "." with " "
                    tokens = dir_name.split(".")
                    # If any tokens have format "S##E##", then skip this directory
                    # regex
                    if any(re.match(r"S\d{2}E\d{2}", token) for token in tokens):
                        print(f"Skipping {source_path} because it looks like a TV show")
                        continue
                    # Strip any tokens that look like 720p, 1080p, etc. Also strip any tokens that follow these.
                    for i, token in enumerate(tokens):
                        if re.match(r"\d{3,4}p", token):
                            tokens = tokens[:i]
                            break

                    movie_title = " ".join(tokens)

                    # Classify the edition as either Main Event, Prelims, or Early Prelims
                    edition = "Main Event"
                    if "early prelims" in movie_title.lower():
                        edition = "Early Prelims"
                    elif "prelims" in movie_title.lower():
                        edition = "Prelims"

                    # Match to an event
                    event_name = find_closest_match(movie_title, titles_to_events_map)
                    if not event_name:
                        print(f"Skipping {source_path} because no match found.")
                        continue
                    movie_title = event_name if event_name else movie_title

                    dest_dir_name = RENAME_FILE_FORMAT.format(
                        movie_title=movie_title, edition_tag=edition
                    )
                    dest_path = os.path.join(DEST_DIR, dest_dir_name)
                    logger.info(f"Found UFC directory: {source_path}")
                    logger.info(f"Destination path: {dest_path}")

                    # Check if destination path exists. If it does, list contents and offer to overwrite.
                    if os.path.exists(dest_path):
                        logger.info(f"Destination path {dest_path} already exists")
                        logger.info("Contents:")
                        for _, _, dest_files in os.walk(dest_path):
                            for file in dest_files:
                                logger.info(f"  {file}")
                        ok_overwrite_destination_file = False
                        if interactive:
                            user_input = input("Overwrite? (y/n): ")
                            if user_input.lower() == "y":
                                ok_overwrite_destination_file = True
                        if auto_overwrite_destination_file:
                            ok_overwrite_destination_file = True
                        if not ok_overwrite_destination_file:
                            continue
                        logger.info(f"Deleting {dest_path}")
                        os.rmdir(dest_path)

                    # Move the directory
                    ok_move_directory = False
                    if interactive:
                        user_input = input("Move? (y/n): ")
                        if user_input.lower() == "y":
                            ok_move_directory = True
                    else:
                        # Not interactive implies it is okay to auto-import
                        ok_move_directory = True
                    if not ok_move_directory:
                        continue
                    os.rename(source_path, dest_path)
                    logger.info(f"Moved {source_path} to {dest_path}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False
    return True
