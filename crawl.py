from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import sqlite3
from datetime import datetime, timedelta
import random

def process_datetime_string(datetime_string):
    try:
        # 상대적인 시간 표현인 경우 처리
        if "전" in datetime_string:
            if "분" in datetime_string:
                minutes = int(datetime_string.split("분")[0])
                datetime_obj = datetime.now() - timedelta(minutes=minutes)
            
            else:
                raise ValueError("잘못된 시간 표현입니다.")
        else:
            # 시간 형식 확인 및 datetime 객체 생성
            datetime_format = "%y/%m/%d %H:%M" if len(datetime_string.split("/")) == 3 else "%m/%d %H:%M"
            datetime_obj = datetime.strptime(datetime_string, datetime_format)
            
            # 연도가 작성되지 않은 경우 기본 연도인 23로 설정
            if datetime_obj.year == 1900:
                datetime_obj = datetime_obj.replace(year=2023)
        
        return datetime_obj
    
    except ValueError as e:
        print("잘못된 날짜 형식 또는 시간 표현입니다.", str(e), datetime_string)
        return None

def db_insert(con, main_text, reply_list):

    cur = con.cursor()

    id = main_text[0]
    

    cur.execute("INSERT INTO MainText Values(?, ?, ?, ?, ?, ?, ?)", main_text)
    
    for reply in reply_list:
        
        cur.execute("INSERT INTO Reply Values(?, ?, ?, ?, ?)", reply)

    con.commit()
    print(id, "입력완료")

def set_db(con):

    cur = con.cursor()

    try:
        cur.execute("CREATE TABLE MainText(ID TEXT, Author TEXT, Date TEXT, Board TEXT, Title TEXT, Main TEXT, Vote INTEAGER);")
        cur.execute("CREATE TABLE Reply(ID TEXT, Author TEXT, Date TEXT, Main TEXT, Vote INTEAGER);")
    except:
        pass

    con.commit()

def get_page(id):

    #쪽지 버튼이 생길때까지 대기
    element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "messagesend")))

    #본문과 글을 담고있는 태그
    main_board = driver.find_element(By.CLASS_NAME, "wrap.articles")

    #본문인 article 에서 p 태그를 추출
    main_text = main_board.find_element(By.CLASS_NAME, "article").find_element(By.TAG_NAME, "p").text
    main_vote = main_board.find_element(By.CLASS_NAME, "article").find_element(By.CLASS_NAME, "vote").text

    reply_list = []
    #코멘트들을 담고있는 comments 클래스에서 article 태그들을 추출
    for reply in main_board.find_element(By.CLASS_NAME, "comments").find_elements(By.TAG_NAME, "article"):
        
        #대댓글 여부 체크
        if reply.get_attribute("class") == 'parent':
            reply_text = reply.find_element(By.TAG_NAME, "p").text 

        #대댓글일 경우 앞에 탭 문자 추가
        else:
            reply_text = "\t" + reply.find_element(By.TAG_NAME, "p").text

        reply_author = reply.find_element(By.TAG_NAME, "h3").text
        
        reply_time = reply.find_element(By.TAG_NAME, "time").text
        
        reply_vote = reply.find_element(By.CLASS_NAME, "vote.commentvote").get_attribute('textContent')

        reply_list.append([id, reply_author, reply_time, reply_text, reply_vote])


    return [main_text, main_vote], reply_list



if __name__ == '__main__':

    service = Service(executable_path='./driver/chromedriver.exe')

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(service = service, options=chrome_options)
    ##################################################################

    #db 생성
    con = sqlite3.connect("./data.db")

    #db 테이블 생성
    set_db(con)

    for page in range(580, 1000):
        driver.get("https://everytime.kr/hotarticle/p/" + str(page))

        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "boardname")))
        
        #element = wait.until(EC.presence_of_all_elements_located(By.CLASS_NAME, "wrap.articles"))
        article_wrap = driver.find_element(By.CLASS_NAME, "wrap.articles")
        
        link_list = []
        for article in article_wrap.find_elements(By.CLASS_NAME, "article"):
            
            try:
                author = article.find_element(By.TAG_NAME, "h3").text
            except:
                author = ''

            try:
                title = article.find_element(By.TAG_NAME, "h2").text
            except:
                title = ''

            try:
                board = article.find_element(By.CLASS_NAME, "boardname").text
            except:
                board = ''
            try:
                date = process_datetime_string(article.find_element(By.TAG_NAME, "time").text)
            except:
                date = ''
            
            link = article.get_attribute('href')

            #링크의 마지막 난수를 id로 삼음
            id = link.split("/")[-1]

            #print(author, title, board, date, vote, link)
            link_list.append([id, author, date, board, title, link])
        

        for link in link_list:
            
            cur = con.cursor()
            
            cur.execute("SELECT * FROM Reply WHERE ID = '" + link[0] + "'")

            #이미 저장되지 않은 본문만을 저장하도록 함.
            if len(cur.fetchall()) != 0:
                
                print(link[0], "이미 존재하는 본문")
                continue

            #본문으로 이동
            driver.get(link.pop())
            
            main_list, reply_list = get_page(link[0])

            db_insert(con, link + main_list, reply_list)

            #무작위 대기
            time.sleep(1 + random.randint(1, 100)/100)
            


            

