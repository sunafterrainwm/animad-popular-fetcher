#!/usr/bin/env python
import argparse
from datetime import timedelta
import json
import logging
import warnings

from config import FILL_NULL_DATA
from src.fetch_list import FetchList
from src.constants import TODAY_DT, YESTERDAY
from src.database import VideoSn, Popular
from src.animad import AnimadVideoResponse, fetch_animad_video

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging_output = logging.StreamHandler()
logging_output.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logging_output.setFormatter(formatter)
logger.addHandler(logging_output)


def update_anime_mapping(video_data: AnimadVideoResponse):
    sn_new_add: "list[VideoSn]" = list()
    sn_need_fetch: "list[VideoSn]" = list()
    for e in video_data.anime.episodes.values():
        for episode in e:
            inserted, cur_video_sn = VideoSn.load_or_insert(
                episode.videoSn, video_data.video.animeSn
            )
            if inserted:
                logger.info(
                    f"Insert video_sn={episode.videoSn}, animeSn={video_data.video.animeSn}"
                )
                sn_new_add.append(cur_video_sn)
            else:
                logger.debug(
                    f"Skip video_sn={episode.videoSn}, animeSn={video_data.video.animeSn}"
                )
            if episode.videoSn != video_data.video.videoSn:
                sn_need_fetch.append(cur_video_sn)
    return sn_new_add, sn_need_fetch


def update_popular(video_data: AnimadVideoResponse):
    video_sn = video_data.video.videoSn
    popular = video_data.anime.popular
    yesterday_data = Popular.load(video_sn=video_sn, date=YESTERDAY)
    today_data = Popular.load(video_sn=video_sn)
    if yesterday_data and yesterday_data.popular == popular:
        warnings.warn(
            "The data currently obtained is the same as yesterday, maybe Animad has not updated the data yet!"
        )
    else:
        today_data = Popular.load(video_sn=video_sn)
        if today_data and today_data.popular == popular:
            warnings.warn(
                "Today's data already exists, please pay attention to whether you are executing the program repeatedly!"
            )
            return

    inserted, _ = Popular.load_or_insert(video_sn=video_sn, popular=popular)
    if inserted:
        print(f"Insert video_sn={video_sn}, popular={popular}")
        logger.info(f"Insert video_sn={video_sn}, popular={popular}")
    else:
        print(f"Skip video_sn={video_sn}, popular={popular}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fetch_list", nargs="?", default="fetchList.txt", help="fetchList.txt path"
    )
    parser.add_argument("-v", "--verbose", dest="verbose", help="Verbose output.")

    args = parser.parse_args()

    if args.verbose:
        logging_output.setLevel(logging.DEBUG)

    fetch_list = FetchList(args.fetch_list)

    sn_new_add: "list[VideoSn]" = list()
    sn_need_fetch: "list[VideoSn]" = list()
    for video_sn_obj in fetch_list.video_sn_list:
        video_data = fetch_animad_video(video_sn=video_sn_obj.video_sn)
        _sn_new_add, _sn_need_fetch = update_anime_mapping(video_data)
        sn_new_add += _sn_new_add
        sn_need_fetch += _sn_need_fetch
        update_popular(video_data)

    if FILL_NULL_DATA and len(sn_new_add):
        for sn in sn_new_add:
            current = fetch_list.fetch_from_timestamp
            while current < TODAY_DT:
                print(sn.video_sn, Popular.format_date(current))
                Popular.load_or_insert(video_sn=sn.video_sn, date=current, popular=0)
                current += timedelta(days=1)
            pass

    for video_sn_obj in sn_need_fetch:
        video_data = fetch_animad_video(video_sn=video_sn_obj.video_sn)
        update_popular(video_data)


if __name__ == "__main__":
    main()
