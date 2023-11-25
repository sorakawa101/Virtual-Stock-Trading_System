import streamlit as st
import functions.func_common as fc
# import sys
# sys.path.append("../../functions")
# import func_common as fc

def main_complete_page(df_buy, df_sell):
	
	col1_1, col1_2, col1_3 = st.columns((1,5,1))
	with col1_1:
		pass
	with col1_2:
		# st.title("🪙 Trade Page")
		# タイトル
		fc.set_page_title("purchase-system")
		st.markdown("---")

		# 画面の中央に文字を表示
		st.write("<h2 style='text-align: center;'>売買完了しました</h2>", unsafe_allow_html=True)

		st.markdown("")
		st.markdown("")
		# ボタンを画面の中央に配置(強引)
		# 画面をめっちゃ小さくしたら左に移動してしまう
		col2_1, col2_2, button, col2_4, col2_5= st.columns((1.5,1,2,1,1))
		with col2_1:
			pass
		with col2_2:
			pass
		with button:
			back_btn()
		with col2_4:
			pass
		with col2_5:
			pass
	with col1_3:
		pass

# ページ管理
# layer=0 : 売買main, layer=1: 確認画面main, layer=2:完了画面main
def layer_session(layer = 0):
	st.session_state.layer = layer

# 戻るボタン
def back_btn():
	button = st.button("Topへ戻る")
	if button:
		reset_session(0)
		st.experimental_rerun()

# ページリセット
def reset_session(layer=0):
	st.session_state.count_buy = 0
	st.session_state.count_sell = 0
	st.session_state.df_stock = 0

	for i in range(1, 6):
		st.session_state[f"select_code_buy{i}"] = 0
		st.session_state[f"select_company_buy{i}"] = ''
		st.session_state[f"select_code_sell{i}"] = 0
		st.session_state[f"select_company_sell{i}"] = ''

	layer_session(layer)

# ページ設定
def trade_Page():
    # ページ設定
    fc.set_page_config()


# main_complete_page()