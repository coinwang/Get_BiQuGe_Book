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

# # 按书名搜索笔趣阁书库
# def SearchBook(bookName):
#     searchUrl = 'http://www.biquge5200.com/modules/article/search.php?searchkey=' +bookName
#     searchHtml = GetHtml(searchUrl)
#
#     soup = BeautifulSoup(searchHtml, 'html.parser')
#     searchBookNameHtmlList = soup.select('.odd')
#     if len(searchBookNameHtmlList) == 0:
#         return None
#
#     patternBookInfo = r'href'
#     patternBookName = r'/">(.*?)</a>'
#     patternBookUrl = r'http(.*)"'
#
#     for searchBookNameHtml in searchBookNameHtmlList:
#         searchBookNameHtml = str(searchBookNameHtml)
#         getBookInfo = re.search(patternBookInfo, searchBookNameHtml)
#         if getBookInfo is not None:
#             getBookName = re.search(patternBookName, searchBookNameHtml).group().replace('/">', '').replace('</a>', '')
#             if getBookName == bookName:
#                 bookUrl = re.search(patternBookUrl, searchBookNameHtml).group().replace('"', '')
#                 return bookUrl


# 获取小说目录
def GetChapterHtml(htmlSource, bookUrl):
    soup = BeautifulSoup(htmlSource, 'html.parser')
    # 小说书名
    bookName = soup.select('h1')[0]
    bookName = str(bookName).replace('<h1>', '').replace('</h1>', '')
    # print(bookName)

    chapterNumList = []  # 章节url编号列表

    for line in soup.body.find_all('dd'):  # 网页中章节列表
        pattern = r'href="/(.*?)/(\d*?)\.html"'
        List = str(line)
        # print(List)
        chapterNum = re.findall(pattern, List)[0]  # 章节编号
        # print(chapterNum)
        chapterNumList.append(chapterNum[1])
    # print(chapterNumList)

    chapterHtml = []
    for chapterNum in chapterNumList:
        chapterHtml.append(bookUrl + chapterNum +'.html')
    return chapterHtml

# 解析小说标题、正文
def GetArticle(articleHtmlSource, txtFile):
    soup = BeautifulSoup(articleHtmlSource, 'html.parser')

    # 解析小数章节标题
    try:
        articleTitle = soup.select('h1')[0]
        articleTitle = str(articleTitle).replace('<h1>', '').replace('</h1>', '\n')
        print(articleTitle)
        txtFile.write('\n'+ articleTitle)
    except Exception as e:
        print(e)

    txtFile.flush()

    # 解析小说章节正文
    try:
        articleBody = soup.select('#content')[0]
        # print(articleBody)
        articleLine = str(articleBody).replace('<div id="content">', '').replace('</div>', '').replace('<br/>','')
        txtFile.write(articleLine)
    except Exception as e:
        print(e)

    txtFile.flush()


if __name__ == '__main__':
    # BookName = input('Please input a book Name: ')
    BookName = '111'

    Speed = 0
    SleepTime = 2

    # print('\nStart search book...')
    SaveRoute = './'        # 下载保存位置
    # BookUrl = SearchBook(BookName)
    # BookUrl = 'http://www.biqu.cm/2_2077/'
    BookUrl = 'http://www.biquge.com.tw/3_3593/'
    if BookUrl == None:
        print('\tERROR\tNot Find %s' %BookName)
        sys.exit(1)

    print('\nStart download book...')
    print('\nThe book will save at ' +SaveRoute + BookName +'.txt\n')
    # 书籍目录页
    HtmlSource = GetHtml(BookUrl)
    # print(HtmlSource)
    ChapterUrl = GetChapterHtml(HtmlSource, BookUrl)   # 章节地址列表
    # print(ChapterUrl)
    TxtFile = open(SaveRoute+ BookName +'.txt', 'w', encoding='utf-8')

    TotleNum = len(ChapterUrl)    # 要下载的章节总数
    FinishNum = 1                 # 已下载的章节数

    # # 单章节源码分析
    # ArticleHtmlSource = GetHtml('http://www.biqu.cm/2_2077/3757754.html')
    # GetArticle(ArticleHtmlSource, TxtFile)

    for i in ChapterUrl:
        print("%s/%s" %(FinishNum, TotleNum), end='\t')         # 显示爬取进度
        FinishNum += 1

        ArticleHtmlSource = GetHtml(i)
        while ArticleHtmlSource.startswith('http'):       # 异常情况延时下载
            print('\tWARN\tTry Later')
            time.sleep(SleepTime)
            ArticleHtmlSource = GetHtml(i)

        GetArticle(ArticleHtmlSource, TxtFile)
        # 每章节下载间歇
        time.sleep(Speed)

    TxtFile.close()
    print('\tINFO\t'+ BookName +'.txt aleady save at' +SaveRoute)
    sys.exit(0)
