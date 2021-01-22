import requests
from pymongo import *
from bs4 import BeautifulSoup
header = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
            AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"text/html,application/xhtml+xml,application/xml;\
            q=0.9,imgwebp,*/*;q=0.8"
        }
class crawler:
    # 생성자
    def __init__(self, url):
        super(crawler, self).__init__()
        self.url = url
        self.page_num = 1 # 처음 페이지 넘버는 1로 초기화
        self.domain = self.url.split('/')[0] + '//' + self.url.split('/')[2]
        
        driver = requests.get(self.url, verify = False, headers = header)
        html = driver.content.decode('euc-kr', 'replace') # encoding to korean
        # 한글 깨짐 방지, https://blog.naver.com/PostView.nhn?blogId=redtaeung&logNo=221904432971    
        # utf-8이 아닌 euc-kr 변경시 작동 되었다.
        page = BeautifulSoup(html, 'html.parser')
        self.page = page

    
    # set url
    def setURL(self, url):
        self.url = url
    # set page
    def setPage(self):
        driver = requests.get(self.url, verify = False, headers = header)
        html = driver.content.decode('euc-kr', 'replace') # encoding to korean
        # 한글 깨짐 방지, https://blog.naver.com/PostView.nhn?blogId=redtaeung&logNo=221904432971    
        # utf-8이 아닌 euc-kr 변경시 작동 되었다.
        page = BeautifulSoup(html, 'html.parser')
        self.page = page

    # get page
    def getPage(self): # crawler 객체의 url에 요청
        driver = requests.get(self.url, verify = False, headers = header)
        html = driver.content.decode('euc-kr', 'replace') # encoding to korean
        # 한글 깨짐 방지, https://blog.naver.com/PostView.nhn?blogId=redtaeung&logNo=221904432971    
        # utf-8이 아닌 euc-kr 변경시 작동 되었다.
        page = BeautifulSoup(html, 'html.parser')
        return page
    def getURL(self):
        return self.url
    def getDomain(self):
        return self.domain
    
    

class crawler_danawa(crawler):
    def __init__(self, url):
        super().__init__(url)
    
    def getDate(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.date')[index].text
    def getName(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.name')[index].text
    def getTitle(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.title')[index].text.strip()
    def getAverPrice(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.aver_price')[index].text
    def getStatus(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.status')[index].text
    def getLink(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.title a')[index]['href']
    def getRowsToNumber(self):
        return len(self.page.select('.setpc_bbs_tbl>tbody>tr'))

class crawler_danawa_pc(crawler): # db 관리 포함
    def __init__(self, url):
        super().__init__(url)
        # db
        self.myclient = MongoClient("mongodb://localhost:27017/") # mongodb의 port의 기본값은 27017, 일단 로컬로
        #self.db_comtris = MongoClient('mongodb://%s:%s@%s' %(MONGO_ID, MONGO_PW, MONGO_HOST)
        self.db = self.myclient['test']
        self.col = self.db["col"]
    # DB methods
    def insert_one(self, document):
        self.col.insert_one(document) # self.col에 삽입

    # 소멸자
    def __del__(self):
        self.myclient.close()

    def getRows(self):
        rows = self.page.select('.tbl_t3>tbody>tr>.tit')
        print("rows = ", rows)
        print("len(rows) = ", len(rows))
    
    def getKey(self):
        self.keys = []
        self.keys = list(map(lambda page:page.text, self.page.select('.tbl_t3>tbody>tr>.srt')))
        return self.keys

    def getDict(self, keys, id):
        print("getDict")
        result = {}
        for idx, key in enumerate(keys):
            value = self.page.select('.tbl_t3>tbody>tr>.tit')[idx].text
            value = value.strip().split('\n')
            aver_price = self.page.select('.tbl_t3>tbody>tr>.prc')[idx].text
            print("__id = ", id, "idx = ", idx, "key = ", key, "value = ", value[0], aver_price, "원")

            result.update({'_id' : id, 'key':{'name' : value[0], 'aver_price' : aver_price}})
        return result
    def KeysValidation(self, keys):
        if "CPU" in keys:
            if "메인보드" in keys:
                if "메모리" in keys:
                    if "그래픽카드" in keys:
                        if "SSD" in keys:
                            if "파워" in keys: # 모두 존재한다.
                                print("Check 완료")
                                return 1
                            else : 
                                print("파워가 없습니다.")
                                return 0
                        else :
                            print("SSD가 없습니다.")
                            return 0
                    else :
                        print("그래픽카드가 없습니다.")
                        return 0
                else :
                    print("메모리가 없습니다.")
                    return 0
            else :
                print("메인보드가 없습니다.")
                return 0
        else :
            print("CPU가 없습니다.")
            return 0
