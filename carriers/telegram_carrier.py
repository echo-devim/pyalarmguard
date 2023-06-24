import requests
import time
import json
import sys
import os
from sensors.sensor_microphone import SensorMicrophone
from sensors.sensor_camera import SensorCamera
import config
import threading

class CarrierTelegram():

    def __init__(self, logger):
        self.name = "telegram"
        self.logger = logger
        self.max_attempts = 10
        self.attempt_delay_sec = 10
        # Read configuration to retrieve API Key and chat id
        if (config.tg_api_key == ""):
            print("Telegram configuration not found in config, missing mandatory api key and chat id params")
            sys.exit(1)

        self.apiurl = f'https://api.telegram.org/bot{config.tg_api_key}'
        self.chat_id = config.tg_chat_id
        self.last_msg_id = -1
        self.startuptime = time.time()
        super().__init__()
    
    def notify(self, message, attachment=None):
        """
        Send notification, return true if succeeded.
        Note: attachments type is detected by extension
        """
        attempts = self.max_attempts
        while(attempts > 0):
            try:
                if (message != None):
                    response = requests.post(f"{self.apiurl}/sendMessage", json={'chat_id': self.chat_id, 'text': message}, timeout=5)
                
                if (attachment != None):
                    with open(attachment, mode='rb') as file:
                        binfile = file.read()
                    
                    filetype = attachment[-3:]
                    if (filetype == "wav") or (filetype == "ogg"):
                        url = f"{self.apiurl}/sendVoice?chat_id={self.chat_id}"
                        file = {'voice': (f"record.{filetype}", binfile)}
                    elif (filetype == "jpg"):
                        url = f"{self.apiurl}/sendPhoto?chat_id={self.chat_id}"
                        file = {'photo': binfile}
                    else:
                        self.logger.error(f"Unknown attachment extension type ({filetype})")
                    
                    response = requests.post(url, files=file, timeout=5)

                if (response.status_code == 200):
                    return True
            except Exception as e:
                self.logger.error(f"Cannot reach telegram server, exception occurred")
                print(e)
            time.sleep(self.attempt_delay_sec)
            attempts -= 1
        return False
    
    def getLastCommand(self):
        """
        Get latest message on the chat.
        This method assumes that the bot has only one client user.
        The bot can receive only messages starting with '/' (bot commands)
        """
        response = requests.post(f"{self.apiurl}/getUpdates?offset=-1")
        if (response.status_code == 200):
            jres = json.loads(response.text)
            if len(jres["result"]) > 0:
                message = jres["result"][0]["message"]
                msg_id = int(message["message_id"])
                # Check if we found a new message
                if (self.last_msg_id != msg_id):
                    self.last_msg_id = msg_id
                    return message["text"]
        return ""
    
    def backgroundAudioRecording(self, mic, seconds):
        mic.record(seconds)
        self.notify("mic recorded audio", mic.getEvidenceFile(format="opus"))
        with config.mic_mutex:
            config.is_recording = False

    def doAction(self):
        last_cmd = self.getLastCommand()
        if last_cmd == "":
            return
        self.logger.info(f"Received command: {last_cmd}")
        if (last_cmd == "/stop"):
            config.alarm_detection = False
            config.human_detection = False
            config.cat_detection = False
        elif (last_cmd == "/stoph"):
            config.human_detection = False
        elif (last_cmd == "/start"):
            config.alarm_detection = True
            config.human_detection = True
            msg = "intrusion detection started"
            self.logger.info(msg)
            self.notify(msg)
        elif (last_cmd == "/status"):
            self.notify(f"online, alarm detection = {config.alarm_detection} with threshold = {config.db_threshold}")
        elif (last_cmd == "/poweroff"):
            now = time.time()
            elapsed_minutes = ((now - self.startuptime)/60)
            # Shutdown the system only if was booted more than 5 minutes ago
            if elapsed_minutes >= 5:
                self.logger.info("powering off")
                self.notify("bye")
                os.system("poweroff")
            else:
                self.logger.info(f"Refuse to power off.. only {elapsed_minutes} minutes elapsed from startup")
        elif ("/play" in last_cmd):
            config.alarm_detection = False
            sound_index = 1
            if " " in last_cmd:
                sound_index = int(last_cmd.split(" ")[1])
            os.system("killall vlc") # kill existing processes
            os.system(f"cvlc --play-and-exit /opt/data/{sound_index}.wav &")
            self.notify("Reproducing audio, stopped alarm detection")
        elif (last_cmd == "/getphoto"):
            cam = SensorCamera(self.logger)
            self.notify(None, cam.getEvidenceFile())
        elif ("/getaudio" in last_cmd):
            try:
                mic = SensorMicrophone(self.logger)
                seconds = 5
                if " " in last_cmd:
                    seconds = int(last_cmd.split(" ")[1])
                self.logger.info("Starting background recording")
                with config.mic_mutex:
                    config.is_recording = True
                threading.Thread(target=self.backgroundAudioRecording, args=(mic, seconds)).start()
            except Exception as ex:
                print(f"getaudio exception: {ex}")
        elif ("/setdblevel" in last_cmd):
            try:
                config.db_threshold = float(last_cmd.split(" ")[1])
            except Exception as ex:
                print(f"setdblevel exception: {ex}")

