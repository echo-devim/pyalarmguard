# pyAlarmGuard

Python project for Raspberry PI (or other similar boards) to enforce your home security.

The current implementation can be summarized by the following image:
![system overview](system_overview.png)

Imagine to have an audio alarm system (e.g. fire detection system, anti-theft system, etc.). This project has the goal to use a microphone to hear for alarm sounds. When an alarm sound is detected, the system will send to your smartphone a notification with eventually attached evidences (e.g. recorded audio).
pyAlarmGuard can support also a camera featuring object/human detection powered by MobileNetSSD (really fast even on raspberry pi).

The project has the `carriers` directory that contains all available notification methods. Currently only Telegram messages are supported, but future implementations could include emails or other IM apps. Carriers can also perform actions, even if their goal is to notify the user, they can eventually receive commands to execute.

The `sensors` directory contains all the available sensors. Audio recording through microphone and photos from camera are supported. Future implementations could include videos from camera, motion-detection systems, etc.

The `detectors` directory contains tools and algorithms to perform several analysis, currently only alarm detection and human detection are implemented.

The project aims to provide a general structure easy to customize, in order to implement your home security system.


# Installation

Install on the system the package `sox` and optionally `vlc`
Then run `pip install -r requirements.txt`

Copy the bash file `setup/startup.sh` into `/opt` directory. The bash script contains some workarounds to init the user session for pulse audio server and then starts the project.
The project will run as non-root user, you must enable ssh-key authentication between root and pi local users.
Copy the service `setup/alarmguard.service` in `/etc/systemd/system`, then run `systemctl daemon-reload` and `systemctl --now enable alarmguard`.

Before to run the project you need to rename `config_example.py` into `config.py` in the root project directory adding the configuration for Telegram (api key and chat id).


## Technical Details

### Alarm detection
The `detectors` are wrapped by `Detector` class (in `detectory.py` file).
Alarm detection is performed first applying a sinc filter and then measuring db level of wav file.
Finally is applied a custom audio correlation algorithm to exclude false positives (i.e. matches for environmental sounds).

The audio correlation is performed translating the amplitude values into positive values. Thus, the minimum value of the signal (negative number) is summed to all the amplitudes.
Then the time information is discarded by re-ordering all amplitudes in descending order. In this way the same sound recorded at different moment can be recognized.
The resulting curve is then compared to other curves representing the sounds in the dataset calculating the differences with some tollerance.
The final result is a percentage of similarity between two sounds.

### Alarm Correlation with Dejavu3 (archivied)
Previously the project was based on dejavu3 algorithm, but after some tests it showed little effectiveness with short audios.

Actually the repo still includes Dejavu3 audio correlator, but it's not used by the project anymore.

Dejavu3 is derived from [dejavu](https://github.com/worldveil/dejavu), but modified to use a local sqlite database `audio.db`.

Each time, recorded audio is compared to sounds already known (saved in the database) using Dejavu3 algorithm. It is possible to add new sounds putting `wav` files inside the `detectors/dejavu3/samples/` directory. The name of the `wav` file represents its label.

If the audio recorded from mic results to have a correlation to a known sound (found in `audio.db`) its label is retrieved. If the label (i.e. the filename) starts with the `exclude` keyword, the current recording is considered as a sound to ignore (e.g. noise). Otherwise if the label starts with the `include` keyword, the current recording is considered as an alarm.

When the dejavu3 algorhitm fails to classify the recorded audio, then it's applied a sinc filter and measured RMS dB level. If the dB level is greather then a defined threshold, the alarm notification will be triggered.

### Object detection
For object detection is used the MobileNetSSD model for the Single Shot Detector (SSD) that can infer very fast objects in a image.
Object that can be detected: background,aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor

When human is detected with a confidence greather than 60% the user is notified and a sequence of 120 images per second (by default) is acquired from camera.

## Supported Commands
Telegram carrire implements several commands that are described below:

*  `/stop` stop all detectors
*  `/stoph` stop only human detection
*  `/start` start all detectors
*  `/status` get system status
*  `/poweroff` shutdown the system
*  `/play` play a song/sound (if the raspberry has a speaker)
*  `/getphoto` get a photo from camera
*  `/getaudio n` get an audio of n seconds (recording is done with a background thread)
*  `/setdblevel n` set the db level threshold for alarm detection

Logs are saved in `pyalarmguard.log` file in the project directory.
