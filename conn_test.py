import os
from signal import signal, SIGINT
from goprocam import GoProCamera, constants

seconds = 4

# helps with video recording
def handler(s, f):
    gopro.stopWebcam()
    quit()

def takeVideo(time):
    signal(SIGINT, handler)
    gopro = GoProCamera.GoPro()
    gopro.shoot_video(time)
    gopro.downloadLastMedia(custom_filename=(location+"plaintext/" + numFiles() + ".mp4"))
    gopro.delete("last")

takeVideo(seconds)
