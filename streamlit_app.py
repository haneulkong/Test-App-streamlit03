import streamlit as st  

# 제목  
st.title("계산기")  

# 사용자 입력  
num1 = st.number_input("첫 번째 숫자를 입력하세요:", value=0)  
num2 = st.number_input("두 번째 숫자를 입력하세요:", value=0)  
operation = st.selectbox("연산을 선택하세요:", ["덧셈", "뺄셈", "곱셈", "나눗셈"])  

# 연산 수행  
if st.button("계산하기"):  
    if operation == "덧셈":  
        result = num1 + num2  
        st.success(f"결과: {result}")  
    elif operation == "뺄셈":  
        result = num1 - num2  
        st.success(f"결과: {result}")  
    elif operation == "곱셈":  
        result = num1 * num2  
        st.success(f"결과: {result}")  
    elif operation == "나눗셈":  
        if num2 != 0:  
            result = num1 / num2  
            st.success(f"결과: {result}")  
        else:  
            st.error("0으로 나눌 수 없습니다.")
