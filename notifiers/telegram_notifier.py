import requests
import time
import json
import sys
import os
from sensors.sensor_microphone import SensorMicrophone
import config

class NotifierTelegram():

    def __init__(self, logger):
        self.logger = logger
        self.max_attempts = 5
        self.attempt_delay_sec = 10
        # Read configuration to retrieve API Key and chat id
        with open(os.getcwd()+'/config.json') as config:
            file_contents = config.read()
        jconfig = json.loads(file_contents)
        if ("telegram" not in jconfig["notifiers"]):
            print("Telegram configuration not found in config.json, missing mandatory apiKey and chatId params")
            sys.exit(1)
        jconfig = jconfig["notifiers"]["telegram"]
        api_key=jconfig["apiKey"]
        self.apiurl = f'https://api.telegram.org/bot{api_key}'
        self.chat_id = jconfig["chatId"]
        self.last_msg_id = -1
        super().__init__()
    
    def notify(self, message, attachment=None):
        """
        Send notification, return true if succeeded.
        Note: attachments are considered audio file at the moment!!
        """
        attempts = self.max_attempts
        while(attempts > 0):
            try:
                response = requests.post(f"{self.apiurl}/sendMessage", json={'chat_id': self.chat_id, 'text': message})
                if (attachment != None):
                    with open(attachment, mode='rb') as file:
                        voice_file = file.read()
                    url = f"{self.apiurl}/sendVoice?chat_id={self.chat_id}"
                    file = {'voice': ("record.wav", voice_file)}
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
        elif ("/getaudio" in last_cmd):
            try:
                mic = SensorMicrophone(self.logger)
                mic.record(int(last_cmd.split(" ")[1]))
                self.notify(f"mic recorded audio", mic.getEvidenceFile())
            except Exception as ex:
                print(ex)
        elif ("/setdblevel" in last_cmd):
            try:
                config.db_threshold = float(last_cmd.split(" ")[1])
            except Exception as ex:
                print(ex)

