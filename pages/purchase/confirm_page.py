import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import time
import pandas_datareader.stooq as web

import functions.func_common as fc
import functions.func_common as fc2
import functions.func_purchase as fp
# import sys
# sys.path.append("../../functions")
# import func_common as fc

# 確認ページ(本体)
def main_confirm(user_name, df_buy, df_sell):
	col1_1, col1_2, col1_3 = st.columns((1,5,1))
	with col1_1:
		pass
	with col1_2:
		# タイトル
		fc.set_page_title("purchase-system")
		# st.title("🪙 Trade Page")
		# st.markdown("---")

		st.warning('まだご注文は完了していません')
		st.markdown("---")

		st.subheader('購入株一覧')
		# 見やすいようにstr型に変化
		df_buy['企業コード'] = df_buy['企業コード'].astype(str)
		# Dataframeを表示
		st.dataframe(df_buy, use_container_width=True)

		st.subheader('売却株一覧')
		# 見やすいようにstr型に変化
		df_sell['企業コード'] = df_sell['企業コード'].astype(str)
		# Dataframeを表示
		st.dataframe(df_sell, use_container_width=True)

		st.markdown("---")
		# 画面の中央に文字を表示
		st.write("<h3 style='text-align: center;'>上記の内容でよろしいですか？</h2>", unsafe_allow_html=True)
		st.markdown("")
		col2_1, button1, col2_2, button2, col2_3 = st.columns((2.4,2,0.5,2,2))
		with col2_1:
			pass
		with button1:
			yes_button = st.button('はい')
			
		with col2_2:
			pass
		with button2:
			no_button = st.button('いいえ')
			if no_button:
				reset_session(0)
				st.experimental_rerun()
		with col2_3:
			pass

		if yes_button:
			progress_text = "売買しています。少々お待ちください。"
			my_bar = st.progress(0, text=progress_text)

			for percent_complete in range(100):
				time.sleep(0.005)
				my_bar.progress(percent_complete + 1, text=progress_text)
			
			# DBに登録
			db_reg = db_registrasion(user_name, df_buy, df_sell)
			if db_reg:
				layer_session(2)
				# print(st.session_state.layer)
				st.experimental_rerun()
			else:
				st.error('エラー: 株を売買できませんでした。すみませんが、最初からやり直してください。(3秒後にTOPに戻ります)')
				time.sleep(3)
				reset_session(0)
				st.experimental_rerun()
	with col1_3:
		pass


### ページ管理
# layer=0 : 売買main, layer=1: 確認画面main, layer=2:完了画面main
def layer_session(layer = 0):
	st.session_state.layer = layer

# ページリセット
def reset_session(layer = 0):

	st.session_state.count_buy = 0
	st.session_state.count_sell = 0
	st.session_state.df_stock = 0

	for i in range(1, 6):
		st.session_state[f"select_code_buy{i}"] = 0
		st.session_state[f"select_company_buy{i}"] = ''
		st.session_state[f"select_code_sell{i}"] = 0
		st.session_state[f"select_company_sell{i}"] = ''
		st.session_state[f"pre_code_buy{i}"] = 0
		st.session_state[f"pre_code_sell{i}"] = 0

	layer_session(layer)

# ページ設定
def trade_Page():
    # ページ設定
    fc.set_page_config()

### 株価の取得
def get_stock_now(code, days):
    #表記：'%year-%month-%day
    enddate = days
	# 月曜日の場合、金曜日の値までしか取得できないため
	# その他祝日も考慮して過去１週間分を取得
    startdate = enddate + dt.timedelta(days=-7)
    stock_code = str(code) + '.JP'

    df = web.StooqDailyReader(stock_code, start=startdate, end=enddate)
    df = df.read()
    return df

# 企業名の削除
def _delete_company_low(df, column):
	df = df.drop(columns = [column])
	return df

# 現在の株価を取得し、既存のDFに現在株価, 購入価格(現在株価＊株数量)を追加
def _df_add_stock(df):
	df= _delete_company_low(df,'企業名')
	stock_price_list = []
	sum_price_list = []
	# dfに入っている企業コードから株価を取得し、リストの末尾に入れる
	for i in range(len(df)):
		stock_code = df['企業コード'].iloc[i]
		date = df['取引日付'].iloc[i].strftime('%Y-%m-%d')
		# str型をDatetime型に変換
		date = dt.datetime.strptime(date, '%Y-%m-%d').date()
		amount = df['株数量'].iloc[i]
		# 株価を取得し、リストに追加
		stock_price = get_stock_now(stock_code,date)
		stock_price = stock_price['Close'].iloc[0]
		stock_price_list.append(stock_price)

		# 購入価格をリストに追加
		sum_price = stock_price * float(amount)
		sum_price_list.append(sum_price)
	
	# リストの内容をdfに追加
	df.insert(loc=3, column="現在株価", value = stock_price_list)
	df.insert(loc=4, column="購入価格", value = sum_price_list)
	return df


# DB側:Dataframeの内容：colums=企業コード, 株数量, 売買状況, 現在株価, 購入価格, 取引日付

# DBに登録するためのDataframeの作成
def _df_create_registration(df_buy, df_sell):
	# df_buyが空だった場合: df_sellのみを登録
	# df_sellが空だった場合: df_buyのみを登録
	if df_buy.empty:
		return df_sell
	elif df_sell.empty:
		return df_buy
	else:
		df_registration = pd.concat([df_buy, df_sell], axis=0)
		# df_registration = _delete_company_low(df_registration,'企業名')
		print(df_registration)
		return df_registration

# DBに登録
def db_registrasion(user_name, df_buy, df_sell):
	# 購入用、売却用のDataframeに現在株価、購入価格を追加
	df_buy = _df_add_stock(df_buy)
	df_sell = _df_add_stock(df_sell)

	# 購入用、売却用のDataframeを１つに統合
	df_reg = _df_create_registration(df_buy, df_sell)

	#登録内容確認用
	# registrasion = False
	# print(df_reg)
	registrasion = fp.purchase_registration(user_name, df_reg)
	return registrasion