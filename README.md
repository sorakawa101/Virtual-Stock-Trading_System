# VirtualStockTradingSystem



### ブランチ名(role)
**branch name: feature/(role)/(date(YYYYMMDD))-(name)**
ex: feature/login/20231012-TaroDentsu

* 本体 : /index/
* ログイン : /login/
* グラフ : /graph/
* 売買 : /purchase/
* DB : /db/
* README: /readme/
* その他： /other/

### Pull Request

1. 粒度小さくCommitする
2. 機能などできるだけ小さくまとめてPull Requestする
3. Slackにて#IDを明記して担当者にPRの連絡を送る


**Pull Requestの書き方**

タイトル： ブランチ名（/feature/index/YYYYMMDD-TaroDentsu）
コメント：　Pull Request単位での内容


### login-homeに関して

実行する際にエラーが出るかもしれませんが、それは学内のmariaDBに接続しているためです。ですので、学校のWifiにVPNなどで再接続すれば開けるようになると思います。お手数おかけしますが、ご理解よろしくお願いします。


### データベース接続
秘密情報（DB接続PW等）は，`.streamlit/secrets.toml`に置く．
`st.secrets["secrets.tomlで指定した名前"]`で取得できる．

```py:sample.py
st.write("DB username:", st.secrets["db_username"])
```

```toml:.streamlit/secrets.toml
db_username = "xxxx"
db_password = "**********"
```


### ファイル構成（仮）
```
.
├── README.md
│
├── login-home.py(ログインページ)
│
├── pages(MPAのサブファイル)
│   ├── index.py（メインページ）
│   ├── graph.py（グラフページ）
│   ├── purchase.py(売買ページ)
|
├── .streamlit（.gitignoreに指定．ファイルの中身はTeamsで共有）
│   ├── secrets.toml（シークレットファイル）
│
├── requirements.txt
└── .gitignore

1 directories, 7 files
```


