import os
import json
import yaml
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd

# Visualization & graph libs
import plotly.express as px
from io import StringIO

try:
    import openai
except ImportError:
    openai = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import requests
except ImportError:
    requests = None

try:
    import networkx as nx
    from pyvis.network import Network
except ImportError:
    nx = None
    Network = None

import streamlit.components.v1 as components


# =========================
# WOW UI CONFIG
# =========================

UI_TEXT = {
    "zh": {
        "app_title": "🏥 GUDID 智能代理系統 — WOW 供應鏈分析",
        "chat_tab": "💬 對話介面",
        "agents_tab": "🤖 代理資訊",
        "analytics_tab": "📊 儀表板",
        "agent_hq_tab": "🧠 Agent Headquarters",
        "docs_tab": "📚 使用說明",
        "settings_header": "⚙️ 系統設定",
        "wow_ui_header": "🎨 WOW UI",
        "theme_label": "主題模式",
        "theme_light": "亮色",
        "theme_dark": "暗色",
        "lang_label": "介面語言",
        "lang_zh": "繁體中文",
        "lang_en": "English",
        "style_label": "畫家風格",
        "style_jackslot": "🎰 Jackslot 風格",
        "style_wheel": "🎡 幸運轉盤",
        "api_keys_header": "🔑 API 金鑰設定",
        "api_configured_env": "已從環境變數載入",
        "api_enter_key": "請輸入金鑰",
        "save_keys": "💾 儲存金鑰（本工作階段）",
        "select_agent": "選擇代理",
        "system_status": "📊 系統狀態",
        "active_agents": "活躍代理",
        "processed_requests": "處理請求",
        "clear_chat": "🗑️ 清除對話",
        "chat_subheader": "對話介面",
        "chat_input_placeholder": "請輸入您的查詢...",
        "no_analytics": "尚無分析資料。請開始使用系統以查看統計資訊。",
        "agent_usage_stats": "代理使用統計",
        "recent_activity": "最近活動",
        "supply_chain_analytics": "供應鏈分析",
        "upload_csv": "上傳 Packing List CSV (或使用內建範例)",
        "summary_tables": "📋 數據摘要表",
        "dist_charts": "📈 分佈圖與關聯圖",
        "agent_hq_intro": "逐一執行代理，調整提示與模型，並將輸出串接為下一個代理的輸入。",
        "agent_hq_select_agent": "選擇要執行的代理",
        "agent_hq_user_input": "使用者輸入 / 資料內容",
        "agent_hq_system_prompt": "系統提示（可覆寫，留空使用預設）",
        "agent_hq_model": "選擇模型",
        "agent_hq_max_tokens": "最大輸出 Token（預設 12000，實際視模型支援而定）",
        "agent_hq_run": "🚀 執行代理",
        "agent_hq_output": "代理輸出",
        "agent_hq_view_mode": "檢視模式",
        "view_markdown": "Markdown",
        "view_text": "純文字",
        "agent_hq_edit_output": "可編輯輸出（作為下一個代理的輸入）",
        "agent_hq_use_as_next": "➡️ 將上方內容作為下一個代理輸入",
        "skills_header": "技能說明（來自 SKILL.md）",
    },
    "en": {
        "app_title": "🏥 GUDID Agentic AI — WOW Supply Chain Analytics",
        "chat_tab": "💬 Chat",
        "agents_tab": "🤖 Agents",
        "analytics_tab": "📊 Dashboards",
        "agent_hq_tab": "🧠 Agent Headquarters",
        "docs_tab": "📚 Docs",
        "settings_header": "⚙️ System Settings",
        "wow_ui_header": "🎨 WOW UI",
        "theme_label": "Theme",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "lang_label": "Language",
        "lang_zh": "Traditional Chinese",
        "lang_en": "English",
        "style_label": "Painter Style",
        "style_jackslot": "🎰 Jackslot Style",
        "style_wheel": "🎡 Lucky Wheel",
        "api_keys_header": "🔑 API Keys",
        "api_configured_env": "Loaded from environment",
        "api_enter_key": "Enter API key",
        "save_keys": "💾 Save keys (this session)",
        "select_agent": "Select agent",
        "system_status": "📊 System Status",
        "active_agents": "Active agents",
        "processed_requests": "Processed requests",
        "clear_chat": "🗑️ Clear conversation",
        "chat_subheader": "Chat",
        "chat_input_placeholder": "Enter your query...",
        "no_analytics": "No analytics yet. Use the system to populate statistics.",
        "agent_usage_stats": "Agent usage statistics",
        "recent_activity": "Recent activity",
        "supply_chain_analytics": "Supply Chain Analytics",
        "upload_csv": "Upload Packing List CSV (or use built-in sample)",
        "summary_tables": "📋 Summary Tables",
        "dist_charts": "📈 Distribution & Relation Graphs",
        "agent_hq_intro": "Run agents one by one, tune prompts/models, and chain outputs into the next agent.",
        "agent_hq_select_agent": "Select agent to run",
        "agent_hq_user_input": "User input / data context",
        "agent_hq_system_prompt": "System prompt (override; leave empty to use default)",
        "agent_hq_model": "Model",
        "agent_hq_max_tokens": "Max output tokens (default 12000; subject to model limits)",
        "agent_hq_run": "🚀 Run agent",
        "agent_hq_output": "Agent output",
        "agent_hq_view_mode": "View mode",
        "view_markdown": "Markdown",
        "view_text": "Plain text",
        "agent_hq_edit_output": "Editable output (feed into next agent)",
        "agent_hq_use_as_next": "➡️ Use above content as next agent input",
        "skills_header": "Skills (from SKILL.md)",
    },
}

PAINTER_STYLES = [
    {
        "id": "van_gogh",
        "name_en": "Van Gogh — Starry Night",
        "name_zh": "梵谷 — 星夜",
        "accent": "#fbbf24",
        "bg_light": "linear-gradient(135deg,#eff6ff,#dbeafe)",
        "bg_dark": "linear-gradient(135deg,#0b1120,#1e293b)",
        "text_light": "#0f172a",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "monet",
        "name_en": "Monet — Water Lilies",
        "name_zh": "莫內 — 睡蓮",
        "accent": "#22c55e",
        "bg_light": "linear-gradient(135deg,#ecfdf3,#d1fae5)",
        "bg_dark": "linear-gradient(135deg,#022c22,#064e3b)",
        "text_light": "#064e3b",
        "text_dark": "#ecfdf3",
    },
    {
        "id": "picasso_blue",
        "name_en": "Picasso — Blue Period",
        "name_zh": "畢卡索 — 藍色時期",
        "accent": "#38bdf8",
        "bg_light": "linear-gradient(135deg,#e0f2fe,#bae6fd)",
        "bg_dark": "linear-gradient(135deg,#020617,#0f172a)",
        "text_light": "#0f172a",
        "text_dark": "#e5f2ff",
    },
    {
        "id": "mondrian",
        "name_en": "Mondrian — Neoplasticism",
        "name_zh": "蒙德里安 — 新造型主義",
        "accent": "#ef4444",
        "bg_light": "linear-gradient(135deg,#f9fafb,#e5e7eb)",
        "bg_dark": "linear-gradient(135deg,#020617,#111827)",
        "text_light": "#111827",
        "text_dark": "#f9fafb",
    },
    {
        "id": "hokusai",
        "name_en": "Hokusai — Great Wave",
        "name_zh": "葛飾北齋 — 神奈川沖浪裏",
        "accent": "#0ea5e9",
        "bg_light": "linear-gradient(135deg,#e0f2fe,#fef9c3)",
        "bg_dark": "linear-gradient(135deg,#020617,#0f172a)",
        "text_light": "#082f49",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "klimt",
        "name_en": "Klimt — Golden Phase",
        "name_zh": "克林姆 — 黃金時期",
        "accent": "#facc15",
        "bg_light": "linear-gradient(135deg,#fffbeb,#fef3c7)",
        "bg_dark": "linear-gradient(135deg,#1f2937,#111827)",
        "text_light": "#78350f",
        "text_dark": "#fef9c3",
    },
    {
        "id": "munch",
        "name_en": "Munch — The Scream",
        "name_zh": "孟克 — 吶喊",
        "accent": "#fb923c",
        "bg_light": "linear-gradient(135deg,#fff7ed,#fee2e2)",
        "bg_dark": "linear-gradient(135deg,#111827,#4b5563)",
        "text_light": "#111827",
        "text_dark": "#f9fafb",
    },
    {
        "id": "pollock",
        "name_en": "Pollock — Drip Paint",
        "name_zh": "波洛克 — 滴畫",
        "accent": "#22d3ee",
        "bg_light": "linear-gradient(135deg,#f1f5f9,#e5e7eb)",
        "bg_dark": "linear-gradient(135deg,#020617,#1e293b)",
        "text_light": "#020617",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "warhol",
        "name_en": "Warhol — Pop Art",
        "name_zh": "華荷 — 普普藝術",
        "accent": "#ec4899",
        "bg_light": "linear-gradient(135deg,#fdf2f8,#fee2e2)",
        "bg_dark": "linear-gradient(135deg,#1f2937,#4b5563)",
        "text_light": "#1e293b",
        "text_dark": "#f9fafb",
    },
    {
        "id": "dali",
        "name_en": "Dalí — Surrealism",
        "name_zh": "達利 — 超現實",
        "accent": "#a855f7",
        "bg_light": "linear-gradient(135deg,#eef2ff,#e0f2fe)",
        "bg_dark": "linear-gradient(135deg,#020617,#111827)",
        "text_light": "#111827",
        "text_dark": "#e5e7eb",
    },
    # 10 more simple variations to reach 20
    {
        "id": "cezanne",
        "name_en": "Cézanne — Landscapes",
        "name_zh": "塞尚 — 風景畫",
        "accent": "#16a34a",
        "bg_light": "linear-gradient(135deg,#ecfdf5,#cffafe)",
        "bg_dark": "linear-gradient(135deg,#022c22,#0f172a)",
        "text_light": "#022c22",
        "text_dark": "#ecfdf5",
    },
    {
        "id": "chagall",
        "name_en": "Chagall — Dreamscapes",
        "name_zh": "夏卡爾 — 夢境",
        "accent": "#a855f7",
        "bg_light": "linear-gradient(135deg,#fdf2ff,#eff6ff)",
        "bg_dark": "linear-gradient(135deg,#111827,#312e81)",
        "text_light": "#111827",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "gauguin",
        "name_en": "Gauguin — Tahiti",
        "name_zh": "高更 — 大溪地",
        "accent": "#fb7185",
        "bg_light": "linear-gradient(135deg,#fff7ed,#fee2e2)",
        "bg_dark": "linear-gradient(135deg,#7f1d1d,#111827)",
        "text_light": "#111827",
        "text_dark": "#fee2e2",
    },
    {
        "id": "renoir",
        "name_en": "Renoir — Impression",
        "name_zh": "雷諾瓦 — 印象",
        "accent": "#f97316",
        "bg_light": "linear-gradient(135deg,#fff7ed,#fef9c3)",
        "bg_dark": "linear-gradient(135deg,#111827,#4b5563)",
        "text_light": "#111827",
        "text_dark": "#f9fafb",
    },
    {
        "id": "whistler",
        "name_en": "Whistler — Tonal",
        "name_zh": "惠斯勒 — 調性畫",
        "accent": "#0ea5e9",
        "bg_light": "linear-gradient(135deg,#e5e7eb,#f3f4f6)",
        "bg_dark": "linear-gradient(135deg,#020617,#111827)",
        "text_light": "#020617",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "kandinsky",
        "name_en": "Kandinsky — Abstract",
        "name_zh": "康定斯基 — 抽象",
        "accent": "#22c55e",
        "bg_light": "linear-gradient(135deg,#f9fafb,#e5e7eb)",
        "bg_dark": "linear-gradient(135deg,#020617,#020617)",
        "text_light": "#020617",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "miro",
        "name_en": "Miró — Constellations",
        "name_zh": "米羅 — 星座",
        "accent": "#facc15",
        "bg_light": "linear-gradient(135deg,#eef2ff,#fef9c3)",
        "bg_dark": "linear-gradient(135deg,#020617,#111827)",
        "text_light": "#111827",
        "text_dark": "#fef9c3",
    },
    {
        "id": "magritte",
        "name_en": "Magritte — Surreal Skies",
        "name_zh": "馬格利特 — 超現實天空",
        "accent": "#38bdf8",
        "bg_light": "linear-gradient(135deg,#e0f2fe,#f9fafb)",
        "bg_dark": "linear-gradient(135deg,#0f172a,#1e293b)",
        "text_light": "#0f172a",
        "text_dark": "#e5e7eb",
    },
    {
        "id": "rothko",
        "name_en": "Rothko — Color Fields",
        "name_zh": "羅斯科 — 色塊",
        "accent": "#ea580c",
        "bg_light": "linear-gradient(135deg,#fee2e2,#fef3c7)",
        "bg_dark": "linear-gradient(135deg,#111827,#4b5563)",
        "text_light": "#111827",
        "text_dark": "#f9fafb",
    },
    {
        "id": "frida",
        "name_en": "Frida Kahlo — Vivid Portraits",
        "name_zh": "芙烈達 — 鮮豔肖像",
        "accent": "#ec4899",
        "bg_light": "linear-gradient(135deg,#fdf2f8,#dcfce7)",
        "bg_dark": "linear-gradient(135deg,#111827,#4b5563)",
        "text_light": "#111827",
        "text_dark": "#f9fafb",
    },
]


def tr(key: str) -> str:
    lang = st.session_state.get("lang", "zh")
    return UI_TEXT.get(lang, UI_TEXT["en"]).get(key, key)


def current_style():
    idx = st.session_state.get("painter_style_idx", 0) % len(PAINTER_STYLES)
    return PAINTER_STYLES[idx]


def apply_wow_theme():
    theme = st.session_state.get("theme", "light")
    style = current_style()
    bg = style["bg_light"] if theme == "light" else style["bg_dark"]
    text_color = style["text_light"] if theme == "light" else style["text_dark"]
    accent = style["accent"]

    st.markdown(
        f"""
        <style>
        body {{
            background: {bg};
            color: {text_color};
        }}
        .main-header {{
            font-size: 2.5rem;
            font-weight: 800;
            text-align: center;
            padding: 1rem 0;
            color: {accent};
            text-shadow: 0 2px 10px rgba(0,0,0,0.25);
        }}
        .agent-card {{
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(10px);
            padding: 1rem;
            border-radius: 0.75rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(148,163,184,0.4);
        }}
        .metric-card {{
            background: rgba(15,23,42,0.85);
            color: #e5e7eb;
            padding: 1.25rem;
            border-radius: 0.75rem;
            text-align: center;
            box-shadow: 0 10px 25px rgba(15,23,42,0.5);
        }}
        .wow-badge {{
            display:inline-block;
            padding:0.15rem 0.5rem;
            border-radius:9999px;
            font-size:0.75rem;
            font-weight:600;
            background: {accent};
            color:#0f172a;
            margin-right:0.25rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# SAMPLE DATASET (fallback)
# =========================

SAMPLE_CSV = """Suppliername,deliverdate,customer,licenseID,DeviceCategory,UDI,DeviceName,LotNumber,SN,ModelNum,Numbers,Unit
B00079,45968,C05278,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576331,“波士頓科技”英吉尼心臟節律器,890057,,L111,1,組
B00079,45967,C06030,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576331,“波士頓科技”英吉尼心臟節律器,872177,,L111,1,組
B00079,45967,C00123,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576331,“波士頓科技”英吉尼心臟節律器,889490,,L111,1,組
B00079,45966,C06034,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576331,“波士頓科技”英吉尼心臟節律器,889253,,L111,1,組
B00079,45964,C05363,衛部醫器輸字第029100號,E.3610植入式心律器之脈搏產生器,00802526576461,“波士頓科技”艾科雷心臟節律器,869531,,L311,1,組
B00079,45964,C06034,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576331,“波士頓科技”英吉尼心臟節律器,889230,,L111,1,組
B00079,45964,C05278,衛部醫器輸字第029100號,E.3610植入式心律器之脈搏產生器,00802526576485,“波士頓科技”艾科雷心臟節律器,182310,,L331,1,組
B00079,45960,C00123,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576324,“波士頓科技”英吉尼心臟節律器,915900,,L110,1,組
B00079,45947,C06034,衛部醫器輸字第030901號,E.3610植入式心律器之脈搏產生器,00802526594069,“波士頓科技”恩璽植入式心律去顫器,710753,,D433,1,組
B00079,45946,C06028,衛部醫器輸字第029675號,E.3610植入式心律器之脈搏產生器,00802526576447,“波士頓科技”艾科雷心臟節律器,809748,,L301,1,組
B00079,45943,C06034,衛部醫器輸字第033951號,E.3610植入式心律器之脈搏產生器,00802526576331,“波士頓科技”英吉尼心臟節律器,888053,,L111,1,組
"""


def excel_serial_to_date(val):
    try:
        serial_int = int(float(val))
        origin = datetime(1899, 12, 30)
        return origin + timedelta(days=serial_int)
    except Exception:
        return pd.NaT


def load_packing_list(csv_file) -> pd.DataFrame:
    if csv_file is not None:
        text = csv_file.read().decode("utf-8")
    else:
        text = SAMPLE_CSV
    # Clean full-width quotes that break parsing
    text = text.replace("“", "").replace("”", "").replace("”", "").replace("“", "")
    df = pd.read_csv(StringIO(text))
    if "deliverdate" in df.columns:
        df["deliverdate_dt"] = df["deliverdate"].apply(excel_serial_to_date)
    if "Numbers" in df.columns:
        df["Numbers"] = pd.to_numeric(df["Numbers"], errors="coerce").fillna(0).astype(int)
    return df


def build_supply_chain_graph(df: pd.DataFrame):
    if nx is None or Network is None:
        return None

    G = nx.DiGraph()
    for _, row in df.iterrows():
        supplier = str(row.get("Suppliername", ""))
        device = str(row.get("DeviceName", ""))
        customer = str(row.get("customer", ""))
        qty = int(row.get("Numbers", 0))

        if supplier:
            G.add_node(supplier, type="supplier")
        if device:
            G.add_node(device, type="device")
        if customer:
            G.add_node(customer, type="customer")

        if supplier and device:
            G.add_edge(supplier, device, weight=qty)
        if device and customer:
            G.add_edge(device, customer, weight=qty)

    net = Network(height="500px", width="100%", directed=True, bgcolor="#0b1120", font_color="#e5e7eb")
    net.from_nx(G)

    # Apply simple physics
    net.force_atlas_2based()
    return net


def render_supply_chain_graph(net: Optional[Network]):
    if net is None:
        st.warning("networkx / pyvis not installed; graph view unavailable.")
        return
    net.set_options(
        """
        var options = {
          "nodes": {
            "borderWidth": 1,
            "size": 16,
            "font": {"size": 16}
          },
          "edges": {
            "arrows": {"to": {"enabled": true}},
            "color": {"inherit": "from"},
            "smooth": false
          },
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 500}
          }
        }
        """
    )
    net.show("supply_chain_graph.html")
    with open("supply_chain_graph.html", "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=520, scrolling=True)


# =========================
# MODEL MAP
# =========================

MODEL_PROVIDER_MAP = {
    "gpt-4o-mini": "openai",
    "gpt-4.1-mini": "openai",
    "gemini-2.5-flash": "gemini",
    "gemini-2.5-flash-lite": "gemini",
    "claude-3-5-sonnet-latest": "anthropic",
    "claude-3-haiku-latest": "anthropic",
    "grok-4-fast-reasoning": "grok",
    "grok-3-mini": "grok",
}


# =========================
# AGENT IMPLEMENTATION
# =========================

class Agent:
    """Individual agent for specific GUDID use case"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.llm_provider = config.get("llm_provider", "openai")
        self.model = config.get("model", "gpt-4o-mini")
        self.system_prompt = config.get("system_prompt", "")
        self.capabilities = config.get("capabilities", [])

    def execute(
        self,
        query: str,
        system_prompt_override: Optional[str] = None,
        model_override: Optional[str] = None,
        max_tokens: int = 12000,
    ) -> str:
        effective_model = model_override or self.model
        effective_system = system_prompt_override or self.system_prompt

        # If model override implies provider, respect that
        provider = self.llm_provider
        if model_override and model_override in MODEL_PROVIDER_MAP:
            provider = MODEL_PROVIDER_MAP[model_override]

        try:
            if provider == "openai":
                return self._execute_openai(query, effective_model, effective_system, max_tokens)
            elif provider == "anthropic":
                return self._execute_anthropic(query, effective_model, effective_system, max_tokens)
            elif provider == "gemini":
                return self._execute_gemini(query, effective_model, effective_system, max_tokens)
            elif provider == "grok":
                return self._execute_grok(query, effective_model, effective_system, max_tokens)
            else:
                return f"Unsupported LLM provider: {provider}"
        except Exception as e:
            return f"Error executing agent {self.name}: {str(e)}"

    def _execute_openai(self, query: str, model: str, system_prompt: str, max_tokens: int) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "OpenAI API key not configured"
        if openai is None:
            return "OpenAI library not installed"

        client = openai.OpenAI(api_key=api_key) if hasattr(openai, "OpenAI") else openai

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        else:
            # Legacy completion fallback
            completion = client.Completion.create(
                model=model,
                prompt=f"{system_prompt}\n\nUser: {query}\nAssistant:",
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return completion.choices[0].text

    def _execute_anthropic(self, query: str, model: str, system_prompt: str, max_tokens: int) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "Anthropic API key not configured"
        if Anthropic is None:
            return "Anthropic library not installed"

        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )
        return response.content[0].text

    def _execute_gemini(self, query: str, model: str, system_prompt: str, max_tokens: int) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Gemini API key not configured"
        if genai is None:
            return "Google Generative AI library not installed"

        genai.configure(api_key=api_key)
        full_prompt = f"{system_prompt}\n\nUser Query:\n{query}"
        model_obj = genai.GenerativeModel(model)
        response = model_obj.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": max_tokens},
        )
        return getattr(response, "text", str(response))

    def _execute_grok(self, query: str, model: str, system_prompt: str, max_tokens: int) -> str:
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            return "Grok (xAI) API key not configured"
        if requests is None:
            return "requests library not installed"

        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            return f"Grok API error: {resp.status_code} {resp.text}"
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            return json.dumps(data, ensure_ascii=False, indent=2)


class AgentOrchestrator:
    """Main orchestrator for the GUDID agentic AI system"""

    def __init__(self, config_path: str = "agents.yaml"):
        self.config = self.load_config(config_path)
        self.agents: Dict[str, Agent] = {}
        self.conversation_history: List[Dict] = []
        self.initialize_agents()

    def load_config(self, path: str) -> Dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            st.error(f"Failed to load config: {e}")
            return {}

    def initialize_agents(self):
        for agent_name, agent_config in self.config.get("agents", {}).items():
            self.agents[agent_name] = Agent(agent_name, agent_config)

    def route_query(self, user_query: str) -> str:
        query_lower = user_query.lower()
        routing_keywords = {
            "nlp_analyzer": ["分析", "文字", "analyze", "text", "nlp", "實體"],
            "anomaly_detector": ["異常", "anomaly", "偵測", "detect", "檢測"],
            "duplicate_checker": ["重複", "duplicate", "相似", "similar"],
            "label_matcher": ["標籤", "label", "比對", "match", "ocr"],
            "data_standardizer": ["標準化", "standardize", "正規化", "normalize"],
            "adverse_event_linker": ["不良事件", "adverse", "連結", "link"],
            "recall_manager": ["回收", "recall", "追蹤", "track"],
            "eifu_manager": ["說明書", "eifu", "instructions"],
            "customs_verifier": ["海關", "customs", "查驗", "verify"],
            "international_connector": ["國際", "international", "同步", "sync"],
        }
        for agent_name, keywords in routing_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return agent_name
        return "nlp_analyzer"

    def process_query(
        self,
        user_query: str,
        selected_agent: Optional[str] = None,
        system_prompt_override: Optional[str] = None,
        model_override: Optional[str] = None,
        max_tokens: int = 12000,
    ) -> Dict:
        agent_name = selected_agent if selected_agent else self.route_query(user_query)
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}

        agent = self.agents[agent_name]
        response = agent.execute(
            user_query,
            system_prompt_override=system_prompt_override,
            model_override=model_override,
            max_tokens=max_tokens,
        )

        record = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "query": user_query,
            "response": response,
            "model": model_override or agent.model,
        }
        self.conversation_history.append(record)

        return {
            "agent": agent_name,
            "response": response,
            "timestamp": record["timestamp"],
            "model": record["model"],
        }


# =========================
# UI HELPERS
# =========================

def render_api_key_section():
    with st.expander(tr("api_keys_header"), expanded=False):
        # OpenAI
        openai_env = os.getenv("OPENAI_API_KEY")
        if openai_env:
            st.text(f"OpenAI: {tr('api_configured_env')}")
        else:
            openai_key = st.text_input("OpenAI", type="password", placeholder=tr("api_enter_key"))
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key

        # Anthropic
        anth_env = os.getenv("ANTHROPIC_API_KEY")
        if anth_env:
            st.text(f"Anthropic: {tr('api_configured_env')}")
        else:
            anthropic_key = st.text_input("Anthropic", type="password", placeholder=tr("api_enter_key"))
            if anthropic_key:
                os.environ["ANTHROPIC_API_KEY"] = anthropic_key

        # Gemini
        gem_env = os.getenv("GEMINI_API_KEY")
        if gem_env:
            st.text(f"Gemini: {tr('api_configured_env')}")
        else:
            gemini_key = st.text_input("Gemini", type="password", placeholder=tr("api_enter_key"))
            if gemini_key:
                os.environ["GEMINI_API_KEY"] = gemini_key

        # Grok (xAI)
        grok_env = os.getenv("GROK_API_KEY")
        if grok_env:
            st.text(f"Grok (xAI): {tr('api_configured_env')}")
        else:
            grok_key = st.text_input("Grok (xAI)", type="password", placeholder=tr("api_enter_key"))
            if grok_key:
                os.environ["GROK_API_KEY"] = grok_key

        if st.button(tr("save_keys")):
            st.success("Keys stored for this process. They are not persisted on disk.")


def render_wow_status(orchestrator: AgentOrchestrator):
    st.subheader(tr("system_status"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(tr("active_agents"), len(orchestrator.agents))
    with col2:
        st.metric(tr("processed_requests"), len(st.session_state.get("messages", [])))
    with col3:
        style = current_style()
        lang = st.session_state.get("lang", "zh")
        style_name = style["name_zh"] if lang == "zh" else style["name_en"]
        st.markdown(
            f"<div class='metric-card'><div>{tr('style_label')}</div>"
            f"<div style='font-weight:700;margin-top:.25rem;'>{style_name}</div></div>",
            unsafe_allow_html=True,
        )

    # API health badges
    def provider_badge(name, env_var):
        ok = bool(os.getenv(env_var))
        color = "#22c55e" if ok else "#ef4444"
        status = "OK" if ok else "Missing"
        st.markdown(
            f"<span class='wow-badge' style='background:{color};'>{name}: {status}</span>",
            unsafe_allow_html=True,
        )

    provider_badge("OpenAI", "OPENAI_API_KEY")
    provider_badge("Gemini", "GEMINI_API_KEY")
    provider_badge("Anthropic", "ANTHROPIC_API_KEY")
    provider_badge("Grok", "GROK_API_KEY")


def render_agent_headquarters(orchestrator: AgentOrchestrator):
    st.markdown(tr("agent_hq_intro"))
    if "agent_chain" not in st.session_state:
        st.session_state.agent_chain = {"last_output": "", "current_input": ""}

    agents = list(orchestrator.agents.keys())
    if not agents:
        st.warning("No agents configured in agents.yaml")
        return

    col_top1, col_top2 = st.columns([2, 1])
    with col_top1:
        selected_agent = st.selectbox(tr("agent_hq_select_agent"), options=agents)
    with col_top2:
        model_options = list(MODEL_PROVIDER_MAP.keys())
        selected_model = st.selectbox(tr("agent_hq_model"), options=model_options, index=0)

    max_tokens = st.number_input(tr("agent_hq_max_tokens"), min_value=128, max_value=120000, value=12000, step=512)

    base_input_default = st.session_state.agent_chain.get("current_input", "")
    user_input = st.text_area(tr("agent_hq_user_input"), value=base_input_default, height=160)

    system_override = st.text_area(tr("agent_hq_system_prompt"), value="", height=120)

    if st.button(tr("agent_hq_run"), type="primary"):
        if not user_input.strip():
            st.warning("Please provide input for the agent.")
        else:
            with st.spinner("Running agent..."):
                result = orchestrator.process_query(
                    user_input,
                    selected_agent=selected_agent,
                    system_prompt_override=system_override or None,
                    model_override=selected_model,
                    max_tokens=max_tokens,
                )
            response = result.get("response", "No response generated")
            st.session_state.agent_chain["last_output"] = response

    if st.session_state.agent_chain.get("last_output"):
        st.subheader(tr("agent_hq_output"))
        view_mode = st.radio(tr("agent_hq_view_mode"), [tr("view_markdown"), tr("view_text")], horizontal=True)
        output_text = st.session_state.agent_chain["last_output"]

        if view_mode == tr("view_markdown"):
            st.markdown(output_text)
        else:
            st.text(output_text)

        st.markdown("---")
        st.subheader(tr("agent_hq_edit_output"))
        editable = st.text_area(
            "", value=output_text, height=220, key="editable_agent_output"
        )
        if st.button(tr("agent_hq_use_as_next")):
            st.session_state.agent_chain["current_input"] = editable
            st.success("Set as next agent input. Scroll up to adjust agent/model and run again.")


def render_supply_chain_analytics():
    st.subheader(tr("supply_chain_analytics"))
    uploaded = st.file_uploader(tr("upload_csv"), type=["csv"])
    df = load_packing_list(uploaded)

    if df.empty:
        st.info("No data.")
        return

    # Basic filters
    st.markdown("### Filters")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        customers = sorted(df["customer"].dropna().unique().tolist()) if "customer" in df.columns else []
        selected_customers = st.multiselect("Customer", options=customers, default=customers)
    with col_f2:
        if "deliverdate_dt" in df.columns and df["deliverdate_dt"].notna().any():
            min_d = df["deliverdate_dt"].min()
            max_d = df["deliverdate_dt"].max()
            date_range = st.slider("Deliver Date Range", min_value=min_d, max_value=max_d, value=(min_d, max_d))
        else:
            date_range = None

    mask = pd.Series([True] * len(df))
    if selected_customers:
        mask &= df["customer"].isin(selected_customers)
    if date_range:
        mask &= df["deliverdate_dt"].between(date_range[0], date_range[1])
    df_f = df[mask].copy()

    # ========== 3 SUMMARY TABLES ==========
    st.markdown(tr("summary_tables"))

    # Table 1: Global metrics
    total_units = int(df_f["Numbers"].sum()) if "Numbers" in df_f.columns else len(df_f)
    summary_1 = pd.DataFrame(
        [
            {
                "Total Lines": len(df_f),
                "Total Units": total_units,
                "Suppliers": df_f["Suppliername"].nunique(),
                "Customers": df_f["customer"].nunique(),
                "Devices": df_f["DeviceName"].nunique(),
                "Models": df_f["ModelNum"].nunique(),
                "Lots": df_f["LotNumber"].nunique(),
            }
        ]
    )
    st.dataframe(summary_1, use_container_width=True)

    # Table 2: Volume by customer
    if "customer" in df_f.columns:
        tbl_customer = (
            df_f.groupby("customer")
            .agg(
                Total_Units=("Numbers", "sum"),
                Lines=("customer", "count"),
                Unique_Models=("ModelNum", "nunique"),
            )
            .reset_index()
            .sort_values("Total_Units", ascending=False)
        )
        st.dataframe(tbl_customer, use_container_width=True)

    # Table 3: Device / Model performance
    if "ModelNum" in df_f.columns:
        tbl_device = (
            df_f.groupby(["DeviceName", "ModelNum"])
            .agg(
                Total_Units=("Numbers", "sum"),
                Customers=("customer", "nunique"),
                Lots=("LotNumber", "nunique"),
            )
            .reset_index()
            .sort_values("Total_Units", ascending=False)
        )
        st.dataframe(tbl_device, use_container_width=True)

    # ========== 5 DISTRIBUTION / RELATION CHARTS ==========
    st.markdown(tr("dist_charts"))

    charts_col1, charts_col2 = st.columns(2)

    # Chart 1: Deliveries over time
    if "deliverdate_dt" in df_f.columns and df_f["deliverdate_dt"].notna().any():
        time_agg = (
            df_f.groupby("deliverdate_dt")
            .agg(Total_Units=("Numbers", "sum"), Lines=("Suppliername", "count"))
            .reset_index()
            .sort_values("deliverdate_dt")
        )
        fig_time = px.line(
            time_agg,
            x="deliverdate_dt",
            y="Total_Units",
            markers=True,
            title="Deliveries Over Time (Units)",
        )
        charts_col1.plotly_chart(fig_time, use_container_width=True)

    # Chart 2: Volume by Customer
    if "customer" in df_f.columns:
        cust_agg = (
            df_f.groupby("customer")
            .agg(Total_Units=("Numbers", "sum"))
            .reset_index()
            .sort_values("Total_Units", ascending=False)
        )
        fig_cust = px.bar(
            cust_agg,
            x="customer",
            y="Total_Units",
            title="Volume by Customer",
        )
        charts_col2.plotly_chart(fig_cust, use_container_width=True)

    # Chart 3: Volume by DeviceName (Top 10)
    if "DeviceName" in df_f.columns:
        dev_agg = (
            df_f.groupby("DeviceName")
            .agg(Total_Units=("Numbers", "sum"))
            .reset_index()
            .sort_values("Total_Units", ascending=False)
            .head(10)
        )
        fig_dev = px.bar(
            dev_agg,
            x="DeviceName",
            y="Total_Units",
            title="Top Devices by Volume",
        )
        st.plotly_chart(fig_dev, use_container_width=True)

    # Chart 4: Volume by LicenseID / DeviceCategory (pie or bar)
    if "licenseID" in df_f.columns:
        lic_agg = (
            df_f.groupby("licenseID")
            .agg(Total_Units=("Numbers", "sum"))
            .reset_index()
            .sort_values("Total_Units", ascending=False)
        )
        fig_lic = px.pie(
            lic_agg,
            names="licenseID",
            values="Total_Units",
            title="Share by License ID",
        )
        st.plotly_chart(fig_lic, use_container_width=True)

    # Chart 5: Supply chain relation graph
    st.markdown("#### Supply Chain Relation Graph (Supplier → Device → Customer)")
    net = build_supply_chain_graph(df_f)
    render_supply_chain_graph(net)


def load_skill_md():
    if not os.path.exists("SKILL.md"):
        return None
    with open("SKILL.md", "r", encoding="utf-8") as f:
        return f.read()


# =========================
# MAIN APP
# =========================

def main():
    st.set_page_config(
        page_title="GUDID Agentic AI — WOW Supply Chain Analytics",
        page_icon="🏥",
        layout="wide",
    )

    # Initialize core session state
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "lang" not in st.session_state:
        st.session_state.lang = "zh"
    if "painter_style_idx" not in st.session_state:
        st.session_state.painter_style_idx = 0
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize orchestrator
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = AgentOrchestrator()

    # Apply WOW theme
    apply_wow_theme()

    # Header
    st.markdown(f"<div class='main-header'>{tr('app_title')}</div>", unsafe_allow_html=True)
    st.markdown("---")

    orchestrator: AgentOrchestrator = st.session_state.orchestrator

    # Sidebar
    with st.sidebar:
        st.header(tr("settings_header"))

        # WOW UI controls
        st.subheader(tr("wow_ui_header"))
        col_ui1, col_ui2 = st.columns(2)
        with col_ui1:
            st.session_state.theme = st.radio(
                tr("theme_label"),
                options=["light", "dark"],
                format_func=lambda x: tr("theme_light") if x == "light" else tr("theme_dark"),
            )
        with col_ui2:
            lang_opt = st.radio(
                tr("lang_label"),
                options=["zh", "en"],
                format_func=lambda x: tr("lang_zh") if x == "zh" else tr("lang_en"),
            )
            st.session_state.lang = lang_opt

        col_style1, col_style2 = st.columns(2)
        with col_style1:
            if st.button(tr("style_jackslot")):
                st.session_state.painter_style_idx = (st.session_state.painter_style_idx + 1) % len(PAINTER_STYLES)
                st.experimental_rerun()
        with col_style2:
            if st.button(tr("style_wheel")):
                st.session_state.painter_style_idx = random.randint(0, len(PAINTER_STYLES) - 1)
                st.experimental_rerun()

        style = current_style()
        style_name = style["name_zh"] if st.session_state.lang == "zh" else style["name_en"]
        st.caption(f"{tr('style_label')}: {style_name}")

        render_api_key_section()
        st.markdown("---")

        # Agent selection (for chat tab)
        st.subheader(tr("select_agent"))
        agent_options = {
            "auto": "🎯 Auto Routing",
            "nlp_analyzer": "📝 NLP Analyzer",
            "anomaly_detector": "🔍 Anomaly Detector",
            "duplicate_checker": "👥 Duplicate Checker",
            "label_matcher": "🏷️ Label Matcher",
            "data_standardizer": "📊 Data Standardizer",
            "adverse_event_linker": "⚠️ Adverse Event Linker",
            "recall_manager": "📢 Recall Manager",
            "eifu_manager": "📖 eIFU Manager",
            "customs_verifier": "🛃 Customs Verifier",
            "international_connector": "🌍 International Connector",
        }
        selected_agent = st.selectbox(
            tr("select_agent"),
            options=list(agent_options.keys()),
            format_func=lambda x: agent_options.get(x, x),
        )

        st.markdown("---")
        render_wow_status(orchestrator)

        if st.button(tr("clear_chat"), use_container_width=True):
            st.session_state.messages = []
            orchestrator.conversation_history = []
            st.experimental_rerun()

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [tr("chat_tab"), tr("agents_tab"), tr("analytics_tab"), tr("agent_hq_tab"), tr("docs_tab")]
    )

    # Chat Interface
    with tab1:
        st.subheader(tr("chat_subheader"))

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "agent" in message:
                    st.caption(f"🤖 Agent: {message['agent']} | Model: {message.get('model', 'N/A')}")

        if prompt := st.chat_input(tr("chat_input_placeholder")):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    agent_to_use = None if selected_agent == "auto" else selected_agent
                    result = orchestrator.process_query(prompt, selected_agent=agent_to_use)
                    response = result.get("response", "No response generated")
                    agent_used = result.get("agent", "unknown")
                    model_used = result.get("model", "N/A")
                    st.markdown(response)
                    st.caption(f"🤖 Agent: {agent_used} | Model: {model_used}")

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                            "agent": agent_used,
                            "model": model_used,
                        }
                    )

    # Agent information
    with tab2:
        st.subheader(tr("agents_tab"))
        for agent_name, agent in orchestrator.agents.items():
            with st.expander(f"🤖 {agent_name}", expanded=False):
                col_a1, col_a2 = st.columns([2, 1])
                with col_a1:
                    st.write("**Description:**", agent.config.get("description", "N/A"))
                    st.write("**LLM Provider:**", agent.llm_provider)
                    st.write("**Default Model:**", agent.model)
                with col_a2:
                    st.write("**Capabilities:**")
                    for capability in agent.capabilities:
                        st.write(f"- {capability}")
                st.write("**System Prompt:**")
                st.code(agent.system_prompt, language="text")

    # Analytics dashboard (Agent usage + Supply chain)
    with tab3:
        subtab_a, subtab_b = st.tabs([tr("agent_usage_stats"), tr("supply_chain_analytics")])

        with subtab_a:
            if orchestrator.conversation_history:
                agent_usage = {}
                for entry in orchestrator.conversation_history:
                    ag = entry["agent"]
                    agent_usage[ag] = agent_usage.get(ag, 0) + 1

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.metric("Total Requests", len(orchestrator.conversation_history))
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.metric("Most Used Agent", max(agent_usage, key=agent_usage.get))
                    st.markdown("</div>", unsafe_allow_html=True)
                with col3:
                    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                    st.metric("Active Agents", len(agent_usage))
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                df_usage = pd.DataFrame(list(agent_usage.items()), columns=["Agent", "Usage Count"])
                st.bar_chart(df_usage.set_index("Agent"))

                st.subheader(tr("recent_activity"))
                recent = orchestrator.conversation_history[-10:]
                for activity in reversed(recent):
                    with st.container():
                        col_r1, col_r2 = st.columns([1, 4])
                        with col_r1:
                            st.write(f"**{activity['agent']}**")
                            st.caption(activity["timestamp"])
                            st.caption(f"Model: {activity.get('model', 'N/A')}")
                        with col_r2:
                            st.write(f"Query: {activity['query'][:120]}...")
            else:
                st.info(tr("no_analytics"))

        with subtab_b:
            render_supply_chain_analytics()

    # Agent HQ: advanced controls, model/prompt chaining
    with tab4:
        render_agent_headquarters(orchestrator)

    # Docs
    with tab5:
        st.subheader(tr("docs_tab"))
        st.markdown(
            """
            ### GUDID Chronicles — Supply Chain Analytics Platform

            - Hybrid deterministic + generative analytics
            - Agentic architecture (agents.yaml)
            - Supports OpenAI, Gemini, Anthropic, Grok (xAI)
            - WOW UI: themes, painter styles, status indicators
            - Supply chain visual analytics: tables + distributions + graph

            **Key Usage Steps:**

            1. Configure API keys (sidebar).
            2. Load or upload supply chain CSV (Dashboard → Supply Chain Analytics).
            3. Explore tables and 5 visualizations (including relation graph).
            4. Use Chat for natural language Q&A.
            5. Use Agent Headquarters to:
               - Override system prompts
               - Switch models
               - Adjust max tokens (default 12000)
               - Chain outputs across agents.
            """
        )

        skill_text = load_skill_md()
        if skill_text:
            st.markdown("---")
            st.subheader(tr("skills_header"))
            st.markdown(skill_text)
        else:
            st.info("SKILL.md not found. Place it next to app.py to show skill documentation.")


if __name__ == "__main__":
    main()
