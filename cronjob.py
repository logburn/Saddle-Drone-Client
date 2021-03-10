'''
  This script records videos of a particular length and then takes the normal file and encrypts it,
  storing both the encrypted file and the randomly generated iv (and deleting the plaintext video
  file). It is designed to be called every x seconds, where x is the length of the desired video.
  If it is not, then the resulting videos will have gaps between them.
'''

# import things
from Crypto.PublicKey import ECC
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP as pkrsa
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import glob
from signal import signal, SIGINT
from goprocam import GoProCamera, constants

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

# method to encrypt with ECC, however this is unsupported in pycryptodome
def encryptECC(data):
    with open("publickey.pem", "rt") as keyfile:
        key = ECC.import_key(keyfile.read())
    return key.encrypt(data)

# current method of public key encryption
def encryptRSA(data):
    key = RSA.import_key(open("publickey.pem", "r").read())
    cipher = pkrsa.new(key)
    encd = cipher.encrypt(data)
    print(f"{data}\n{encd}")
    return encd
    
# allowsp public key encryption method to be changed later
def PKEncrypt(data):
    return encryptRSA(data)

# encrypt given (video) file and store both encrypted video and encrypted key
def encryptVideo(file):
    # open file, generate cyrpto
    message = open(file, "rb").read()
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    # save encrypted file
    file_out = open(location + "encrypted/" + numFiles() + ".mpc", "wb")
    [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
    file_out.close()
    # save the encrypted key
    with open("keys/" + str(int(numFiles()) - 1) + ".asc", "wb+") as keyf:
        keyf.write(PKEncrypt(key))

# record the video and store in file location
takeVideo(seconds)

# get all video files in folder, encrypt (get all just in case one was missed previously)
fileset = [file for file in glob.glob(location + "plaintext/*.mp4", recursive=False)]

with open("numFiles.txt", "w+") as numf:
    numf.write(numFiles())

for file in fileset:
    encryptVideo(file)
    os.remove(file)

