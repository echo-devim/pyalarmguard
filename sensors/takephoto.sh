#! /bin/sh
# This script acquires images from camera connected to Raspberry PI with ribbon cable
# Needs root permissions

v4l2-ctl --device /dev/video0 --set-fmt-video=width=640,height=480,pixelformat=UYVY
v4l2-ctl --device /dev/video0 --stream-mmap --stream-to=/opt/data/frame.raw --stream-count=1
convert -size 640x480 -depth 16 uyvy:/opt/data/frame.raw /opt/data/photo.jpg

