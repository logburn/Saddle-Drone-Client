'''
  This script records videos of a particular length and then takes the normal file and encrypts it,
  storing both the encrypted file and the randomly generated iv (and deleting the plaintext video
  file). It is designed to be called every x seconds, where x is the length of the desired video.
  If it is not, then the resulting videos will have gaps between them.
'''

# import things
from cryptography.fernet import Fernet
from Crypto.Cipher import PKCS1_OAEP as RSA
from Crypto.Cipher import AES
import os
import glob
from signal import signal, SIGINT
from goprocam import GoProCamera, constants
from base64 import b64decode, b64encode

# global vars
location = "/home/pi/final/videos/" # location of video files, subfolders "plaintext" and "encrypted" assumed to exist
seconds = int(open("interval", "r").read()) # seconds to record video for

# helps with video recording
def handler(s, f):
    gopro.stopWebcam()
    quit()

# returns the current file number for naming convention
def numFiles():
    return str(len([item for item in os.listdir(location+"encrypted/") if os.path.isfile(os.path.join(location+"encrypted/", item))]))


# take video for time seconds, transfer to local storage and delete from gopro
def takeVideo(time):
    signal(SIGINT, handler)
    gopro = GoProCamera.GoPro(ip_address=GoProCamera.GoPro.getWebcamIP())
    gopro.shoot_video(time)
    gopro.downloadLastMedia(custom_filename=(location+"plaintext/" + numFiles() + ".mp4"))
    gopro.delete("last")

# TODO encrypt file data with assumed pgp key (file should already be read, this essentially
# encrypts the text or contents of the file)
def encryptPGP(file):
    return file
    #with open("pubkey.pem", "r") as keyfile:
    #    key = RSA.importKey(b64decode(str(keyfile)))
    keytext = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLjon5dPwTgHUr44KndKz0W7bN\nwEqs6IImvnh/X++FD8vpMNPpepgEpZBC52vTyhmsgJYbkNnp8DxSUApE+IL5FlKr\nDCTLp3KLfjD8onjHf7mtD7uMpxWkafmor4BGq05M/QRwttYjaQNBGT3BFYHi5NdX\negPZLolmwrqwndwGAQIDAQAB\n-----END PUBLIC KEY-----"
    key = RSA.importKey(keytext)
    return key.encrypt(file, 'x')[0]

# encrypt given (video) file and store both encrypted video and (TODO) encrypted random iv
def encryptVideo(file):
    # open the file as bytes
    with open(file, "rb") as og:
        message = og.read()
    # generate keys
    key = Fernet.generate_key()
    fernet = Fernet(key)
    # encrypt file
    enc = fernet.encrypt(message)
    # save the encrypted mp4
    with open(location+"encrypted/" + numFiles() + ".mpc", "wb") as encf:
        encf.write(enc)
    # save the key
    with open("keys/" + str(int(numFiles()) - 1) + ".asc", "wb") as keyf:
        keyf.write(encryptPGP(key))

# record the video and store in file location
takeVideo(seconds)

# get all video files in folder, encrypt (get all just in case one was missed previously)
fileset = [file for file in glob.glob(location + "plaintext/*.mp4", recursive=False)]

# whether or not to print out current action
verbose = True

for file in fileset:
    if verbose:
        print("Working on file " + file)
        print("Encrypting...")
    encryptVideo(file)
    
    if verbose:
        print("Deleting...")
    os.remove(file)
    
    if verbose:
        print("Done.")

