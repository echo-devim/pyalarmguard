import requests
import time
import json
import sys
import os
from sensors.sensor_microphone import SensorMicrophone
from sensors.sensor_camera import SensorCamera
import config

class CarrierTelegram():

    def __init__(self, logger):
        self.name = "telegram"
        self.logger = logger
        self.max_attempts = 5
        self.attempt_delay_sec = 10
        # Read configuration to retrieve API Key and chat id
        if (config.tg_api_key == ""):
            print("Telegram configuration not found in config, missing mandatory api key and chat id params")
            sys.exit(1)

        self.apiurl = f'https://api.telegram.org/bot{config.tg_api_key}'
        self.chat_id = config.tg_chat_id
        self.last_msg_id = -1
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
                    response = requests.post(f"{self.apiurl}/sendMessage", json={'chat_id': self.chat_id, 'text': message})
                
                if (attachment != None):
                    with open(attachment, mode='rb') as file:
                        binfile = file.read()
                    
                    filetype = attachment[-3:]
                    if (filetype == "wav"):
                        url = f"{self.apiurl}/sendVoice?chat_id={self.chat_id}"
                        file = {'voice': ("record.wav", binfile)}
                    elif (filetype == "jpg"):
                        url = f"{self.apiurl}/sendPhoto?chat_id={self.chat_id}"
                        file = {'photo': binfile}

                    response = requests.post(url, files=file, timeout=3)

                if (response.status_code == 200):              
                    return True
            except Exception as e:
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
    
    def doAction(self):
        last_cmd = self.getLastCommand()
        if last_cmd == "":
            return
        self.logger.info(f"Received command: {last_cmd}")
        if (last_cmd == "/stop"):
            config.alarm_detection = False
        elif (last_cmd == "/start"):
            config.alarm_detection = True
        elif (last_cmd == "/status"):
            self.notify(f"online, alarm detection = {config.alarm_detection} with threshold = {config.db_threshold}")
        elif (last_cmd == "/poweroff"):
            os.system("poweroff")
        elif (last_cmd == "/getphoto"):
            cam = SensorCamera(self.logger)
            self.notify(None, cam.getEvidenceFile())
        elif ("/getaudio" in last_cmd):
            try:
                mic = SensorMicrophone(self.logger)
                mic.record(int(last_cmd.split(" ")[1]))
                self.notify("mic recorded audio", mic.getEvidenceFile())
            except Exception as ex:
                print(ex)
        elif ("/setdblevel" in last_cmd):
            try:
                config.db_threshold = float(last_cmd.split(" ")[1])
            except Exception as ex:
                print(ex)

