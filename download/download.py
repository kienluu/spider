import threading
import urllib


class DownloadAsset(threading.Thread):
    def __init__(self, url, save_path):
        self.url = url
        self.save_path = save_path

    def run(self):
        urllib.urlretrieve(self.url, self.save_path)



