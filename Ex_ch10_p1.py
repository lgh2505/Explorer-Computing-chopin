# 아래에 코드를 작성해주세요.
import streamlit as st
import pandas as pd

st.markdown("# 나의 소개 페이지")
st.markdown("## 자기소개")
st.markdown("안녕하세요, 저는 음악학과 25학번 이건희입니다. 저는 **음악**, **심리학**, **코딩**에 관심이 있습니다. 이번 자기소개를 통해 제가 좋아하는 것들에 대해 소개하고자 합니다.")

st.markdown("### 좋아하는 것")
st.text("저는 음악 듣는 것과 글쓰기를 좋아합니다.")
st.markdown("최근 연습하고 있는 클래식 음악은 [쇼팽 발라드 1번](https://www.youtube.com/watch?v=xVuKQ9Pr0b8)입니다.")

st.write("### 좋아하는 음악") 
st.write(pd.DataFrame({"음악가": ['Day6','하현상','백예린'], "제목" : [{'한 페이지가 될 수 있게','어쩌다 보니', 'Hi Hello'},{'MAGIC','불꽃놀이','하이웨이'},{'0310','Bye bye my blue', '산책'}]})) # 데이터프레임
st.write(pd.DataFrame({"작품" : ['위키드(Wicked)', '위대한 쇼맨(The Greatest Showman)', '멜로가 체질'], "장르" : ['뮤지컬', '영화', '드라마'], "OST 제목" : ['For Good', 'Never Enough', 'Moonlight']}))

st.write("### 관심있는 수학 공식")
st.latex(r"P(A∩B)=P(A)×P(B∣A)")
st.caption("확률의 곱셈법칙입니다. A와 B가 일어날 확률은 A가 일어날 확률에 A가 일어났을 때 B가 일어날 확률을 곱한 것이라는 의미를 담고 있습니다.")

st.markdown("### 앞으로의 목표")
st.write("컴퓨팅 탐색 수업을 통해 python과 더 친해지고, 게임, GUI 프로그램 등 다양한 프로그램을 만들고 싶습니다.")
st.caption("python으로 인사하기")
st.code("print('읽어주셔서 감사합니다.')", language="python")