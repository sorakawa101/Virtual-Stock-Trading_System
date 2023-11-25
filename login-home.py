import streamlit as st
import streamlit.components.v1 as components
import smtplib
import math
import random
import re
import uuid
import datetime

import functions.func_login as fl
import functions.func_common as fc
import functions.func_common2 as fc2

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.hash import argon2     #pip install passlib


#ユーザー名：hokuto
#パスワード：testpassword でログインの確認できる

magic_index = 2


#ページ設定
def page_config():
    fc.set_page_config()

    fc.set_page_title("login-home")


#サイドバーを消す関数
def delete_sidebar():
    css = """
    <style>
    [data-testid="collapsedControl"] {visibility: hidden;}
    [data-testid="stSidebar"] {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    #サイドバーを閉じた状態にし、画面の見た目を多少良くした
    js = """
    <script>
    doc = window.parent.document
    elems = doc.querySelector('[data-testid="stSidebar"]')
    elem = elems.querySelector('[kind="header"]')
    elem.click()
    </script>
    """
    components.html(js,width=0,height=0,)


def set_cookie(key, value, max_age = -1):
    if max_age < 0:
        value2 = ""
    else:
        value2 = f";max-age={max_age}"
    js = f'''
    <script>
    window.parent.document.cookie = "{key}={value}{value2}";
    </script>
    '''
    components.html(js, height=0, width=0,)


#rerunをする関数
def streamlit_rerun():
    #streamlit 1.27.0以降
    #st.rerun()
    #streamlit 1.26.0以前
    st.experimental_rerun()




#関数定義はここから下に書く。
def page_change():
    html = f'''
    <script>
    doc = window.parent.document;
    elems = doc.querySelectorAll('[data-testid="stSidebarNav"]>ul>*');
    elem = elems[{magic_index}];
    elem = elem.getElementsByTagName('a')[0];
    elem.click()
    </script>
    '''
    components.html(html, height=0, width=0,)

def push_login_button(user_name, user_pass, texts):
    """
    ここではログインボタンを押された時に行う処理をかく。

    ユーザー名とパスワードが一致するユーザーをSQLで確認して、もし正しい組が存在するのであればログインする。
    存在しないのであれば、間違っていることを知らせる。
    """

    h = fl.is_user_exist(user_name)
    if not len(h) == 0:
        if argon2.verify(user_pass+st.secrets["PEPPER"], h):
            st.session_state.username = user_name
            #セッションIDをクッキーに保存し、セッションIDとその期限(1日後)、IPv4アドレス、ユーザー名をDBに保存する。
            id = uuid.uuid4()
            set_cookie("sessionID", id)
            jst = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(microsecond=0)
            #セッションIDとユーザー名、期限をSQLに保存する処理
            fl.insert_session(sessionID=id, username=user_name, expire=jst)
            page_change()
        else:
            texts.markdown(''':red[ユーザー名(メールアドレス)またはパスワードが違います]''')
    else:
        texts.markdown(''':red[ユーザー名(メールアドレス)またはパスワードが違います]''')

def makeAccountCheckCode(address, error_text):
    #メールアドレスの確認、確認コードの送信、次のパネルへの移行
    check = True
    #使用可能なメールアドレスかどうかを確認
    re_isTrue = re.compile(r'^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$')
    if len(address) == 0:
        error_text.markdown(''':red[メールアドレスを入力してください]''')
        check = False
    elif re.match(re_isTrue, address) == None:
        error_text.markdown(''':red[不正なメールアドレスです]''')
        check = False
    
    #メールアドレスがすでに使用されているものかどうかを確認する。
    if fl.is_mail_exist(address):
        error_text.markdown(''':red[そのメールアドレスはすでに使用されています。]''')
        check = False
    
    if check:
        #まだ使用されていないメールアドレスかつ、使うことができるメールアドレスならば、ここに書いてある処理を実行する。
        rand = math.floor(1 + (random.random() * 9)) * 100000 + math.floor(random.random() * 10) * 10000 + math.floor(random.random() * 10) * 1000 + math.floor(random.random() * 10) * 100 + math.floor(random.random() * 10) * 10 + math.floor(random.random() * 10)
        text = "会員登録のお手続きありがとうございます。\nこの度はVirtual Stock Trading Systemに仮登録していただき、ありがとうございます。\n\n現在の段階では会員登録手続きは完了しておりません。会員登録を完了するには次の認証コードをサイトに入力し、ユーザー名とパスワードを設定してください。\n\n認証コード:"+str(rand) + "\n\n本メールにお心当たりのない場合は、お手数ですが本メールの破棄をお願いいたします。"
        send_mail(title= "【Virtual Stock Trading System】新規登録のお知らせ",text= text, mail_address= address)

        st.session_state.checker = 2
        st.session_state.mail = address
        st.session_state.username = str(rand)
        streamlit_rerun()

def change_password_mail_check(username, text):
    #パスワード変更時のメール確認
    res = fl.is_user_mail_exist(username)
    if res[0]:
        txt= res[1]

        rand = math.floor(1 + (random.random() * 9)) * 100000 + math.floor(random.random() * 10) * 10000 + math.floor(random.random() * 10) * 1000 + math.floor(random.random() * 10) * 100 + math.floor(random.random() * 10) * 10 + math.floor(random.random() * 10)
        text2 = "パスワードの再設定をご希望の場合は次の認証コードをサイトに入力し、パスワードの変更を行ってください。\n\n認証コード:"+str(rand) + "\n\n本メールにお心当たりのない場合は、お手数ですが本メールの破棄をお願いいたします。"
        send_mail(title= "【Virtual Stock Trading System】パスワード変更のお知らせ",text= text2, mail_address= txt)


        st.session_state.checker = 5
        st.session_state.username = str(rand)
        st.session_state.mail = txt
        streamlit_rerun()
    else:
        text.markdown(''':red[そのユーザー名またはメールアドレスは登録されていません。]''')

def registar_check(mail, username4, pass1, pass2, text):
    re_alnum = re.compile(r'^[a-zA-z0-9]+$')
    if len(username4) == 0:
        text.markdown(''':red[ユーザー名を入力してください。]''')
    elif re.match(re_alnum, username4) == None:
        text.markdown(''':red[ユーザー名に使用できない文字が含まれています。]''')
    else:
        if pass1 != pass2:
            text.markdown(''':red[確認用パスワードがパスワードと異なります。]''')
        elif len(pass1) < 8 or len(pass1) > 64:
            text.markdown(''':red[パスワードの文字数は8~32文字です。]''')
        else:
            re_alnumsym = re.compile(r'^[!-\[\]-\}]+$')
            if re.match(re_alnumsym, pass1) == None:
                text.markdown(''':red[パスワードに使用できない文字が含まれています。]''')
            else:
                if fl.insert_user(username4, argon2.using(rounds=st.secrets["ROUND"], salt_size=128,digest_size=256).hash(pass1+st.secrets["PEPPER"]), mail):
                    #メールの送信
                    st.session_state.checker = 0
                    streamlit_rerun()
                else:
                    text.markdown(''':red[そのユーザー名はすでに使用されています。]''')

def check_new_password(mail, pass1,pass2, text):
    if pass1 != pass2:
        text.markdown(''':red[確認用パスワードがパスワードと異なります。]''')
    elif len(pass1) < 8 or len(pass1) > 64:
        text.markdown(''':red[パスワードの文字数は8~32文字です。]''')
    else:
        re_alnumsym = re.compile(r'^[!-\[\]-\}]+$')
        if re.match(re_alnumsym, pass1) == None:
            text.markdown(''':red[パスワードに使用できない文字が含まれています。]''')
        else:
            if fl.insert_changed_password(mail, argon2.using(rounds=st.secrets["ROUND"], salt_size=128,digest_size=256).hash(pass1+st.secrets["PEPPER"])):
                #メールの送信
                st.session_state.checker = 0
                streamlit_rerun()



def send_mail(title, text, mail_address):
    server = smtplib.SMTP(st.secrets["GMAIL_SMTP"],st.secrets["GMAIL_PORT"])
    server.starttls()

    login_address = st.secrets["GMAIL_ADDRESS"]
    server.login(login_address, st.secrets["GMAIL_PASSWORD"])

    message = MIMEMultipart()
    message["Subject"] = title
    message["From"] = login_address
    message["To"] = mail_address
    text = MIMEText(text)
    message.attach(text)
    server.send_message(message)
    server.quit()







#パネル関連の関数はこれ以降に書く

def login_main():
    #ログインのメインパネルを作成する関数
    username = st.text_input("ユーザー名またはメールアドレス")
    password = st.text_input("パスワード",type='password',max_chars=32)
    texts = st.empty()
    button = st.button("ログイン")
    btn = st.button("新規登録")
    btn2 = st.button("パスワード変更")
    delete_sidebar()
    if btn:
        st.session_state.checker = 1
        streamlit_rerun()
    if button:
        #ログインボタンが押された後の処理をここに書く。
        push_login_button(user_name=username,user_pass=password, texts=texts)
    if btn2:
        st.session_state.checker = 4
        streamlit_rerun()



def sign_up1():
    #新規登録のページを作成する関数
    mail = st.text_input("メールアドレス")
    texts2 = st.empty()
    button2 = st.button("メールを送信する")
    btn = st.button("ログイン画面へ")
    delete_sidebar()
    if button2:
        #メール送信ボタンが押された後の処理
        makeAccountCheckCode(address=mail,error_text=texts2)
    if btn:
        st.session_state.checker = 0
        streamlit_rerun()

def sign_up2(rand, mail_address):
    #メールアドレス確認後のパネル(確認コードの確認画面)を作成する。
    st.write("入力したメールアドレスに届いた認証コードを入力してください")
    checkcode = st.text_input("認証コード",max_chars=6)
    text = st.empty()
    button3 = st.button("確認する")
    delete_sidebar()
    if button3:
        if str(checkcode) == rand:
            st.session_state.checker = 3
            st.session_state.mail = mail_address
            streamlit_rerun()
        else:
            text = st.markdown(''':red[認証コードが違います]''')

def sign_up3(mail):
    #ユーザー情報登録画面
    username2 = st.text_input("ユーザー名", key="uname2",max_chars=16)
    st.markdown("""
                <ul>
                <li>ユーザー名は16文字以内で構成してください。</li>
                <li>ユーザー名は半角アルファベットと数字が使えます。</li>
                </ul>
                """, unsafe_allow_html=True)
    password = st.text_input("パスワード",type='password',max_chars=32)
    password2 = st.text_input("パスワード(確認用)",type='password',max_chars=32)
    st.markdown("""
                <ul>
                <li>パスワードは8~32文字で構成してください。</li>
                <li>パスワードは半角アルファベット、数字、記号が使えます。</li>
                </ul>
                """, unsafe_allow_html=True)
    text = st.empty()
    button = st.button("登録する")
    delete_sidebar()
    if button:
        registar_check(mail, username2, password, password2, text)



def change_password_panel():
    #パスワード変更の最初の画面
    username3 = st.text_input("ユーザー名またはメールアドレス", key="uname3")
    text2 = st.empty()
    button2 = st.button("パスワードを変更する")
    btn = st.button("ログイン画面へ")
    delete_sidebar()
    if button2:
        change_password_mail_check(username=username3, text=text2)
    if btn:
        st.session_state.checker = 0
        streamlit_rerun()

def change_password_panel2(rand, mail_address):
    #認証コード確認画面
    st.write("入力したメールアドレスに届いた認証コードを入力してください")
    checkcode = st.text_input("認証コード",max_chars=6)
    text = st.empty()
    button3 = st.button("確認する")
    delete_sidebar()
    if button3:
        if checkcode == rand:
            #認証コードが一緒な場合
            st.session_state.checker = 6
            st.session_state.mail = mail_address
            streamlit_rerun()
        else:
            text = st.markdown(''':red[認証コードが違います]''')

def remake_password(mail):
    password1 = st.text_input("パスワード",type='password',max_chars=32)
    password2 = st.text_input("パスワード(確認用)",type='password',max_chars=32)
    st.markdown("""
                <ul>
                <li>パスワードは8~32文字で構成してください。</li>
                <li>パスワードは半角アルファベット、数字、記号が使えます。</li>
                </ul>
                """, unsafe_allow_html=True)
    text = st.empty()
    button = st.button("再設定")
    delete_sidebar()
    if button:
        check_new_password(mail = mail,pass1 = password1,pass2=password2, text=text)



def page_select(num):
    if num == 0:
        login_main()
    if num == 1:
        sign_up1()
    if num == 2:
        sign_up2(rand=st.session_state.username, mail_address=st.session_state.mail)
    if num == 3:
        sign_up3(mail=st.session_state.mail)
    if num == 4:
        change_password_panel()
    if num == 5:
        change_password_panel2(rand=st.session_state.username ,mail_address=st.session_state.mail)
    if num == 6:
        remake_password(mail=st.session_state.mail)











#main関数
def main():
    page_config()
    if 'checker' not in st.session_state:
        st.session_state.checker = 0
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'mail' not in st.session_state:
        st.session_state.mail = ""
    #クッキーにセッションIDがあり、その期限内ならばログイン後のページに遷移する。
    sessionID = fc2.get_sessionID()
    if sessionID is None:
        res = [False,""]
    else:
        res = fl.check_session(sessionID)
    if res[0]:
       st.session_state.username = res[1]
       page_change()
    else:
        page_select(st.session_state.checker)

if __name__ == "__main__":
    main()