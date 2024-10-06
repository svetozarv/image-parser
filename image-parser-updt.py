# This file is used to parse a static(pre-downloaded) HTML file using BS4 
# and save images, prompt and datetime, 
# sort them into folders by date(YYYY-MM-DD) or by prompt
# removed complicated usage of Selenium
# TODO: add metadata support 
# TODO: extension change to png
# TODO: move folder management to separate method
# TODO: compare entire length of prompts

import os
import bs4
import datetime as dt
import urllib
import urllib.error
import urllib.request
import shutil
import pyexiv2
import lxml
import time
from difflib import SequenceMatcher

# Path to the pre-downloaded HTML file
from settings import HTML_PATH_G_old as HTML_PATH, WORKING_DIR

# Percentage of similarity between 2 strings, used when comparing promts
# in this example if two prompts are 80% similar, the corresponding images are plased into one folder
EDIT_DIST_PRNT = 0.8


class Image:
    def __init__(self, name=None, time:str=None, date:str=None, prompt:str=None, href:str=None) -> None:
        self.name = name        # filename
        self.time = time
        self.date = date
        self.prompt = prompt
        self.href = href


    def retrieve(self):
        foldername = self.prompt[:255].replace(":", "").replace("\n", "").replace("|", "").strip()
        
        foundFolder = False
        for name in os.listdir(WORKING_DIR):
            if self.simmilarity(foldername, name) > EDIT_DIST_PRNT:
                self.img_dest_dir = os.path.join(WORKING_DIR, name)
                foundFolder = True

        if not foundFolder:
            if foldername not in os.listdir(WORKING_DIR):
                try:
                    os.chdir(WORKING_DIR)
                    os.mkdir(os.path.join(WORKING_DIR, foldername))
                except (FileExistsError, OSError):
                    print(f"Failed to make dir on img: {self.name} with foldername:{foldername}")
                    
                    foldername = "1unhandled"
                    if foldername not in os.listdir(WORKING_DIR):
                        os.mkdir(os.path.join(WORKING_DIR, foldername))
                
            self.img_dest_dir = os.path.join(WORKING_DIR, foldername)
        
        os.chdir(self.img_dest_dir)

        if self.href.split("/")[0] == ".":
            self.__retrieve_disk()
        else: # if == "https:"
            self.__retrieve_web()


    def __retrieve_web(self):
        try:
            urllib.request.urlretrieve(self.href, self.name)
        except urllib.error.HTTPError:
            print(f"HTTPError on file: {self.href}\n")
        # print(f"Downloaded {self.name}.")


    def __retrieve_disk(self):
        """
        Get absolute path to image and copy to destination folder
        """
        img_href = "\\".join(self.href.split("/")[1:])
        img_src_dir = "\\".join(HTML_PATH.split("\\")[:-1])
        self.abs_path = os.path.join(img_src_dir, img_href)

        # self.convert_image_type()
        try:
            shutil.copy2(self.abs_path, self.img_dest_dir)
            # print(f"Moved {self.name}.")
        except FileNotFoundError:
            print(f"No such file in source dir: {self.href}")


    def simmilarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
    

def benchmark_time(func):
    def inner(self, *args):
        start = time.time()
        func(self, *args)
        end = time.time()
        print(f"{func.__name__}():   {end - start} seconds\n")
    return inner


class ImageParser:

    @benchmark_time
    def __init__(self) -> None:
        with open(HTML_PATH, encoding="utf8") as file:
            self.soup = bs4.BeautifulSoup(file, "lxml")
        self.images: dict[str : Image] = {}
        self.existing_images: dict[str : bool] = {}
        self.__get_all_existing_images()
        print(f"Found {len(self.existing_images)} existing images")
    

    def start(self):
        self.find_group()
        self.extract_group()
        self.retrieve_images()


    @benchmark_time
    def find_group(self):
        """
        Find all divs with prompt and image containers
        """
        self.containers = self.soup.find_all("div", class_="c-msg-item")
        print(f"Found {len(self.containers)} containers.")


    @benchmark_time
    def extract_group(self):
        """
        Traverse all containers, extract prompt, date, time and 4 images, create an Image object
        """
        for i, container in enumerate(self.containers):
            prompt_tag = container.find_all("div", class_="message-text-content-text")[0]
            prompt = prompt_tag.get_text()

            datetime_tag = container.find_all("span", class_="chat-message__title-time")[0]
            datetime = datetime_tag.get_text().split()
            try:
                date = datetime[0]
                time = datetime[1]
            except IndexError:
                date = str(dt.datetime.today())
                time = datetime[0]

            image_tags = container.find_all("div", class_="image-render-box")
            for tag in image_tags:
                image_src = tag.find("img")["src"]
                img_name = image_src.split("/")[-1]
                new_img = Image(img_name, time, date, prompt, image_src)
                self.images[img_name] = new_img
            # print("Container proccessed")

        print(f"self.images filled with {len(self.images)}")


    @benchmark_time
    def retrieve_images(self):
        print(f"Retrieving the images")
        i = 0
        retrieved_imgs = 0
        for name, img in self.images.items():
            self.progress_bar(i, len(self.images))
            if name not in self.existing_images:
                img.retrieve()
                retrieved_imgs += 1
            i += 1
        print(f"\nRetrieved {retrieved_imgs}/{len(self.images)} images")


    def progress_bar(self, progress, total):
        percent = 100 * (progress / float(total))
        bar = '-' * int(percent) + ' ' * (100 - int(percent))
        print(f"\r|{bar}| {percent:.2f}%", end="\r")
        if progress == total:
            print()


    def __get_all_existing_images(self, working_dir=WORKING_DIR):
        filenames = os.listdir(working_dir)
        for filename in filenames:
            if ".webp" not in filename and ".png" not in filename:
                self.__get_all_existing_images(working_dir + "\\" + filename)
            else:
                self.existing_images[filename] = True



if __name__ == "__main__":
    parser = ImageParser()
    parser.start()
