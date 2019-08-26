import requests
import re
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
import os


def getTimeRange():
    starttime = "00000000"
    endtime = "00000000"
    while starttime == "00000000" or endtime == "000000000":
        starttime = input("\r\nPlease enter the start date in the form of yyyymmdd: ")
        endtime = input("\r\nPlease enter the end date in the form of yyyymmdd: ")
        try:
            startdate = datetime.datetime(int(starttime[0:4]), int(starttime[4:6]), int(starttime[6:8]))
            enddate = datetime.datetime(int(endtime[0:4]), int(endtime[4:6]), int(endtime[6:8]))
            if startdate.year < 2008:
                print("\r\nData before 2008 is not accessible. Please input again.")
                # Initialize the date again
                starttime = "00000000"
                endtime = "00000000"
            else:
                if startdate > enddate:
                    print("\r\nThe end-date you inputted was before start-date. Please input again.")
                    # Initialize the date again
                    starttime = "00000000"
                    endtime = "00000000"
        except:
            print("\r\nYou are inputting in a wrong format. Please input again.")
            # Initialize the date again
            starttime = "00000000"
            endtime = "00000000"
    print("\r\n Thank you for inputting the date!")
    dateList = getTimeZone(starttime, endtime)
    return dateList


def getTimeZone(starttime, endtime):
    startdate = datetime.datetime(int(starttime[0:4]), int(starttime[4:6]), int(starttime[6:8]))
    # now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    # my_yestoday = startdate + delta
    # my_yes_time = my_yestoday.strftime('%Y%m%d')
    n = 0
    date_list = []
    while 1:
        if starttime <= endtime:
            days = (startdate + delta * n).strftime('%Y%m%d')
            n = n + 1
            date_list.append(days)
            if days == endtime:
                break
    return date_list


def getTimeGap():
    print("\r\nUsually you will need time gap for web crawling, since web crawling easily cause " +
          "the page to crash. The recommended time gap is 3s")
    timeGap = 0.0
    while timeGap == 0.0:
        try:
            timeGap = float(input("\r\nPlease input an number for the time gap you want of each crawl:"))
            if timeGap == 0:
                print("\r\nYou inputed 0. Not accepted. Please input again.")
        except:
            print("\r\nWhat you input was not a number. Please input again.")
    return timeGap


def getHTMLText(date, url, failList, timeGap):
    kv = {'User-Agent': 'Mozilla/5.0'}
    try:
        time.sleep(timeGap)
        r = requests.get(url, headers=kv, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print(date + " fail." + '\r\n')
        saveFailedDate(failList, date, path)


def getPageList(html, datetype1):
    page = []
    pageNamelist = {}
    soup = BeautifulSoup(html, "html.parser")
    a = soup.find_all('a')
    for i in a:
        try:
            href = i.attrs['href']
            rawurl = re.findall(r'nbs.D110000gmrb_\d{2}.htm', href)
            pagename = i.get_text()
            if rawurl != [] and pagename != '下一版 ' and pagename != '返回目录' and pagename != ' 上一版':
                newurl = "http://epaper.gmw.cn/gmrb/html/" + datetype1 + '/' + rawurl[0]
                if newurl not in page:
                    page.append(newurl)
                    pageNamelist[newurl] = pagename
        except:
            continue
    return page, pageNamelist


def getArticleList(html, date):
    articleList = []
    soup = BeautifulSoup(html, "html.parser")
    a = soup.find_all('a')
    datetype1 = date[0:4] + '-' + date[4:6] + '/' + date[6:]
    for i in a:
        try:
            href = i.attrs['href']
            pattern = re.compile(r'nw.D110000gmrb_%s_\d-\d{2}.htm' % date)
            rawurl = pattern.findall(href)
            if rawurl != []:
                newurl = "http://epaper.gmw.cn/gmrb/html/" + datetype1 + '/' + rawurl[0]
                if newurl not in articleList:
                    articleList.append(newurl)
        except:
            continue
    return articleList


def getArticle(date, html, pageName, articleurl):
    soup = BeautifulSoup(html, "html.parser")
    title = ''
    articleDict = ''
    articleText = ''
    if soup.title.string is None:
        return title, articleDict, articleText
    pagenum = re.split(r'<.?founder-pagenum>', html)[1]
    keyword = re.split(r'<.?founder-keyword>', html)[1]
    author = re.split(r'<.?founder-author>', html)[1]
    papername = re.split(r'<.?founder-papername>', html)[1]
    title = soup.title.string
    pagepicurl = re.split(r'<.?founder-pagepicurl>', html)[1]
    file = str("guangming/" + date + title + '.txt')
    rawarticle = soup.select('#articleContent')[0]
    for ss in rawarticle.select("script"):  # 删除无用项 deleting useless components in the article
        ss.decompose()
    # 按照指定格式替换章节内容，运用正则表达式
    # Appropriate the content of the articles to the format requirement of the file
    articleText = re.sub('\s+', '\r\n\t', rawarticle.text).strip('\r\n')  # Paragraphing is necessary for reading txt
    articleDict = re.sub('\s+', '', rawarticle.text)  # Paragraphing is not for csv
    return pagenum, pageName, keyword, author, papername, title, pagepicurl, articleurl, articleDict, articleText, file, date


def createPath():
    path = ""
    while path == "":
        try:
            path = input(
                "\r\nPlease input the path for the folder name you want to save the files in (e.g. D:/guangming): ")
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
            path = ""
        else:
            print("Successfully created the directory %s " % path)
    return path


def saveDateText(title, article, date, path):
    filename = os.path.join(path, str(date + '《' + title + '》' + '.txt'))
    f = open(filename, 'ab+')
    f.write(('\r' + title + '\r\n').encode('UTF-8'))
    f.write(article.encode('UTF-8'))
    f.close()


def saveDateCsv(pagenum, pageName, keyword, author, papername, title, pagepicurl, articleurl, articleDict, file, date,
                path):
    name = ['pagenum', 'pagename', 'keyword', 'author', 'papername', 'title', 'pagepicurl', 'articleurl', 'content',
            'file', 'date']
    fileyear = date[0:4]
    filename = os.path.join(path, str("GM_Csv" + fileyear + '.csv'))
    list = [[pagenum, pageName, keyword, author, papername, title, pagepicurl, articleurl, articleDict, file, date]]
    test = pd.DataFrame(columns=name, data=list)
    test.to_csv(filename, mode='a', encoding='utf_8_sig', header=False)


def saveFailedDate(list, date, path):
    list.append(date)
    filename = os.path.join(path, str('failDateList.txt'))
    f = open(filename, 'ab+')
    f.write(('\r' + date + ',\r\n').encode('UTF-8'))
    f.close()


def saveFailedUrl(failurlList, url, path):
    failurlList.append(url)
    filename = os.path.join(path, str('failurlList.txt'))
    f = open(filename, 'ab+')
    f.write(('\r' + url + ',\r\n').encode('UTF-8'))
    f.close()


# 主函数如下
def main():
    faildateList = []  # 得到爬虫失败的日期 Get the dates that failed to be crawled
    failurlList = []  # 得到爬虫失败的网页 Get the links that failed to be crawled

    # 第一步：从用户处得到日期、爬虫间隙、保存文件的路径
    # The 1st step: Get the date, time gap for web-crawling, and path from the user
    dateList = getTimeRange()
    timeGap = getTimeGap()
    path = createPath()

    print("\r\nWeb-crawling begins! Please wait for the web crawling process to be completed.")
    # 开始爬虫
    # Begin the crawling process
    for date in dateList:
        try:
            datetype1 = date[0:4] + '-' + date[4:6] + '/' + date[6:]
            # 第二步：定义每天的初始爬虫页面
            # The 2nd Step: Instantiate the starting link of each date
            start_url = 'http://epaper.gmw.cn/gmrb/html/' + datetype1 + '/nbs.D110000gmrb_02.htm'
            html = getHTMLText(date, start_url, faildateList,
                               timeGap)  # 得到该日期对应的网址 Get the link to the page of that day
            # 第三步：得到每天日报里每版的网址
            # The 3rd step: Get the link to each page of the paper each day
            pageList, pageNamelist = getPageList(html, datetype1)
            for pageurl in pageList:
                # 第四步：得到每版全部文章网址
                # The 4th Step: Get the link to the articles
                try:
                    pageName = pageNamelist[pageurl]
                    html1 = getHTMLText(date, pageurl, faildateList, timeGap)
                    articleList = getArticleList(html1, date)
                    if articleList != []:
                        for articleurl in articleList:
                            try:
                                # 第五步：得到每篇文章中的text
                                # The 5th Step: Get the text of the articles
                                html2 = getHTMLText(date, articleurl, faildateList, timeGap)
                                pagenum, pageName, keyword, author, papername, title, pagepicurl, articleurl, articleDict, articleText, file, date = getArticle(
                                    date, html2, pageName, articleurl)
                                # 第六步：将文章保存为txt
                                # The 6th Step: Saving the article as txt
                                if title != '':
                                    saveDateText(title, articleText, date, path)
                                # 第七步：将当日的所有文章保存到csv文档里
                                # The 7th Step: Saving all the articles of the date to the csv file
                                saveDateCsv(pagenum, pageName, keyword, author, papername, title, pagepicurl,
                                            articleurl, articleDict, file, date, path)
                            except:
                                print(str('        article ' + articleurl + ' failed.\r\n'))
                                saveFailedUrl(failurlList, articleurl, path)
                                continue
                                # 爬完一篇文章
                                # Finishing crawling an article
                except:
                    print(str('    page ' + pageurl + ' failed.\r\n'))
                    continue
                    # 爬完一版
                    # Finishing crawling a page
            print("Saving of " + date + " is done.\r\n")
            # 爬完一天
            # Finishing crawling all the articles of one date
            timenow = time.ctime()
            print(str(date + " is done at " + timenow + '\r\n'))  # 显示爬虫时间 Displaying the time
        except:
            continue
    print('The dates that failed are the following: ')
    print(faildateList)
    print('The links that failed are the following: ')
    print(failurlList)


main()
