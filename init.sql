CREATE TABLE IF NOT EXISTS `videoSnMap`(
    `videoSn` INTEGER PRIMARY KEY,
    `animeSn` INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS `popular` (
    `videoSn` INTEGER NOT NULL,
    `date` TEXT NOT NULL,
    `popular` INTEGER DEFAULT 0,
    FOREIGN KEY (`videoSn`) REFERENCES `videoSnMap`(`videoSn`),
    PRIMARY KEY (`videoSn`, `date`)
);
CREATE TABLE IF NOT EXISTS `animeTitle` (
    `animeSn` INTEGER PRIMARY KEY,
    `title` TEXT NOT NULL,
    FOREIGN KEY (`animeSn`) REFERENCES `videoSnMap`(`animeSn`),
);