
from threading import Lock
# App configuration file

# GENERAL
data_directory = "/opt/data"

# SOUND
db_threshold = -75 # dB level threshold, lower values increase sensitivity
high_pass_filter_cutoff = "3k"
alarm_detection = True # Enable/Disable audio analysis for alarm detection
recording_seconds = 1 # Number of seconds to record for alarm detection
mic_mutex = Lock()
is_recording = False

# IMAGE
human_detection = True
object_detection_threshold = 0.6 # detection probability threshold
capture_all = False # Enable continous camera image acquisition
DEFAULT_CAPTURES = 120
captures = DEFAULT_CAPTURES # Number of photos to capture when a human is detected
photo_evidence_path = "/opt/data/photos"

# CARRIERS
# TELEGRAM
tg_api_key = ""
tg_chat_id = 123