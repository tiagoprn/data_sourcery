class BaseImageDownloader:
    # TODO: to not need an env file, local_repository_path must be
    #       $HOME/.local/share/data_sourcery
    #       (each derived class must be a directory
    #        e.g. images/nasa, images/commitstrip etc...)
    local_repository_path = ''
    remote_path = ''

    def __init__(self, remote_path):
        self.local_repository_path = ''
        self.remote_path = remote_path

    def _download(self):
        return True

    def download(self):
        if self._download():
            return self.local_repository_path
