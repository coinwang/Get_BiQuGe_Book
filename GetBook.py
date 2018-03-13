#!/usr/bin/python3
# coding=utf-8

import requests
from bs4 import BeautifulSoup
import re, time, sys


# 获取网页源码
def GetHtml(htmlUrl):
    head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
    try:
        req = requests.get(htmlUrl, headers=head, timeout=30)
        req.raise_for_status()                          # 获取http请求的返回状态，如果状态不是200，则引发异常
        req.encoding = req.apparent_encoding            # 配置编码为网页响应内容编码
        return req.text
    except Exception as e:
        print('\n\tWARN\t%s' %e)
        return htmlUrl

# 按书名搜索笔趣阁书库
def SearchBook(bookName):
    searchUrl = 'http://www.biquge5200.com/modules/article/search.php?searchkey=' +bookName
    searchHtml = GetHtml(searchUrl)

    soup = BeautifulSoup(searchHtml, 'html.parser')
    searchBookNameHtmlList = soup.select('.odd')
    if len(searchBookNameHtmlList) == 0:
        return None

    patternBookInfo = r'href'
    patternBookName = r'/">(.*?)</a>'
    patternBookUrl = r'http(.*)"'

    for searchBookNameHtml in searchBookNameHtmlList:
        searchBookNameHtml = str(searchBookNameHtml)
        getBookInfo = re.search(patternBookInfo, searchBookNameHtml)
        if getBookInfo is not None:
            getBookName = re.search(patternBookName, searchBookNameHtml).group().replace('/">', '').replace('</a>', '')
            if getBookName == bookName:
                bookUrl = re.search(patternBookUrl, searchBookNameHtml).group().replace('"', '')
                return bookUrl


# 获取小说目录
def GetChapterHtml(htmlSource, bookUrl):
    soup = BeautifulSoup(htmlSource, 'html.parser')
    bookName = soup.select('h1')[0]
    bookName = str(bookName).replace('<h1>', '').replace('</h1>', '')

    chapterNumList = []
    for line in soup.body.find_all('dd'):
        pattern = bookUrl +r'(.*?)\.html'
        List = str(line)
        chapterNumList.append(re.findall(pattern, List)[0])

    chapterNumList = set(chapterNumList)
    chapterNumList = list(chapterNumList)
    chapterNumList.sort()

    chapterHtml = []
    for chapterNum in chapterNumList:
        chapterHtml.append(bookUrl + chapterNum +'.html')
    return chapterHtml

# 解析小说标题、正文
def GetArticle(articleHtmlSource, txtFile):
    soup = BeautifulSoup(articleHtmlSource, 'html.parser')

    # 解析小数章节标题
    articleTitle = soup.select('h1')[0]
    articleTitle = str(articleTitle).replace('<h1>', '').replace('</h1>', '\n')
    print(articleTitle)
    txtFile.write(articleTitle)
    txtFile.flush()

    # 解析小说章节正文
    articleBody = soup.select('#content')[0]
    txtFile.write(str(articleBody).replace('<div id="content">', '').replace('</div>', '').replace('<br/>','\n'))
    txtFile.flush()


if __name__ == '__main__':

    BookName = input('Please input a book Name: ')

    Speed = 0.1
    SleepTime = 2

    print('\nStart search book...')
    SaveRoute = './'
    BookUrl = SearchBook(BookName)
    if BookUrl == None:
        print('\tERROR\tNot Find %s' %BookName)
        sys.exit(1)

    print('\nStart download book...')
    print('\nThe book will save at ' +SaveRoute + BookName +'.txt\n')
    HtmlSource = GetHtml(BookUrl)
    ChapterUrl = GetChapterHtml(HtmlSource, BookUrl)
    TxtFile = open(SaveRoute+ BookName +'.txt', 'w', encoding='utf-8')

    TotleNum = len(ChapterUrl)
    FinishNum = 1

    for i in ChapterUrl:
        print("%s/%s" %(FinishNum, TotleNum), end='\t')         # 显示爬取进度
        FinishNum += 1

        ArticleHtmlSource = GetHtml(i)
        while ArticleHtmlSource.startswith('http'):
            print('\tWARN\tTry Later')
            time.sleep(SleepTime)
            ArticleHtmlSource = GetHtml(i)

        GetArticle(ArticleHtmlSource, TxtFile)
        time.sleep(Speed)

    TxtFile.close()
    print('\tINFO\t'+ BookName +'.txt aleady save at' +SaveRoute)
    sys.exit(0)
