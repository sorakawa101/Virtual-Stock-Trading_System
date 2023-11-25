import re
import pymysql.cursors
import streamlit as st
import datetime
import pandas as pd
import functions.func_common as co

def isMail(str):
    # メールアドレスかどうか判定 boolean
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, str) is not None


def all_data():
    # 全データ取得 辞書型 in List
    connection = co.get_connection_to_MySQL()
    
    with connection:
        with connection.cursor() as cursor:
            # データ読み込み
            sql = "SELECT `Name`, `Mail`, `Password` FROM `users`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result


def is_user_exist(username):
    # ユーザ名とパスワードが一致するかどうか判定 boolean
    datas = all_data()
    if isMail(username):
        key = "Mail"
    else:
        key = "Name"
    for d in datas:
        if d[key] == username:
            return d["Password"]
    return ""
#is_user_exist("testuser", "testpassword")  # テスト用
#is_user_exist("testmail@gmail.com", "testpassword")  # テスト用
#is_user_exist("test2", "testtest")  # テスト用


def is_mail_exist(mail):
    # メールアドレスがすでに使われているかどうか判定 boolean
    # 使われてなければFalseを返す
    datas = all_data()
    for d in datas:
        if d["Mail"] == mail:
            return True
    return False
#is_mail_exist("test@icloud.com")  # テスト用


def insert_user(username, password, mail):
    # ユーザ名が使われていないか確認し，使われていなければ登録 boolean
    datas = all_data()
    for d in datas:
        if d["Name"] == username:
            return False
    # 登録する関数
    # 全データ取得 辞書型 in List
    connection = co.get_connection_to_MySQL()
    
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            # usersという表にemailとpasswordを追加 値は文字型
            sql = "INSERT INTO `users` (`Name`, `Mail`, `Password`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, mail, password))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    return True
#insert_user("test4", "test4pass", "test4@gmail.com")  # テスト用


def is_user_mail_exist(username):
    # ユーザ名,メールアドレスが登録済みか確認 [boolean, string]
    datas = all_data()
    if isMail(username):
        key = "Mail"
    else:
        key = "Name"
    for i in range(len(datas)):
        # 登録済みだった場合
        if datas[i][key] == username:
            # 入力がメールアドレス
            if key == "Mail":
                return [True, username]
            # 入力がユーザ名だったらメールアドレスを取得
            else:
                usermail = datas[i]["Mail"]
                return [True, usermail]
            
    return [False, ""]
#print(is_user_mail_exist("test3@gmail.com"))  # テスト用
#print(is_user_mail_exist("test2"))  # テスト用
#print(is_user_mail_exist("dummy@gmail.com"))  # テスト用


def insert_changed_password(mail, password):
    # メールアドレスを元にパスワードの変更 boolean
    datas = all_data()
    for d in datas:
        if d["Mail"] == mail:
            connection = co.get_connection_to_MySQL()
            
            with connection:
                with connection.cursor() as cursor:
                    sql = "SELECT `Name`, `Mail`, `Password` FROM `users`"
                    cursor.execute(sql)
                    sql = "UPDATE `users` SET `Password` = %s WHERE `Mail` = %s"
                    cursor.execute(sql, (password, mail))
                connection.commit()
                return True
    return False
#insert_changed_password("test3@gmail.com", "updatedpass")  # テスト用
#insert_changed_password("dummy@gmail.com", "updatedpass")  # テスト用

def insert_session(sessionID, username, expire):
    # セッションIDとユーザー名、有効期限をDBに保存
    # ユーザー名は複数あってもそのまま保存して良い
    connection = co.get_connection_to_MySQL()
    
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            # sessionテーブルにsessionID, username, expireを追加 
            sql = "INSERT INTO `session` (`Name`, `Id`, `Expire`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, sessionID, expire))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

    return 0
#insert_session("asdfghjkl","Erika",datetime.datetime.now())
#insert_session("zxcvbnm","Erika",datetime.datetime.now())
#insert_session("qwertyuiop","Erika","2023-11-16 12:00:00")

def delete_session(username):
    # sessionテーブルから有効期限切れのデータを削除する関数(return値はなし)
    connection = co.get_connection_to_MySQL()
    
    with connection:
            with connection.cursor() as cursor:
                # sessionテーブルから期限切れのデータを削除 
                sql = "DELETE  FROM `session` WHERE `Name` = %s AND `Expire` <= %s"
                cursor.execute(sql, (username, datetime.datetime.now()))
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

# delete_session("Erika") 
               
def is_name_expire_exist(username):
    # sessionテーブル内にユーザー名とsessionIDが有効かどうかを判別する関数(true or falseで返す)
    connection = co.get_connection_to_MySQL()
    
    with connection:
            with connection.cursor() as cursor:
                # sessionテーブルからユーザー名と期限が切れていないデータを取り出す
                sql = "SELECT *  FROM `session` WHERE `Name` = %s AND `Expire` > %s"
                cursor.execute(sql, (username, datetime.datetime.now()))
                result =  cursor.fetchall()
    
    data = pd.DataFrame(result)
    
    if data.empty: 
        return False
    else:
        return True

# print(is_name_expire_exist("Erika"))           
            
   
def check_session(sessionID):
    # 引数のsessionIDが有効かどうかを判断する関数(return値は[bool, 名前])
    
    # sessionIDからユーザー名を検索
    name = co.get_username(sessionID)
    
    if not len(name)==0: # ユーザー名が存在するかを確認 ←元のコードだと存在しないときにエラーがでたので、修正
        # sessionIDの有効期限が切れているものを削除し、有効であるものがテーブル内にまだあるかのかを確認
        delete_session(name[0])
        bool = is_name_expire_exist(name[0])
    else:
        bool = False
    
    # 判定結果と名前をリスト型で返す
    if bool == True:
        return [bool, name[0]]
    else:
        return [bool, ""]    
    
# print(check_session("qwertyuiop"))    