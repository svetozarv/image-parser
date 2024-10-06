import os
import shutil
from settings import *


def get_all_existing_images(working_dir: str, storage: dict):
    """
    Explores all sub-folders in 'working_dir' and adds files in 'storage' as {<filename>: True}
    """
    filenames = os.listdir(working_dir)
    for filename in filenames:
        if "." not in filename:
            get_all_existing_images(working_dir + "\\" + filename, storage)
        else:
            storage[filename] = True


def delete_all_common_images(working_dir: str, images: dict):
    """
    Recursively deletes files in 'working_dir' if present in 'images'
    """
    filenames = os.listdir(working_dir)
    for filename in filenames:
        if "." in filename:
            if filename in images.keys():
                os.remove(f"{working_dir}\\{filename}")
                print(f"{filename} removed in {working_dir}")
        else:
            delete_all_common_images(working_dir + "\\" + filename, images)


def count_extensions(working_dir: str, storage: dict):
    """
    Explores all files and add their extensions in 'storage' ex. {"png": 1}
    """
    filenames = os.listdir(working_dir)
    for filename in filenames:
        if "." in filename:
            extension = filename.split(".")[-1]
            if extension in storage:
                storage[extension] += 1
            else:
                storage[extension] = 1
        else:
            count_extensions(working_dir + "\\" + filename, storage)


os.chdir(new_dir1)

images = {}
get_all_existing_images(new_dir1, images)

# count_images = 0
# for image in images:
#     if image.split(".")[-1] == "webp":
#         count_images += 1
#         print(image)


delete_all_common_images(old_dir, images)

# print(count_images)
print("done.")
