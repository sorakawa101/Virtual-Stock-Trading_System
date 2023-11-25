# 所持株表示ページ
import streamlit as st
import datetime
import pandas as pd
from pandas_datareader import data
import numpy as np

import functions.func_purchase as fp
from pages.purchase import purchase_show_func


def purchase_show_main():
    st.title("所持株一覧")

    tab1, tab2 = st.tabs(["所持株", "売買履歴"])

    with tab1:
        purchase_pl_df()

    with tab2:
        b = 0

def purchase_pl_df():
    #所持株と損益見込みのdfを表示
    #所持株dfの列名
    #Code, Count, Price, Date

    # holdstock_df = fp.stock_holding(st.session_state.username)




    comment = '''
    if holdstock_df.empty:
        st.write("現在所持している株がありません")
    
    else:
        pl_df = purchase_show_func.stock_pl(holdstock_df)

        #証券コード順にソート
        pl_df_s = (pl_df.sort_values('Code')).reset_index()

        companies = pd.DataFrame() #ここに証券コードと企業の対応一覧
        limited_comp = companies.filter(items = pl_df_s['Code'])

        #会社名の列を追加
        pl_df.insert(1, '会社名', '')
        for i in range(len(pl_df)):
            pl_df['会社名'][i] = limited_comp['Company']

        st.table(pl_df)
        #st.bar_chart(pl_df['保有株の価値'], x='企業', y='金額')
        '''
    
    #ダミーのデータ
    #Code, Count, Price, Date
    df_test = pd.DataFrame({'Code':     [9672, 4216, 7936, 5032],
                            'Count':    [200, 100, 100, 200],
                            'Price':    [-600000, -350000, -200000, -400000],
                            'Date':     ['2023-10-27', '2023-10-27', '2023-11-03', '2023-11-03']})
    
    pl_df = purchase_show_func.stock_pl(df_test)

    #証券コード順にソート
    pl_df_s = (pl_df.sort_values('Code')).reset_index(drop=True)

    companies = pd.DataFrame() #ここに証券コードと企業の対応一覧
    limited_comp = companies.filter(items = pl_df_s['Code'])

    comment = '''
    #会社名の列を追加
    pl_df_s.insert(1, '会社名', '')
    for i in range(len(pl_df_s)):
        pl_df_s['会社名'][i] = limited_comp['Company']'''
    
    pl_df_s = pl_df_s.rename(columns={'Code': '証券コード', 'Count': '所持株数', 'Price': '購入時の価格', 'Date': '購入日'})
    
    comment = '''
    cols = st.columns(len(pl_df_s))
    names = pl_df_s['会社名']
    i = 0
    for name, col in zip(names, cols):
        value = pl_df_s['保有株の価値'][i]
        delta = pl_df_s['購入時の価格'][i] - pl_df_s['保有株の価値'][i]
        col.metric(label=name, value=f"{value}円", delta=f"{delta}円")
        i += 1
    '''
    
    st.subheader("現時点の損益見込み")
    st.table(pl_df_s)


def purchase_df_graph(df, column_name):
    st.bar_chart(df[column_name])


if __name__ == "__main__":
    purchase_show_main()
