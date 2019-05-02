# TODO: adapt here to the class from base.py
"""
This script downloads NASA's Astronomy Picture of the Day and automatically
sets it as the gnome desktop background.

It relies on the python-decouple lib that provides file-based environment
variables. So, for this script to work, you
only need to copy `download_wallpaper.env.sample to download_wallpaper.env,
and edit the last file with the path where
the script will save its wallpapers.`

Some functionalities were based on this code:
https://github.com/tiagoprn/space-pics/blob/master/pic.py
"""

import logging
import subprocess

import lxml
import os
import sys

from PIL import Image
from parsel import Selector
import requests

from decouple import Config, RepositoryEnv

os.environ['PYTHONBREAKPOINT'] = 'ipdb.set_trace'

CURRENT_SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]

# Sets the environment file used by decouple to load the Configuration
BASE_DIR = os.path.abspath(__file__)
config_file_path = os.path.join(os.path.dirname(
    BASE_DIR), f'{CURRENT_SCRIPT_NAME}.env')

# Configure the logging both to file and to console. Works from python 3.3+
LOG_FORMAT = ('[%(asctime)s PID %(process)s '
              '%(filename)s:%(lineno)s - %(funcName)s()] '
              '%(levelname)s '
              '%(message)s')
logging.basicConfig(
    format=LOG_FORMAT,
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'{CURRENT_SCRIPT_NAME}.log'),
        logging.StreamHandler(sys.stdout)
    ])


def set_image_as_desktop_background(file_url):
    #    cmd = [
    #        'gsettings',
    #        'set',
    #        'org.gnome.desktop.background',
    #        'picture-uri',
    #        'file://{0}'.format(file_url)
    #    ]
    #    subprocess.call(cmd)

    cmd = [
        'feh',
        '--bg-scale',
        file_url
    ]
    subprocess.call(cmd)


def remove_tags(text):
    return lxml.html.fromstring(text).text_content().replace(
        '\n', ' ').replace('  ', ' ')


def get_wallpaper_url():
    domain = 'https://apod.nasa.gov'

    html = requests.get(f'{domain}/apod/astropix.html', verify=False).text
    sel = Selector(text=html)
    image_url = sel.xpath('/html/body/center[1]/p[2]/a/@href').get()

    image_explanation = remove_tags(sel.xpath('/html/body/p[1]').get())

    logging.info('-'*80)
    logging.info(f'ABOUT THIS IMAGE ==> {image_explanation} ')
    logging.info('-'*80)

    url = image_url if image_url.startswith('http') \
            else f'{domain}/{image_url}'

    return url


def download_wallpaper(url, folder):
    already_downloaded = True

    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True, verify=False)

    if not folder.endswith('/'):
        folder += '/'

    downloaded_name = f'{folder}{local_filename}'
    converted_name = '{}.png'.format(downloaded_name.split('.')[0])

    if not os.path.exists(converted_name):
        already_downloaded = False
        if not os.path.exists(downloaded_name):
            with open(downloaded_name, 'wb') as f:
                # download in chunks to use less resources
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                f.flush()

        cmd = [
            'convert',
            downloaded_name,
            converted_name
        ]
        subprocess.call(cmd)

        os.unlink(downloaded_name)

    return converted_name, already_downloaded


if __name__ == "__main__":
    logging.info('Starting...')

    try:
        config = Config(RepositoryEnv(config_file_path))
    except FileNotFoundError:
        logging.info(f'The config file "{config_file_path}" does not exist. '
                     f'Create one based on the example '
                     f'from "{config_file_path}.sample".')
        sys.exit(1)

    DOWNLOAD_FOLDER = config('DOWNLOAD_FOLDER')

    logging.info(f'The wallpaper will be downloaded at "{DOWNLOAD_FOLDER}".')

    if not os.path.exists(DOWNLOAD_FOLDER):
        logging.debug(f'Creating download folder '
                      f'{DOWNLOAD_FOLDER} which does not exist...')
        os.makedirs(DOWNLOAD_FOLDER)

    try:
        logging.info('Parsing the site to get the image of the day url...')

        wallpaper_url = get_wallpaper_url()

        logging.info(f'URL gotten successfully. Now '
                     f'I will download "{wallpaper_url}" locally...')

        local_downloaded_path, already_downloaded = download_wallpaper(
            wallpaper_url, DOWNLOAD_FOLDER)

        if already_downloaded:
            downloaded_message = f'File had already ' \
                                 f'been downloaded at "{local_downloaded_path}"'
        else:
            downloaded_message = f'File successfully ' \
                                 f'downloaded at "{local_downloaded_path}"'

        logging.info(downloaded_message)


        logging.info(f'Setting image as gnome desktop background...')

        set_image_as_desktop_background(local_downloaded_path)

        logging.info('Finished.')
        sys.exit(0)
    except Exception as ex:
        logging.exception(f'Error running script. It seems '
                          f'your desktop will not be set this time :(')
        sys.exit(1)
