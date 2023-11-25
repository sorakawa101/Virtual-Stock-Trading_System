import pymysql.cursors
import streamlit as st
import pandas as pd

def company_data():
    # 全データ取得 辞書型 in List
    connection = pymysql.connect(host=st.secrets["SQL_HOST"],
                                 port=st.secrets["SQL_PORT"],
                                 user=st.secrets["SQL_USER"],
                                 password=st.secrets["SQL_PASSWORD"],
                                 db=st.secrets["SQL_DB"],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            # データ読み込み
            sql = "SELECT `Code`, `Company` FROM `companys`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return pd.DataFrame(result).set_index("Code")
        
