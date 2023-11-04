import subprocess
import config
import os
import time

class SensorCamera:

    def __init__(self, logger):
        self.logger = logger
        self.imagefile = f'{config.data_directory}/photo.jpg'
    
    def getEvidenceFile(self):
        return self.imagefile

    def takephoto(self):
        if os.path.exists(self.imagefile):
            os.remove(self.imagefile)
        
        attempts = 3

        while (attempts > 0):
            #subprocess.call(['bash', 'sensors/takephoto.sh', self.imagefile], timeout=10, shell=True)
            os.system(f"timeout 5 bash sensors/takephoto.sh {self.imagefile}")
            # Check if output file exists and contains data
            if not os.path.exists(self.imagefile) or (os.path.getsize(self.imagefile) < 10):
                self.logger.error("Photo capture failed")
            else:
                return True

            attempts -= 1
            time.sleep(1)
        
        return False



