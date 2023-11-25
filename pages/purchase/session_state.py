import streamlit as st

# 必要なst.session_stateを作成

# 現状リロードするとuser_nameが取得できないっぽい

# def session_state_user_name():
# 	# リロードの時に初期化が必要?
# 	if 'username' not in st.session_state:
# 		st.session_state.username = ""

# 所持株管理のための関数
def session_state_stock_info():

	# それぞれのボタンが押された回数を数える変数
	if 'count_buy' not in st.session_state:
		st.session_state.count_buy = 0
	if 'count_sell' not in st.session_state:
		st.session_state.count_sell = 0
		
	# ボタンが押されたときに企業コード, 企業名を保持する変数
	# 購入変数
	if 'select_code_b' not in st.session_state:
		st.session_state.select_code_b = 0
	if 'select_company_b' not in st.session_state:
		st.session_state.select_company_b = ''
	# 売却変数
	if 'select_code_s' not in st.session_state:
		st.session_state.select_code_s = 0
	if 'select_company_s' not in st.session_state:
		st.session_state.select_company_s = ''
	
	# リセット
	if 'reset' not in st.session_state:
		st.session_state.reset = 0

	num_indexes = 5  # インデックスの数
	
	# それぞれの押された回数ごとに値を保持する変数
	for i in range(1, num_indexes + 1):
		# 購入変数
		# select_code_buy のセッションステート変数を初期化
		code_name_buy = f'select_code_buy{i}'
		if code_name_buy not in st.session_state:
			st.session_state[code_name_buy] = 0

		# select_company_buy のセッションステート変数を初期化
		var_name_buy = f'select_company_buy{i}'
		if var_name_buy not in st.session_state:
			st.session_state[var_name_buy] = ''
	
		# 売却変数
		# select_code_sell のセッションステート変数を初期化
		code_name_sell = f'select_code_sell{i}'
		if code_name_sell not in st.session_state:
			st.session_state[code_name_sell] = 0

		# select_company_sell のセッションステート変数を初期化
		var_name_sell = f'select_company_sell{i}'
		if var_name_sell not in st.session_state:
			st.session_state[var_name_sell] = ''
	
		# それぞれの行ごとの企業コードの値を記憶しておく変数
		# 購入欄
		pre_code_buy = f'pre_code_buy{i}'
		if pre_code_buy not in st.session_state:
			st.session_state[pre_code_buy] = 0
		# 売却欄
		pre_code_sell = f'pre_code_sell{i}'
		if pre_code_sell not in st.session_state:
			st.session_state[pre_code_sell] = 0




# ページ遷移用変数
def session_state_page_change():

	if 'layer' not in st.session_state:
		st.session_state.layer = 0
	
	# Dataframeを記憶
	if "df_buy" not in st.session_state:
		st.session_state.df_buy = None
	if "df_sell" not in st.session_state:
		st.session_state.df_sell = None
	if "df_stock" not in st.session_state:
		st.session_state.df_stock = None
	
