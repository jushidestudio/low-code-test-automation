DB接続（SQLiteを手動で使う場合）
def get_testcases():
     conn = sqlite3.connect(app.instance_path + '/testcases.db')
     conn.row_factory = sqlite3.Row
     cursor = conn.cursor()
     cursor.execute('SELECT * FROM testcases')
     rows = cursor.fetchall()
     conn.close()
     return rows
