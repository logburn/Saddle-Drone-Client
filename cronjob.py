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
import zipfile
import os
import glob
from signal import signal, SIGINT
from goprocam import GoProCamera, constants
import time
import shutil

# global vars
location = os.getcwd() + "/videos/" # location of video files, subfolders "plaintext" and "encrypted" assumed to exist
locpt = location + "plaintext/"
locec = location + "encrypted/"
seconds = int(open("interval", "r").read()) # seconds to record video for

# helps with video recording
def handler(s, f):
    gopro.stopWebcam()
    quit()

# returns the current file number for naming convention
def numFiles():
    return str(len([item for item in os.listdir(locec) if os.path.isfile(os.path.join(locec, item))]))

# compresses a given file, new file is named same filename with .zip at end
# returns name of new file
def compress(filename):
    zf = zipfile.ZipFile(filename + ".zip", mode='w', compression=zipfile.ZIP_DEFLATED)
    zf.write(filename)
    zf.close()
    return filename + ".zip"

# take video for time seconds, transfer to local storage and delete from gopro
def takeVideo(time):
    signal(SIGINT, handler)
    gopro = GoProCamera.GoPro(ip_address=GoProCamera.GoPro.getWebcamIP())
    gopro.video_settings("480p", fps='30')
    gopro.shoot_video(time)
    gopro.downloadLowRes(custom_filename=(location+"plaintext/" + numFiles() + ".mp4"))
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
    file_out = open(locec + numFiles() + ".mpc", "wb")
    [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
    file_out.close()
    # save the encrypted key
    with open("keys/" + str(int(numFiles()) - 1) + ".asc", "wb+") as keyf:
        keyf.write(PKEncrypt(key))

# OLD METHOD
''''''
# record the video and store in file location
takeVideo(seconds)

# get all video files in folder, encrypt (get all just in case one was missed previously)
fileset = [file for file in glob.glob(location + "plaintext/*.mp4", recursive=False)]

with open("numFiles.txt", "w+") as numf:
    numf.write(numFiles())

# compress and encrypt
for file in fileset:
    newf = compress(file)
    encryptVideo(newf)
    os.remove(file)
    os.remove(newf)
''''''

# FORK
def child():
    # child compresses and encrypts
    fileset = [file for file in glob.glob(locpt + "*.mp4", recursive=False)]
    if(len(fileset) == 0):
        os._exit(0)
    # prevents double encryption
    folder = locpt + str(int(time.time()))
    os.mkdir(folder)
    for file in fileset:
        shutil.move(file, folder)
    fileset = [file for file in glob.glob(folder + "/*.mp4", recursive=False)]
    for file in fileset:
        print("Encrypting file " + file)
        newf = compress(file)
        encryptVideo(newf)
        os.remove(file)
        os.remove(newf)
    shutil.rmtree(folder)
    with open("numFiles.txt", "w+") as numf:
        numf.write(numFiles())
    os._exit(0)  

def parent():
    # parent records, child does everything else
    try:
        while True:
            newpid = os.fork()
            if newpid == 0:
                child()
            else:
                takeVideo(seconds)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            #child()
            os._exit(0)
        except SystemExit:
            os._exit(0)
#parent()

