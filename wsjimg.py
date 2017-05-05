# # # #!/usr/bin/python

import sys, re, os, shutil, traceback, json, platform, threading, logging
from bs4 import BeautifulSoup
from datetime import *
from urlparse import urlparse

from pyvin.spider import Spider, Persist, SpiderSoup
from persist import WsjPersist

reload(sys)
sys.setdefaultencoding('utf8')

page_charset = 'GB2312'

class WsjImg:
    proxy_host = ''
    proxy_user = ''
    proxy_pass = ''
    site_root = 'http://cn.wsj.com/'
    page_root = 'http://cn.wsj.com/gb/'
    img_root = 'http://cn.wsj.com/pictures/photo/'
    starts = [
        'http://cn.wsj.com/gb/pho.asp',
        # 'http://cn.wsj.com/gb/20140818/PHO091509.asp',
        # 'http://cn.wsj.com/gb/20140807/PHO100842.asp'
        ]
    # starts = ['http://cn.wsj.com/gb/20141230/PHO094555.asp']
    # callbacks = {'http://cn.wsj.com/gb/pho.asp':WsjImg.find_links, 'http://cn.wsj.com/gb/':WsjImg.parse_page, 'http://cn.wsj.com/pictures/photo/':WsjImg.save_img}

    # page url path
    # ['', 'gb', '20130528', 'PHO184538.asp']
    idx_page_date = 2
    idx_page_filename = 3
    # img url path
    # ['', 'pictures', 'photo', 'BJ20141226094555', '01.jpg']
    idx_img_dir = 3
    idx_img_filename = 4

    # persist
    DIR_BASE = 'base'
    DIR_ROOT = 'dat'
    DIR_IMG = 'img'

    def __init__(self, start='', end=''):
        # logging.basicConfig(
        #     format='%(asctime)s:%(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        #     datefmt='%a, %d %b %Y %H:%M:%S',
        #     filename=os.path.join(os.getcwd(),'log.txt')
        #
        # )
        self.log = logging.getLogger(WsjImg.__name__)
        self.log.setLevel(logging.INFO)
        formatStr = '%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s'
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(formatStr))
        self.log.addHandler(console)
        filelogger = logging.FileHandler('log-1.txt', 'a')
        filelogger.setLevel(logging.INFO)
        filelogger.setFormatter(logging.Formatter(formatStr))
        self.log.addHandler(filelogger)

        self.init_date(start, end)

        # self.db = WsjPersist()
        self.lock = threading.Lock()

        self.callbacks = {
                'http://cn.wsj.com/gb/pho.asp': self.find_links, 
                'http://cn.wsj.com/gb/20': self.parse_page,
                'http://cn.wsj.com/pictures/photo/': self.save_img
        }
        self.spider = Spider('WsjImg', log=self.log)
        self.spider.bind(Spider.EVT_ON_ADD_URL, self.on_add_url)
        self.spider.bind(Spider.EVT_ON_REMOVE_URL, self.on_remove_url)
        self.spider.bind(Spider.EVT_ON_URL_ERR, self.on_err_url)
        self.spider.set_proxy(WsjImg.proxy_host, WsjImg.proxy_user, WsjImg.proxy_pass)
        self.spider.add_callbacks(self.callbacks)
        self.spider.add_urls(self.starts)
        self.spider.set_max_thread(20)

        self.log.info('Started...')
        self.spider.start()

    def init_date(self, strStart='', strEnd=''):
        '''Initiate start/end date'''
        self.strStart = strStart
        self.strEnd = strEnd

    def find_links(self, url, response):
        '''Parse the photos news default page and find photos news page urls'''
        self.log.info('find links in %s' % url)
        links = ImgPageLinks(response, self.strStart, self.strEnd, log=self.log)
        urls = links.getLinks(response)
        self.spider.add_urls(urls)

        self.lock.acquire()
        # links.persistToDB(self.db)
        self.lock.release()

    def parse_page(self, url, response):
        '''Parse photos news page, find content and image urls, also with other photos news page urls.'''
        # find img page links
        self.find_links(url, response)
        # process image page.
        imgPage = ImgPage(url, response, log=self.log)
        imgPage.clear()
        imgPage.parseImgUrls()
        if len(imgPage.imgUrls.keys()) > 1:
            imgPage.save(os.path.join(WsjImg.DIR_ROOT, imgPage.filePath))

            with open(os.path.join(WsjImg.DIR_ROOT, imgPage.data['path']), 'w') as f:
                f.write(json.dumps(imgPage.data))

            self.lock.acquire()
            # imgPage.persistToDB(self.db)
            # self.db.updateArt(url, imgPage.title, imgPage.summary)
            self.lock.release()

            # save imgs of the page
            self.save_imgs(imgPage)

            # copy base files to here
            # os.system('cp -a %s/* %s/' % (WsjImg.dir_base, os.path.join(WsjImg.dir_root, page_date)))

            # self.spider.fetch.copyall(WsjImg.DIR_BASE, os.path.join(WsjImg.DIR_ROOT, imgPage.pageDate))
        else:
            self.log.warning('no link find in %s' % url)

    def save_img(self, url, response):
        self.log.info('ignore %s' % url)

    def save_imgs(self, imgPage):
        for url in imgPage.imgUrls.keys():
            dstfile = os.path.join(WsjImg.DIR_ROOT, imgPage.imgUrls[url]['path'])
            self.spider.download(url, dstfile)

    def on_add_url(self, event, url):
        os.system('echo %s >> queued.txt' % url)

    def on_remove_url(self, event, url):
        os.system('echo %s >> finished.txt' % url)

    def on_err_url(self, event, url):
        self.log.warning('Grasp %s failed' % url)

class ImgPageLinks:
    '''Find photos news page urls'''
    KEY_URL = 'url'
    KEY_DATE = 'date'

    def __init__(self, page, strStart, strEnd, log=None):
        if log:
            self.log = log
        else:
            self.log = logging.getLogger(ImgPageLinks.__name__)
        self.log.info('[ImgPageLinks]')
        # self.soup = BeautifulSoup(page, from_encoding=page_charset)
        self.strStart = strStart
        self.strEnd = strEnd
        self.links = {}

    def getLinks(self, html):
        # 'http://cn.wsj.com/gb/20130528/PHO184538.asp'
        p = re.compile('\d{4}\d{2}\d{2}/PHO\d{6}.asp');
        urls = p.findall(html)
        # unique urls
        for url in urls:
            self.links[url] = url

        # check date and correct links
        p = re.compile('\d{4}\d{2}\d{2}');
        for url in self.links.keys():
            strDate = p.findall(url)[0]
            # print strDate
            del(self.links[url])
            if (DateUtils.checkDate(strDate, self.strStart, self.strEnd, log=self.log)):
                url = '%s%s' % (WsjImg.page_root, url)
                self.links[url] = {}
                self.links[url][ImgPageLinks.KEY_DATE] = strDate
                self.links[url][ImgPageLinks.KEY_URL] = url
            else:
                self.log.info('skip %s' % url)
        # print self.links
        return self.links.keys()

    def persistToDB(self, db):
        '''add self.links to db, return new added link list'''
        for url in self.links.keys():
            ret = db.addArt(self.links[url][ImgPageLinks.KEY_URL], self.links[url][ImgPageLinks.KEY_DATE])
            ret = db.isArtDownload(url)
            if ret:
                del(self.links[url])
        return self.links.keys()

class ImgPage:
    '''Parse photos news page, get content and image urls'''
    def __init__(self, url, page, log=None):
        if log:
            self.log = log
        else:
            self.log = logging.getLogger(ImgPage.__name__)
        self.log.info('[ImgPage]')
        # print url
        # print page
        self.url = url
        self.soup = BeautifulSoup(page, "html5lib", from_encoding=page_charset)
        self.title = self.soup.title.text
        self.summary = ''
        self.imgUrls = {}

        segs = ImgPage.parseUrl(url)
        self.pageDate = segs[WsjImg.idx_page_date]
        self.filePath = os.path.join(self.pageDate, "%s-%s" % (self.title, segs[WsjImg.idx_page_filename].replace('.asp', '.html')))

        # create a data object for data exchange
        self.data = {}
        self.data['path'] = os.path.join(self.pageDate, segs[WsjImg.idx_page_filename].replace('.asp', '.json'))
        self.data['url'] = url
        self.data['title'] = self.title
        self.data['summary'] = self.summary
        self.data['date'] = self.pageDate
        self.data['imgs'] = []


    # after clear, find image urls
    ## orignal link in html: '../../pictures/photo/BJ20141226094555/01.jpg'
    def parseImgUrls(self):
        # print 'parseImgUrls'
        img_nodes = self.soup.findAll('img')
        for item in img_nodes:
            url = item['src']
            if url:
                # print url
                # change img src to local relative path.
                item['src'] = url.replace('../../pictures/photo', WsjImg.DIR_IMG)
                # save url for download
                url = url.replace('../../pictures/photo/', 'http://cn.wsj.com/pictures/photo/')
                if url.startswith('http://cn.wsj.com/pictures/photo/'):
                    self.imgUrls[url] = {}
                    self.imgUrls[url]['url'] = url
                    self.imgUrls[url]['alt'] = item['alt']
                    segs = ImgPage.parseUrl(url)
                    self.imgUrls[url]['path'] = os.path.join(self.pageDate, WsjImg.DIR_IMG, segs[WsjImg.idx_img_dir], segs[WsjImg.idx_img_filename])
                    self.imgUrls[url]['src'] = os.path.join(WsjImg.DIR_IMG, segs[WsjImg.idx_img_dir], segs[WsjImg.idx_img_filename])
                    self.data['imgs'].append(self.imgUrls[url])
        return self.imgUrls.keys()

    def parse(self):
        ul_node = self.soup.find('ul', attrs={'data-role':'listview'})
        li_nodes = ul_node.findAll('li')
        for li_node in li_nodes:
            img_node = li_node.find('img')
            # print img_node['src']
            div_node = li_node.find('div')
            # print div_node.find('p').text
            # print div_node.find('samp').text

    # clear no used tags
    def clear(self):
        # find summary
        # print 'clear'
        summary = self.soup.findAll('div', attrs={'id':'summary'})
        if len(summary) > 0:
            # print summary
            self.summary = summary[0].text
            # print self.summary
            self.data['summary'] = self.summary

        # find imgs
        divTs = self.soup.findAll('div', attrs={'id': 'sliderBox'})

        # clear
        self.soup.body.clear()
        del self.soup.body['onload']
        SpiderSoup.clearNode(self.soup, 'script')
        SpiderSoup.clearNode(self.soup, 'noscript')
        SpiderSoup.clearNode(self.soup, 'style')
        SpiderSoup.clearNode(self.soup, 'link')
        SpiderSoup.clearNode(self.soup, 'meta', {'name': 'keywords'})
        SpiderSoup.clearNode(self.soup, 'meta', {'name': 'description'})
        # set css
        SpiderSoup.insertCss(self.soup, "../assets/css/jquery.mobile-1.4.5.min.css")
        SpiderSoup.insertCss(self.soup, "../assets/css/swipebox.css")
        SpiderSoup.insertCss(self.soup, "../assets/css/wsj.img.css")
        # set script
        SpiderSoup.insertScript(self.soup, "../assets/js/jquery-2.1.3.min.js")
        SpiderSoup.insertScript(self.soup, "../assets/js/jquery.mobile-1.4.5.min.js")
        SpiderSoup.insertScript(self.soup, "../assets/js/jquery.swipebox.js")
        SpiderSoup.insertScript(self.soup, "../assets/js/wsj.img.js")

        # add ul
        ul_tag = self.soup.new_tag("ul")
        ul_tag['data-role'] = 'listview'
        self.soup.body.append(ul_tag)

        # add imgs list
        if len(divTs) > 0:
            divT = divTs[0]
            liTs = divT.findAll('li')
            for liT in liTs:
                ul_tag.append(liT)

        # set img class as swipebox
        img_nodes = self.soup.findAll('img')
        for item in img_nodes:
            item['class'] = 'swipebox'

        return str(self.soup)

    def save(self, filename):
        per = Persist(filename)
        per.store_soup(self.soup)
        per.close()

    def persistToDB(self, db):
        id = db.getArtIdByUrl(self.url)
        if len(self.imgUrls) > 0:
            for url in self.imgUrls.keys():
                db.addPic(id, self.imgUrls[url]['url'], self.imgUrls[url]['src'], self.imgUrls[url]['alt'])
        db.setArtDownload(self.url)

    @staticmethod
    def parseUrl(url):
        return urlparse(url).path.split('/')

class DateUtils:

    @staticmethod
    def checkDate(strDate, strStart='', strEnd='', log=None):
        # print 'date: [%s]' % strDate
        # print 'strStart: [%s]' % strStart
        # print 'strEnd: [%s]' % strEnd

        dStart = date.min
        dEnd = date.today()

        if len(strStart) > 0:
            dStart = DateUtils.dateFromStr(strStart, log=log)

        # until today
        if len(strEnd) > 0:
            dEnd = DateUtils.dateFromStr(strEnd, log=log)

        dDate = DateUtils.dateFromStr(strDate, log=log)

        return (dDate >= dStart and dDate <= dEnd)

    @staticmethod
    def dateFromStr(strDate='', strFmt='%Y%m%d', log=None):
        '''return date object from string'''
        try:
            return datetime.strptime(strDate, strFmt).date()
        except:
            traceback.print_exc()
            if log:
                log.warning('invalid date string %s ' % strDate)
                log.exception(traceback.format_exc())

if __name__ == "__main__":
    # print 'wsjimg'

    dateStart = ''
    dateEnd = ''
    argc = len(sys.argv)
    if (argc == 2):
        dateStart = sys.argv[1]
    elif (argc == 3):
        dateStart = sys.argv[1]
        dateEnd = sys.argv[2]

    logging.info("get [%s ~ %s]" % (dateStart, dateEnd))

    wsj = WsjImg(start=dateStart, end=dateEnd)
