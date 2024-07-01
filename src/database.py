import sqlite3
from datetime import datetime
from contextlib import closing
from typing import Callable

from .constants import TODAY, TZ


db = sqlite3.connect("./data.db")
db.execute("PRAGMA foreign_keys = ON;")


def init_database():
    with closing(db.cursor()) as cursor:
        with open("init.sql", encoding="utf-8") as f:
            cursor.executescript(
                f"""
        BEGIN;
        {f.read()}
        COMMIT;
    """
            )
        db.commit()
    pass


class _KeyDefaultDict[_KT, _VT](dict[_KT, _VT]):
    def __init__(self, default_factory: "Callable[[_KT], _VT]", *args, **kwargs):
        self.default_factory = default_factory
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        value = self.default_factory(key)
        self[key] = value
        return value


class VideoSn:
    _instance_cache: "dict[int, VideoSn|None]" = _KeyDefaultDict(
        lambda x: VideoSn._load_from_db(x)
    )

    @classmethod
    def _load_from_db(cls, video_sn: int):
        assert isinstance(video_sn, int)
        with closing(db.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM `videoSnMap` WHERE `videoSn` = ?", (video_sn,)
            )
            row = cursor.fetchone()
            if row is not None:
                return cls(*row)
            return None

    @classmethod
    def load(cls, video_sn: int) -> "VideoSn|None":
        return cls._instance_cache[video_sn]

    @classmethod
    def load_or_insert(cls, video_sn: int, anime_sn: int):
        inserted = False
        result = cls.load(video_sn)
        if not result:
            inserted = True
            result = cls(video_sn=video_sn, anime_sn=anime_sn)
            result.save()
        return inserted, result

    @classmethod
    def _save(cls, video_sn: int, anime_sn: int):
        print(f"({video_sn}, {anime_sn})")
        with closing(db.cursor()) as cursor:
            cursor.execute(
                "INSERT OR REPLACE INTO `videoSnMap` (`videoSn`, `animeSn`) VALUES (?, ?)",
                (video_sn, anime_sn),
            )
            db.commit()

    def __init__(self, video_sn: int, anime_sn: int | None = None) -> None:
        self.video_sn = video_sn
        self.anime_sn = anime_sn
        pass

    def save(self):
        if (
            self.video_sn in self._instance_cache
            and self._instance_cache[self.video_sn] is not None
        ):
            return

        if self.anime_sn is None:
            raise RuntimeError("animeSn is None")

        with closing(db.cursor()) as cursor:
            cursor.execute(
                "INSERT OR REPLACE INTO `videoSnMap` (`videoSn`, `animeSn`) VALUES (?, ?)",
                (self.video_sn, self.anime_sn),
            )
            db.commit()

        self._instance_cache[self.video_sn] = self

    @classmethod
    def fetch_all(cls):
        with closing(db.cursor()) as cursor:
            cursor.execute("SELECT * FROM `videoSnMap`")
            return list(map(lambda x: cls(*x), cursor.fetchall()))

    @classmethod
    def fetch_all_by_anime_sn(cls, anime_sn: int):
        with closing(db.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM `videoSnMap` WHERE (`animeSn`) = (?)",
                (anime_sn,),
            )
            return list(map(lambda x: cls(*x), cursor.fetchall()))


class Popular(object):
    _instance_cache: "dict[tuple[int, str], Popular|None]" = _KeyDefaultDict(
        lambda x: Popular._load_from_db(x[0], x[1])
    )

    @staticmethod
    def date_from_str(date: str):
        return datetime.strptime(date.replace("/", "-"), "%Y-%m-%d").replace(tzinfo=TZ)

    @staticmethod
    def format_date(date: datetime):
        return date.strftime("%Y-%m-%d")

    @classmethod
    def _load_from_db(cls, video_sn: int, date: str):
        with closing(db.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM `popular` WHERE (`videoSn`, `date`) = (?, ?)",
                (video_sn, date),
            )
            row = cursor.fetchone()
            if row is not None:
                return cls(*row)

        return None

    @classmethod
    def load(cls, video_sn: int, date: str | datetime = TODAY):
        if isinstance(date, datetime):
            date = cls.format_date(date)
        instance = cls._instance_cache[(video_sn, date)]
        if instance:
            return instance
        sn = VideoSn.load(video_sn=video_sn)
        if not sn:
            raise RuntimeError(f"videoSn {video_sn} isn't exist.")
        return None

    @classmethod
    def load_or_insert(
        cls, /, video_sn: int, popular: int, date: str | datetime = TODAY
    ):
        inserted = False
        result = cls.load(video_sn, date)
        if not result:
            inserted = True
            result = cls(video_sn=video_sn, date=date, popular=popular)
            result.save()
        elif result.popular is None:
            inserted = True
            result.save()
        return inserted, result

    def __new__(
        cls,
        video_sn: int,
        date: str | datetime = TODAY,
        popular: int | None = None,
    ):
        if isinstance(date, datetime):
            date = cls.format_date(date)
        if (video_sn, date) in cls._instance_cache:
            instance = cls._instance_cache[(video_sn, date)]
            if instance:
                if popular is not None and instance.popular != popular:
                    instance.popular = popular
                    instance.save()
                return instance
        instance = super(Popular, cls).__new__(cls)
        instance.__init__(video_sn=video_sn, date=date, popular=popular)
        return instance

    def __init__(
        self,
        video_sn: int,
        date: str | datetime = TODAY,
        popular: int | None = None,
    ) -> None:
        self.video_sn = video_sn
        self.date = isinstance(date, datetime) and date or self.date_from_str(date)
        self.popular = popular
        pass

    def save(self):
        if self.popular is None:
            raise RuntimeError("popular is None")

        with closing(db.cursor()) as cursor:
            try:
                cursor.execute(
                    "INSERT OR REPLACE INTO `popular` (`videoSn`, `date`, `popular`) VALUES (?, ?, ?)",
                    (self.video_sn, self.format_date(self.date), self.popular),
                )
            except sqlite3.IntegrityError as e:
                if "FOREIGN KEY constraint failed" in str(e):
                    raise RuntimeError(
                        f"animeSn for videoSn {self.video_sn} doesn't exist in database."
                    ) from e
                raise e
            db.commit()

        self._instance_cache[(self.video_sn, self.format_date(self.date))] = self

    @classmethod
    def fetch_all_by_video_sn(cls, video_sn: int):
        with closing(db.cursor()) as cursor:
            cursor.execute(
                "SELECT `videoSn`, `date`, `popular` FROM `popular` WHERE (`videoSn`) = (?)",
                (video_sn,),
            )
            return list(map(lambda x: cls(*x), cursor.fetchall()))

    @classmethod
    def fetch_all_by_anime_sn(cls, anime_sn: int):
        with closing(db.cursor()) as cursor:
            cursor.execute(
                """
    SELECT
        `popular`.`videoSn`, `popular`.`date`, `popular`.`popular`
    FROM `popular`
    JOIN `videoSnMap` 
        ON `videoSnMap`.`videoSn` = `popular`.`videoSn`
    WHERE (`animeSn`) = (?)
    """,
                (anime_sn,),
            )

            return list(map(lambda x: cls(*x), cursor.fetchall()))
