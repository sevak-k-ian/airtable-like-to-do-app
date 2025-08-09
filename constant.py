import datetime
# Get current time to generate realistic timestamps
from zoneinfo import ZoneInfo

# 1. Get the current time in UTC (as you did)
now_utc = datetime.datetime.now(datetime.timezone.utc)
# 2. Convert it to the French timezone (Europe/Paris)
french_timezone = ZoneInfo("Europe/Paris")
now_french = now_utc.astimezone(french_timezone)
# 3. Format the result into your desired string format
NOW_FR_DATE = now_french.strftime("%d/%m/%Y %H:%M")

# DB columns
STATUS_OPTIONS = ["Todo", "Done"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]
SOURCE_OPTIONS = ["🔒 Perso", "👩‍❤️‍👨 Famille", "👶 Yeraz", "🤱 Mama", "💼 Hameaux Légers"]
FIRE_OPTIONS = ["🔥", "⏰", ""]