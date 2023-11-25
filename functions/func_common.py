import streamlit as st
import pandas as pd
import pymysql.cursors


# ページ設定
def set_page_config():
    st.set_page_config(
        page_title="Virtual Stock Trading System",
        page_icon="📈",
        layout="wide",
    )
    _set_sidebar()

# ページ（indexなど）を引数として，ページタイトルをセットする関数
def set_page_title(page):
    page_dic = {
        "login-home": "VSTS Login",
        "index": "MyPage",
        "graph": "Stock Data Analysis",
        "purchase-history": "Trade History",
        "purchase-system": "🪙 Trade Page",
    }
    if page in page_dic:
        page_title = page_dic[page]
    else:
        page_title = "New Page"

    st.title(page_title)

def _set_sidebar():
    #サイドバーからlogin-homeの選択肢をなくす処理↓
    css = """
    <style>
    [data-testid="stSidebarNav"]>ul>*:first-child {visibility: hidden; width:0; height:0;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# MySQLとの接続を得る関数
def get_connection_to_MySQL():
    connection = pymysql.connect(
        host=st.secrets["SQL_HOST"],
        port=st.secrets["SQL_PORT"],
        user=st.secrets["SQL_USER"],
        password=st.secrets["SQL_PASSWORD"],
        db=st.secrets["SQL_DB"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


# companyの全データ取得 辞書型 in List
def company_data():
    connection = get_connection_to_MySQL()

    with connection:
        with connection.cursor() as cursor:
            # データ読み込み
            sql = "SELECT `Code`, `Company` FROM `companys`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return pd.DataFrame(result).set_index("Code")


# test = company_data()  # テスト用
# print(test.shape)  # テスト用
# print(test[4251:4252])  # テスト用


# sessionIDからユーザー名を取得する関数
def get_username(sessionID):
    connection = get_connection_to_MySQL()

    with connection:
        with connection.cursor() as cursor:
            # sessionテーブルに登録されている値を全て抽出
            sql = "SELECT * FROM `session` WHERE `Id` = %s" #ここでエラーが出ているみたいだが、直し方が分からなかった。なぜか正常に動作はしている。
            cursor.execute(sql, (sessionID))
            result = cursor.fetchall()

    data = pd.DataFrame(result)

    if data.empty:
        return ""
    else:
        return data["Name"]
