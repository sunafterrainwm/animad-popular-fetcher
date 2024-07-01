import json
import os

from .database import Popular, VideoSn


class FetchList:
    CURRENT_VERSION = 1

    def __init__(self, fetch_list: os.PathLike) -> None:
        self.video_sn_list: "list[VideoSn]" = list()
        with open(fetch_list, encoding="utf-8") as f:
            header = f.readline()
            if header[0] != "#":
                raise RuntimeError("Header of fetchList.txt isn't valid.")
            try:
                header_data = json.loads(header[1:].strip())
            except json.JSONDecodeError as e:
                raise RuntimeError("Fail to parse header of fetchList.txt.") from e

            header_version = header_data["version"]
            if header_version != FetchList.CURRENT_VERSION:
                raise RuntimeError(
                    f"FetchList version validate fail, current version: {FetchList.CURRENT_VERSION}, header version: {header_version}"
                )

            self.fetch_from_timestamp = Popular.date_from_str(header_data["from"])

            for line in f.readlines():
                if "#" in line:
                    line = line[0 : line.index("#")]
                line = line.strip()
                if line == "":
                    continue
                print(int(line))
                self.video_sn_list.append(VideoSn(int(line)))
