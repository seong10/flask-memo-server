import mysql.connector

def get_connection() :
    connection = mysql.connector.connect(
        host = 'yh-db.clmt07jbjcoe.ap-northeast-2.rds.amazonaws.com',
        database = 'memo_db',
        user = 'memo_user',
        # 어드민 유저로 하면 안됨
        password = 'memo1234'
    )
    return connection