#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class style:
    RED = '\033[31m'
    GREEN = '\033[32m'
    MAGENTA = '\033[35m'
    CYAN = '\033[96m'
    WARNING = '\033[93m'
    RESET = '\033[0m'
    YELLOW =' \033[31m'
    BLINK = '\033[5m' # Slow Blink
    FRAMED = '\033[32;51;35m'
    ABORT = '\033[97;101;5;1m'

welcome_message = r"""
                           ___________                     
 ___________        .-----"" ""    "" ""-----.             
:_______.--':      :  .-------------------.  :             
| ________  |      | :                     : |   <3 Jordan Lambrecht         
|:________B:|      | |      ENHANCED       | |             
|:________B:|      | |        WEBSITE      | |             
|:________B:|      | |      DOWNLOADER     | |             
|           |      | |         3000™       | |             
|:_______:  |      | |                     | |             
|    ==     |      | :                     : |             
|         O |      :  '--------------------' :             
|         o |      :'-----...______...-------'              
|         o |-._.-i_____/'             \._              
|'-.______o_|   '-.     '-...______...-'  `-._          
:___________:         `.____________________   `-.___.-. 
                    .'.eeeeeeeeeeeeeeeeeeee.'.      :___:
    fsc           .'.eeeeeeeeeeeeeeeeeeeeeeee.'.         
                 :______________________________:        
"""


def get_rendered_html_and_links(driver, url):
    driver.get(url)
    rendered_html = driver.page_source
    css_links = [link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, 'link') if link.get_attribute('rel') == 'stylesheet' and link.get_attribute('href') is not None]
    img_links = [img.get_attribute('src') for img in driver.find_elements(By.TAG_NAME, 'img') if img.get_attribute('src') is not None]
    page_links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a') if a.get_attribute('href') is not None]
    return rendered_html, css_links, img_links, page_links

logging.basicConfig(filename='website_downloader.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    urls = set()
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url, headers=HEADERS).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            continue
        if href in urls:
            continue
        if domain_name not in href:
            continue
        urls.add(href)
    return urls


def download_file(url, folder):
    try:
        r = requests.get(url)
        filename = url.split("/")[-1]
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        logging.info(f'Downloaded {url}')
    except Exception as e:
        logging.error(f'Error downloading {url}: {e}')
        print(f"{style.WARNING}Error downloading {url}: {e} 🚫{style.RESET}")
        
        
        
        
def download_website(url, crawl_entire_site=False):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    domain_name = urlparse(url).netloc.replace("www.", "")
    output_folder = os.path.join("output", domain_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    visited_links = set()
    links_to_visit = {url}

    # Initialize the progress bar
    total_links = len(links_to_visit)
    crawl_progress = tqdm(desc="Crawling", total=total_links, unit="page")
    
    while links_to_visit:
        current_url = links_to_visit.pop()
        if current_url in visited_links:
            continue
        visited_links.add(current_url)

        rendered_html, css_links, img_links, page_links = get_rendered_html_and_links(driver, current_url)
        path = urlparse(current_url).path.strip('/')
        filename = 'index.html' if path.endswith('/') or not path else path.split('/')[-1]
        directory = os.path.join(output_folder, os.path.dirname(path))
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as f:
            f.write(rendered_html)

        for css_link in css_links:
                    css_url = urljoin(current_url, css_link)
                    download_file(css_url, output_folder)
                    
        if download_images:
            for img_link in img_links:
                img_url = urljoin(current_url, img_link)
                download_file(img_url, output_folder)

        if crawl_entire_site:
            for page_link in page_links:
                if urlparse(page_link).netloc.replace("www.", "") == domain_name and page_link not in visited_links:
                    links_to_visit.add(page_link)
                    total_links += 1
                    crawl_progress.total = total_links
                    
        crawl_progress.update(1)
    
    crawl_progress.close()
    driver.quit() 

# def download_website(url, download_images=False):
#     domain_name = urlparse(url).netloc.replace("www.", "")
#     output_folder = os.path.join("output", domain_name)
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
#     links = get_all_website_links(url)
#     for link in tqdm(links, desc="Downloading HTML pages", unit="page"):
#         download_file(link, output_folder)
#     if download_images:
#         soup = BeautifulSoup(requests.get(url, headers=HEADERS).content, "html.parser")
#         for img_tag in soup.findAll("img"):
#             img_url = img_tag.attrs.get("src")
#             if img_url == "" or img_url is None:
#                 continue
#             img_url = urljoin(url, img_url)
#             download_file(img_url, output_folder)



if __name__ == "__main__":
    print(f" ")
    print(f"{style.MAGENTA}{welcome_message}{style.RESET}")
    print(f"{style.FRAMED}   🚀 Welcome to the Enhanced Website Downloader 3000™ ! {style.RESET}")
    try:
        while True:
            url = input(f"{style.CYAN}🧑‍💻 Enter the website URL to crawl (https://): {style.RESET}")
            if not is_valid(url):
                print(f"{style.RED}Invalid URL. Please try again. 🚫{style.RESET}")
                continue
            crawl_entire_site = input(f"{style.GREEN}🌝 Do you want to crawl the entire site? (y/n): ").lower().strip() == 'y'
            download_images = input(f"{style.CYAN}📸 Do you want to download images? (y/n): {style.RESET}").lower().strip() == 'y'

            download_website(url, download_images)
            print(f"{style.CYAN}Process complete! Check the output folder for the downloaded website.{style.RESET}")
            logging.info(f'Process complete for {url}')
            again = input(f"{style.YELLOW}Do you want to download another website? (y/n): {style.RESET}")
            if again.lower() != 'y':
                break
    except KeyboardInterrupt:
        print(f"\n{style.ABORT}Program was rudely interrupted by user. 😤 Exiting...{style.RESET}")
    finally:
        print(f"{style.CYAN}----------------------------------------------------------------------------")         
        print(f"{style.CYAN}Thanks for using the Enhanced Website Downloader 3000! Have a blessed day! 👋{style.RESET}")
        print(f"{style.CYAN}----------------------------------------------------------------------------")         
        print(f" ")
