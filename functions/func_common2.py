import streamlit as st
import streamlit.components.v1 as components
import extra_streamlit_components as stx
import uuid

import functions.func_login as fl
import functions.func_common as fc

def get_sessionID():
    #streamlitの標準機能でできないか色々と試しましたが、難しかったため、新たなライブラリを使用しました。
    #pip install extra-streamlit-components
    #でライブラリのインストールをお願いします。
    #また、この関数を使用する際はset_page_config()などのページコンフィグを設定した後に使用してください。
    return stx.CookieManager().get(cookie='sessionID')

def _page_change():
    html = '''
    <script>
    doc = window.parent.document;
    elems = doc.querySelectorAll('[data-testid="stSidebarNav"]>ul>*');
    elem = elems[0];
    elem = elem.getElementsByTagName('a')[0];
    elem.click()
    </script>
    '''
    components.html(html, height=0, width=0,)

def setUsername():
    rec = fl.check_session(get_sessionID())
    if rec[0]:
        st.session_state.username = rec[1]
    else:
        #login-homeに戻す
        _page_change()

def _delete_from_sessionID(sessionID):
    connection = fc.get_connection_to_MySQL()
    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE  FROM `session` WHERE `Id` = %s"
            cursor.execute(sql, (sessionID))
        connection.commit()

def logout():
    #cookieのUUIDを変更して、loginページへ遷移する。
    #get old sessionID
    old = get_sessionID()
    #delete data which sessionID is old
    _delete_from_sessionID(old)
    #set new sessionID
    value = uuid.uuid4()
    js = f'''
    <script>
    window.parent.document.cookie = "sessionID={value}";
    </script>
    '''
    components.html(js, height=0, width=0,)
    #ページ遷移
    _page_change()

def put_logout_button():
    return  st.button("Logout", on_click=logout)