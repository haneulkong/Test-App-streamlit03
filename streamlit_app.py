import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Streamlit 앱 제목
st.title("Button Controlled Plot in Streamlit")

# 버튼 추가
if st.button("Show Plot"):
    # 데이터 생성
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # 그래프 그리기
    fig, ax = plt.subplots()
    ax.plot(x, y, label="y = sin(x)")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_title("Simple Line Plot")
    ax.legend()

    # Streamlit에서 그래프 보여주기
    st.pyplot(fig)
else:
    st.write("Click the button to show the plot!")
