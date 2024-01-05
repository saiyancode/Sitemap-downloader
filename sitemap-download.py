import requests
import gzip
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
import logging
from queue import Queue

log = open('errors.log', 'w')

class Sitemap_boss():
    def __init__(self, sitemap):
        self._to_run = Queue()
        self._to_run.put_nowait(sitemap)
        self.run()

    def _identify_format(self, sitemap):
        # Returns 1 if the sitemap is a gzip file
        if sitemap.find('.gz') != -1:
            return self._read_compressed(sitemap)
        else:
            return self._read_standard(sitemap)

    def _add_to_queue(self, soup):
        sitemaps = soup.find_all('sitemap')
        [self._to_run.put_nowait(u.find('loc').text) for u in sitemaps]

    def _read_standard(self, sitemap):
        parser = et.XMLParser(strip_cdata=False)
        with requests.get(sitemap, stream=True) as r:
            soup = BeautifulSoup(r.content, 'html.parser')
            if len(soup.find_all('sitemap')) != 0:
                return self._add_to_queue(soup)
            urls = soup.find_all('url')
            clean = [u.find('loc').text for u in urls]
            return clean

    def _read_compressed(self,sitemap):
        try:
            with requests.get(sitemap, stream=True) as r:
                sitemap = gzip.GzipFile(fileobj=BytesIO(r.content)).read()
                soup = BeautifulSoup(sitemap, 'html.parser')
                if len(soup.find_all('sitemap')) != 0:
                    return self._add_to_queue(soup)
                urls = soup.find_all('url')
                clean = [u.find('loc').text for u in urls]
                return clean
        # If the sitemap is incorrectly encoded then try with standard encoding
        except OSError:
            print("Incorrect sitemap encoding trying with no compression")
            log.write("Incorrect extension,{}\n".format(sitemap))
            return self._read_standard(sitemap)

        except Exception as e:
            log.write(str(e))  # log exception info at FATAL log level
            raise(e)

    def save(self, urls, sitemap):
        error_count = 0
        for url in urls:
            try:
                self.file.write("{},{}\n".format(url,sitemap))
            except:
                error_count +=1
        log.write("{},{}\n".format(sitemap, error_count))

    def run(self):
        while self._to_run.qsize() > 0:
            sitemap = self._to_run.get_nowait()
            a = self._identify_format(sitemap)
            if a is not None:
                self.save(a, sitemap)

# print(requests.get("https://willcecil.co.uk/sitemap.xml"))

Sitemap_boss("https://willcecil.co.uk/sitemap.xml")
