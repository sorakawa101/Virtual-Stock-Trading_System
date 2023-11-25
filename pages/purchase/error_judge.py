import streamlit as st
import pandas as pd

# 登録されている株が正しいか判断
def check_judge(df_buy, df_sell, df_stock, df_company_list):
	# エラーがあるかを保持する変数
	error_judge_buy = 0
	error_judge_sell = 0
	error_judge_buy_correct = True
	error_judge_sell_correct = True
	# Dataframeが空かどうかを判定する変数
	error_judge_empty = False

	# Dataframeが空かどうか判断
	buy_empty = _df_empty_ans(df_buy)
	sell_empty = _df_empty_ans(df_sell)

	# 購入用データのjudge
	if buy_empty:
		# 問題なし
		pass
	else:
		error_judge_empty = True
		# 企業コードに対する処理
		# エラー判定 0:問題なし 1:企業コードにNoneがある 2:企業コードが4桁でない 3:同じ企業コードがある
		error_judge_buy_code = _check_code(df_buy)
		if error_judge_buy_code == 1:
			error_judge_buy = 1
			st.error('購入欄の企業コードが入力されていません')
		elif error_judge_buy_code == 2:
			# セレクトボックスにしたことでいらないかも
			error_judge_buy = 1
			st.error('購入欄の企業コードは4桁の数字で入力してください')
		elif error_judge_buy_code == 3:
			error_judge_buy = 1
			st.error('購入欄に同じ企業コードが複数入力されています')
		else:
			# 企業名と企業コードが対応しているかを判定
			# 確認用:所持株から取得
			# error_judge_buy_correct = _check_code_company(df_buy, df_stock)
			# 企業株リストと比較
			error_judge_buy_correct = _check_code_company(df_buy, df_company_list)
			if error_judge_buy_correct == False:
				st.error('購入欄の企業コードと企業名が対応していません')
		
		# 企業名に対する処理
		error_judge_buy_company = _check_company(df_buy)
		if error_judge_buy_company == 1:
			error_judge_buy = 1
			st.error('購入欄に企業名が入力されていません')
			
	# 売却用データのjudge
	if sell_empty:
		pass
	else:
		error_judge_empty = True
		# print(df_sell)
		# 企業コードに対する処理
		# エラー判定 0:問題なし 1:企業コードにNoneがある 2:売却ではなし 3:同じ企業コードがある
		error_judge_sell_code = _check_code(df_sell)
		if error_judge_sell_code == 1:
			error_judge_sell = 1
			st.error('売却欄の企業コードが入力されていません')
		elif error_judge_sell_code == 3:
			error_judge_sell = 1
			st.error('売却欄に同じ企業コードが複数入力されています')
		else:
			# 企業名と企業コードが対応しているかを判定
			error_judge_sell_correct = _check_code_company(df_sell, df_stock)
			if error_judge_sell_correct == False:
				st.error('売却欄の企業コードと企業名が対応していません')
		
		# 企業名に対する処理
		error_judge_sell_company = _check_company(df_sell)
		if error_judge_sell_company == 1:
			error_judge_sell = 1
			st.error('売却欄に企業名が入力されていません')
		
		# 企業コードが入力されていない場合エラーになるため、入力されている前提にする
		if error_judge_sell_code == 0 and error_judge_sell_correct == True:
			# 株数量に対する処理
			error_judge_sell_stock = _check_stock(df_sell, df_stock)
			if error_judge_sell_stock == 1:
				error_judge_sell = 1
				st.error('売却欄の株数量が所持株を超えています')
	
	if error_judge_buy == 0 and error_judge_sell == 0 and error_judge_sell_correct == True and error_judge_buy_correct == True and error_judge_empty == True:
		return True
	else:
		return False
		
	

# 関数定義
#-----売買エラー処理------#
# コードを判定
def _check_code(df):
	# エラー判定 0:問題なし 1:企業コードにNoneがある 2:企業コードが4桁でない 3:同じ企業コードがある
	error_judge = 0
	# 企業コードにNoneがあるかを判定(あったらTrue)
	none_judge = any(df['企業コード'].isna())
	if none_judge == True:
		error_judge = 1
	else:
		for i in range(len(df)):
			if not (int(df['企業コード'][i]) >= 1000 and int(df['企業コード'][i]) <= 9999):
				error_judge = 2

	# 企業コードの列を取得
	company_codes = df['企業コード']
	# 重複した企業コードが存在するか確認
	if company_codes.duplicated().any() == True:
		error_judge = 3
	
	return error_judge
	
# 会社を判定
def _check_company(df):
	# エラー判定 0:問題なし 1:企業名にNoneがある
	error_judge = 0
	# 企業コードにNoneがあるかを判定(あったらTrue)
	none_judge = any(df['企業名'].isna())
	if none_judge == True:
		error_judge = 1
	
	return error_judge

# 株数量を判定
def _check_stock(df, df_stock):
	error_judge = 0
	# dfをint型に直す
	df['企業コード'] = df['企業コード'].astype(int)
	# 所持株情報のデータフレームと売却株情報のデータフレームを企業コードでマージ
	merged_df = pd.merge(df_stock, df, on='企業コード', suffixes=('_所持', '_売却'), how='inner')
	# 株数量を比較して新しい列を追加
	merged_df['株数量比較'] = merged_df['株数量_所持'] + merged_df['株数量_売却']
	for i in range(len(merged_df)):
		if merged_df['株数量比較'][i] < 0:
			error_judge = 1
	return error_judge

# Dataframeが空だったらTrue, そうでなかったらFalse
def _df_empty_ans(df):
	if df.empty:
		return True
	else:
		return False

# 企業コードと企業名が対応しているかを判断する関数
def _check_code_company(df, stock_info):
	df['企業コード'] = df['企業コード'].astype(int)
	judge = True
	df_len = len(df)
	for i in range(df_len):
		# df に入っている企業コード、企業名を取り出す
		code = df['企業コード'][i]
		company = df['企業名'][i]
		# stock_infoの中の企業コードがcodeに一致する行の企業名の値を取り出し、companyと比較
		# 一致しなかった場合judgeにFalseを入れる
		stock_company = df_filter(stock_info, code, '企業コード', '企業名')
		if stock_company != company:
			judge = False
	return judge
		
def df_filter(df, data, columns1, columns2):
	# 条件を指定してデータをフィルタリング
	filtered_df = df[df[columns1] == data]
	# 別のカラムの値を抽出
	desired_column_value = filtered_df[columns2].values[0]
	return desired_column_value
