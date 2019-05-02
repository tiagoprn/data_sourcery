"""
This script downloads NASA's Astronomy Picture of the Day and automatically
sets it as the gnome desktop background.

Some functionalities were based on this code:
https://github.com/tiagoprn/space-pics/blob/master/pic.py
"""

import logging
import subprocess

import lxml
import os
import sys

from parsel import Selector
import requests

from data_sourcery.images.base import BaseImageDownloader


class NasaImageDownloader(BaseImageDownloader):
    def __init__(self, remote_path=''):
        super().__init__(remote_path)
        self.local_repository_path = f'{self.local_repository_path}/nasa'
        self.create_local_repository_if_not_exists()
        if not remote_path:
            self.remote_path = self._get_wallpaper_url()
            logging.info(f'remote_path={self.remote_path}')

    @staticmethod
    def _remove_tags(text):
        return lxml.html.fromstring(text).text_content().replace(
            '\n', ' ').replace('  ', ' ')

    def _get_wallpaper_url(self):
        domain = 'https://apod.nasa.gov'

        html = requests.get(f'{domain}/apod/astropix.html', verify=False).text
        sel = Selector(text=html)
        image_url = sel.xpath('/html/body/center[1]/p[2]/a/@href').get()

        image_explanation = self._remove_tags(
            sel.xpath('/html/body/p[1]').get())

        logging.info('-' * 80)
        logging.info(f'ABOUT THIS IMAGE ==> {image_explanation} ')
        logging.info('-' * 80)

        url = image_url if image_url.startswith('http') \
            else f'{domain}/{image_url}'

        return url

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

            cmd = [
                'convert',
                downloaded_name,
                converted_name
            ]
            subprocess.call(cmd)

            logging.info('Removing original (not converted) image...')

            os.unlink(downloaded_name)

        return converted_name, already_downloaded

    def download(self):
        """
        Main function here.
        """
        logging.info('Starting...')

        logging.info(
            f'The wallpaper will be downloaded '
            f'at "{self.local_repository_path}".')

        try:
            logging.info('Parsing the site to get the image of the day url...')

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

            logging.info('Finished.')
            sys.exit(0)
        except Exception as ex:
            logging.exception(f'Error running script.')
            sys.exit(1)
