import datetime
import streamlit as st
from triago import (
    GreedyRouter,
    NaiveBayesClassifier,
    Technician,
    append_decision_log,
    load_category_durations,
    load_decision_logs,
    load_technicians,
    load_training_data,
)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Triago", page_icon="🎫", layout="wide", initial_sidebar_state="expanded")

CATEGORIES = ["Banco de Dados", "Rede", "Acesso/Login", "Hardware", "Financeiro"]
CATEGORY_COLORS = {
    "Banco de Dados": "#6366F1",
    "Rede": "#0EA5E9",
    "Acesso/Login": "#10B981",
    "Hardware": "#F59E0B",
    "Financeiro": "#EC4899",
}
URGENCY = {"Baixa": 1, "Média": 2, "Alta": 3}
URGENCY_LABELS = {1: "Baixa", 2: "Média", 3: "Alta"}
URGENCY_COLORS = {1: "#10B981", 2: "#F59E0B", 3: "#EF4444"}


# ---------------------------------------------------------------------------
# Tema (claro / escuro)
# ---------------------------------------------------------------------------
def theme_palette(dark: bool) -> dict:
    if dark:
        return {
            "bg": "#0E0F13", "surface": "#16181F", "surface2": "#1B1E27",
            "border": "#262932", "text": "#ECECF1", "muted": "#8A8D98",
            "accent": "#818CF8", "accent_soft": "#1E2030", "track": "#262932",
            "shadow": "0 1px 3px rgba(0,0,0,.45)",
        }
    return {
        "bg": "#FBFBFD", "surface": "#FFFFFF", "surface2": "#F6F7F9",
        "border": "#ECECF1", "text": "#1C1C1E", "muted": "#8A8A8E",
        "accent": "#6366F1", "accent_soft": "#EEF0FE", "track": "#F0F1F4",
        "shadow": "0 1px 2px rgba(16,24,40,.05)",
    }


def inject_css(p: dict):
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {{
            --bg:{p['bg']}; --surface:{p['surface']}; --surface2:{p['surface2']};
            --border:{p['border']}; --text:{p['text']}; --muted:{p['muted']};
            --accent:{p['accent']}; --accent-soft:{p['accent_soft']};
            --track:{p['track']}; --shadow:{p['shadow']};
        }}
        html, body, [class*="css"], .stApp {{ font-family:'Inter',sans-serif; }}
        .stApp {{ background:var(--bg); }}
        .block-container {{ max-width:1000px; padding-top:1.6rem; padding-bottom:4rem; }}
        #MainMenu, footer, [data-testid="stHeader"] {{ background:transparent; }}
        footer {{ visibility:hidden; }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{ background:var(--surface); border-right:1px solid var(--border); }}
        section[data-testid="stSidebar"] * {{ color:var(--text); }}

        /* Inputs */
        .stTextArea textarea, .stTextInput input {{
            background:var(--surface2)!important; color:var(--text)!important;
            border:1px solid var(--border)!important; border-radius:10px!important;
        }}
        .stTextArea textarea::placeholder {{ color:var(--muted)!important; opacity:1; }}
        .stSelectbox div[data-baseweb="select"] > div {{
            background:var(--surface2)!important; border-color:var(--border)!important; color:var(--text)!important;
        }}
        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] svg {{ color:var(--text)!important; fill:var(--text)!important; }}
        /* Dropdown aberto do selectbox */
        div[data-baseweb="popover"] div[data-baseweb="menu"],
        div[data-baseweb="popover"] ul {{ background:var(--surface)!important; }}
        div[data-baseweb="popover"] li {{ background:var(--surface)!important; color:var(--text)!important; }}
        div[data-baseweb="popover"] li:hover {{ background:var(--surface2)!important; }}
        .stRadio label, .stSelectbox label, .stTextArea label {{ color:var(--text)!important; font-weight:500; }}
        /* Prioridade / tema como segmentos */
        div[role="radiogroup"] {{ gap:.4rem; }}
        div[role="radiogroup"] label {{ color:var(--text)!important; }}

        div.stButton > button {{
            width:100%; border-radius:10px; border:0; background:var(--accent); color:#fff;
            font-weight:600; font-size:.92rem; padding:.6rem .8rem; white-space:nowrap;
            box-sizing:border-box; transition:filter .15s;
        }}
        div.stButton > button p {{ font-size:.92rem; margin:0; }}
        div.stButton > button:hover {{ filter:brightness(1.08); color:#fff; }}

        /* Alertas (warning / error / info) seguindo o tema */
        [data-testid="stAlert"] {{
            background:var(--surface2)!important; color:var(--text)!important;
            border:1px solid var(--border)!important; border-radius:12px!important;
        }}
        [data-testid="stAlert"] * {{ color:var(--text)!important; }}

        /* Texto base */
        .stApp, .stMarkdown, p, span, label, .stCaption {{ color:var(--text); }}
        [data-testid="stCaptionContainer"], .stCaption {{ color:var(--muted)!important; }}

        /* Cabeçalho */
        .brand {{ display:flex; align-items:center; gap:.7rem; margin-bottom:.2rem; }}
        .brand .logo {{ width:38px; height:38px; border-radius:11px; background:var(--accent);
            display:grid; place-items:center; color:#fff; font-size:1.2rem; box-shadow:var(--shadow); }}
        .brand h1 {{ font-size:1.7rem; font-weight:800; letter-spacing:-.03em; margin:0; color:var(--text); }}
        .brand .sub {{ color:var(--muted); font-size:.9rem; margin-top:-2px; }}

        .eyebrow {{ font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
            color:var(--muted); margin:2rem 0 .8rem; }}

        /* Cartão de chamado */
        .ticket {{ background:var(--surface); border:1px solid var(--border); border-radius:18px;
            padding:1.5rem 1.6rem; box-shadow:var(--shadow); }}
        .ticket-head {{ display:flex; align-items:center; gap:.6rem; margin-bottom:.9rem; }}
        .ticket-id {{ font-weight:700; font-size:.95rem; color:var(--text); font-variant-numeric:tabular-nums; }}
        .badge {{ font-size:.7rem; font-weight:700; padding:.2rem .6rem; border-radius:999px; letter-spacing:.02em; }}
        .badge-ok {{ background:var(--accent-soft); color:var(--accent); }}
        .ticket-desc {{ font-size:1.12rem; font-weight:600; color:var(--text); line-height:1.4; margin-bottom:1.1rem; }}
        .meta {{ display:flex; flex-wrap:wrap; gap:.55rem; align-items:center; }}
        .tag {{ font-size:.76rem; font-weight:700; color:#fff; padding:.22rem .7rem; border-radius:8px; }}
        .dot-meta {{ font-size:.82rem; color:var(--muted); display:inline-flex; align-items:center; gap:.35rem; }}
        .dot-meta b {{ color:var(--text); font-weight:600; }}

        /* Grids de cartões */
        .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
        .card {{ background:var(--surface); border:1px solid var(--border); border-radius:16px;
            padding:1.3rem 1.4rem; box-shadow:var(--shadow); }}
        .card .ctitle {{ font-size:.74rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase;
            color:var(--muted); margin-bottom:.9rem; }}
        .conf-num {{ font-size:2.4rem; font-weight:800; letter-spacing:-.03em; color:var(--text); line-height:1; }}
        .conf-cap {{ font-size:.84rem; color:var(--muted); margin-top:.3rem; }}

        /* Barras de probabilidade */
        .prow {{ display:grid; grid-template-columns:118px 1fr 46px; align-items:center; gap:.6rem; margin:.5rem 0; }}
        .plabel {{ font-size:.82rem; color:var(--text); font-weight:500; }}
        .ptrack {{ background:var(--track); border-radius:999px; height:8px; overflow:hidden; }}
        .pfill {{ height:100%; border-radius:999px; }}
        .pval {{ font-size:.8rem; color:var(--muted); text-align:right; font-variant-numeric:tabular-nums; }}

        /* Justificativa */
        .chips {{ display:flex; flex-wrap:wrap; gap:.5rem; }}
        .chip {{ background:var(--surface2); border:1px solid var(--border); border-radius:10px;
            padding:.5rem .8rem; font-size:.8rem; color:var(--muted); }}
        .chip b {{ color:var(--text); font-weight:700; }}

        /* Quadro de equipe */
        .team {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:.85rem; }}
        .member {{ background:var(--surface); border:1px solid var(--border); border-radius:15px; padding:1.05rem 1.1rem; }}
        .member.on {{ border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-soft); }}
        .member .av {{ width:34px; height:34px; border-radius:50%; display:grid; place-items:center;
            color:#fff; font-weight:700; font-size:.9rem; margin-bottom:.6rem; }}
        .member .mname {{ font-weight:700; color:var(--text); font-size:.98rem; }}
        .member .mspec {{ font-size:.76rem; color:var(--muted); margin-bottom:.7rem; }}
        .load-track {{ background:var(--track); border-radius:999px; height:6px; overflow:hidden; margin-top:.2rem; }}
        .load-fill {{ height:100%; border-radius:999px; background:var(--accent); }}
        .mstat {{ font-size:.78rem; color:var(--muted); margin-top:.5rem; }}
        .mstat b {{ color:var(--text); }}

        /* Lista de recentes */
        .row {{ display:flex; align-items:center; gap:.7rem; padding:.7rem 0; border-bottom:1px solid var(--border); }}
        .row:last-child {{ border-bottom:0; }}
        .row .txt {{ flex:1; min-width:0; color:var(--text); font-size:.9rem;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
        .row .who {{ font-size:.8rem; color:var(--muted); white-space:nowrap; }}

        @media (max-width:680px) {{
            .grid {{ grid-template-columns:1fr; }}
            .prow {{ grid-template-columns:100px 1fr 40px; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Dados / modelos
# ---------------------------------------------------------------------------
@st.cache_data
def load_training_dataset():
    return load_training_data()


@st.cache_resource
def build_router():
    technicians = [Technician(**t) for t in load_technicians()]
    return GreedyRouter(technicians, load_category_durations())


@st.cache_resource
def build_classifier():
    td = load_training_data()
    clf = NaiveBayesClassifier(alpha=1.0)
    clf.fit([r["text"] for r in td], [r["category"] for r in td])
    return clf


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def render_ticket(ticket_id, text, category, urgency, technician, timestamp):
    cat_color = CATEGORY_COLORS.get(category, "var(--accent)")
    urg_color = URGENCY_COLORS[urgency]
    tech_name = technician.name if technician else "Nenhum disponível"
    status = "Atribuído" if technician else "Pendente"
    st.markdown(
        f"""
        <div class="ticket">
          <div class="ticket-head">
            <span class="ticket-id">#{ticket_id}</span>
            <span class="badge badge-ok">{status}</span>
          </div>
          <div class="ticket-desc">{text}</div>
          <div class="meta">
            <span class="tag" style="background:{cat_color}">{category}</span>
            <span class="dot-meta"><span style="color:{urg_color}">●</span> Prioridade <b>{URGENCY_LABELS[urgency]}</b></span>
            <span class="dot-meta">Responsável <b>{tech_name}</b></span>
            <span class="dot-meta">{timestamp}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(confidence, probabilities, metrics):
    bars = ""
    for cat, prob in sorted(probabilities.items(), key=lambda x: x[1], reverse=True):
        pct = prob * 100
        color = CATEGORY_COLORS.get(cat, "var(--accent)")
        bars += (
            f'<div class="prow"><div class="plabel">{cat}</div>'
            f'<div class="ptrack"><div class="pfill" style="width:{pct:.1f}%;background:{color}"></div></div>'
            f'<div class="pval">{pct:.0f}%</div></div>'
        )
    match = "Compatível" if metrics.get("specialty_penalty", 0) == 0 else "Realocado por carga"
    st.markdown(
        f"""
        <div class="grid">
          <div class="card">
            <div class="ctitle">Confiança da classificação</div>
            <div class="conf-num">{confidence*100:.0f}%</div>
            <div class="conf-cap">Probabilidade da categoria escolhida pelo Naive Bayes.</div>
          </div>
          <div class="card">
            <div class="ctitle">Decisão de roteamento</div>
            <div class="chips">
              <div class="chip">Score <b>{metrics['score']:.1f}</b></div>
              <div class="chip">Espera <b>{metrics['estimated_wait']:.0f} min</b></div>
              <div class="chip">Especialidade <b>{match}</b></div>
              <div class="chip">Sobrecarga <b>{metrics['overload_penalty']:.0f}</b></div>
            </div>
          </div>
        </div>
        <div class="card" style="margin-top:1rem">
          <div class="ctitle">Distribuição de probabilidades</div>
          {bars}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_team(router, assigned_name=None):
    cards = ""
    max_load = max((t.queue_length for t in router.get_technicians()), default=0) or 1
    for t in router.get_technicians():
        color = CATEGORY_COLORS.get(t.specialty, "var(--accent)")
        on = " on" if t.name == assigned_name else ""
        initials = t.name[0].upper()
        width = (t.queue_length / max_load) * 100
        cards += (
            f'<div class="member{on}">'
            f'<div class="av" style="background:{color}">{initials}</div>'
            f'<div class="mname">{t.name}</div>'
            f'<div class="mspec">{t.specialty}</div>'
            f'<div class="load-track"><div class="load-fill" style="width:{width:.0f}%"></div></div>'
            f'<div class="mstat"><b>{t.queue_length}</b> na fila · <b>{t.estimated_wait:.0f} min</b></div>'
            f"</div>"
        )
    st.markdown(f'<div class="team">{cards}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
def main():
    with st.sidebar:
        mode = st.radio("Aparência", ["☀️ Claro", "🌙 Escuro"], horizontal=True)
    dark = mode.startswith("🌙")
    inject_css(theme_palette(dark))

    st.markdown(
        '<div class="brand"><div class="logo">🎫</div>'
        '<div><h1>Triago</h1><div class="sub">Triagem e roteamento inteligente de chamados</div></div></div>',
        unsafe_allow_html=True,
    )

    training_data = load_training_dataset()
    if not training_data:
        st.warning("Nenhum dado de treinamento disponível. Verifique data/training_data.csv.")
        return

    classifier = build_classifier()
    router = build_router()

    with st.sidebar:
        st.markdown("### Novo chamado")
        text = st.text_area("Descrição", height=150, placeholder="Descreva o problema do usuário...")
        category_override = st.selectbox("Categoria", ["Detectar automaticamente"] + CATEGORIES)
        urgency_label = st.radio("Prioridade", list(URGENCY), index=1, horizontal=True)
        urgency = URGENCY[urgency_label]
        process = st.button("Classificar e rotear")
        st.caption(f"Modelo treinado com {len(training_data)} chamados.")

    assigned_name = None

    if process and text.strip():
        override = None if category_override == "Detectar automaticamente" else category_override
        probabilities = classifier.predict_proba(text)
        category = override or max(probabilities, key=probabilities.get)
        confidence = probabilities[category]

        if override is None:
            known, total = classifier.coverage(text)
            if total == 0 or known == 0:
                st.warning("⚠️ Nenhuma palavra deste chamado está no vocabulário de treino — a categoria foi adivinhada. Selecione-a manualmente.")
            elif confidence < 0.40 or known / total < 0.34:
                st.warning(f"⚠️ Baixa confiança: apenas {known} de {total} termos são conhecidos pelo modelo.")

        ticket = router.build_ticket(text, category, urgency)
        technician, metrics = router.assign(ticket)
        assigned_name = technician.name if technician else None
        now = datetime.datetime.now()
        append_decision_log({
            "text": text, "category": category, "urgency": urgency,
            "probabilities": probabilities,
            "technician": assigned_name, "metrics": metrics,
            "timestamp": now.astimezone(datetime.timezone.utc).isoformat(),
        })

        ticket_id = f"TRG-{len(load_decision_logs()):04d}"
        st.markdown('<div class="eyebrow">Chamado processado</div>', unsafe_allow_html=True)
        render_ticket(ticket_id, text, category, urgency, technician, now.strftime("%d/%m/%Y %H:%M"))
        st.markdown('<div class="eyebrow">Análise da IA</div>', unsafe_allow_html=True)
        render_analysis(confidence, probabilities, metrics)
    elif process:
        st.error("Informe a descrição do chamado antes de processar.")
    else:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2.4rem 1rem">'
            '<div style="font-size:2rem">🎫</div>'
            '<div style="font-weight:700;margin-top:.5rem;color:var(--text)">Nenhum chamado em análise</div>'
            '<div style="color:var(--muted);margin-top:.3rem">Preencha um chamado na barra lateral e clique em <b>Classificar e rotear</b>.</div>'
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="eyebrow">Equipe e filas</div>', unsafe_allow_html=True)
    render_team(router, assigned_name)

    logs = load_decision_logs()
    st.markdown(f'<div class="eyebrow">Chamados recentes ({len(logs)})</div>', unsafe_allow_html=True)
    if logs:
        rows = ""
        for e in reversed(logs[-6:]):
            color = CATEGORY_COLORS.get(e.get("category"), "var(--accent)")
            rows += (
                f'<div class="row"><span class="tag" style="background:{color}">{e.get("category","?")}</span>'
                f'<span class="txt">{e.get("text","")}</span>'
                f'<span class="who">{e.get("technician","—")}</span></div>'
            )
        st.markdown(f'<div class="card">{rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card" style="color:var(--muted)">Ainda não há decisões registradas.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
