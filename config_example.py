
# App configuration file

# GENERAL
data_directory = "/opt/data"

# SOUND
db_threshold = -75 # dB level threshold, lower values increase sensitivity
high_pass_filter_cutoff = "4k"
alarm_detection = True # Enable/Disable audio analysis for alarm detection
recording_seconds = 1 # Number of seconds to record for alarm detection

# IMAGE
human_detection = True
object_detection_threshold = 0.5 # detection probability threshold

# CARRIERS
# TELEGRAM
tg_api_key = ""
tg_chat_id = 123