import os
import re
import json

def comp(startpath, startdirs):
    file_list = []
    """
    for item in startdirs:
        for dirpath, dirs, files in os.walk(startpath + item):
            for file in files:
                if re.search("\.jpg|\.png|\.gif|\.webm|\.mp4", file):
                    if "beast" in dirpath:
                        pass
                    else:
                        file_list.append("{}/{}".format(dirpath, file))
    """
    with open('res/filesources.json', 'r') as x:
        file_sources = json.load(x)

    for start_path in file_sources["sources"]:
        for filtered_dir in file_sources["sources"][start_path]:
            for dir_path, dirs, files in os.walk(start_path + filtered_dir):
                for file in files:
                    if re.search("\.(jpg|jpeg|png|apng|gif|webp|mp4|mkv|mov|3gp|webm)", file):
                        if any(blacklist in dir_path for blacklist in file_sources["blacklist"]):
                            pass
                        else:
                            file_list.append("{}/{}".format(dir_path, file))
    return file_list