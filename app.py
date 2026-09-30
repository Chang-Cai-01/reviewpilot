import streamlit as st
import pandas as pd
import plotly.express as px
from processor import process_batch
from llm_client import MODEL_FAST, MODEL_STRONG

st.set_page_config(page_title="ReviewPilot", page_icon="💬", layout="wide")

st.title("💬 ReviewPilot")
st.caption("客户评论智能分析与回复助手 · Powered by Claude")

# ============ 侧边栏 ============
with st.sidebar:
    st.header("⚙️ 配置")
    brand = st.text_input("品牌名", value="review")
    tone = st.selectbox("回复语气", ["亲切", "专业", "幽默"])
    demo_mode = st.checkbox("演示模式（只处理前10条）", value=True)
    model_choice = st.radio(
        "模型",
        ["快速模式 (Haiku)", "高质量模式 (Sonnet)"],
        help="Haiku 便宜快，Sonnet 效果更好但更贵",
    )
    model = MODEL_FAST if "Haiku" in model_choice else MODEL_STRONG
    st.divider()
    st.markdown("**使用说明**")
    st.markdown("1. 上传含 `review` 列的 CSV\n2. 点击开始分析\n3. 查看结果并导出")

# ============ Session State 初始化 ============
if "use_sample" not in st.session_state:
    st.session_state["use_sample"] = False

# ============ 上传 / 示例数据 ============
uploaded = st.file_uploader("📤 上传评论 CSV", type=["csv"])

if uploaded is None:
    st.info("👆 请上传 CSV 文件，或点击下面按钮使用示例数据")
    if st.button("📋 使用示例数据（10 条评论）"):
        st.session_state["use_sample"] = True
        st.rerun()

# ============ 加载数据 ============
if uploaded is not None:
    df = pd.read_csv(uploaded)
    if "review" not in df.columns:
        st.error("CSV 必须包含 `review` 列")
        st.stop()
    st.session_state["df"] = df
elif st.session_state["use_sample"]:
    if "df" not in st.session_state:
        st.session_state["df"] = pd.DataFrame({
            "review": [
                "质量很好，物流也快，下次还来！",
                "收到货有点破损，客服态度还不好，差评。",
                "东西还行吧，价格有点贵。",
                "用了一周就坏了，什么破质量！",
                "包装很精美，送人很合适。",
                "客服回复很及时，问题解决得很快。",
                "尺码偏小，建议买大一号。",
                "颜色和图片有点色差，但整体还行。",
                "性价比很高，回购第三次了。",
                "发货太慢了，等了一周才到。",
            ]
        })
else:
    st.stop()

df = st.session_state["df"]
if demo_mode:
    df = df.head(10)

st.success(f"已加载 {len(df)} 条评论")
st.dataframe(df.head(), use_container_width=True)

# ============ 开始分析 ============
if st.button("🚀 开始分析", type="primary"):
    progress = st.progress(0, text="准备中...")

    def update(done, total):
        progress.progress(done / total, text=f"处理中 {done}/{total}")

    try:
        with st.spinner("AI 正在分析中..."):
            results = process_batch(
                reviews=df["review"].astype(str).tolist(),
                brand=brand,
                tone=tone,
                model=model,
                progress_callback=update,
            )
        progress.empty()
        st.session_state["results"] = pd.DataFrame(results)
    except Exception as e:
        progress.empty()
        st.error(f"分析失败：{e}")
        st.exception(e)

# ============ 结果展示 ============
if "results" in st.session_state:
    result_df = st.session_state["results"]

    st.divider()
    st.subheader("📊 分析结果")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总评论数", len(result_df))
    col2.metric("正面", (result_df["sentiment"] == "positive").sum())
    col3.metric("负面", (result_df["sentiment"] == "negative").sum())
    col4.metric("中性", (result_df["sentiment"] == "neutral").sum())

    fig = px.pie(
        result_df, names="sentiment", title="情感分布",
        color="sentiment",
        color_discrete_map={
            "positive": "#2ecc71",
            "neutral": "#f39c12",
            "negative": "#e74c3c",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    all_pains = []
    for p in result_df["pain_points"].dropna():
        if p:
            all_pains.extend(p.split("、"))
    if all_pains:
        pain_df = pd.Series(all_pains).value_counts().head(5).reset_index()
        pain_df.columns = ["痛点", "出现次数"]
        fig2 = px.bar(pain_df, x="出现次数", y="痛点", orientation="h", title="Top 5 痛点")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 详细结果")
    st.dataframe(result_df, use_container_width=True, height=400)

    csv_bytes = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 下载结果 CSV",
        csv_bytes,
        "reviewpilot_result.csv",
        "text/csv",
        type="primary",
    )