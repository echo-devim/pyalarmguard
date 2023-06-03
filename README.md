# pyAlarmGuard

Python project for Raspberry PI (or other similar boards) to enforce your home security.

The current implementation can be summarized by the following image:
![system overview](system_overview.png)

Imagine to have an audio alarm system (e.g. fire detection system, anti-theft system, etc.). This project has the goal to use a microphone to hear for alarm sounds. When an alarm sound is detected, the system will send to your smartphone a notification with eventually attached evidences (e.g. recorded audio).

The project has the `notifiers` directory that contains all available notification methods. Currently only Telegram messages are supported, but future implementations could include emails or other IM apps. Notifiers can also perform actions, even if their scope is to notify the user, they can eventually receive commands to exeute.

The `sensors` directory contains all the available sensors. Currently only audio recording through microphone are supported. Future implementations could include images or videos from camera, motion-detection systems, etc.

The `detectors` directory contains tools and algorithms to perform several analysis, currently only alarm detection is implemented.

The project aims to provide a general structure easy to customize, in order to implement your home security system.

Before to run the project you need to create a `config.json` file in the root project directory containing the configuration for Telegram (apiKey and chatId).

# Installation

Install on the system the package `sox`
Then run `pip install -r requirements.txt`