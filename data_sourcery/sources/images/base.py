import os


class BaseImageDownloader:
    local_repository_path = ''
    remote_path = ''

    def __init__(self, remote_path=''):
        home_folder = os.environ.get('HOME')
        local_repository_home = (f'{home_folder}/.local/'
                                 f'share/data_sourcery')
        self.local_repository_path = f'{local_repository_home}/images'
        self.remote_path = remote_path
        self.create_local_repository_if_not_exists()

    def create_local_repository_if_not_exists(self):
        if not os.path.exists(self.local_repository_path):
            os.makedirs(self.local_repository_path, exist_ok=True)

    def _download(self):
        """
        Core download logic goes here.
        """
        raise NotImplementedError

    def download(self):
        """
        Main funcion.
        """
        raise NotImplementedError
