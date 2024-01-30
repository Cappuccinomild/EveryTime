import sqlite3

con = sqlite3.connect("./data.db")

cur = con.cursor()

cur.execute("SELECT * FROM Reply MainText WHERE ID = ID")

id_set = set()

for line in cur.fetchall():

    print(line)



'''  
    if None in line:
        id_set.add(line[0])

print(id_set)
for id in id_set:
    cur.execute("DELETE FROM MainText WHERE ID = '" + id +"'")        
    cur.execute("DELETE FROM Reply WHERE ID = '" + id +"'")        

con.commit()
'''
con.close()