# Crawler code
===

Crawls http://wallpaperswide.com for wallpapers of a specific resolution.

## Usage

To crawl the mac wallpaper at http://wallpaperswide.com/mac-desktop-wallpapers.html
remove the ".html" from the end of the url and set that as the start_url in the
Spider object, then use the run method:

``` python
spider = Spider('http://wallpaperswide.com/mac-desktop-wallpapers')
spider.run()
```

The images will be saved to images/mac-desktop-wallpapers/ folder.

