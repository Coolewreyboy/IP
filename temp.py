import sqlite3


conn = sqlite3.connect('individual_project.db')
cursor = conn.cursor()
f = open('words.txt', 'r', encoding='utf-8')
for line in f:
    line = line.strip()
    print(line)
    res = cursor.execute("""INSERT INTO words_task_1(word) VALUES(?)""", (line,))
conn.commit()
conn.close()
f.close()