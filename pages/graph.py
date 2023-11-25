import streamlit as st
import pandas as pd
from pandas_datareader import data
import numpy as np
import mplfinance as mpf
from PIL import Image
from datetime import datetime

from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

#画像の名前と場所を保存するリスト
global tab_titles
tab_titles = {}

def del_value(list, value):
    list.remove(value)

#タブに追加する画像の名前と場所を登録する関数．
#画像を作成したタイミングで呼び出す
def add_tab(name, img):
    tab_titles[name] = img
    
#タブの作成
#画像の登録が終わったら一度だけ実行
def mk_tabs():
    l = []
    i = 0
    for key, value in tab_titles.items():
        l.append(key)
    tabs = st.tabs(l)
    for key, value in tab_titles.items():
        img = Image.open(value)
        with tabs[i]:
            st.image(img, caption=key,use_column_width=True)
        i = i+1

def calc_timedelta(ststart, stend):
    dtstart = datetime(ststart.year, ststart.month, ststart.day)
    dtend   = datetime(  stend.year,   stend.month,   stend.day)
    delta   = dtend - dtstart
    deltad  = delta.days
    return deltad
                

# ページ設定
st.set_page_config(
    page_title="Virtual Stock Trading System",
    page_icon="🧊",
    layout="wide",
)

st.title("Virtual Stock Trading System")
st.header("銘柄名から銘柄コードを検索")
#csvファイル読み込みの前処理
csvfile_path = './pages/data/stocklist.csv'
df_name = pd.read_csv(csvfile_path)
name = st.text_input('銘柄名を入力')


# 初めての実行時にsession_stateを初期化
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False
if 'previous_name' not in st.session_state:
    st.session_state.previous_name = ""

# テキスト入力が変わった場合、button_clickedをFalseにリセット
if st.session_state.previous_name != name:
    st.session_state.button_clicked = False
    st.session_state.previous_name = name

# ボタンがクリックされたときにsession_stateを更新
if st.button("銘柄名で検索", key=0):
    st.session_state.button_clicked = True
    
# session_stateの状態に基づいて表を表示
if st.session_state.button_clicked:
    df_part = df_name[df_name['銘柄名'].str.contains(name)]
    gd = GridOptionsBuilder.from_dataframe(df_part)
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    gridoptions = gd.build()
    grid_table = AgGrid(df_part, gridOptions=gridoptions, 
                        update_mode=GridUpdateMode.SELECTION_CHANGED, key=1)
    st.write('## Selected')
    selected_row = grid_table["selected_rows"]
    st.dataframe(selected_row)# セッション内でリストをキャッシュする
@st.cache(allow_output_mutation=True)
def get_stock_codes():
    return []

# 銘柄コードを取得
stock_codes = get_stock_codes()


st.header("銘柄コードを描画リストに追加")

# "銘柄コードを追加" ボタンが押されたらテキストボックスを表示
new_code = st.text_input("新しい銘柄コードを入力してください:")
if st.button("追加",key=2):
    i = 0
    for code in stock_codes:
        if code == new_code:
            i = 1
    if i == 0:
        stock_codes.append(new_code)
st.write("登録された銘柄コード:")
selected =  st.selectbox('codes', stock_codes, key=100)
if st.button("選択された要素を削除",key=3):
    del_value(stock_codes, selected)
st.write(stock_codes)
    
start = st.date_input('開始日を指定')
end = st.date_input('終了日を指定')
if st.button("グラフ描画", key=4):

    #start = datetime.strptime(start, '%Y%m%d')
    #end = datetime.strptime(end, '%Y%m%d')
    td = calc_timedelta(start, end)
    st.write(str(td)+"日の描画期間")
    flag_macd = False
    flag_ichimoku = False
    flag_rsi = False

    if(td>26):
        st.write("描画日数が26日より長いためMACDが描画できます")
        flag_macd = True
    else:
        st.write("描画日数が26日以下のためMACDが描画できません")
    if(td>52):
        st.write("描画日数が52日より長いため一目均衡表が描画できます")
        flag_ichimoku = True
    else:
        st.write("描画日数が52日以下のため一目均衡表が描画できません")
    if(td>14):
        st.write("描画日数が14日より長いためRSIが描画できます")
        flag_rsi = True
    else:
        st.write("描画日数が14日以下のためRSIが描画できません")

    for code in stock_codes:
        
        filename = 'pages/data/'+code+'.png'
        df = data.DataReader(code+'.JP', 'stooq', start, end)
        df = df.sort_index(ascending=True)

        # dfのインデックスを確認
        if not isinstance(df.index, pd.DatetimeIndex):
            # インデックスがDatetimeIndexでない場合、エラーを発生させる代わりに変換を試みます
            try:
                # インデックスをpd.to_datetimeを使用してDatetimeIndexに変換
                df.index = pd.to_datetime(df.index)
            except Exception as e:
                # 変換できない場合は、エラーメッセージを表示
                st.error(f"インデックスをDatetimeIndexに変換できませんでした。エラー: {e}")
                # 以降の処理をスキップ
                continue
        st.table(df)
        #並び順のソート
        df = df.sort_index()
        if(flag_macd):

            #MACDの計算
            exp12 = df['Close'].ewm(span=12, adjust=False).mean()
            exp26 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp12 - exp26
            # シグナル計算
            df['Signal'] = df['MACD'].rolling(window=9).mean()
            # ヒストグラム(MACD - シグナル)
            df['Hist'] = df['MACD'] - df['Signal']
        if(flag_ichimoku):

            #一目均衡表 9、26、52日間のMAX、MIN値の計算

            max_9 = df['High'].rolling(window=9, min_periods=1).max()
            min_9 = df['Low'].rolling(window=9, min_periods=1).min()

            max_26 = df['High'].rolling(window=26, min_periods=1).max()
            min_26 = df['Low'].rolling(window=26, min_periods=1).min()

            max_52 = df['High'].rolling(window=52).max()
            min_52 = df['Low'].rolling(window=52).min()

            # ５本線の計算

            df['tenkan'] = (max_9 + min_9)/2
            df['base'] = (max_26 + min_26)/2
            df['senkou1'] = ((df['tenkan'] + df['base'])/2).iloc[:-26]
            df['senkou2'] = ((max_52 + min_52)/2).iloc[:-26]
            df['chikou'] = df['Close'].iloc[:-26]
        if(flag_rsi):

            #RSI(相対力指数)
            # 終値の差分

            df_diff = df['Close'].diff()

            # 値上がり幅と値下がり幅

            df_up, df_down = df_diff.copy(), df_diff.copy()
            df_up[df_up < 0] = 0
            df_down[df_down > 0] = 0
            df_down = df_down * -1

            # 14日間の単純移動平均

            sim14_up = df_up.rolling(window=14).mean()
            sim14_down = df_down.rolling(window=14).mean()

            # RSI
            df['RSI'] = sim14_up / (sim14_up + sim14_down) * 100
        add_plot = []
        panel_num = 1
        if flag_macd:
            add_plot.extend([
                mpf.make_addplot(df['MACD'], color='m', panel=panel_num, secondary_y=False),
                mpf.make_addplot(df['Signal'], color='c', panel=panel_num, secondary_y=False),
                mpf.make_addplot(df['Hist'], type='bar', color='g', panel=panel_num, secondary_y=True),
            ])
            panel_num+=1

        if flag_ichimoku:
            add_plot.extend([
                mpf.make_addplot(df['base'], color='black'),
                mpf.make_addplot(df['tenkan'], color='red'),
                mpf.make_addplot(df['chikou'], color='darkorange'),
            ])

        if flag_rsi:
            add_plot.append(
                mpf.make_addplot(df['RSI'], panel=panel_num),
            )
            panel_num+=1
        # データをチェックする
        if df.empty or df.isnull().values.any():
            st.write("データフレームが空、またはNaN値を含んでいます。")
        else:
            # NaN値を前の有効なデータで埋める
            df.fillna(method='ffill', inplace=True)
        # 有効なデータのみをプロットする
        try:
            if add_plot:
                st.write("add_plotリストは空ではありません")
                mpf.plot(df, title='\n' + code, type='candle', mav=(5, 25), volume=True, addplot=add_plot, volume_panel=panel_num, savefig=filename)
            else:
                st.write("add_plotリストが空です")
                mpf.plot(df, title='\n' + code, type='candle', mav=(5, 25), volume=True,volume_panel=panel_num, savefig=filename)
            
        except ValueError as e:
            st.write(f"プロット中にエラーが発生しました: {e}")
                
        #画像のサイズ取得
        img = Image.open(filename)
        #st.image(img, caption=filename,use_column_width=True)
        add_tab(code, filename)
    mk_tabs()
    

"""
Run Command is:
```
streamlit run index.py
```
現在は日本株にしか対応していません．
"""
