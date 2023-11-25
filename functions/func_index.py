import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
import func_common as fc
import datetime as dt
# * サイドバー


# ログイン情報（session_state）から，現在ログイン中のusernameを取得する関数
def get_username():
    if st.session_state.username:
        return st.session_state.username
    else:
        return "Username Error"


# getUsername()で取得したusernameをindexページのサイドバーに表示する関数
def set_username(username):
    if username is "Username Error":
        st.error("ログインエラーが発生しました．再度ログインしてください")
    else:
        st.write(username)


# * メインコンテンツ①

def set_page_explanation():
    with st.chat_message('assistant'):
        st.write('VSTS（Virtual Stock Trading System）へようこそ！各ページの説明を一覧したい方は↓をクリック！')
        with st.expander('Pages Explanation'):
            st.markdown(
            '''
            - **index**
                - 本ページです．全体の入口となるページで，各ページの説明・売買履歴・本システム開発についての説明などがあります．
            - **graph**
                - 企業の株式データをグラフで分析できます．企業や期間など色々選択してみてください．
            - **purchase-history**
                - 株式の売買履歴を閲覧できます．何度か売買した後に覗いてみましょう．
            - **purchase-system**
                - 株式の売買を行うことができます．まずはこちらで好きな企業の株式を購入してみましょう．
            ''')


# * メインコンテンツ②
def set_purchase_contribution():
    st.subheader('あなたの売買履歴')
    df = get_trading_activity_dataframe(get_username())
    st.line_chart(df)
    # st.dataframe(get_trading_activity_dataframe(get_username()))


# * メインコンテンツ③

# 今回の開発について紹介するコンテンツを表示する関数
def set_development_explanation(nodes, edges):
    st.subheader('VSTSの開発について')
    set_development_info()
    st.divider()
    st.caption('開発担当/メンバー紹介図（気になる所をクリックしたり動かしたりしてみよう！）')
    set_development_agraph(nodes, edges)

# 今回の開発に関する文字ベースの説明を表示する関数
# 開発概要紹介
def set_development_info():
    st.markdown('''
        橋山研究室には，プログラミングを勉強するためのPゼミがあります．
        VSTSは，2023年度のPゼミにおける集大成となるシステムです．
        | 使用言語   | 使用ライブラリ | 使用ツール        | チーム分担 |
        | ------ | ---------- | ----------------- | ---------- |
        | Python | Streamlit  | Git/Github，Slack，Streamlit Share | 各ページ，データベース・デプロイ，PullRequest対応 |
''')

# Agraphを表示する関数
# 今回の開発の担当，メンバー紹介
def set_development_agraph(nodes, edges):
    set_nodes(nodes)
    set_role_edges(edges)

    config = Config(width=1200,
                    height=500,
                    directed=True,
                    physics=True,
                    hierarchical=False,
                    )

    return_value = agraph(nodes=nodes,
                        edges=edges,
                        config = config)

    return return_value


# DBから'nodes'のテーブルをDataframe形式で取得する関数
def get_nodes_dataframe_from_db():
    # 全データ取得 辞書型 in List
    connection = fc.get_connection_to_MySQL()

    with connection:
        with connection.cursor() as cursor:
            # データ読み込み
            sql = "SELECT * FROM `nodes`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return pd.DataFrame(result)


# nodesの情報をセットする関数
def set_nodes(nodes):
    df = get_nodes_dataframe_from_db()

    for row in df.itertuples():

        nodes.append( Node(id=row.id,
                        title=row.title,
                        label=row.label,
                        size=row.commits,
                        shape=row.shape,
                        image=row.image_url,
                        color=row.color
                        )
                    )


# 担当エッジを設定する関数
def set_role_edges(edges):
    # Index
    set_role_edge(edges, "sasakawa", "index")

    # Login
    set_role_edge(edges, "hosokawa", "login")

    # Graph
    set_role_edge(edges, "ohara", "graph")
    set_role_edge(edges, "niitsuma", "graph")
    set_role_edge(edges, "yanagiya", "graph")
    set_role_edge(edges, "yoshioka", "graph")
    set_role_edge(edges, "sasakawa", "graph")
    set_role_edge(edges, "hosokawa", "graph")

    # Purchase
    set_role_edge(edges, "ogawa", "purchase")
    set_role_edge(edges, "higashikawa", "purchase")
    set_role_edge(edges, "takeda", "purchase")

    # DB/Deploy
    set_role_edge(edges, "hayashi", "db")
    set_role_edge(edges, "deguchi", "db")
    set_role_edge(edges, "sasakawa", "db")
    set_role_edge(edges, "natori", "db")

    # PR
    set_role_edge(edges, "sasakawa", "pr")
    set_role_edge(edges, "natori", "pr")


# 仮のデータフレームを取得する関数
def get_tmp_dataframe():
    df_tmp = pd.DataFrame(
        data={
            "銘柄コード": [9434, 8316, 6178, 4661],
            "銘柄名": ["ソフトバンクグループ", "三井住友FG", "日本郵政", "オリエンタルランド"],
            "保有数": [100, 200, 300, 400],
            "現在値": [6307, 7198, 1305, 4680],
            "評価額": [630700, 1439600, 261000, 936000],
        }
    )
    return df_tmp


# 各エッジを追加セットする関数
def set_role_edge(edges, source, target):
    edges.append( Edge(source=source,
                    target=target,
                    color='gray'
                    )
                )

# historyテーブルから最終売買日付を返す関数
def get_last_trading_date(username):
    connection = fc.get_connection_to_MySQL()

    with connection:
        with connection.cursor() as cursor:
            # historyテーブル内のuserのデータから最新日付を取り出す
            sql = "SELECT MAX(CAST(Date AS date)) FROM `history` WHERE `Name` = %s"
            cursor.execute(sql, (username))
            result = cursor.fetchall()

    date = result[0]["MAX(CAST(Date AS date))"]
    if date == None:
        return ""
    else:
        return date.strftime('%Y/%m/%d')
# print(get_last_trading_date("sasakawa"))
#test = get_last_trading_date("natori")  # テスト用
#test = get_last_trading_date("noiman")  # テスト用


# 日付ごとの取引状況をdataframeにして返す関数
# TODO 依頼関数が出来次第差し替える
def get_trading_activity_dataframe(username):
    connection = fc.get_connection_to_MySQL()

    with connection:
        with connection.cursor() as cursor:
            # historyテーブル内のuserのデータから企業コード,企業名,株数取引日付を取り出す
            sql = "SELECT `Code`, `Company`, `Count`, CAST(Date AS date) FROM `history` WHERE `Name` = %s"
            cursor.execute(sql, (username))
            result = cursor.fetchall()

    data = pd.DataFrame(result)

    if data.empty:          # history内にデータが存在するか確認(なければ空をdataframeを作成)
        dataframe = pd.DataFrame({"Date":[""], "Company":[""], "Count":[0]})
        dataframe.set_index("Date", inplace=True)
    else:
        list_company = []
        list_date = []
        
        for _, row in data.iterrows():  # historyを1行ずつ読んでいく
            current_date = row["CAST(Date AS date)"]
            current_company = row["Company"]

            if current_date > dt.date(2023,10,31) :  # 取引した日付が有効かどうかを確認
                if current_date not in list_date:    # list内に登録されていなければ追加
                    list_date.append(current_date)
                if current_company not in list_company:
                    list_company.append(current_company)
        
        ##### 一旦ここまででfor一周 #####
        ## この操作でlist_companyの内容とlist_dateの内容がわかったので、あとは二次元配列に埋めるだけ

        list_count = [[0] * len(list_company) for _ in range(len(list_date))]  # 2次元配列, Date * Company; 0で初期化
        for _, row in data.iterrows():  # historyを1行ずつ読んでいく
            current_date = row["CAST(Date AS date)"]
            current_company = row["Company"]
            current_count = row["Count"]

            if current_date > dt.date(2023,10,31) :  # 取引した日付が有効かどうかを確認
                i_date = list_date.index(current_date)
                i_company = list_company.index(current_company)
                list_count[i_date][i_company] += current_count  # 二次元配列にCountを埋める

        dataframe = pd.DataFrame(data=list_count, columns=list_company, index=list_date)  # 完成した二次元配列をDataFrameにする
        


        '''以下昔のコード
        # 空のリストを作成
        list_code = []
        list_count = []
        list_company = []
        list_date = []

        for _, row in data.iterrows():
            if row["CAST(Date AS date)"] > dt.date(2023, 10,31) : # 取引した日付が有効かどうかを確認

                date = row["CAST(Date AS date)"]

                # list内に同じ日付が登録されているか確認
                if date in list_date:
                    # かつ、同じ企業で取引を行なっていたかを確認
                    if row["Code"] in list_code: 
                        index = list_code.index(row["Code"])
                        list_count[index] += row["Count"] # Countを加算
                    else:
                        # 新規の取引だった場合, listに追加
                        list_count.append(row["Count"])
                        list_code.append(row["Code"])
                        list_company.append(row["Company"])
                        list_date.append(date)
                else:
                    # 取引した日付がlist内に登録されていない場合, listに全て追加
                    list_count.append(row["Count"])
                    list_code.append(row["Code"])
                    list_company.append(row["Company"])
                    list_date.append(date)

        # データは存在したが、有効な取引日付が存在しなかった場合、list_* に空の値を入れる
        if len(list_code) == 0:
            list_date.append("")
            list_company.append("")
            list_count.append(0)
        
        # 重複なしで日付, 企業名のリストを作成
        date = []    
        for d in list_date:
            if d not in date:
                date.append(d)
        
        company = []    
        for c in list_company:
            if c not in company:
                company.append(c)

        # 最終的に返すdataframeを作成(初期値として0を入れておく)
        dataframe = pd.DataFrame(0,columns=company, index = date)
        
        # 空のlistを作成
        list = [0] * len(company)
        
        # i:日付のインデックス, index: list_* のインデックス 
        i = 0
        index = 0
        for d in list_date:
            if date[i] == d:  # 列の日付が一致しているかを確認
                index_c = company.index(list_company[index])    # 企業名が同じインデックスを代入
                list[index_c] = list_count[index]       # 一致していた場所に値を代入
            else:
                dataframe.loc[date[i]] = list           # 一度dataframeにlistの値を挿入
                list = [0] * len(company)               # listを空にする
                index_c = company.index(list_company[index])    # 企業名が同じインデックスを代入
                list[index_c] = list_count[index]       # 一致していた場所に値を代入
                i = i + 1                               # dateのindexを更新
            
            if i+1 == len(date):                    # forループの最後だった場合、最終取引日の株数が反映されないため、ここで確認する
                dataframe.loc[date[i]] = list
            index = index + 1
        '''
         
    return dataframe 
#print(get_trading_activity_dataframe("Yosshy"))  # テスト用

