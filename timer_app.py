import streamlit as st
import time
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 페이지 설정
st.set_page_config(
    page_title="⏰ Fancy Timer App",
    page_icon="⏰",
    layout="wide",
)

# CSS 스타일 적용
st.markdown("""
<style>
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    @keyframes glow {
        0% {text-shadow: 0 0 10px rgba(255, 75, 75, 0.5);}
        50% {text-shadow: 0 0 20px rgba(255, 75, 75, 0.8), 0 0 30px rgba(255, 75, 75, 0.6), 0 0 40px rgba(255, 75, 75, 0.4);}
        100% {text-shadow: 0 0 10px rgba(255, 75, 75, 0.5);}
    }
    
    @keyframes pulse {
        0% {transform: scale(1);}
        50% {transform: scale(1.05);}
        100% {transform: scale(1);}
    }
    
    .main {
        background: linear-gradient(-45deg, #1E1E1E, #2E2E2E, #1a1a1a, #2a2a2a);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        font-size: 18px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(45deg, #FF6B6B, #FF4B4B);
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.5);
    }
    
    .timer-display {
        font-family: 'Arial Black', sans-serif;
        font-size: 80px !important;
        background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        animation: glow 2s ease-in-out infinite, pulse 2s ease-in-out infinite;
    }
    
    .css-1kyxreq {
        justify-content: center;
    }
    
    /* 입력 필드 스타일링 */
    .stNumberInput input {
        background: rgba(255, 75, 75, 0.1);
        border: 2px solid rgba(255, 75, 75, 0.3);
        border-radius: 10px;
        color: #FF4B4B !important;
        transition: all 0.3s ease;
    }
    
    .stNumberInput input:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.3);
    }
    
    /* 프로그레스 바 컨테이너 스타일링 */
    .js-plotly-plot {
        animation: pulse 2s ease-in-out infinite;
    }
</style>

<!-- 파티클 효과를 위한 canvas -->
<canvas id="particles" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;"></canvas>

<script>
const canvas = document.getElementById('particles');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];
const particleCount = 50;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 3 - 1.5;
        this.speedY = Math.random() * 3 - 1.5;
        this.color = `rgba(255, ${Math.floor(Math.random() * 75) + 75}, 75, ${Math.random() * 0.5 + 0.3})`;
    }
    
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        if (this.y < 0) this.y = canvas.height;
    }
    
    draw() {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

// 파티클 초기화
for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });
    
    requestAnimationFrame(animate);
}

animate();
</script>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration' not in st.session_state:
    st.session_state.duration = 0
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'pause_time' not in st.session_state:
    st.session_state.pause_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0

# 자동 새로고침 (1초마다)
st_autorefresh(interval=1000, key="timer_refresh")

# 타이틀
st.markdown("<h1 style='text-align: center; color: #FF4B4B; margin-bottom: 50px;'>⏰ Fancy Timer</h1>", unsafe_allow_html=True)

# 타이머 컨트롤 컬럼 설정
col1, col2, col3 = st.columns([1,2,1])

with col2:
    # 시간 입력
    hours = st.number_input("시간", min_value=0, max_value=23, value=0, key="hours")
    minutes = st.number_input("분", min_value=0, max_value=59, value=0, key="minutes")
    seconds = st.number_input("초", min_value=0, max_value=59, value=0, key="seconds")
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    # 버튼 컨테이너
    button_cols = st.columns([1,1,1])
    
    # 시작/일시정지 버튼
    with button_cols[0]:
        if not st.session_state.is_running:
            if st.button("시작 ▶"):
                st.session_state.duration = total_seconds
                st.session_state.start_time = time.time()
                st.session_state.is_running = True
        else:
            if st.button("일시정지 ⏸"):
                st.session_state.is_running = False
                st.session_state.pause_time = time.time()
                st.session_state.elapsed_time += time.time() - st.session_state.start_time
    
    # 재개 버튼
    with button_cols[1]:
        if not st.session_state.is_running and st.session_state.pause_time:
            if st.button("재개 ⏵"):
                st.session_state.is_running = True
                st.session_state.start_time = time.time()
    
    # 리셋 버튼
    with button_cols[2]:
        if st.button("리셋 🔄"):
            st.session_state.start_time = None
            st.session_state.is_running = False
            st.session_state.pause_time = None
            st.session_state.elapsed_time = 0

# 타이머 디스플레이 로직
if st.session_state.is_running:
    elapsed = st.session_state.elapsed_time + (time.time() - st.session_state.start_time)
    remaining = max(st.session_state.duration - elapsed, 0)
    
    if remaining == 0:
        st.session_state.is_running = False
        st.balloons()
        st.snow()
        st.markdown("""
            <div style="text-align: center; animation: celebrate 1s ease-in-out infinite;">
                <h1 style="font-size: 48px; background: linear-gradient(45deg, #FF4B4B, #FFD700, #FF4B4B);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                           text-shadow: 0 0 20px rgba(255, 75, 75, 0.5);">
                    🎉 타이머 완료! �
                </h1>
            </div>
            <style>
                @keyframes celebrate {
                    0% {transform: scale(1);}
                    50% {transform: scale(1.1);}
                    100% {transform: scale(1);}
                }
            </style>
        """, unsafe_allow_html=True)
else:
    if st.session_state.start_time is None:
        remaining = total_seconds
    else:
        remaining = max(st.session_state.duration - st.session_state.elapsed_time, 0)

# 시각적 타이머 디스플레이
hours_remaining = int(remaining // 3600)
minutes_remaining = int((remaining % 3600) // 60)
seconds_remaining = int(remaining % 60)

# 원형 프로그레스 차트
if st.session_state.duration > 0:
    progress = 1 - (remaining / st.session_state.duration)
else:
    progress = 0

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = progress * 100,
    domain = {'x': [0, 1], 'y': [0, 1]},
    gauge = {
        'axis': {'range': [0, 100]},
        'bar': {'color': "#FF4B4B"},
        'bgcolor': "lightgray",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 100], 'color': '#1E1E1E'}
        ]
    }
))

fig.update_layout(
    height=300,
    font={'color': "#FF4B4B", 'size': 20},
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# 타이머 디스플레이
st.markdown(f"""
    <div class="timer-display">
        {hours_remaining:02d}:{minutes_remaining:02d}:{seconds_remaining:02d}
    </div>
""", unsafe_allow_html=True)

# 프로그레스 차트 표시
st.plotly_chart(fig, use_container_width=True)
