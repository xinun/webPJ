import streamlit as st
import random

st.title("🎲 로또 번호 생성기")

if st.button("번호 뽑기"):
    numbers = sorted(random.sample(range(1, 46), 6))
    st.success(f"✨ 생성된 번호: {numbers}")
