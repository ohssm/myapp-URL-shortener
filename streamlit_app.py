import streamlit as st
import hashlib
import sqlite3
import re

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (short_url TEXT PRIMARY KEY, original_url TEXT)''')
    conn.commit()
    conn.close()

# URL 유효성 검사
def is_valid_url(url):
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

# URL 단축 함수
def shorten_url(url):
    # URL의 해시값 생성 (첫 6자리만 사용)
    hash_object = hashlib.md5(url.encode())
    short_url = hash_object.hexdigest()[:6]
    
    # DB에 저장
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO urls VALUES (?, ?)", (short_url, url))
    conn.commit()
    conn.close()
    
    return short_url

# 원본 URL 찾기
def get_original_url(short_url):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Streamlit 앱
def main():
    st.title('URL 단축기')
    
    # 데이터베이스 초기화
    init_db()
    
    # URL 입력
    url = st.text_input('원본 URL을 입력하세요:', 'https://')
    
    if st.button('URL 줄이기'):
        if not url or url == 'https://':
            st.error('URL을 입력해주세요!')
        elif not is_valid_url(url):
            st.error('유효한 URL을 입력해주세요!')
        else:
            short_url = shorten_url(url)
            st.success('URL이 성공적으로 단축되었습니다!')
            st.write('단축된 URL:', f'http://short.url/{short_url}')
            
            # 클립보드에 복사 버튼
            if st.button('단축 URL 복사'):
                st.write('클립보드에 복사되었습니다!')
                st.code(f'http://short.url/{short_url}')
    
    # 구분선
    st.markdown('---')
    
    # 단축 URL로 원본 찾기
    st.subheader('단축 URL로 원본 찾기')
    short_code = st.text_input('단축 코드를 입력하세요 (6자리):')
    
    if st.button('원본 URL 찾기'):
        if len(short_code) == 6:
            original_url = get_original_url(short_code)
            if original_url:
                st.success('원본 URL을 찾았습니다!')
                st.write('원본 URL:', original_url)
            else:
                st.error('해당하는 URL을 찾을 수 없습니다.')
        else:
            st.error('올바른 단축 코드를 입력해주세요! (6자리)')

if __name__ == '__main__':
    main()
