#!/usr/bin/env python
import argparse
import logging

from src.fetch_list import FetchList
from src.database import VideoSn, Popular

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging_output = logging.StreamHandler()
logging_output.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logging_output.setFormatter(formatter)
logger.addHandler(logging_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", help="csv data to export")
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output.")

    restrict_fetch_group = parser.add_mutually_exclusive_group(required=False)
    restrict_fetch_group.add_argument(
        "-r",
        "--restrict-in-fetch-list",
        action="store_true",
        dest="restrict_in_fetch_list",
        help="Restrict output via fetchList.txt.",
    )
    restrict_fetch_group.add_argument(
        "--restrict-in-fetch-list-path",
        type=str,
        dest="restrict_in_fetch_list_path",
        help="Restrict output via specified fetchList.",
    )

    args = parser.parse_args()

    if args.verbose:
        logging_output.setLevel(logging.DEBUG)

    fetch_list_path: "str|None" = None
    if args.restrict_in_fetch_list:
        fetch_list_path = "fetchList.txt"
    elif args.restrict_in_fetch_list_path:
        fetch_list_path = args.restrict_in_fetch_list_path

    if fetch_list_path:
        fetch_list = FetchList(fetch_list_path)
    else:
        fetch_list = None

    with open(args.data, encoding="utf-8", mode="w") as csv_file:
        total_row_count = 0

        def write_data_callback(anime_sn: int, popular_list: "list[Popular]"):
            nonlocal total_row_count
            total_row_count += len(popular_list)
            for popular in popular_list:
                line = "{anime_sn},{video_sn},{date},{popular}".format(
                    anime_sn=anime_sn,
                    video_sn=popular.video_sn,
                    date=Popular.format_date(popular.date).replace("-", "/"),
                    popular=popular.popular,
                )
                logger.debug(line)
                csv_file.write(f"{line}\n")

        if fetch_list:
            all_anime_sn: "list[int]" = []
            for video_sn in fetch_list.video_sn_list:
                db_video_sn = VideoSn.load(video_sn=video_sn.video_sn)
                if not db_video_sn:
                    logger.warning(
                        "videoSn=%d was skipped because the videoSn was not found in the database.",
                        video_sn.video_sn,
                    )
                    continue
                all_anime_sn.append(db_video_sn.anime_sn)

            for anime_sn in all_anime_sn:
                popular_list = Popular.fetch_all_by_anime_sn(anime_sn=anime_sn)
                write_data_callback(anime_sn, popular_list)
        else:
            all_video_sn = VideoSn.fetch_all()

            for video in all_video_sn:
                popular_list = Popular.fetch_all_by_video_sn(video_sn=video.video_sn)
                write_data_callback(video.anime_sn, popular_list)

        logger.info("done, export %d rows.", total_row_count)


if __name__ == "__main__":
    main()
