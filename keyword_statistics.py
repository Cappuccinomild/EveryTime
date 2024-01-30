import numpy as np
import pandas as pd
import sqlite3

def split_text(line):
    return [sentence for sentence in line.split('\n') if sentence.strip()]


def extract_line(ID, keyword):

    #db 연결
    con = sqlite3.connect("./data.db")

    cur = con.cursor()

    #본문에 키워드를 포함하는 ID 추출
    cur.execute("SELECT main FROM MainText WHERE ID = '" + ID +"'")
    
    #TABLE MainText(ID TEXT, Author TEXT, Date TEXT, Board TEXT, Title TEXT, Main TEXT, Vote INTEAGER);")
    #TABLE Reply(ID TEXT, Author TEXT, Date TEXT, Main TEXT, Vote INTEAGER);")
    maintext_data = cur.fetchall()
    found_main = len(maintext_data)
    used_main = 0
    for main in maintext_data:
        
        #본문을 줄바꿈 기준으로 키워드 탐색
        for text in split_text(main[0]):
            used_main += text.count(keyword)

    
    
    #댓글정보 추출
    cur.execute("SELECT main FROM Reply WHERE Main LIKE '%" + keyword +"%' AND ID = '" + ID + "'")
    reply_data = cur.fetchall()
    found_reply = len(reply_data)
    used_reply = 0

    #댓글별로 키워드 탐색
    for reply in reply_data:
        reply = reply[0]

        #본문을 줄바꿈 기준으로 키워드 탐색
        for text in split_text(reply):
            used_reply += text.count(keyword)

    
    con.close()

    return [found_main, found_reply, used_main, used_reply]

def read_id(keyword):
    #db 연결
    con = sqlite3.connect("./data.db")

    cur = con.cursor()

    #본문에 키워드를 포함하는 ID 추출
    cur.execute("SELECT ID FROM MainText WHERE Main LIKE '%" + keyword +"%'")
    
    id_set = set()

    for line in cur.fetchall():
        
        id_set.add(line[0])

    #댓글에 키워드를 포함하는 ID 추출
    cur.execute("SELECT ID FROM Reply WHERE Main LIKE '%" + keyword +"%'")

    for line in cur.fetchall():
        
        id_set.add(line[0])

    con.close()

    print(id_set)
    return id_set

def list_merge(a, b):
    for i in range(len(a)):
        a[i] = a[i] + b[i]

    return a

if __name__ == "__main__":
    
    #검색어 읽어오기
    keyword_list = pd.read_excel("input.xlsx")

    keyword_list = list(keyword_list['검색어'])
    
    df_col = ['키워드', '발견된 건', '발견된 본문', '발견된 댓글', '전체 사용횟수', '본문내 사용횟수', '댓글내 사용횟수']
    df_result = pd.DataFrame(columns = df_col, )

    #db 연결
    con = sqlite3.connect("./data.db")

    cur = con.cursor()

    cur.execute("SELECT count(*) FROM MainText")
    total_main = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM Reply")
    total_reply = cur.fetchone()[0]

    #첫 행에 전체 개수 입력
    df_result.loc[0] = ["전체 본문 수", total_main, "전체 댓글 수", total_reply, '','', '']

    for keyword in keyword_list:
        total_result = [0,0,0,0]
        for id in read_id(keyword):
            total_result = list_merge(total_result, extract_line(id, keyword))

        found_main, found_reply, used_main, used_reply = total_result

        col = [keyword, found_main + found_reply, found_main, found_reply, used_main + used_reply, used_main, used_reply]

        df_result = pd.concat([df_result, pd.DataFrame(data = [col], columns = df_col)])    
    
    
    df_result.to_excel("통계.xlsx", index = False)
