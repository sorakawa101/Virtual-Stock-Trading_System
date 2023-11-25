import streamlit as st
import datetime
import pandas as pd
from pandas_datareader import data
import numpy as np

#想定されるつかいかた
#st.table(stock_pl(stock_his2hold(dictlist2df(売買履歴), dictlist2df(持ち株))))

def dictlist2df(dictlist):
    #DBから送られるのは辞書型のリストなのでこれをdfに変換する
    return pd.json_normalize(dictlist)

def re_indexing(df):
    #インデックス(行番号)振り直し
    return df.set_axis(list(range(len(df))))


def delete_rows(df, n_list):
    #特定の行(行番号のリストで指定)を削除する
    df = df.drop(n_list)
    df = re_indexing(df)
    #インデックス(行番号)振り直し(行を抜くと連番が崩れる)

    return df


def stock_his2hold(df_purchase_his, df_stock):
    #ある時点の持ち株とその時点以降の売買履歴から最新の持ち株データに直す

    if df_stock == None:
        df_stock = df_purchase_his[0:1]
        #持ち株がNoneのとき＝最初の時は，売買履歴の先頭行を初期値として持ち株dfに入れる

        df_purchase_his = delete_rows(df_purchase_his, [0])
        #この分岐の場合，売買履歴の先頭は既に持ち株に入っているので抜いてok
        print(df_stock)

    #df_stock = pd.DataFrame(np.arange(5).reshape(5,0),
    #                        columns=['username', 'code', 'amount', 'trans', 'date'])
    #dfの列名は仮


    for i in range(len(df_purchase_his)):
        #print(df_stock['code'])
        #print(df_purchase_his['code'][i])
        if df_purchase_his['code'][i] in df_stock['code'].values.tolist():
            #持ち株dfに既にある会社の株について，売買履歴にあった場合
            #df['列名']とするとSeries型になるので，df.values.tolist()でリストに変換する

            code_index = (df_stock['code'].values.tolist()).index(df_purchase_his['code'][i]) 
            #いま見ている企業の持ち株を保持しているdf_stockのindexを抽出

            df_stock['amount'][code_index] += df_purchase_his['amount'][i]
            df_stock['trans'][code_index] += df_purchase_his['trans'][i]
            #売買数と取引金額をそれぞれ足し合わせる

            df_stock['date'][code_index] = df_purchase_his['date'][i]
            #日付を最終取引の日にする？

        else:
            #持ち株dfにない会社の売買履歴があったとき

            df_stock = pd.concat([df_stock, df_purchase_his[i:i+1]])
            #売買履歴の当該行を持ち株dfに追加
            #concatの引数は連結したいdfどうしをリスト等にする
            df_stock = re_indexing(df_stock)

            print('recorded')
            print(df_stock)

    #足した結果amountが0になった株は持ち株から消す
    rec = []
    for i in range(len(df_stock)):
        if df_stock['amount'][i] == 0:
            rec.append(i)
            #該当行を記録
    
    df_stock = delete_rows(df_stock, rec)
    #該当行を削除

    return df_stock

#ここまでの関数当面使用予定なし

def stock_pl(df_stock):
    #最新の終値に基づく損得状況の可視化
    #df_stockはすでにあるユーザの持ち株のdf
    #dfのindex名
    #Code, Count, Price, Date

    df_stock_pl = df_stock #損益情報用にコピー

    #損益のための新しい項目(列)を増やす
    df_stock_pl['現在の株価(最新終値)'] = 0 #その会社の今の株価
    df_stock_pl['保有株の価値'] = 0 #株価×持っている株数＝持っている株の価値
    df_stock_pl['手数料'] = 0 #売値の0.5% * 1.1(消費税)
    df_stock_pl['受領金額'] = 0 #上２つの合算（手数料はマイナス）
    df_stock_pl['損益見込み'] = 0 #持ち株にあるその株にいくら使ったか(マイナス) + 上の値
    
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(1)
    oneweek_ago = yesterday - datetime.timedelta(6)
    #最大6連休なので最低7日取れば最新の終値がわかる(年末年始12/31~1/3に土日が接続した場合)
    
    for i in range(len(df_stock_pl)):
        #7日前〜昨日までの株価データの一番上ー>最新の終値
        df_nowvalue = data.DataReader(df_stock['Code'][i].astype(str) + '.JP', 'stooq', oneweek_ago, yesterday)

        df_stock_pl['現在の株価(最新終値)'][i] = df_nowvalue['Close'][0]
        df_stock_pl['保有株の価値'][i] = df_nowvalue['Close'][0] * df_stock_pl['Count'][i] #列名は仮定
        df_stock_pl['手数料'][i] = df_stock_pl['保有株の価値'][i] * 0.005 * 1.10
        df_stock_pl['受領金額'][i] = df_stock_pl['保有株の価値'][i] - df_stock_pl['手数料'][i]
        df_stock_pl['損益見込み'][i] = df_stock_pl['Price'][i] + df_stock_pl['受領金額'][i]

    return df_stock_pl


#以下テスト
#df1 = pd.DataFrame({'username': ['chimata', 'chimata', 'chimata', 'chimata', 'chimata'],
#                    'code': ['9672', '4216', '7936', '5032', '7951'],
#                    'amount': [300, 200, 200, 100, 200],
#                    'trans': [-1500000, -600000, -900000, -300000, -700000],
#                    'date': ['2023-10-04', '2023-10-04', '2023-10-27', '2023-10-27','2023-10-27']
#                    })


#st.table(df1)
#st.table(stock_his2hold(df1, None))
#st.table(stock_pl(stock_his2hold(df1, None)))

#print(df1)
#print(stock_pl(df1))
#print(stock_his2hold(df1, None))
#print(stock_pl(stock_his2hold(df1, None)))
        
