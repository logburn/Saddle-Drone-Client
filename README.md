## Overview
This code is designed to be paired with the [Drone Server](https://github.com/logburn/Saddle-Drone-Server). The concept is pretty simple: as a drone flies to it's destination, video will be captured and stored encrypted on board. Upon landing, this footage can be decrypted and viewed on a computer running [Drone Server](https://github.com/logburn/Saddle-Drone-Server).

## Hardware used
This code coud probably run on similar hardware but this has not been tested and is not guaranteed to work. The "server" running [Drone Server](https://github.com/logburn/Saddle-Drone-Server) code can be any computer with Python 3.
 - Raspberry Pi 4
 - GoPro Hero 8 Black
 
## Software dependancies
 - Python3
 - [GoProCam](https://github.com/KonradIT/gopro-py-api/)
 - [PyCryptodome](https://www.pycryptodome.org/en/latest/)

## How the code works
Recording is initiated by the RPi by sending a "start recording" signal to the GoPro. After the set interval, the "stop recording" signal will be sent. The specifics of this are handled by the GoProCam API. Once recording is completed, the video is then downloaded and symmetric encryption keys are generated and used to encrypt the video file. However, storing the key in plaintext on the drone is undesireable so the public key file is used to asymmetrically encrypt the symmetric key. Once this is done, the recording starts again and cycles in the same way.

## How files are transfered
A simple http server is started by `server.py`, at a port which is then printed out on the RPi terminal. The [Drone Server](https://github.com/logburn/Saddle-Drone-Server) then reads a file called `numFiles.txt` to know how many files to download, and then downloads both symmetrically encrypted video file and the corresponding asymmetrically encrypted key file. After downloading all files, the server will then decrypt the key file with the private key stored on computer, and then procede to decrypt the video files. Video files are stored in `videos/plaintext/<unix timestamp>/`. Storing with the timestamp allows multiple sessions to store files without interference or confusion. 
