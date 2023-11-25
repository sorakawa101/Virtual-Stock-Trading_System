# 売買を行うページ
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# ログインページから実行するならこっち
from pages.purchase import session_state
from pages.purchase import confirm_page
from pages.purchase import error_judge
from pages.purchase import complete_page
from pages.purchase import reset_page
# 現在のページだけ見るならこっち
# from purchase import session_state
# from purchase import confirm_page
# from purchase import error_judge
# from purchase import complete_page
# from purchase import reset_page

# ページ設定
import functions.func_common as fc
import functions.func_common2 as fc2
import functions.func_purchase as fp

def trade_Page():
    # ページ設定
    fc.set_page_config()
	# Cookieにsession_state_usernameを保持
    fc2.setUsername()



# メインページ
def purchase_main(user_name):
	# タイトル
	fc.set_page_title("purchase-system")
	# st.title("🪙 Trade Page")
	st.markdown("---")
	st.write(user_name)

	# 株価リストを取得
	df_stock_list = fc.company_data()
	df_stock_list = df_stock_list.reset_index()
	df_stock_list.columns = ['企業コード','企業名']

	# """株の購入の入力欄"""
	st.subheader('所持株一覧')
	df_stock_holds = stock_holds_info(user_name, df_stock_list)
	st.session_state.df_stock = df_stock_holds
	
	st.markdown("---")
	# """株の購入の入力欄"""
	# df_stock_lists = df_stock_holds
	st.subheader('株を購入', help = "先に所持株から選択してください。選択しない場合上書きされます")
	df_buy = purchase_table(df_stock_list)

	# """株の売却の入力欄"""
	st.subheader('株を売却', help = "先に所持株から選択してください。選択しない場合上書きされます")
	df_sell = sell_table(df_stock_holds)

	# リセット機能
	reset_btn = st.button('全てリセット', help = "注意: 入力が全てリセットされます")
	if reset_btn:
		st.session_state.layer = 3
		st.experimental_rerun()
	
	st.markdown("---")

	# 次の画面へ遷移するボタン
	next_button = st.button('次へ')
	
	if next_button:
		# 次へボタンが押された後の処理を書く
		df_buy = df_delect_row(df_buy)
		df_sell = df_delect_row(df_sell)
		# Dataframeの確認用
		# st.write(df_buy)
		# st.write(df_sell)

		# 売買のDataframeをst.session_stateに追加
		st.session_state.df_buy = df_buy
		st.session_state.df_sell = df_sell

		# エラー処理
		# ローカル確認用:所持株
		# error_judge_flag = error_judge.check_judge(df_buy, df_sell, df_stock_holds, df_stock_holds)
		# 企業株リストを含む
		error_judge_flag = error_judge.check_judge(df_buy, df_sell, df_stock_holds, df_stock_list)
		# print(error_judge_flag)
		if error_judge_flag == True:
			st.session_state.layer = 1
			st.experimental_rerun()
		


# 関数定義

def stock_holds_info(user_name, df_stock_list):
	comment = """
		所持株のデータを持ってきて、一覧として表示する。
		現在は仮置きでDataframeを作成し表示させているが、今後、別に関数を作って持ってくる予定
	"""
	stock_holds, stock_purchase = st.columns((5,2))
	with stock_holds:
		st.markdown("")
		st.markdown("")
		# colums = ["企業コード", "企業名", "保有株数", "取引日付", "株価の増減"]
		# 仮データ
		# data = {"企業コード": [1305],
		# 			"企業名": ['ダイワ上場投信－トピックス'],
		# 			"株数量": [100],
		# 			"取引日付": [dt.date.today()],
		# 			}
		# df_stock_holds = pd.DataFrame(data)

		# 所持株データ
		df_stock_holds = fp.stock_holding(user_name)
		# カラム名を変更
		column_change = {'Code': '企業コード', 'Count': '株数量', 'Price': '株全体価格', 'Date': '取引日付'}
		df_stock_holds.rename(columns=column_change, inplace=True)
		# 企業名の列を追加
		stock_company_list = _df_add_company(df_stock_holds, df_stock_list)
		df_stock_holds.insert(loc=1, column="企業名", value = stock_company_list)

		# 株全体価格を削除
		df_stock_holds = df_stock_holds.drop(columns = '株全体価格')

		# 見やすいように文字列型に変化
		df_stock_holds['企業コード'] = df_stock_holds['企業コード'].astype(str)
		# 'count'列が0の行を削除
		df_stock_holds = df_stock_holds.drop(df_stock_holds[df_stock_holds['株数量'] == 0].index)
		df_stock_holds.reset_index(drop=True, inplace=True)

		st.dataframe(df_stock_holds, use_container_width=True)

		# int型に戻す
		df_stock_holds['企業コード'] = df_stock_holds['企業コード'].astype(int)
	with stock_purchase:
		if df_stock_holds.empty:
			stock_company = ''
		else:
			stock_company = df_select(df_stock_holds, 1)
		# st.write(df_stock_holds.empty)
		select_company = st.selectbox("売買する所持株の選択", options = stock_company, help = "売買したいコードを選択し、ボタンを押すと下の表に追加されます。(各5つまで)")
		
		session_state.session_state_stock_info()
		
		# 購入、売却へ移動するボタンを作成
		buy_button, sell_button = st.columns(2)
		with buy_button:
			b_purchase = st.button('購入へ')
			if b_purchase:
				st.session_state.count_buy += 1
				# 5回まで企業を選択できる
				if st.session_state.count_buy < 5:
					st.session_state.select_code_b = df_filter(df_stock_holds, select_company, "企業名", "企業コード")
					st.session_state.select_company_b = select_company

		with sell_button:
			s_purchase = st.button('売却へ')
			if s_purchase:
				st.session_state.count_sell += 1
				# 5回まで企業を選択できる
				if st.session_state.count_sell <= 5:
					st.session_state.select_code_s = df_filter(df_stock_holds, select_company, "企業名", "企業コード")
					st.session_state.select_company_s = select_company
		if b_purchase :
			if st.session_state.count_buy > 5:
				st.warning("これ以上購入できません")
		if s_purchase:
			if st.session_state.count_sell > 5:
				st.warning("これ以上売却できません")
	
	return df_stock_holds

def purchase_table(df):
	# 企業株リストのコードを取得
	stock_code = df_select(df, 0)
	# 空の値を入れたDFをセレクトボックスに入れる
	stock_code = _df_insert_empty(stock_code)

	# 企業株リストの企業名を取得
	stock_company = df_select(df, 1)
	# 空の値を入れたDFをセレクトボックスに入れる
	stock_company = _df_insert_empty(stock_company)

	# """株の購入の入力欄"""
	# 複数の株を同時に買えるようにする(5社)
	buy_col1_1,buy_col1_2,buy_col1_3 = st.columns((1,2,1))
	with buy_col1_1:
		if st.session_state.count_buy == 1:
			# 企業株を購入するボタンを押された場合
			st.session_state.select_code_buy1 = st.session_state.select_code_b
			# 企業株の何番目にあるか判定()
			st.session_state.index_buy1 = _df_return_index(stock_code, st.session_state.select_code_buy1)
		
		if st.session_state.select_code_buy1 != 0:
			buy_code1 = st.selectbox("企業コード(購入用):", options = stock_code, index = int(st.session_state.index_buy1) + 1)
		else:
			buy_code1 = st.selectbox("企業コード(購入用):", options = stock_code)

	with buy_col1_2:
		if st.session_state.count_buy == 1:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_company_buy1 = st.session_state.select_company_b
		
		if st.session_state.select_company_buy1 != '':
			buy_company1 = st.selectbox("企業名(購入用):", options = stock_company, index = int(st.session_state.index_buy1) + 1)
		else:
			if buy_code1 != '' :
				if st.session_state.pre_code_buy1 != int(buy_code1):
					index = _df_return_index(stock_code, int(buy_code1))
					buy_company1 = st.selectbox("企業名(購入用):", options = stock_company, index = int(index) + 1)
			else:
				buy_company1 = st.selectbox("企業名(購入用):", options = stock_company)

	with buy_col1_3:
		buy_amount1 = st.number_input("株数量(購入用):", min_value=100, step=100)
	buy_day1 = dt.datetime.today() # デフォルト値は今日の日付
	# 入力された値をDataframeに追加
	df_buy = pd.DataFrame({
				'企業コード':[str(buy_code1)],
				'企業名':[buy_company1],
				'株数量':[buy_amount1],
				'売買状況':["buy"],
				'取引日付':[buy_day1]})

	# 同じcolumnsを5つ分作成
	# 2つ目の入力欄
	buy_col2_1,buy_col2_2,buy_col2_3 = st.columns((1,2,1))
	with buy_col2_1:
		if st.session_state.count_buy == 2:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_code_buy2 = st.session_state.select_code_b
			# 所持株の何番目にあるか判定()
			st.session_state.index_buy2 = _df_return_index(stock_code, st.session_state.select_code_buy2)
		
		if st.session_state.select_code_buy2 != 0:
			buy_code2 = st.selectbox("企業コード(購入用)2:", options = stock_code, index = int(st.session_state.index_buy2) + 1, label_visibility="collapsed")
		else:
			buy_code2 = st.selectbox("企業コード(購入用)2:", options = stock_code, label_visibility="collapsed")
	
	with buy_col2_2:
		if st.session_state.count_buy == 2:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_company_buy2 = st.session_state.select_company_b
		
		if st.session_state.select_company_buy2 != '':
			buy_company2 = st.selectbox("企業名(購入用)2:", options = stock_company, index = int(st.session_state.index_buy2) + 1,label_visibility="collapsed")
		else:
			if buy_code2 != '':
				if st.session_state.pre_code_buy2 != int(buy_code2):
					index2 = _df_return_index(stock_code, int(buy_code2))
					buy_company2 = st.selectbox("企業名(購入用2):", options = stock_company, index = int(index2) + 1, label_visibility="collapsed")
			else:
				buy_company2 = st.selectbox("企業名(購入用)2:", options = stock_company,label_visibility="collapsed")
	
	with buy_col2_3:
		buy_amount2 = st.number_input("株数量(購入用)2:",label_visibility="collapsed", min_value=100, step=100)
	buy_day2 = dt.datetime.today() # デフォルト値は今日の日付

	# 購入欄の情報をdf_buyに追加
	buy_info2 = [buy_code2,buy_company2,buy_amount2,"buy",buy_day2]
	df_include(df_buy, buy_info2)

	# 3つ目の入力欄
	buy_col3_1,buy_col3_2,buy_col3_3 = st.columns((1,2,1))
	with buy_col3_1:
		if st.session_state.count_buy == 3:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_code_buy3 = st.session_state.select_code_b
			# 所持株の何番目にあるか判定()
			st.session_state.index_buy3 = _df_return_index(stock_code, st.session_state.select_code_buy3)

		if st.session_state.select_code_buy3 != 0:
			buy_code3 = st.selectbox("企業コード(購入用)3:", options = stock_code, index = int(st.session_state.index_buy3) + 1, label_visibility="collapsed")
		else:
			buy_code3 = st.selectbox("企業コード(購入用)3:", options = stock_code, label_visibility="collapsed")
	
	with buy_col3_2:
		if st.session_state.count_buy == 3:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_company_buy3 = st.session_state.select_company_b
		
		if st.session_state.select_company_buy3 != '':
			buy_company3 = st.selectbox("企業名(購入用)3:", options = stock_company, index = int(st.session_state.index_buy3) + 1,label_visibility="collapsed")
		else:
			if buy_code3 != '':
				if st.session_state.pre_code_buy3 != int(buy_code3):
					index3 = _df_return_index(stock_code, int(buy_code3))
					buy_company3 = st.selectbox("企業名(購入用3):", options = stock_company, index = int(index3) + 1, label_visibility="collapsed")
			else:
				buy_company3 = st.selectbox("企業名(購入用)3:", options = stock_company,label_visibility="collapsed")
	
	with buy_col3_3:
		buy_amount3 = st.number_input("株数量(購入用)3:",label_visibility="collapsed", min_value=100, step=100)
	buy_day3 = dt.datetime.today() # デフォルト値は今日の日付
	
	# 購入欄の情報をdf_buyに追加
	buy_info3 = [buy_code3,buy_company3,buy_amount3,"buy",buy_day3]
	df_include(df_buy, buy_info3)

	# 4つ目の入力欄
	buy_col4_1,buy_col4_2,buy_col4_3 = st.columns((1,2,1))
	with buy_col4_1:
		if st.session_state.count_buy == 4:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_code_buy4 = st.session_state.select_code_b
			# 所持株の何番目にあるか判定()
			st.session_state.index_buy4 = _df_return_index(stock_code, st.session_state.select_code_buy4)
		
		if st.session_state.select_code_buy4 != 0:
			buy_code4 = st.selectbox("企業コード(購入用)4:", options = stock_code, index = int(st.session_state.index_buy4) + 1, label_visibility="collapsed")
		else:
			buy_code4 = st.selectbox("企業コード(購入用)4:", options = stock_code, label_visibility="collapsed")
	
	with buy_col4_2:
		if st.session_state.count_buy == 4:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_company_buy4 = st.session_state.select_company_b
		
		if st.session_state.select_company_buy4 != '':
			buy_company4 = st.selectbox("企業名(購入用)4:", options = stock_company, index = int(st.session_state.index_buy4) + 1,label_visibility="collapsed")
		else:
			if buy_code4 != '':
				if st.session_state.pre_code_buy4 != int(buy_code4):
					index4 = _df_return_index(stock_code, int(buy_code4))
					buy_company4 = st.selectbox("企業名(購入用4):", options = stock_company, index = int(index4) + 1, label_visibility="collapsed")
			else:
				buy_company4 = st.selectbox("企業名(購入用)4:", options = stock_company,label_visibility="collapsed")
	
	with buy_col4_3:
		buy_amount4 = st.number_input("株数量(購入用)4:",label_visibility="collapsed", min_value=100, step=100)
	buy_day4 = dt.datetime.today() # デフォルト値は今日の日付
	
	# 購入欄の情報をdf_buyに追加
	buy_info4 = [buy_code4,buy_company4,buy_amount4,"buy",buy_day4]
	df_include(df_buy, buy_info4)

	# 5つ目の入力欄
	buy_col5_1,buy_col5_2,buy_col5_3 = st.columns((1,2,1))
	with buy_col5_1:
		if st.session_state.count_buy == 5:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_code_buy5 = st.session_state.select_code_b
			# 所持株の何番目にあるか判定()
			st.session_state.index_buy5 = _df_return_index(stock_code, st.session_state.select_code_buy5)
		
		if st.session_state.select_code_buy5 != 0:
			buy_code5 = st.selectbox("企業コード(購入用)5:", options = stock_code, index = int(st.session_state.index_buy5) + 1, label_visibility="collapsed")
		else:
			buy_code5 = st.selectbox("企業コード(購入用)5:", options = stock_code, label_visibility="collapsed")
	with buy_col5_2:
		if st.session_state.count_buy == 5:
			# 所持株を購入するボタンを押された場合
			st.session_state.select_company_buy5 = st.session_state.select_company_b
		
		if st.session_state.select_company_buy5 != '':
			buy_company5 = st.selectbox("企業名(購入用)5:", options = stock_company, index = int(st.session_state.index_buy5) + 1,label_visibility="collapsed")
		else:
			if buy_code5 != '':
				if st.session_state.pre_code_buy5 != int(buy_code5):
					index5 = _df_return_index(stock_code, int(buy_code5))
					buy_company5 = st.selectbox("企業名(購入用5):", options = stock_company, index = int(index5) + 1, label_visibility="collapsed")
			else:
				buy_company5 = st.selectbox("企業名(購入用)5:", options = stock_company,label_visibility="collapsed")

	with buy_col5_3:
		buy_amount5 = st.number_input("株数量(購入用)5:",label_visibility="collapsed", min_value=100, step=100)
	buy_day5 = dt.datetime.today() # デフォルト値は今日の日付
	
	# 購入欄の情報をdf_buyに追加	
	buy_info5 = [buy_code5,buy_company5,buy_amount5,"buy",buy_day5]
	df_include(df_buy, buy_info5)

	# 企業コードを文字列に統一
	# 表示のために文字列にしているが、今後DBに送るときはint型に直す予定
	df_buy['企業コード'] = df_buy['企業コード'].astype(str)

	return df_buy

def sell_table(df):

	# 所持株のコードを取得
	stock_code = df_select(df, 0)
	# 空の値を入れたDFをセレクトボックスに入れる
	stock_code = _df_insert_empty(stock_code)

	# 所持株の企業名を取得
	stock_company = df_select(df, 1)
	# 空の値を入れたDFをセレクトボックスに入れる
	stock_company = _df_insert_empty(stock_company)

	# """株の売却の入力欄"""
	# 複数の株を同時に売れるようにする(5社)
	sell_col1_1,sell_col1_2,sell_col1_3 = st.columns((1,2,1))
	with sell_col1_1:
		if st.session_state.count_sell == 1:
			# 所持株を購入するボタンが押された場合
			st.session_state.select_code_sell1 = st.session_state.select_code_s
			# 所持株の何番目にあるか判定()
			st.session_state.index1 = _df_return_index(stock_code, st.session_state.select_code_sell1)
		
		if st.session_state.select_code_sell1 != 0:
			sell_code1 = st.selectbox("企業コード(売却用):", options = stock_code, index = int(st.session_state.index1) + 1)
		else:
			sell_code1 = st.selectbox("企業コード(売却用):", options = stock_code)

	with sell_col1_2:
		if st.session_state.count_sell == 1:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_company_sell1 = st.session_state.select_company_s
		
		if st.session_state.select_company_sell1 != '':
			sell_company1 = st.selectbox("企業名(売却用):", options = stock_company, index = int(st.session_state.index1) + 1)
		else:
			if sell_code1 != '':
				if st.session_state.pre_code_sell1 != int(sell_code1):
					index = _df_return_index(stock_code, int(sell_code1))
					sell_company1 = st.selectbox("企業名(売却用):", options = stock_company, index = int(index) + 1)
			else:
				sell_company1 = st.selectbox("企業名(売却用):", options = stock_company)
		
	with sell_col1_3:
		sell_amount1 = -(st.number_input("株数量(売却用):", min_value=100, step=100))
	sell_day1 = dt.datetime.today() # デフォルト値は今日の日付

	# 入力された値をDataframeに追加
	df_sell = pd.DataFrame({
				'企業コード':[str(sell_code1)],
				'企業名':[sell_company1],
				'株数量':[sell_amount1],
				'売買状況':["sell"],
				'取引日付':[sell_day1]})
	
	# 同じcolumnsを5つ分作成
	# 2つ目の入力欄
	sell_col2_1,sell_col2_2,sell_col2_3 = st.columns((1,2,1))
	with sell_col2_1:
		if st.session_state.count_sell == 2:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_code_sell2 = st.session_state.select_code_s
			# 所持株の何番目にあるか判定()
			st.session_state.index2 = _df_return_index(stock_code, st.session_state.select_code_sell2)
		
		if st.session_state.select_code_sell2 != 0:
			sell_code2 = st.selectbox("企業コード(売却用)2:", options = stock_code, index = int(st.session_state.index2) + 1, label_visibility="collapsed")
		else:
			sell_code2 = st.selectbox("企業コード(売却用)2:", options = stock_code, label_visibility="collapsed")

	with sell_col2_2:
		if st.session_state.count_sell == 2:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_company_sell2 = st.session_state.select_company_s
		
		if st.session_state.select_company_sell2 != '':
			sell_company2 = st.selectbox("企業名(売却用)2:", options = stock_company, index = int(st.session_state.index2) + 1,label_visibility="collapsed")
		else:
			if sell_code2 != '':
				if st.session_state.pre_code_sell2 != int(sell_code2):
					index2 = _df_return_index(stock_code, int(sell_code2))
					sell_company2 = st.selectbox("企業名(売却用)2:", options = stock_company, index = int(index2) + 1, label_visibility="collapsed")
			else:
				sell_company2 = st.selectbox("企業名(売却用)2:", options = stock_company, label_visibility="collapsed")

	with sell_col2_3:
		sell_amount2 = -(st.number_input("株数量(売却用)2:",label_visibility="collapsed", min_value=100, step=100))
	sell_day2 = dt.datetime.today() # デフォルト値は今日の日付

	# 売却欄の情報をdf_sellに追加
	sell_info2 = [sell_code2,sell_company2,sell_amount2,"sell",sell_day2]
	df_include(df_sell, sell_info2)

	# 3つ目の入力欄
	sell_col3_1,sell_col3_2,sell_col3_3 = st.columns((1,2,1))
	with sell_col3_1:
		if st.session_state.count_sell == 3:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_code_sell3 = st.session_state.select_code_s
			# 所持株の何番目にあるか判定()
			st.session_state.index3 = _df_return_index(stock_code, st.session_state.select_code_sell3)
		
		if st.session_state.select_code_sell3 != 0:
			sell_code3 = st.selectbox("企業コード(売却用)3:", options = stock_code, index = int(st.session_state.index3) + 1, label_visibility="collapsed")
		else:
			sell_code3 = st.selectbox("企業コード(売却用)3:", options = stock_code, label_visibility="collapsed")

	with sell_col3_2:
		if st.session_state.count_sell == 3:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_company_sell3 = st.session_state.select_company_s
		
		if st.session_state.select_company_sell3 != '':
			sell_company3 = st.selectbox("企業名(売却用)3:", options = stock_company, index = int(st.session_state.index3) + 1,label_visibility="collapsed")
		else:
			if sell_code3 != '':
				if st.session_state.pre_code_sell3 != int(sell_code3):
					index3 = _df_return_index(stock_code, int(sell_code3))
					sell_company3 = st.selectbox("企業名(売却用)3:", options = stock_company, index = int(index3) + 1, label_visibility="collapsed")
			else:
				sell_company3 = st.selectbox("企業名(売却用)3:", options = stock_company, label_visibility="collapsed")

	with sell_col3_3:
		sell_amount3 = -(st.number_input("株数量(売却用)3:",label_visibility="collapsed", min_value=100, step=100))
	sell_day3 = dt.datetime.today() # デフォルト値は今日の日付

	# 売却欄の情報をdf_sellに追加
	sell_info3 = [sell_code3,sell_company3,sell_amount3,"sell",sell_day3]
	df_include(df_sell, sell_info3)

	# 4つ目の入力欄
	sell_col4_1,sell_col4_2,sell_col4_3 = st.columns((1,2,1))
	with sell_col4_1:
		if st.session_state.count_sell == 4:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_code_sell4 = st.session_state.select_code_s
			# 所持株の何番目にあるか判定()
			st.session_state.index4 = _df_return_index(stock_code, st.session_state.select_code_sell4)
		
		if st.session_state.select_code_sell4 != 0:
			sell_code4 = st.selectbox("企業コード(売却用)4:", options = stock_code, index = int(st.session_state.index4) + 1, label_visibility="collapsed")
		else:
			sell_code4 = st.selectbox("企業コード(売却用)4:", options = stock_code, label_visibility="collapsed")
	
	with sell_col4_2:
		if st.session_state.count_sell == 4:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_company_sell4 = st.session_state.select_company_s
		
		if st.session_state.select_company_sell4 != '':
			sell_company4 = st.selectbox("企業名(売却用)4:", options = stock_company, index = int(st.session_state.index4) + 1,label_visibility="collapsed")
		else:
			if sell_code4 != '':
				if st.session_state.pre_code_sell4 != int(sell_code4):
					index4 = _df_return_index(stock_code, int(sell_code4))
					sell_company4 = st.selectbox("企業名(売却用)4:", options = stock_company, index = int(index4) + 1, label_visibility="collapsed")
			else:
				sell_company4 = st.selectbox("企業名(売却用)4:", options = stock_company, label_visibility="collapsed")

	with sell_col4_3:
		sell_amount4 = -(st.number_input("株数量(売却用)4:",label_visibility="collapsed", min_value=100, step=100))
	sell_day4 = dt.datetime.today() # デフォルト値は今日の日付

	# 売却欄の情報をdf_sellに追加
	sell_info4 = [sell_code4,sell_company4,sell_amount4,"sell",sell_day4]
	df_include(df_sell, sell_info4)

	# 5つ目の入力欄
	sell_col5_1,sell_col5_2,sell_col5_3 = st.columns((1,2,1))
	with sell_col5_1:
		if st.session_state.count_sell == 5:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_code_sell5 = st.session_state.select_code_s
			# 所持株の何番目にあるか判定()
			st.session_state.index5 = _df_return_index(stock_code, st.session_state.select_code_sell5)
		
		if st.session_state.select_code_sell5 != 0:
			sell_code5 = st.selectbox("企業コード(売却用)5:", options = stock_code, index = int(st.session_state.index5) + 1, label_visibility="collapsed")
		else:
			sell_code5 = st.selectbox("企業コード(売却用)5:", options = stock_code, label_visibility="collapsed")

	with sell_col5_2:
		if st.session_state.count_sell == 5:
			# 所持株を売却するボタンを押された場合
			st.session_state.select_company_sell5 = st.session_state.select_company_s
		
		if st.session_state.select_company_sell5 != '':
			sell_company5 = st.selectbox("企業名(売却用)5:", options = stock_company, index = int(st.session_state.index5) + 1,label_visibility="collapsed")
		else:
			if sell_code5 != '':
				if st.session_state.pre_code_sell5 != int(sell_code5):
					index5 = _df_return_index(stock_code, int(sell_code5))
					sell_company5 = st.selectbox("企業名(売却用)5:", options = stock_company, index = int(index5) + 1, label_visibility="collapsed")
			else:
				sell_company5 = st.selectbox("企業名(売却用)5:", options = stock_company,label_visibility="collapsed")

	with sell_col5_3:
		sell_amount5 = -(st.number_input("株数量(売却用)5:",label_visibility="collapsed", min_value=100, step=100))
	sell_day5 = dt.datetime.today() # デフォルト値は今日の日付

	# 売却欄の情報をdf_sellに追加	
	sell_info5 = [sell_code5,sell_company5,sell_amount5,"sell",sell_day5]
	df_include(df_sell, sell_info5)

	# 企業コードを文字列に統一
	# 表示のために文字列にしているが、今後DBに送るときはint型に直す予定
	df_sell['企業コード'] = df_sell['企業コード'].astype(str)

	return df_sell

def df_select(df, n):
	# Dataframeのn番目の列の情報を取得する関数
	df_n = df.iloc[:,n]
	return df_n

def df_filter(df, data, columns1, columns2):
	# 条件を指定してデータをフィルタリング
	filtered_df = df[df[columns1] == data]
	# 別のカラムの値を抽出
	desired_column_value = filtered_df[columns2].values[0]
	return desired_column_value

# 企業名の列を元のDFに追加する補助関数
def _df_add_company(df, df_stock_list):
	company_list = []
	for i in range(len(df)):
		# 所持株の企業コードを取得
		stock_code = int(df['企業コード'].iloc[i])
		stock_company = df_filter(df_stock_list, stock_code, '企業コード', '企業名')
		company_list.append(stock_company)
	return company_list

def df_include(df, list):
	# Dataframeとlistを受け取ってDataframeに追加する
	# 2つ目以降の入力欄の情報をDataframeに入力する関数
	if list[0] == '' and list[1] == '':
		# listの中身が何もなければスキップ
		pass
	else:
		# Dataframeの最後の行に追加する
		df.loc[len(df)] = list

def df_delect_row(df):
	# ' ' をNanに置き換え
	# 企業コード、企業名両方入っていない行を削除
	# その後indexを振り直す
	df.replace('', np.nan, inplace=True)
	df.dropna(subset=['企業コード', '企業名'], how='all', inplace=True)
	df.reset_index(drop=True, inplace=True)
	return df

# dfの先頭に空の文字列を追加
def _df_insert_empty(df):
	air = ['']
	# DataFrameに変換する
	df_insert = pd.Series(air, index=[-1])
	return pd.concat([df_insert,df])

def _df_return_index(df, data):
	# pandas.Seriesで値dataと一致する値が上から何番目にあるかを出力する関数
	# :return dataと一致する値が最初に見つかる位置（0から始まるインデックス）
	ans_index = df[df == data].index[0]
	return ans_index

#--------ページ遷移--------
def page_select(page_number):
	trade_Page()
	if page_number == 0:
		purchase_main(st.session_state.username)

	if page_number == 1:
		confirm_page.main_confirm(st.session_state.username, st.session_state.df_buy, st.session_state.df_sell)
	
	if page_number == 2:
		complete_page.main_complete_page(st.session_state.df_buy, st.session_state.df_sell)
	
	if page_number == 3:
		reset_page.reset_page()

# -------メイン関数-------
def main():
	# session_state.session_state_user_name()
	session_state.session_state_stock_info()
	session_state.session_state_page_change()

	page_select(st.session_state.layer)

# 実行
if __name__ == "__main__":
	main()