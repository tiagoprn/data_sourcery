import logging
import os
import sys

import click

from data_sourcery.sources.images.nasa import NasaImageDownloader
from data_sourcery.sources.images.commitstrip import CommitstripRandomImageDownloader

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
    'nasa': NasaImageDownloader,
    'commitstrip': CommitstripRandomImageDownloader
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

    try:
        SOURCES[source]().download()
        exit_code = 0
    except:
        logging.exception('An exception occurred.')
        exit_code = 1

    message = 'Successfully quitting' if exit_code == 0 \
        else 'Quitting on failure'
    logging.info(message)

    os._exit(exit_code)  # that way it does not trigger SystemExit exception


if __name__ == "__main__":
    run()
