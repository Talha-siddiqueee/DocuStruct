from pathlib import Path

class FileHandler:
    #Supporte document formats
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".xlsx",
        ".xlsm",
        ".txt",
        ".csv",
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".bmp"
    }
    def __init__(self,file_path):
        self.file_path = Path(file_path)
    def validate_files(self):
        #Check whether file exists
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )
        #Check whether path points to a file
        if not self.file_path.is_file():
            raise ValueError(
                "The provided path is not a file."
            )
        #check file extension
        if self.file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {self.file_path.suffix}"
            )
        
        return True
    def get_file_extension(self):
        return self.file_path.suffix.lower()
    def get_file_name(self):
        return self.file_path.name
    def get_file_size(self):
        return self.file_path.stat().st_size