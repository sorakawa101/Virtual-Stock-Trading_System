import streamlit as st
import pandas as pd
import numpy as np

import functions.func_common as fc
import functions.func_common2 as fc2
import functions.func_index as fi

# NOTE 内容的には，Mypage兼，サイト訪問者への説明ページ


def index_page():
    # ページ設定
    fc.set_page_config()
    # Cookieにsession_state_usernameを保持
    fc2.setUsername()
    # タイトル
    fc.set_page_title("index")


# * サイドバー
def index_sidebar():
    with st.sidebar:
        st.header("ユーザー名：")
        # ログイン情報からユーザー名を取得
        fi.set_username(fi.get_username())

        st.header("最終売買日付：")
        st.write(fi.get_last_trading_date(fi.get_username()))

        # ログアウトボタン配置＆ログアウト実行
        fc2.put_logout_button()


# * メインコンテンツ①
# NOTE サイト訪問者へ向けてサイト・ページ説明を行うコンテンツ
def index_main_content1():
    fi.set_page_explanation()

# * メインコンテンツ②
# NOTE 売買活動のアクティブ状況を表示するコンテンツ（GithubのContribution的な）
# NOTE 具体的には，横軸日付，縦軸売買株数で，Scatterでその日の売買株数を企業ごとに可視化する
def index_main_content2():
    fi.set_purchase_contribution()


# * メインコンテンツ③
# NOTE 今回の開発について紹介するコンテンツ
# NOTE 具体的には，開発概要，担当，メンバー紹介など
def index_main_content3():
    nodes = []
    edges = []
    fi.set_development_explanation(nodes, edges)


# * メイン関数（関数まとめ）
def main():
    index_page()
    index_sidebar()
    index_main_content1()
    index_main_content2()
    index_main_content3()


# * 実行
if __name__ == "__main__":
    main()
