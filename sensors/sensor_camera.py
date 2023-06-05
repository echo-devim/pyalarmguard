import subprocess
import config

class SensorCamera:

    def __init__(self, logger):
        self.logger = logger
        self.imagefile = f'{config.data_directory}/photo.jpg'
    
    def getEvidenceFile(self):
        return self.imagefile

    def takephoto(self):
        subprocess.run(['bash', 'sensors/takephoto.sh', self.imagefile])



