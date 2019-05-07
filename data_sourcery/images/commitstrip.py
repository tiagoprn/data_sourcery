"""
This script downloads a random comic from commitstrip.
"""

import logging
import subprocess
from time import sleep

import lxml
import os

from parsel import Selector
import requests

from data_sourcery.images.base import BaseImageDownloader


class CommitstripRandomImageDownloader(BaseImageDownloader):
    def __init__(self, remote_path=''):
        super().__init__(remote_path)
        self.local_repository_path = f'{self.local_repository_path}/commitstrip'
        self.create_local_repository_if_not_exists()
        if not remote_path:
            self.remote_path = self._get_random_comic_url()
            logging.info(f'remote_path={self.remote_path}')

    def _get_random_comic_url(self):
        domain = 'http://www.commitstrip.com'

        html = requests.get(f'{domain}/?random=1', verify=False).text
        sel = Selector(text=html)
        random_url_xpath = ('/html/body/div[2]/div[2]/div[1]/div/div/div/div/'
                            'article/header/div/a/@href')

        random_image_url = sel.xpath(random_url_xpath).get()

        html = requests.get(random_image_url, verify=False).text
        sel = Selector(text=html)
        image_xpath = ('/html/body/div[2]/div[2]/div[1]/div/div/div/div/'
                       'article/div/p/img/@src')
        image_url = sel.xpath(image_xpath).get()

        return image_url

    @staticmethod
    def _get_image_height(downloaded_path):
        height_command = f'identify -ping -format "%h" {downloaded_path}'
        image_height = os.popen(height_command).read()
        return int(image_height)

    def _download(self):
        """
        Downloads and convert the image to the png format.

        :return: local file name converted,
                if the file has already been downloaded
        :rtype: tuple(str, bool)
        """
        already_downloaded = True

        local_filename = self.remote_path.split('/')[-1]

        r = requests.get(self.remote_path, stream=True, verify=False)

        if not self.local_repository_path.endswith('/'):
            self.local_repository_path += '/'

        downloaded_name = f'{self.local_repository_path}{local_filename}'
        converted_name = '{}{}.png'.format(
            self.local_repository_path,
            downloaded_name.replace(self.local_repository_path, '').split(
                '.')[0]
        )

        if not os.path.exists(converted_name):
            already_downloaded = False
            if not os.path.exists(downloaded_name):
                logging.info('Downloading image...')
                with open(downloaded_name, 'wb') as f:
                    # download in chunks to use less resources
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                    f.flush()

            logging.info('Converting image to png format...')
            image_height = self._get_image_height(downloaded_name)
            resize_subcommand = '-resize x1080' if image_height > 1080 else ''
            if resize_subcommand:
                logging.info("Image will be resized, since its' "
                             "size exceeds 1080 px.")
            command = (f'convert {resize_subcommand} '
                      f'{downloaded_name} {converted_name}')
            os.popen(command)

            logging.info('Removing original (not converted) image...')

        return converted_name, already_downloaded

    def download(self):
        """
        Main function here.
        """
        logging.info('Starting...')

        logging.info(
            f'The wallpaper will be downloaded '
            f'at "{self.local_repository_path}".')

        logging.info('Parsing the site to get the random image url...')

        local_downloaded_path, already_downloaded = self._download()

        if already_downloaded:
            downloaded_message = f'File had already ' \
                                 f'been downloaded at ' \
                                 f'"{local_downloaded_path}"'
        else:
            downloaded_message = f'File successfully ' \
                                 f'downloaded at ' \
                                 f'"{local_downloaded_path}"'

        logging.info(downloaded_message)

        original_jpg_file = local_downloaded_path.replace('.png', '.jpg')
        logging.info(f'Removing original jpg file {original_jpg_file}...')
        sleep(1)  # Had to be added so convert command worked with no errors.
        os.popen(f'rm -f {original_jpg_file}')

        logging.info(f'Finished downloading to {local_downloaded_path}.')

        return local_downloaded_path
