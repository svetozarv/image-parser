# project started on Jan 13, 2024
import os
import shutil
import urllib.request
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from time import sleep

from settings import EMAIL2 as EMAIL
from settings import PASSWORD2  as PASSWORD
from settings import URL, working_dir


def login_google(browser) -> None:
    find_element_By(browser, "identifierId", id_mode=True).send_keys(EMAIL)
    find_element_By(browser, """//*[@id="identifierNext"]/div/button""", xpath_mode=True).click()
    find_element_By(browser, "Passwd", name_mode=True).send_keys(PASSWORD)
    find_element_By(browser, """//*[@id="passwordNext"]/div/button/span""", xpath_mode=True).click()


def find_element_By(browser, element_identifier: str, id_mode=False, class_mode=False, name_mode=False, xpath_mode=False): # -> WebElement
    wait = WebDriverWait(browser, 15)
    if class_mode:
        wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, element_identifier)))
        return browser.find_element(By.CLASS_NAME, element_identifier)
    elif id_mode:
        wait.until(expected_conditions.element_to_be_clickable((By.ID, element_identifier)))
        return browser.find_element(By.ID, element_identifier)
    elif name_mode:
        wait.until(expected_conditions.element_to_be_clickable((By.NAME, element_identifier)))
        return browser.find_element(By.NAME, element_identifier)
    elif xpath_mode:
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, element_identifier)))
        return browser.find_element(By.XPATH, element_identifier)


def get_all_existing_images(working_dir, storage: dict):
    filenames = os.listdir(working_dir)
    for filename in filenames:
        if "." not in filename:
            get_all_existing_images(working_dir + "\\" + filename, storage)
        else:
            storage[filename] = 1


def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")
    if progress == total:
        print()


scroll_times = 25    # 200 images per scroll

log = open("log.txt", "w")
browser = uc.Chrome()
browser.set_window_size(1600, 800)
browser.get(URL)
browser.implicitly_wait(5)
browser.find_element(By.XPATH, """//*[@id="app"]/section/header/div[2]/div[3]/div/button""").click()
element = WebDriverWait(browser, 10).until(lambda x: x.find_element(By.CLASS_NAME, "google-login").is_displayed())
browser.find_element(By.CLASS_NAME, "google-login").click()
browser.switch_to.window(browser.window_handles[1])
login_google(browser)
browser.switch_to.window(browser.window_handles[0])

sleep(20)
element = WebDriverWait(browser, 30).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "paint-left")))
painting = find_element_By(browser, "paint-left", class_mode=True)
painting.click()
sleep(8)

dowloaded_images_count = 1
scroll_height = browser.execute_script("return document.body.scrollHeight")
print(f"Total page height - {scroll_height}")

action = ActionChains(browser)
canvas = browser.find_element(By.CLASS_NAME, "scroll-wrapper")

delay = 3
scroll_count = 0
print(f"Waiting {delay * scroll_times} seconds to begin. Scrolling.")
while scroll_count < scroll_times:
    # print(f"{delay*(scroll_times - scroll_count)} seconds left")
    action.scroll_from_origin(ScrollOrigin.from_element(canvas), 0, -1000).perform()
    sleep(delay)
    scroll_count += 1
    progress_bar(scroll_count, scroll_times)

dowloaded_images = {}
get_all_existing_images(working_dir, dowloaded_images)

wait = WebDriverWait(browser, 15)
wait.until(expected_conditions.element_to_be_clickable((By.TAG_NAME, "img")))
images = browser.find_elements(By.TAG_NAME, "img")
len_images = len(images)
print(f"Found {len_images} images")
os.chdir(working_dir)
processed_images = 0

for image in images:
    if "media-attachments-img" not in image.get_attribute("class"): processed_images += 1; continue
    link = image.get_property("src")
    filename = link.split('/')[-1]
    if filename.rfind("_low.") != -1: processed_images += 1; continue
    id = link.split('/')[-2]
    date = link.split('/')[-3]
    
    if id + ", " + filename not in dowloaded_images:
        if date in os.listdir(working_dir):
            os.chdir(working_dir + "\\" + date)
        else:
            try:
                # print(f"Creating new directory: {date}")
                log.write(f"Creating new directory: {date}\n")
                os.chdir(working_dir)
                os.mkdir(f".\\{date}")
                os.chdir(date)
            except FileExistsError:
                print(f"\nEXCEPTION: FileExistsError:  {date}\n")
                #log.write(f"\nEXCEPTION: FileExistsError:  {date}\n")
        
        # print(f"\rDownloading {dowloaded_images_count}th image:  {filename}", end="\r")
        log.write(f"Downloading {dowloaded_images_count}th image:  {date}\\{filename}\n")
        try:
            urllib.request.urlretrieve(link, id + ", " + filename)
        except:
            print(f"HTTPError 404. File not found: {link}\n")
            log.write(f"HTTPError 404. File not found: {link}\n")
        dowloaded_images[filename] = 1
        dowloaded_images_count += 1
        processed_images += 1
    else:
        processed_images += 1
    progress_bar(processed_images, len_images)


print("\nProgram is finished\n")
print(f"processed_images = {processed_images}\nlen_images = {len_images}\ndownloaded_images = {dowloaded_images_count}\n")
log.write(f"processed_images = {processed_images}\nlen_images = {len_images}\ndownloaded_images = {dowloaded_images_count}\n")
log.close()
browser.quit()
