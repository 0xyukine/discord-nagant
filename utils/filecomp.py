import os
import re
import json

def comp():
    """
    Compiles and returns a list of filepaths for local files,
    values in filesources points to directories to walk through 
    and provides blacklisted terms to be filtered out of the 
    final list
    """

    file_list = []
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

def tree():
    tree_txt = ""

    file_list = []
    with open('res/filesources.json', 'r') as x:
        file_sources = json.load(x)

    for start_path in file_sources["sources"]:
        for filtered_dir in file_sources["sources"][start_path]:
            for dir_path, dirs, files in os.walk(start_path + filtered_dir):
                if len(dir_path.split("/")) <= 6:
                    if any(blacklist in dir_path for blacklist in file_sources["blacklist"]):
                        for blacklist in file_sources["blacklist"]:
                            if blacklist in dir_path:
                                path = "/".join(dir_path.split("/")[4:]).replace(blacklist, "REDACTED")
                    else:
                        path= "/".join(dir_path.split("/")[4:])

                    if len(path.split("/")) > 1:
                        tree_txt += "└── " + path.split("/")[1] + "\n"
                    else:
                        tree_txt += path + "\n"

    return tree_txt