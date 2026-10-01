# ReviewPilot 💬

> 客户评论智能分析与回复助手 —— 用 Claude 批量完成情感分类、痛点提取与回复生成

---

## 🎯 项目简介

电商和社媒运营每天面对大量客户评论，人工逐条阅读、判断情感、写回复效率低。ReviewPilot 让运营上传 CSV，自动完成情感分类、痛点提取和回复生成。

---

## ✨ 核心功能

- 📤 上传 CSV（自动识别 `review` 列）
- 🎯 情感分类（正面 / 中性 / 负面）
- 🔍 痛点提取
- 💬 智能回复（亲切 / 专业 / 幽默三种语气）
- 📊 可视化（情感分布饼图 + Top 5 痛点柱状图）
- 📥 导出结果 CSV
- 🚀 双模型切换（Haiku / Sonnet）

---

## 🔧 技术栈

- 前端：Streamlit
- AI：Claude API（通过 iuseapi 中转）
- 数据处理：pandas
- 并发：ThreadPoolExecutor
- 可视化：Plotly
- 部署：Streamlit Cloud

---

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone git@github.com:Chang-Cai-01/reviewpilot.git
cd reviewpilot

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
# 复制 .env.example 为 .env，填入 iuseapi 令牌
# ANTHROPIC_API_KEY=sk-你的令牌

# 5. 运行
streamlit run app.py

🌐 在线体验
https://reviewpilot-ejr3ek9fe5ygjpewfvyxfg.streamlit.app

📂 项目结构
```text
reviewpilot/
│
├── app.py                  # Streamlit 主程序
├── prompts.py              # Prompt 模板
├── llm_client.py           # Claude API 封装
├── processor.py            # 批处理逻辑
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
📄 License
MIT License

---

## 保存与推送

1. 在 Cursor 里打开 `README.md`
2. 全部替换成上面的内容
3. `Ctrl + S` 保存

然后在 Cursor 终端执行：

```powershell
git add README.md
git commit -m "docs: simplify README"
git push
