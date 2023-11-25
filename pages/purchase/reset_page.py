import streamlit as st
from pages.purchase import confirm_page
# from purchase import confirm_page

# ページ設定
import functions.func_common as fc

import time

def reset_page():
	# タイトル
	fc.set_page_title("purchase-system")
	st.markdown("---")
	# st.title("🪙 Trade Page")
	st.markdown("")
	st.info('リセットします。もう一度押してください')
	st.markdown("")
	reset = st.button('リセット')
	if reset:
		# time.sleep(3)
		confirm_page.reset_session(0)
		st.experimental_rerun()