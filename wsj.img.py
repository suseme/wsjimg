# # # #!/usr/bin/python

import sys, re, os, shutil
from bs4 import BeautifulSoup
from datetime import *
from urlparse import urlparse

from pyvin.spider import Spider, Persist, SpiderSoup

reload(sys)
sys.setdefaultencoding('utf8')

page_charset = 'GB2312'


def dateFromStr(strDate, strFmt='%Y%m%d'):
    ddTT = datetime.strptime(strDate, strFmt)
    dd = ddTT.date()
    # print dd
    return dd


class WsjImg:
    site_root = 'http://cn.wsj.com/'
    page_root = 'http://cn.wsj.com/gb/'
    img_root = 'http://cn.wsj.com/pictures/photo/'
    starts = ['http://cn.wsj.com/gb/pho.asp']
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
    dir_base = 'base'
    dir_root = 'dat'
    dir_img = 'img'

    def __init__(self, start='', end=''):
        self.init_date(start, end)
        self.persistInfo = {}

        self.callbacks = {'http://cn.wsj.com/gb/pho.asp': self.find_links, 'http://cn.wsj.com/gb/20': self.parse_page,
                          'http://cn.wsj.com/pictures/photo/': self.save_img}
        self.spider = Spider('WsjImg')
        self.spider.set_proxy('proxy-amer.delphiauto.net:8080', 'rzfwch', '6yhnbgt5')
        self.spider.add_callbacks(self.callbacks)
        self.spider.add_urls(self.starts)
        self.spider.start()

    def init_date(self, strStart='', strEnd=''):
        # from long long ago
        if len(strStart) > 0:
            self.dStart = dateFromStr(strStart)
        else:
            self.dStart = date.min

        # until today
        if len(strEnd) > 0:
            self.dEnd = dateFromStr(strEnd)
        else:
            self.dEnd = date.today()

    def find_links(self, url, response):
        links = ImgPageLinks(response, self.dStart, self.dEnd)
        self.spider.add_urls(links.getLinks(response))

    def parse_page(self, url, response):
        # find img page links
        self.find_links(url, response)
        # process image page.
        art = ImgPage(response)
        # clear no used tags
        art.clear()
        # get img urls
        img_urls = art.getImgUrls()
        if len(img_urls) > 1:
            segs = self.parseUrl(url)
            page_date = segs[WsjImg.idx_page_date]
            # save page
            segs[WsjImg.idx_page_filename] = "%s-%s" % (
            art.getTitle(), segs[WsjImg.idx_page_filename].replace('.asp', '.html'))
            art.save(os.path.join(WsjImg.dir_root, page_date, segs[WsjImg.idx_page_filename]))
            # save imgs of the page
            self.save_imgs(img_urls, page_date)
            # copy base files to here
            # os.system('cp -a %s/* %s/' % (WsjImg.dir_base, os.path.join(WsjImg.dir_root, page_date)))
            self.spider.fetch.copyall(WsjImg.dir_base, os.path.join(WsjImg.dir_root, page_date))
        pass

    def save_img(self, url, response):
        print 'ignore %s' % url

    def save_imgs(self, urls, page_date):
        for url in urls:
            segs = self.parseUrl(url)
            dstfile = os.path.join(WsjImg.dir_root, page_date, WsjImg.dir_img, segs[WsjImg.idx_img_dir],
                                   segs[WsjImg.idx_img_filename])
            self.spider.download(url, dstfile)

    def parseUrl(self, url):
        url = urlparse(url)
        segs = url.path.split('/')
        return segs


class ImgPageLinks:
    def __init__(self, page, dStart, dEnd):
        print '[ImgPageLinks]'
        # self.soup = BeautifulSoup(page, from_encoding=page_charset)
        self.dStart = dStart
        self.dEnd = dEnd

    def getLinks(self, html):
        # 'http://cn.wsj.com/gb/20130528/PHO184538.asp'
        p = re.compile('\d{4}\d{2}\d{2}/PHO\d{6}.asp');
        urls = p.findall(html)
        # unique urls
        pages = {}
        for url in urls:
            pages[url] = url
        urls = pages.keys()
        # check date and correct links
        links = []
        p = re.compile('\d{4}\d{2}\d{2}');
        for url in urls:
            strDate = p.findall(url)[0]
            if (self.checkDate(strDate)):
                url = '%s%s' % (WsjImg.page_root, url)
                links.append(url)
        return links

    def checkDate(self, strDate):
        dDate = dateFromStr(strDate)
        return (dDate >= self.dStart and dDate <= self.dEnd)


class ImgPage:
    def __init__(self, page):
        print '[ImgPage]'
        self.soup = BeautifulSoup(page, "html5lib", from_encoding=page_charset)

    # after clear, find image urls
    ## orignal link in html: '../../pictures/photo/BJ20141226094555/01.jpg'
    def getImgUrls(self):
        img_urls = []
        img_nodes = self.soup.findAll('img')
        for item in img_nodes:
            url = item['src']
            if url:
                # change img src to local relative path.
                item['src'] = url.replace('../../pictures/photo', WsjImg.dir_img)
                # save url for download
                url = url.replace('../../pictures/photo/', 'http://cn.wsj.com/pictures/photo/')
                if url.startswith('http://cn.wsj.com/pictures/photo/'):
                    img_urls.append(url)
        return img_urls

    #
    def getTitle(self):
        return self.soup.title.text

    # clear no used tags
    def clear(self):
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
        SpiderSoup.insertCss(self.soup, "css/jquery.mobile-1.4.5.min.css")
        SpiderSoup.insertCss(self.soup, "css/swipebox.css")
        SpiderSoup.insertCss(self.soup, "css/wsj.img.css")
        # set script
        SpiderSoup.insertScript(self.soup, "js/jquery-2.1.3.min.js")
        SpiderSoup.insertScript(self.soup, "js/jquery.mobile-1.4.5.min.js")
        SpiderSoup.insertScript(self.soup, "js/jquery.swipebox.js")
        SpiderSoup.insertScript(self.soup, "js/wsj.img.js")

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


if __name__ == "__main__":
    # print 'wsjimg'

    sStart = ''
    sEnd = ''
    argc = len(sys.argv)
    if (argc == 2):
        sStart = sys.argv[1]
    elif (argc == 3):
        sStart = sys.argv[1]
        sEnd = sys.argv[2]

    print "get [%s ~ %s]" % (sStart, sEnd)

    wsj = WsjImg(start=sStart, end=sEnd)
