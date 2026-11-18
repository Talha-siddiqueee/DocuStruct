print("PROGRAM STARTED")
from extractors.file_handler import FileHandler
print("IMPORT SUCCESSFUL")
#Create a file handler
handler = FileHandler("requirements.txt")
print("OBJECT CREATED")
#Validate file
try:
    if handler.validate_files():
        print("File validation successful!")
        print("File name:",handler.get_file_name())
        print("Extension:",handler.get_file_extension())
        print("File Size:",handler.get_file_size(), "bytes")
except (FileNotFoundError,ValueError) as error:
    print("Error:",repr(error))
        