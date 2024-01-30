import sqlite3


con = sqlite3.connect("data.db")  # 데이터베이스 파일명 또는 경로를 적절히 수정하세요
cur = con.cursor()
cur.execute("SELECT Main FROM Reply")

total = 0
for line in cur.fetchall():

    #print(line[0].strip())
    total += len(line[0].strip().split())

print(total)
