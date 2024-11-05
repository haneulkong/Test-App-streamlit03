import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from textblob import TextBlob
import plotly.express as px
import re
import json

class DiaryApp:
    def __init__(self):
        # 데이터베이스 초기화
        self.conn = sqlite3.connect('diary.db', check_same_thread=False)
        self.create_table()
        
    def create_table(self):
        """데이터베이스 테이블 생성"""
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS entries
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             date TEXT NOT NULL,
             title TEXT NOT NULL,
             content TEXT NOT NULL,
             mood TEXT,
             tags TEXT,
             sentiment REAL)
        ''')
        self.conn.commit()

    def add_entry(self, date, title, content, mood, tags):
        """일기 항목 추가"""
        # 감정 분석
        blob = TextBlob(content)
        sentiment = blob.sentiment.polarity
        
        # 태그 처리
        tags_json = json.dumps(tags)
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO entries (date, title, content, mood, tags, sentiment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, title, content, mood, tags_json, sentiment))
        self.conn.commit()

    def get_entries(self):
        """모든 일기 항목 가져오기"""
        return pd.read_sql('SELECT * FROM entries ORDER BY date DESC', self.conn)

    def search_entries(self, keyword):
        """일기 검색"""
        query = '''
            SELECT * FROM entries 
            WHERE title LIKE ? OR content LIKE ? 
            ORDER BY date DESC
        '''
        return pd.read_sql(query, self.conn, params=(f'%{keyword}%', f'%{keyword}%'))

    def get_entry_by_id(self, entry_id):
        """ID로 일기 항목 가져오기"""
        return pd.read_sql('SELECT * FROM entries WHERE id = ?', self.conn, params=(entry_id,))

    def delete_entry(self, entry_id):
        """일기 항목 삭제"""
        c = self.conn.cursor()
        c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()

def main():
    st.set_page_config(page_title="나의 일기장", layout="wide")
    
    # 앱 초기화
    if 'diary_app' not in st.session_state:
        st.session_state.diary_app = DiaryApp()
    
    # 사이드바 메뉴
    menu = st.sidebar.selectbox(
        "메뉴",
        ["새 일기 쓰기", "일기 목록", "감정 분석", "검색"]
    )
    
    if menu == "새 일기 쓰기":
        st.title("✍️ 새로운 일기 쓰기")
        
        # 일기 입력 폼
        with st.form("diary_form"):
            date = st.date_input("날짜", datetime.now())
            title = st.text_input("제목")
            content = st.text_area("내용", height=300)
            mood = st.selectbox("오늘의 기분", ["😊 행복", "😌 평온", "😢 슬픔", "😠 화남", "😴 피곤"])
            tags_input = st.text_input("태그 (쉼표로 구분)")
            
            submit = st.form_submit_button("저장")
            
            if submit and title and content:
                tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                st.session_state.diary_app.add_entry(
                    date.strftime("%Y-%m-%d"),
                    title,
                    content,
                    mood,
                    tags
                )
                st.success("일기가 저장되었습니다!")
    
    elif menu == "일기 목록":
        st.title("📖 일기 목록")
        entries = st.session_state.diary_app.get_entries()
        
        if not entries.empty:
            for _, entry in entries.iterrows():
                with st.expander(f"{entry['date']} - {entry['title']}"):
                    st.write(f"**기분:** {entry['mood']}")
                    st.write(entry['content'])
                    tags = json.loads(entry['tags'])
                    if tags:
                        st.write("**태그:**", ", ".join(tags))
                    
                    if st.button("삭제", key=f"delete_{entry['id']}"):
                        st.session_state.diary_app.delete_entry(entry['id'])
                        st.experimental_rerun()
        else:
            st.info("아직 작성된 일기가 없습니다.")
    
    elif menu == "감정 분석":
        st.title("📊 감정 분석")
        entries = st.session_state.diary_app.get_entries()
        
        if not entries.empty:
            # 감정 추이 그래프
            fig = px.line(entries, x='date', y='sentiment',
                         title='일기 감정 분석 추이',
                         labels={'sentiment': '긍정도', 'date': '날짜'})
            st.plotly_chart(fig)
            
            # 기분 분포 파이 차트
            mood_counts = entries['mood'].value_counts()
            fig_pie = px.pie(values=mood_counts.values,
                           names=mood_counts.index,
                           title='기분 분포')
            st.plotly_chart(fig_pie)
        else:
            st.info("분석할 데이터가 없습니다.")
    
    elif menu == "검색":
        st.title("🔍 일기 검색")
        search_term = st.text_input("검색어를 입력하세요")
        
        if search_term:
            results = st.session_state.diary_app.search_entries(search_term)
            if not results.empty:
                for _, entry in results.iterrows():
                    with st.expander(f"{entry['date']} - {entry['title']}"):
                        st.write(f"**기분:** {entry['mood']}")
                        st.write(entry['content'])
                        tags = json.loads(entry['tags'])
                        if tags:
                            st.write("**태그:**", ", ".join(tags))
            else:
                st.info("검색 결과가 없습니다.")

if __name__ == "__main__":
    main()
