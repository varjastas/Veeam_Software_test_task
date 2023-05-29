import logging
import sys
import os
import filecmp
import shutil
from time import sleep
import keyboard

exit = False

def on_key_release(event):
    '''
    Function that handles key pressed. Sets exit flag to True if pressed key is esc
    '''
    if event.name == 'esc': 
        print("Program ended by user")
        global exit
        exit = True

def sync_folders(source_folder: str, copy_folder: str, buffer_size: int, logger):
    '''
    Function that makes synchronization beetwen buffers. Takes arguments:
    source_folder: path to source folder
    copy_folder: path to source folder
    buffer_size: size of buffer that will be used in copying
    logger: object of logger type to which logs will be written
    '''
    # Iterate over files in the source folder
    for root, dirs, files in os.walk(source_folder):
        # Get the corresponding destination folder
        dest_folder = os.path.join(copy_folder, os.path.relpath(root, source_folder))

        # Create the destination folder if it doesn't exist
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # Synchronize files in the current folder
        for file in files:
            source_path = os.path.join(root, file)
            dest_path = os.path.join(dest_folder, file)

            # Copy the file if it doesn't exist in the destination folder
            if not os.path.exists(dest_path):
                logger.debug(f"Creating file and copying info to it {dest_path}")
                with open(source_path, 'rb') as src_file, open(dest_path, 'wb') as dest_file:
                    while True:
                        data = src_file.read(buffer_size) 
                        if not data:
                            break
                        dest_file.write(data)

            # Copy the file if it's different
            if not filecmp.cmp(source_path, dest_path):
                logger.debug(f"Copying info into file {dest_path}")
                with open(source_path, 'rb') as src_file, open(dest_path, 'wb') as dest_file:
                    while True:
                        data = src_file.read(buffer_size)
                        if not data:
                            break
                        dest_file.write(data)

        # Remove files that exist in the destination folder but not in the source folder
        for file in os.listdir(dest_folder):
            file_path = os.path.join(dest_folder, file)
            if not os.path.exists(os.path.join(root, file)):
                if os.path.isfile(file_path):
                    logger.debug(f"Removing file: {file_path}")
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    logger.debug(f"Removing directory: {file_path}")
                    shutil.rmtree(file_path)
def main():
    if len(sys.argv) < 5:
        print("You didn`t provide enough arguments. Please enter all four arguments")
        raise ValueError("You didn`t provide enough arguments. Please enter all four arguments")

    BUFFER_SIZE = 4096
    SOURCE_FOLDER = sys.argv[1]
    COPY_FOLDER = sys.argv[2]
    try:
        SYNCHRONIZATION_INTERVAL = float(sys.argv[3])
        SYNCHRONIZATION_INTERVAL_INT = int(SYNCHRONIZATION_INTERVAL)
    except:
        raise TypeError("Cannot parse time beetwen synchronizations.")

    LOG_FILE_PATH = sys.argv[4]

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)


    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    keyboard.on_release(on_key_release)

    while True:
        if exit == True:
            break

        sync_folders(SOURCE_FOLDER, COPY_FOLDER, BUFFER_SIZE, logger)
        logger.info(f"Synchronization has been succesful. Sleeping before next one for {SYNCHRONIZATION_INTERVAL}")

        if SYNCHRONIZATION_INTERVAL < 1: 
            sleep(SYNCHRONIZATION_INTERVAL)
        else:
            for i in range(round(SYNCHRONIZATION_INTERVAL_INT)):
                if exit == True:
                    break
                sleep(1)
            sleep(SYNCHRONIZATION_INTERVAL - SYNCHRONIZATION_INTERVAL_INT)

    
if __name__ == "__main__":
    main()