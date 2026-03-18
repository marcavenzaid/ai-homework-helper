import os, time
import logging

logger = logging.getLogger(__name__)

class FileDeleter:
    
    def __init__(self, folder_path, age_in_days=7, max_files=7):
        """ 
        If there are more than max_files in a folder, delete the files that are older than age_days.

        Parameters:
            folder_path: Path to the folder with files to delete.
            age_in_days: The number of days after the files creation, before it gets deleted.
        """
        self._age_in_days = age_in_days
        self._folder_path = folder_path
        self._max_files = max_files

        self._age_in_seconds = age_in_days * 86400   # Convert age in days to seconds


    def delete_files(self):
        current_time = time.time()
        files_in_dir = os.listdir(self._folder_path)

        # Check if the folder exceeds the number of max files
        if len(files_in_dir) > self._max_files:
            # Create a list of (file_path, creation_time) tuples
            files_with_ctime = []
            for file_name in files_in_dir:
                file_path = os.path.join(self._folder_path, file_name)
                creation_time = os.path.getctime(file_path)
                files_with_ctime.append((file_path, creation_time))

            # Sort the list by creation_time (oldest first)
            sorted_files_with_ctime = sorted(files_with_ctime, key=lambda x: x[1])

            # Calculate how many files need to be deleted
            num_files_to_delete = len(files_in_dir) - self._max_files

            # Iterate over the sorted list and remove the oldest files if they are past the age threshold
            for file_path, creation_time in sorted_files_with_ctime[:num_files_to_delete]:
                age_in_seconds = creation_time + self._age_in_seconds
                if current_time > age_in_seconds:
                    os.remove(file_path)
                    logger.debug(f"File {file_path} was deleted due to exceeding max files (> {self._max_files} files) and age (> {self._age_in_days} days).")
