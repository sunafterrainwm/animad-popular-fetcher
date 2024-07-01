#!/usr/bin/env python
import argparse
import csv
import logging
import sqlite3

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
    parser.add_argument("data", help="csv data to import")
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output.")

    args = parser.parse_args()

    if args.verbose:
        logging_output.setLevel(logging.DEBUG)

    with open(args.data, encoding="utf-8", mode="r") as csvfile:
        csv_reader = csv.reader(csvfile)
        line_no = 0
        for row in csv_reader:
            line_no += 1

            if len(row) != 4:
                logger.warn(f"line {line_no} isn't valid")
                continue

            try:
                (animeSn, videoSn, date, popular) = row
                (animeSn, videoSn, popular) = map(int, (animeSn, videoSn, popular))
                VideoSn(video_sn=videoSn, anime_sn=animeSn).save()
                Popular(video_sn=videoSn, date=date, popular=popular).save()
                logger.debug(f"insert line {line_no} ({animeSn}, {date}) = ({popular})")
            except (RuntimeError, sqlite3.Error) as e:
                logger.error(f"fail to insert line {line_no}:")
                logger.error(e, exc_info=1)

        logger.info(f"done.")


if __name__ == "__main__":
    main()
