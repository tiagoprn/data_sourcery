import logging
import os
import sys

import click

from data_sourcery.images.nasa import NasaImageDownloader

os.environ['PYTHONBREAKPOINT'] = 'ipdb.set_trace'

BASE_DIR = os.path.abspath(__file__)
CURRENT_DIR_NAME = BASE_DIR.split('/')[-2]

# Configure the logging both to file and to console. Works from python 3.3+
LOG_FORMAT = ('[%(asctime)s PID %(process)s '
              '%(filename)s:%(lineno)s - %(funcName)s()] '
              '%(levelname)s '
              '%(message)s')
logging.basicConfig(
    format=LOG_FORMAT,
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'/tmp/{CURRENT_DIR_NAME}.log'),
        logging.StreamHandler(sys.stdout)
    ])


CONTENT_TYPES = ['image']
SOURCES = {
    'nasa': NasaImageDownloader
}


@click.command()
@click.option('--content-type',
              type=click.Choice(CONTENT_TYPES),
              required=True,
              help=('Available content types: ('
                    '{})'.format(', '.join(CONTENT_TYPES))))
@click.option('--source',
              type=click.Choice(SOURCES.keys()),
              required=True,
              help=('Available sources: ('
                    '{})'.format(', '.join(SOURCES.keys()))))
def run(content_type, source):
    message = ['The values this script will use are: ',
               'CONTENT_TYPE: {}'.format(content_type),
               'SOURCE: {}'.format(source)]

    logging.info('\n'.join(message))


if __name__ == "__main__":
    run()
