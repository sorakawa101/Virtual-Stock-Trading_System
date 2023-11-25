# 売買履歴表示ページ
# purchaseディレクトリ内に配置する予定でしたが、ページ表示ができないようなのでここに置いています
import streamlit as st
import pandas as pd

import functions.func_common as fc
import functions.func_common2 as fc2
import functions.func_purchase as fp
import functions.func_index as fi

# ページ設定
fc.set_page_config()
fc2.setUsername()  # Cookieにsession_state_usernameを保持

# メインページ
def purchase_history_main():
    fc.set_page_title("purchase-history")

    # """session_stateの用意"""
    session_state_history()
    # """株の売買履歴表示"""
    purchase_history_info()


def session_state_history():
    # 銘柄コード検索用
    if 'code' not in st.session_state:
        st.session_state.code = None
    # 銘柄名検索用
    if 'name' not in st.session_state:
        st.session_state.name = None
    
def purchase_history_info():
	# 所持株のデータをDBからdataframe形式で保存
    PurchaseHistoryData = fp.purchase_history(fi.get_username())

    if PurchaseHistoryData.empty:
        ### 売買履歴がない時の処理 ###
        st.write('売買履歴がありません。')
    else:
        ### 売買履歴がある時の処理 ###
        # 売買履歴からName列を削除
        df = PurchaseHistoryData.drop('Name', axis=1)

        # 購入/売却のタグ付け
        BS = []
        for row in range(0, df.shape[0]):
            if df.at[row, "Count"] > 0:
                BS.append("購入")
            else:
                BS.append("売却")
        df.insert(0, '購入/売却', BS)

        # Selectbox用に履歴から銘柄コードと銘柄名を重複排除で抽出
        Company_list = df.loc[:, ['Code', 'Company']].drop_duplicates(subset='Code')
        Company_list = Company_list.reset_index()

        # 元dfのコピー
        history = df


        ## 表、ボタンの配置 ##
        # パレットの用意
        col1, col2 = st.columns(2)

        # 銘柄コード検索
        with col1:
            # selectbox
            select_code = st.selectbox('銘柄コードで検索', Company_list['Code'])
            if select_code != None:
                if st.session_state.code != int(select_code):
                    CodeId = int(list(Company_list['Code']).index(select_code))
                    st.write(Company_list['Company'][CodeId])
            # button
            if st.button('検索', key='button1'):
                history = df[df['Code'] == select_code]

        # 企業名検索
        with col2:
            # selectbox
            select_name = st.selectbox('企業名で検索', Company_list['Company'])
            if select_name != None:
                if st.session_state.name != str(select_name):
                    CompanyId = int(list(Company_list['Company']).index(select_name))
                    st.write(Company_list['Code'][CompanyId])
            # button
            if st.button('検索', key='button2'):
                history = df[df['Company'] == select_name]
            
        # 表配置
        st.dataframe(history, use_container_width=True)

        # Reset Button
        if st.button('元に戻す'):
                history = df
        
    
# 実行
if __name__ == "__main__":
	purchase_history_main()