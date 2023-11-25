import re
import pymysql.cursors
import json
import pandas as pd
import streamlit as st
import functions.func_common as fc


def purchase_history(username):
    # 売買状況を返す関数
    # DB:VSTS, table:history

    print(st.secrets["SQL_HOST"])
    connection = fc.get_connection_to_MySQL()
    with connection:
        with connection.cursor() as cursor:
            # usernameのデータのみを抽出
            sql = "SELECT * FROM `history` WHERE `Name` = %s"
            cursor.execute(sql, (username))
            result = cursor.fetchall()
    
    # resultのデータをdataframe変換
    # 辞書型だけど、リストの長さが同じであれば変換可能
    dataframe = pd.DataFrame(result)
    return dataframe
#test = purchase_history("AAA") # テスト用


def code_history(username):
    # userが扱った銘柄コード一覧を返す関数

    history = purchase_history(username)

    # usernameのhistoryがなければ空を作る
    if history.empty:
        code_list = pd.DataFrame({"Code":[]})
    else:
        # historyからcodeだけ取り出す
        code_list = history[["Code"]]

        # 重複を削除する
        code_list = code_list.drop_duplicates(subset="Code")

    return code_list
#test = code_history("natori") # テスト用


def stock_holding(username):
    # ユーザーの持ち株状況を返す関数

    # 売買履歴を持ってくる
    history = purchase_history(username)
    
    # usernameのhistoryがなければ空を作る
    if history.empty:
        dataframe = pd.DataFrame({"Code":[], "Count":[], "Price":[], "Date":[]})
    else:
        # 銘柄コード,株数,取引した最終日付だけを取り出す
        data = history[["Code","Count","Price","Date"]]

        # 銘柄コード一覧と売買履歴の銘柄コードが一致していたら銘柄コードの挿入、株数と取引日付を更新
        list_code = []
        list_count = []
        list_price = []
        list_date = []

        for _, row in data.iterrows():
            # 現在の行の銘柄コードがすでに探索済みの場合
            if row["Code"] in list_code:
                index = list_code.index(row["Code"])
                list_count[index] += row["Count"]  # Amountを加算
                list_price[index] += row["Price"]  # Priceを加算
                list_date[index] = row["Date"]       # Dateを上書き
            # 現在の行の銘柄コードが新規の場合
            else:
                list_code.append(row["Code"])
                list_count.append(row["Count"])
                list_price.append(row["Price"])
                list_date.append(row["Date"])

        dataframe = pd.DataFrame({"Code":list_code, "Count":list_count, "Price":list_price, "Date":list_date})

    return dataframe
#test = stock_holding("natori") #テスト用

def company_name(company_code):
    # 企業コードから銘柄名を出力する関数　int -> Srting
    connection = fc.get_connection_to_MySQL()
    
    with connection:
        with connection.cursor() as cursor:
            # companysテーブルに登録されていて指定のCodeに合致する値を抽出
            sql = "SELECT * FROM `companys` WHERE `Code` = %s"
            cursor.execute(sql, (company_code))
            result = cursor.fetchall()
    # 1つに決まる場合はエラーなし
    if len(result) == 1:
        return result[0]["Company"]
    # 0個or2つ以上の場合はエラーあり
    else:
        return ""

def company_code(company_name):
    # 銘柄名から企業コードを出力する関数　String -> int
    connection = fc.get_connection_to_MySQL()
    
    with connection:
        with connection.cursor() as cursor:
            # companysテーブルに登録されていて指定のCodeに合致する値を抽出
            sql = "SELECT * FROM `companys` WHERE `Company` = %s"
            cursor.execute(sql, (company_name))
            result = cursor.fetchall()
    # 1つに決まる場合はエラーなし
    if len(result) == 1:
        return result[0]["Code"]
    # 0個or2つ以上の場合はエラーあり
    else:
        return 0

def purchase_registration(username, df):
    # Dataframeをhistoryに登録する関数
    # Dataframeの内容：colums=企業コード, 株数量, 売買状況, 現在株価, 購入価格, 取引日付
    l_df = df.values.tolist()
    for l in l_df:
        try:
            connection = fc.get_connection_to_MySQL()
    
            with connection:
                with connection.cursor() as cursor:
                    # Create a new record
                    sql = "INSERT INTO `history` (`Name`, `Code`, `Company`, `Count`, `Price`, `Date`) VALUES (%s, %s, %s, %s, %s, %s)"

                    # コードを間違えると登録できないようにした
                    companyname = company_name(l[0])
                    if companyname == "":
                        print("Error: wrong company code")
                        return False
                    else:
                        if l[2] == "sell":
                            # 売ったら株数は負，金額は正
                            cursor.execute(sql, (username, l[0], companyname, l[1], -l[4], l[5]))
                        else:
                            cursor.execute(sql, (username, l[0], companyname, l[1], l[4], l[5]))

                # connection is not autocommit by default. So you must commit to save
                # your changes.
                connection.commit()
        
        # エラーハンドリング
        except Exception as e:
            print("Error: " + str(e))
            return False
        
    return True
#df_test = pd.DataFrame({"Code":[9613, 456], "Count":[2, 3], "isPurchase": ["購入", "売却"], "CurrentStock": [100, 200], "Price": [200, 600], "Date":["2023-11-09 11:22:33", "2023-11-09 11:22:44"]})
#purchase_registration("natori", df_test)  # テスト用
    