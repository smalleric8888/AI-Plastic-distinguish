import plotly.graph_objects as go
import streamlit as st

def plot_confidence_top3_chart(top3_data):
    """繪製 Top-3 材質信心度排名橫向長條圖"""
    materials = [item["material"] for item in reversed(top3_data)]
    confidences = [item["confidence"] for item in reversed(top3_data)]

    colors = ['#94A3B8', '#3B82F6', '#10B981']  # 金銀銅配色

    fig = go.Figure(go.Bar(
        x=confidences,
        y=materials,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{c}%" for c in confidences],
        textposition='auto',
    ))

    fig.update_layout(
        title="📊 AI 綜合材質前三名信心度排名 (Top 3)",
        height=220,
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis=dict(range=[0, 100], title="信心度 (%)"),
        yaxis=dict(title="材質"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_audio_waveform_and_fft(audio_analysis_res):
    """繪製 Plotly 時域波形與 FFT 頻譜圖"""
    sig = audio_analysis_res["signal"]
    freqs = audio_analysis_res["freqs"]
    fft_vals = audio_analysis_res["fft_vals"]
    peak_freq = audio_analysis_res["peak_freq"]
    centroid = audio_analysis_res.get("spectral_centroid", peak_freq)

    # 1. 波形圖
    fig_wave = go.Figure()
    fig_wave.add_trace(go.Scatter(y=sig[::5], mode='lines', name='波形', line=dict(color='#2563EB')))
    fig_wave.update_layout(
        title="敲擊聲時域波形圖 (Time Domain Waveform)",
        height=230,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_wave, use_container_width=True)

    # 2. 頻譜圖
    fig_fft = go.Figure()
    fig_fft.add_trace(go.Scatter(x=freqs[:400], y=fft_vals[:400], mode='lines', name='FFT 頻譜', line=dict(color='#10B981')))
    fig_fft.update_layout(
        title=f"🎼 頻譜分析 (主峰值: {peak_freq} Hz | 頻譜重心: {centroid} Hz)",
        height=230,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_fft, use_container_width=True)
