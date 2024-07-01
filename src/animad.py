import functools
import requests
import re

from ..config import VIDEO_UPSTREAM


class AnimadVideoResponse:
    video: "AnimadVideoResponseVideo"
    anime: "AnimadVideoResponseAnime"

    def __init__(self, data: dict) -> None:
        self.video = AnimadVideoResponseVideo(data["video"])
        self.anime = AnimadVideoResponseAnime(data["anime"])


class AnimadVideoResponseVideo:
    videoSn: int
    animeSn: int
    title: str
    type: int

    def __init__(self, data: dict) -> None:
        self.videoSn = int(data["videoSn"])
        self.animeSn = int(data["animeSn"])
        self.title = str(data["title"])
        self.type = int(data["type"])


class AnimadVideoResponseAnime:
    title: str
    popular: int
    episodeIndex: int
    episodes: "dict[int, list[AnimadVideoResponseAnimeEpisode]]"

    def __init__(self, data: dict) -> None:
        self.title = str(data["title"])
        self.popular = int(data["popular"])
        self.episodeIndex = int(data["episodeIndex"])
        self.episodes = dict(
            map(
                lambda x: (
                    int(x[0]),
                    list(map(lambda d: AnimadVideoResponseAnimeEpisode(d), x[1])),
                ),
                dict(data["episodes"]).items(),
            )
        )


class AnimadVideoResponseAnimeEpisode:
    episode: str
    videoSn: int

    def __init__(self, data: dict) -> None:
        self.episode = str(data["episode"])
        self.videoSn = int(data["videoSn"])


@functools.cache
def fetch_animad_video(video_sn: int) -> AnimadVideoResponse:
    response = requests.get(VIDEO_UPSTREAM.format(sn=video_sn))
    response_json = response.json()
    if dict(response_json).get("error"):
        raise RuntimeError(response_json["error"]["message"])
    return AnimadVideoResponse(response_json["data"])


def get_cleanup_title(data: AnimadVideoResponse) -> str:
    title = data.anime.title
    episode = str(data.anime.episodes[data.video.type][data.anime.episodeIndex].episode)
    parts: "list[tuple[str, str]]" = re.findall(r"(\s?\[(.*?)\])", title)
    partToRemove = [episode, "電影", "特別篇", "中文配音", "年齡限制版"]
    for full, part in parts:
        if part in partToRemove:
            title = title.replace(full, "", 1)
    return title
