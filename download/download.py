import threading
import urllib2


class DownloadAsset(threading.Thread):
    def __init__(self, url, save_path, headers=[]):
        self.url = url
        self.save_path = save_path
        self.headers = headers

    def run(self):
        request = urllib2.Request(self.url)
        for header in self.headers:
            request.add_header(*header)
        response = urllib2.urlopen(request)
        file = open(self.save_path, 'wb')
        file.write(response.read())



