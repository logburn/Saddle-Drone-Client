import zipfile

w = zipfile.ZipFile("NewZipfile.zip", mode='w', compression=zipfile.ZIP_DEFLATED)

# Write to zip file
w.write("test.txt")
w.close()

r = zipfile.ZipFile("NewZipfile.zip", mode='r', compression=zipfile.ZIP_DEFLATED)

# Reading Zip File
print("\n", r.read('test.txt'))

r.close()
