import numpy as np
import pandas as pd
import sqlite3

def split_text(line):
    return [sentence for sentence in line.split('\n') if sentence.strip()]


def extract_line(ID, keyword):

    #db 연결
    con = sqlite3.connect("./data.db")

    cur = con.cursor()

    df_col = ['검색어', 'ID', '작성자', '일자', '게시판', '추천수', '출처', '문장', '제목', '본문', '댓글']
    df_result = pd.DataFrame(columns = df_col)

    #본문에 키워드를 포함하는 ID 추출
    cur.execute("SELECT * FROM MainText WHERE ID = '" + ID +"'")
    
    #TABLE MainText(ID TEXT, Author TEXT, Date TEXT, Board TEXT, Title TEXT, Main TEXT, Vote INTEAGER);")
    #TABLE Reply(ID TEXT, Author TEXT, Date TEXT, Main TEXT, Vote INTEAGER);")
    maintext_data = cur.fetchall()
    for ID, author, date, board, title, main, vote in maintext_data:
        
        #댓글정보 추출
        cur.execute("SELECT * FROM Reply WHERE ID = '" + ID +"'")
        reply_data = cur.fetchall()
        reply_union = ''
        
        #댓글정보를 ' '로 구분해 union에 합침
        for ID, reply_author, reply_date, reply_main, reply_vote in reply_data:            
            reply_vote = str(reply_vote)
            reply_union += ' '.join([reply_author, reply_date, reply_main, reply_vote]) + "\n"

        flag = False
        #본문을 줄바꿈 기준으로 키워드 탐색
        for text in split_text(main):
            col = [keyword, ID, author, date, board, vote, '본문', text, title, main, reply_union]

            #존재한다면
            if keyword in text:
                
                if flag:
                    col[-2] = ''
                    col[-1] = ''
                
                df_result = pd.concat([df_result, pd.DataFrame(data = [col], columns = df_col)])
                flag = False


        #댓글별로 키워드 탐색
        for reply in reply_data:

            for text in split_text(reply[3]):
                col = [keyword, ID, author, date, board, vote, '댓글', text, title, main, reply_union]

                #존재한다면
                if keyword in text:
                    if flag:
                        col[-2] = ''
                        col[-1] = ''
                
                    df_result = pd.concat([df_result, pd.DataFrame(data = [col], columns = df_col)])
                    flag = False
    
    con.close()

    return df_result

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


if __name__ == "__main__":
    
    #검색어 읽어오기
    keyword_list = pd.read_excel("input.xlsx")

    keyword_list = list(keyword_list['검색어'])
    
    df_col = ['검색어', 'ID', '작성자', '일자', '게시판', '추천수', '출처', '문장', '제목', '본문', '댓글']
    df_result = pd.DataFrame(columns = df_col)
    
    for keyword in keyword_list:
        for id in read_id(keyword):
            df_result = pd.concat([df_result, extract_line(id, keyword)])
    
    df_result.to_excel("검색결과.xlsx", index = False)



    
