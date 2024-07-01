from datetime import datetime, timedelta, timezone


TZ = timezone(timedelta(hours=8))
TODAY_DT = datetime.now(TZ)
TODAY = TODAY_DT.strftime("%Y-%m-%d")
YESTERDAY_DT = TODAY_DT - timedelta(days=1)
YESTERDAY = YESTERDAY_DT.strftime("%Y-%m-%d")
