class BaseImageDownloader:
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
