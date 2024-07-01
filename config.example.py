if __name__ == "__main__":
    raise SystemExit()

# 獲取資料用的api
VIDEO_UPSTREAM = "https://api.gamer.com.tw/mobile_app/anime/v4/video.php?sn={sn}"
# 是否將 fetchList 的 from 直到第一次獲取資料中間的空白區段全部補上 0
FILL_NULL_DATA = True
