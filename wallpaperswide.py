"""
Crawls http://wallpaperswide.com for images.  To download all image at
http://wallpaperswide.com/mac-desktop-wallpapers set
'http://wallpaperswide.com/mac-desktop-wallpapers' as the start_url when
initializing the Spider Object
"""

from Queue import Queue
import logging
import os
from threading import Thread
from time import time
import urlparse
import sys
from datetime import timedelta
from pyquery import PyQuery as PQ
from download.download import DownloadAsset

ch = logging.StreamHandler(stream=sys.stdout)
logger = logging.getLogger('spider')
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


class Spider(object):

    def __init__(self, start_url, start_page=None, end_page=None,
                 target_resolution='1440x900',
                 max_workers=10):
        self.target_resolution = target_resolution
        self.start_gallery_page = start_url
        self.hostname = urlparse.urlparse(start_url).hostname
        self.image_page_urls = set()
        self.image_urls = set()
        self.save_directory = 'images%s' \
                              % urlparse.urlparse(start_url).path
        self.start_page = start_page
        self.end_page = end_page
        self.skip_extensions = set(['.bmp'])
        self.page_count = 0

        # Download thead and queue
        self.max_workers = max_workers
        self.queue = Queue()

    def create_download_image_workers(self):
        for index in range(0, self.max_workers):
            thread = Thread(target=self.download_image_worker, args=(index,))
            thread.setDaemon(True)
            thread.start()

    def download_image_worker(self, thread_num):
        while True:
            image_page_url = self.queue.get()
            logger.info('worker%d: Downloading %s' % (thread_num, image_page_url))
            try:
                self.get_image_page(image_page_url)
            except Exception, e:
                logger.info('worker%d: imagecode "%s" Exception:%s' %
                            (thread_num, image_page_url, e))
            self.queue.task_done()
            logger.info('worker%d: Finnished %s' % (thread_num, image_page_url))

    def spider_gallery_page(self, url):
        logger.info('Spidering gallery page %s' % url)
        pq = PQ(url)
        self.get_image_codes(pq)
        return pq

    def get_all_gallery_pages(self):
        logger.info('Begin spidering gallery pages.')
        self.get_number_of_pages()

        start_page = self.start_page or 1
        end_page = self.end_page or self.page_count
        for page_num in range(start_page, end_page + 1):
            self.spider_gallery_page(
                '%s/page/%s' % (self.start_gallery_page, page_num))

    def get_number_of_pages(self):
        pq = PQ(self.start_gallery_page)

        children = pq('.pagination').children()
        page_length = int(children.eq(children.size() - 2).text())

        self.page_count = page_length
        logger.info('Gallery has %d pages' % page_length)

    def get_image_codes(self, pq):
        logger.info('Discovering images on page.')
        anchor_list = pq('ul.wallpapers li.wall .mini-hud a')

        for anchor in anchor_list:
            image_page_url = anchor.get('href')
            self.image_page_urls.add(image_page_url)
            logger.info('Add image page url.  %s' % image_page_url)

    def get_all_image_pages(self):
        for image_url in self.image_page_urls:
            logger.info('Add %s to queue.' % image_url)
            self.queue.put(image_url)

        logger.info('Waiting for download workers to finnish.')
        # Wait for queue to be empty
        self.queue.join()

    def get_image_page(self, image_page_url):
        logger.info('Getting full size image url for %s' % image_page_url)
        url = 'http://%s%s' % (self.hostname, image_page_url)
        pq = PQ(url)
        # Warning, contains does will match even if text contains more then
        # searched string.
        target_anchor = \
            next((anchor for anchor in pq('.wallpaper-resolutions a')
                 if anchor.text_content() == self.target_resolution), None)

        # if not target_anchor does returns true when target_anchor
        # is an element
        if target_anchor is None:
            logger.error('No such element. Skipped one')
            return pq
        image_src = target_anchor.get('href')
        if image_src not in self.image_urls:
            self.download_image(image_src)
        self.image_urls.add(image_src)
        logger.info('Add image url to downloading list: %s' % image_src)

    def download_image(self, src):
        ext = os.path.splitext(src)[1]
        if ext in self.skip_extensions:
            logger.info('Skipping extension %s for %s' % (ext, src))
            return
        filename = os.path.basename(src)
        save_path = os.path.join(self.save_directory, filename)
        # do not save if file exists
        if os.path.exists(save_path):
            return
        logger.info('Download %s to %s' % (src, save_path))
        thread = DownloadAsset('http://%s%s' % (self.hostname, src), save_path)
        thread.run()

    def create_directories(self):
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def run(self):
        start_time = time()
        logger.info('Begin spidering.')
        self.create_directories()
        self.image_page_urls.clear()
        self.image_urls.clear()
        self.get_all_gallery_pages()
        self.create_download_image_workers()
        self.get_all_image_pages()
        end_time = time()
        dt = end_time - start_time
        logger.info('Time elapsed: %s' % timedelta(seconds=dt))


if __name__ == "__main__":
    spider = Spider(
        'http://wallpaperswide.com/mac-desktop-wallpapers',
        start_page=1,
        max_workers=20)
    spider.run()
    # Rough Performance:
    # 148 1440x900 and totaling 10mb of images downloaded in:
    # 0:00:25.527156
