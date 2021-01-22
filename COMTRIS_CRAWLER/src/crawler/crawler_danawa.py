import time
import requests
from bs4 import BeautifulSoup
from crawler import *
def run_crawler():
    # url 지정 
    header = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
            AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"text/html,application/xhtml+xml,application/xml;\
            q=0.9,imgwebp,*/*;q=0.8"
        }
    url = "http://shop.danawa.com/pc/?controller=estimateDeal&methods=lists&registerSectionSeq=6&page={}"
    
    pageNum=10
    crawler_page = crawler_danawa(url.format(1)) # 객체 생성
    
    while(1): #무한 반복
        try :
            pageNum += 1 # 다음 페이지
            url = url.format(pageNum) # 페이지 넘버 url 지정
            crawler_page.setURL(url) # 객체 url 세팅
            crawler_page.setPage() # 객체 페이지 세팅
            pageRows = crawler_page.getRowsToNumber()

            if pageRows == 0: # 마지막페이지로 갈 경우 break
                print("빈 페이지 입니다.")
                break

        except Exception as e: # setting Error
            print("setting Error")
            print('Error Message = ', e)
            print('Error url = ', url)
            continue
        else : # setting complete
            for i in range(pageRows): # Rows 갯수만큼 반복
                try:
                    # http://shop.danawa.com/pc/?controller=estimateDeal&methods=lists&registerSectionSeq=6&page=1 참고
                    date = crawler_page.getDate(i)
                    name = crawler_page.getName(i)
                    title = crawler_page.getTitle(i).split("\n") 
                    # 비밀글을 걸러내기 위해서 list로 만듬. 비밀글이면 ['title', '비밀글']로 나옴
                    aver_price = crawler_page.getAverPrice(i)
                    status = crawler_page.getStatus(i)
                    link = crawler_page.getDomain() + '/pc/' + crawler_page.getLink(i)
                    id = crawler_page.getLink(i)
                    id = int(id[id.rfind("=")+2 : len(id)].strip())

                except Exception as e:
                    print('getting Error(date, name, title, ...)')
                    print('Error Message = ', e)
                    print("Error url = ", crawler_page.getURL())
                    continue
                else : # getting page complete -> check 비밀글
                    if '비밀글' in title:
                        print("비밀글이므로 pass")
                        continue
                            
                    else: # 비밀글이 아니므로 링크에 접속
                        try :
                            crawler_pc = crawler_danawa_pc(link)
                        except Exception as e:
                            print('link 접속 실패')
                            print(e)
                            continue
                        else : # link 접속 성공 -> 키 가져오기
                            try : 
                                keys = crawler_pc.getKey() # key를 받음
                                result = crawler_pc.getDict(keys, id) # 사전 형식으로 데이터를 받아옴
                                if crawler_pc.KeysValidation(keys):
                                    print("DB작성해야 해")
                                    crawler_pc.insert_one(result) # db에 삽입
                                    print("result = ", result)
                                else :
                                    print("부품 없음")

                            except Exception as e:
                                print('getting Key Error')
                                print(e)
