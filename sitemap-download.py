import requests
import gzip
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
import logging
from queue import Queue

log = open('errors.log', 'w')

class Sitemap_boss():
    def __init__(self):
        self._to_run = Queue()
        self.run()

    def _identify_format(self, sitemap):
        # Returns 1 if the sitemap is a gzip file
        if sitemap.find('.gz') != -1:
            return self._read_compressed(sitemap)
        else:
            return self._read_standard(sitemap)

    def _read_standard(self, sitemap):
        with requests.get(sitemap, stream=True) as r:
            soup = BeautifulSoup(r.content, 'lxml')
            urls = soup.find_all('url')
            clean = [u.find('loc').text for u in urls]
            return clean

    def _read_compressed(self,sitemap):
        try:
            with requests.get(sitemap, stream=True) as r:
                sitemap = gzip.GzipFile(fileobj=BytesIO(r.content)).read()
                soup = BeautifulSoup(sitemap, 'lxml')
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

    def run(self):
        a = self._identify_format('https://www.zoopla.co.uk/xmlsitemap/sitemap/invest_index_1/invest_index_1_invest_article_1.xml.gz')
        b = self._identify_format('https://www.fundingoptions.com/sitemap.xml')
        print(len(a), len (b))


Sitemap_boss()
