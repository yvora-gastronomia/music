import os
import json
import html
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


APP_TITLE = "YVORA Music"
BRAND_BG = "#EFE7DD"
BRAND_BLUE = "#0E2A47"
BRAND_GOLD = "#C6A96A"

USERS_HEADERS = ["username", "password", "role", "active"]

SESS_HEADERS = [
    "session_id",
    "title",
    "genre",
    "total_duration_min",
    "status",
    "updated_at_utc",
]

CH_HEADERS = [
    "session_id",
    "chapter_index",
    "moment_key",
    "chapter_type",
    "planned_duration_sec",
    "prato",
    "musica",
    "artista",
    "texto_card_prato",
    "texto_card_musica",
    "texto_card_harmonizacao",
    "texto_destaque",
    "music_title",
    "music_artist",
    "link_context_input",
    "ai_story_text",
    "ai_music_alternatives",
    "ai_experience_actions",
    "ai_notes",
    "updated_at_utc",
    "vinho",
    "texto_vinho",
]

LIVE_BASE_HEADERS = [
    "session_id",
    "current_chapter_index",
    "updated_at_utc",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    value = str(value)
    if value.lower() == "nan":
        return ""
    return value.strip()


def esc(value: Any) -> str:
    return html.escape(safe_text(value))


def pick_first(row: Dict[str, Any], cols: List[str], default: str = "") -> str:
    for col in cols:
        value = safe_text(row.get(col, ""))
        if value:
            return value
    return default


def fmt_mmss(value: Any) -> str:
    try:
        total_seconds = int(float(value or 0))
    except Exception:
        total_seconds = 0

    total_seconds = max(total_seconds, 0)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def app_bootstrap() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            background: {BRAND_BG} !important;
        }}

        .yv-title {{
            color: #47372E;
            font-family: Georgia, "Times New Roman", serif;
            letter-spacing: 0.5px;
            margin: 0;
            font-size: 48px;
            font-weight: 700;
        }}

        .yv-subtitle {{
            color: rgba(14,42,71,0.72);
            font-size: 18px;
            margin-top: 8px;
        }}

        .top-pill {{
            display:inline-block;
            padding: 10px 18px;
            border-radius: 999px;
            background: rgba(14,42,71,0.08);
            border: 1px solid rgba(14,42,71,0.12);
            color: {BRAND_BLUE};
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}

        .session-pill {{
            display:inline-block;
            padding: 9px 18px;
            border-radius: 999px;
            background: rgba(14,42,71,0.08);
            border: 1px solid rgba(14,42,71,0.12);
            color: {BRAND_BLUE};
            font-weight: 700;
            font-size: 13px;
        }}

        .hero-card {{
            background: {BRAND_BLUE};
            border-radius: 34px;
            padding: 42px 56px;
            margin: 22px 0 28px 0;
            color: #F7F0E8;
            box-shadow: 0 18px 50px rgba(14,42,71,0.16);
        }}

        .hero-label {{
            color: {BRAND_GOLD};
            font-size: 13px;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 24px;
        }}

        .hero-title {{
            font-family: Georgia, "Times New Roman", serif;
            color: #F7F0E8;
            font-size: 30px;
            line-height: 1.25;
            margin: 0 0 20px 0;
            font-weight: 700;
        }}

        .hero-soft {{
            background: rgba(255,255,255,0.55);
            color: #FFFFFF;
            border-radius: 22px;
            padding: 18px 22px;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 20px;
            font-weight: 700;
        }}

        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin-top: 18px;
        }}

        .info-card {{
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(14,42,71,0.10);
            border-radius: 22px;
            padding: 22px 24px;
            min-height: 220px;
            box-shadow: 0 12px 34px rgba(14,42,71,0.07);
        }}

        .info-card h3 {{
            font-family: Georgia, "Times New Roman", serif;
            color: {BRAND_BLUE};
            font-size: 22px;
            margin: 0 0 12px 0;
        }}

        .info-card p {{
            color: rgba(52,43,35,0.78);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 18px;
            line-height: 1.62;
            margin: 0;
        }}

        .wine-card {{
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(14,42,71,0.10);
            border-radius: 22px;
            padding: 22px 24px;
            margin-top: 18px;
            box-shadow: 0 12px 34px rgba(14,42,71,0.06);
        }}

        .wine-card h3 {{
            font-family: Georgia, "Times New Roman", serif;
            color: {BRAND_BLUE};
            font-size: 22px;
            margin: 0 0 10px 0;
        }}

        .wine-name {{
            font-weight: 700;
            color: {BRAND_BLUE};
            margin-bottom: 6px;
            font-size: 17px;
        }}

        .wine-text {{
            color: rgba(52,43,35,0.78);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 17px;
            line-height: 1.55;
        }}

        .service-card {{
            background: rgba(255,255,255,0.72);
            border-radius: 24px;
            padding: 32px 34px;
            margin-top: 22px;
            box-shadow: 0 12px 34px rgba(14,42,71,0.07);
        }}

        .service-title {{
            font-family: Georgia, "Times New Roman", serif;
            color: {BRAND_BLUE};
            font-size: 38px;
            margin-bottom: 8px;
        }}

        .service-subtitle {{
            color: rgba(52,43,35,0.64);
            font-size: 17px;
            line-height: 1.55;
        }}

        .ok-box {{
            background: rgba(14,42,71,0.08);
            border: 1px solid rgba(14,42,71,0.16);
            border-radius: 14px;
            padding: 12px 16px;
            color: {BRAND_BLUE};
            font-weight: 700;
            margin: 8px 0 16px 0;
        }}

        .stButton > button {{
            border-radius: 999px !important;
            background: {BRAND_BLUE} !important;
            color: white !important;
            border: 0 !important;
            font-family: Georgia, "Times New Roman", serif !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            min-height: 48px !important;
        }}

        .stSelectbox label {{
            color: {BRAND_BLUE} !important;
            font-family: Georgia, "Times New Roman", serif !important;
            font-size: 16px !important;
        }}

        @media (max-width: 900px) {{
            .yv-title {{
                font-size: 34px;
            }}

            .hero-card {{
                padding: 30px 24px;
            }}

            .grid-3 {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    try:
        sheet_id = st.secrets["google"]["sheet_id"]
    except Exception:
        raise RuntimeError("Falta [google].sheet_id nos Secrets.")

    google_block = st.secrets.get("google", {})
    sa_info: Dict[str, Any] = {}

    if google_block.get("service_account_json"):
        sa_info = json.loads(google_block["service_account_json"])
    elif "gcp_service_account" in st.secrets:
        sa_info = dict(st.secrets["gcp_service_account"])
    else:
        raise RuntimeError("Use [google].service_account_json ou [gcp_service_account] nos Secrets.")

    private_key = sa_info.get("private_key", "")
    if "\\n" in private_key and "\n" not in private_key:
        sa_info["private_key"] = private_key.replace("\\n", "\n")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id)


def ws_get_or_create(title: str, headers: List[str]):
    sh = get_sheet()

    try:
        ws = sh.worksheet(title)
        if headers and not ws.row_values(1):
            ws.append_row(headers)
        return ws
    except Exception:
        ws = sh.add_worksheet(title=title, rows=1000, cols=max(12, len(headers)))
        if headers:
            ws.append_row(headers)
        return ws


def ws_read_df(title: str, headers: Optional[List[str]] = None) -> pd.DataFrame:
    ws = ws_get_or_create(title, headers or [])
    values = ws.get_all_values()

    if not values or not values[0]:
        return pd.DataFrame(columns=headers or [])

    current_headers = values[0]
    rows = values[1:]

    return pd.DataFrame(rows, columns=current_headers)


def normalize_sessions(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=SESS_HEADERS)

    if "session_id" not in df.columns:
        if "sid" in df.columns:
            df["session_id"] = df["sid"]
        elif "session" in df.columns:
            df["session_id"] = df["session"]

    for col in SESS_HEADERS:
        if col not in df.columns:
            df[col] = ""

    return df[SESS_HEADERS].copy()


def list_sessions() -> pd.DataFrame:
    df = ws_read_df("sessions", SESS_HEADERS)
    df = normalize_sessions(df)

    if df.empty:
        return df

    df["session_id"] = df["session_id"].astype(str)

    if "updated_at_utc" in df.columns:
        df = df.sort_values("updated_at_utc", ascending=False)

    return df.reset_index(drop=True)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    df = list_sessions()

    if df.empty:
        return None

    match = df[df["session_id"].astype(str) == session_id]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def normalize_chapters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=CH_HEADERS)

    for col in CH_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[CH_HEADERS].copy()

    df["session_id"] = df["session_id"].astype(str)
    df["chapter_index"] = pd.to_numeric(df["chapter_index"], errors="coerce").fillna(0).astype(int)
    df["planned_duration_sec"] = pd.to_numeric(df["planned_duration_sec"], errors="coerce").fillna(240).astype(int)

    return df.sort_values("chapter_index").reset_index(drop=True)


def read_chapters(session_id: str) -> pd.DataFrame:
    df = ws_read_df("chapters", CH_HEADERS)

    if df.empty:
        return pd.DataFrame(columns=CH_HEADERS)

    df = normalize_chapters(df)
    df = df[df["session_id"].astype(str) == session_id].copy()

    return df.sort_values("chapter_index").reset_index(drop=True)


def live_ws():
    return ws_get_or_create("live", LIVE_BASE_HEADERS)


def ensure_live_schema() -> Tuple[Any, List[str], Dict[str, int]]:
    ws = live_ws()
    values = ws.get_all_values()

    if not values:
        ws.append_row(LIVE_BASE_HEADERS)
        values = [LIVE_BASE_HEADERS]

    headers = values[0]

    required = ["session_id", "current_chapter_index", "updated_at_utc"]

    changed = False
    for h in required:
        if h not in headers:
            headers.append(h)
            changed = True

    if changed:
        ws.update("A1", [headers])

    col = {h: headers.index(h) + 1 for h in headers}
    return ws, headers, col


def get_live_index(session_id: str) -> int:
    ws, headers, col = ensure_live_schema()
    values = ws.get_all_values()

    if len(values) < 2:
        return 1

    sid_col = col["session_id"] - 1
    idx_col = col["current_chapter_index"] - 1

    for row in values[1:]:
        row = row + [""] * (len(headers) - len(row))

        if safe_text(row[sid_col]) == session_id:
            try:
                return max(int(float(row[idx_col])), 1)
            except Exception:
                return 1

    return 1


def set_live_index(session_id: str, idx: int) -> None:
    ws, headers, col = ensure_live_schema()
    values = ws.get_all_values()

    idx = int(idx)
    now = utc_now()

    sid_col = col["session_id"]
    current_col = col["current_chapter_index"]
    updated_col = col["updated_at_utc"]

    target_row = None

    for row_number, row in enumerate(values[1:], start=2):
        row = row + [""] * (len(headers) - len(row))
        if safe_text(row[sid_col - 1]) == session_id:
            target_row = row_number
            break

    if target_row is None:
        new_row = [""] * len(headers)
        new_row[sid_col - 1] = session_id
        new_row[current_col - 1] = str(idx)
        new_row[updated_col - 1] = now
        ws.append_row(new_row)
    else:
        ws.update_cell(target_row, current_col, str(idx))
        ws.update_cell(target_row, updated_col, now)

    st.session_state[f"live_idx_{session_id}"] = idx


def auth_login(username: str, password: str) -> Optional[Dict[str, str]]:
    df = ws_read_df("users", USERS_HEADERS)

    if df.empty:
        return None

    for _, row in df.iterrows():
        active = safe_text(row.get("active", "1")).lower()

        if active in ["0", "false", "não", "nao", "inativo"]:
            continue

        if safe_text(row.get("username", "")) == safe_text(username) and safe_text(row.get("password", "")) == safe_text(password):
            return {
                "username": safe_text(row.get("username", "")),
                "role": safe_text(row.get("role", "staff")),
            }

    return None


def logout() -> None:
    st.session_state.pop("user", None)
    st.rerun()


def get_default_sid() -> str:
    sid = safe_text(st.query_params.get("sid", ""))

    if sid:
        return sid

    sessions = list_sessions()

    if not sessions.empty:
        return safe_text(sessions.iloc[0]["session_id"])

    return "bossa-nova-yvora"


def get_current_row(session_id: str) -> Tuple[pd.DataFrame, int, Dict[str, Any]]:
    chapters = read_chapters(session_id)

    if chapters.empty:
        return chapters, 1, {}

    current_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == current_idx]

    if current.empty:
        current = chapters.iloc[[0]]
        current_idx = int(current.iloc[0]["chapter_index"])
        set_live_index(session_id, current_idx)

    return chapters, current_idx, current.iloc[0].to_dict()


def render_top(title: str, session_id: str) -> None:
    col_logo, col_title, col_pills = st.columns([0.7, 4.5, 1.6])

    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=90)

    with col_title:
        st.markdown(f'<div class="yv-title">YVORA Music | {esc(title)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="yv-subtitle">Controle do jantar, tempo e sequência da experiência.</div>', unsafe_allow_html=True)

    with col_pills:
        st.markdown(f'<div class="top-pill">{esc(title)}</div><br>', unsafe_allow_html=True)
        st.markdown(f'<div class="session-pill">{esc(session_id)}</div>', unsafe_allow_html=True)


def render_chapter_cards(row: Dict[str, Any]) -> None:
    texto_prato = esc(row.get("texto_card_prato", ""))
    texto_musica = esc(row.get("texto_card_musica", ""))
    texto_harmonizacao = esc(row.get("texto_card_harmonizacao", ""))

    st.markdown(
        f"""
        <div class="grid-3">
            <div class="info-card">
                <h3>Prato</h3>
                <p>{texto_prato}</p>
            </div>
            <div class="info-card">
                <h3>Música</h3>
                <p>{texto_musica}</p>
            </div>
            <div class="info-card">
                <h3>Harmonização</h3>
                <p>{texto_harmonizacao}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    vinho = esc(row.get("vinho", ""))
    texto_vinho = esc(row.get("texto_vinho", ""))

    if vinho or texto_vinho:
        st.markdown(
            f"""
            <div class="wine-card">
                <h3>Vinho sugerido</h3>
                <div class="wine-name">{vinho}</div>
                <div class="wine-text">{texto_vinho}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_client(session_id: str) -> None:
    session = get_session(session_id)

    if not session:
        st.error("Sessão não encontrada.")
        return

    chapters, idx, row = get_current_row(session_id)

    if chapters.empty or not row:
        st.warning("Sessão sem capítulos.")
        return

    musica = pick_first(row, ["musica", "music_title"], "Ao vivo")
    artista = pick_first(row, ["artista", "music_artist"], "")
    prato = pick_first(row, ["prato"], "")
    momento = pick_first(row, ["moment_key"], "")
    destaque = pick_first(row, ["texto_destaque"], "")

    subtitle_parts = [artista, prato, momento]
    subtitle = " · ".join([x for x in subtitle_parts if x])

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-label">Agora tocando</div>
            <div class="hero-title">{esc(musica)}</div>
            <div style="font-size:18px;color:rgba(247,240,232,0.82);margin-bottom:22px;">{esc(subtitle)}</div>
            <div style="font-family:Georgia,'Times New Roman',serif;font-size:28px;line-height:1.48;">{esc(destaque)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_chapter_cards(row)


def render_operation(session_id: str) -> None:
    session = get_session(session_id)

    if not session:
        st.error("Sessão não encontrada.")
        return

    chapters, idx, row = get_current_row(session_id)

    if chapters.empty or not row:
        st.warning("Sessão sem capítulos.")
        return

    indexes = chapters["chapter_index"].tolist()
    min_idx = min(indexes)
    max_idx = max(indexes)

    musica = pick_first(row, ["musica", "music_title"], "")
    prato = pick_first(row, ["prato"], "")

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-label">Controle operacional</div>
            <div class="hero-title">Etapa ativa {idx} de {max_idx}: {esc(prato)} · {esc(musica)}</div>
            <div class="hero-soft">Modo musical: Banda ao vivo</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="ok-box">
            Etapa gravada na aba live: {idx}
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.2])

    with c1:
        if st.button("Voltar", use_container_width=True, key=f"back_{session_id}_{idx}"):
            prev_indexes = [i for i in indexes if i < idx]
            new_idx = max(prev_indexes) if prev_indexes else min_idx
            set_live_index(session_id, new_idx)
            st.rerun()

    with c2:
        if st.button("Avançar", use_container_width=True, key=f"next_{session_id}_{idx}"):
            next_indexes = [i for i in indexes if i > idx]
            new_idx = min(next_indexes) if next_indexes else max_idx
            set_live_index(session_id, new_idx)
            st.rerun()

    with c3:
        selected = st.selectbox(
            "Ir para",
            indexes,
            index=indexes.index(idx) if idx in indexes else 0,
            key=f"jump_{session_id}",
        )

        if int(selected) != int(idx):
            set_live_index(session_id, int(selected))
            st.rerun()

    with c4:
        if st.button("Recarregar", use_container_width=True, key=f"refresh_{session_id}_{idx}"):
            st.rerun()

    st.markdown(
        """
        <div class="service-card">
            <div class="service-title">Status de serviço</div>
            <div class="service-subtitle">
                Use estes estados para coordenar cozinha, salão e música sem depender do relógio.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        st.button("Preparando", use_container_width=True, disabled=True)
    with s2:
        st.button("Pronto", use_container_width=True, disabled=True)
    with s3:
        st.button("Servido", use_container_width=True, disabled=True)

    st.markdown("### Narrativas da etapa ativa")
    render_chapter_cards(row)

    st.markdown("### Sequência completa")

    show = chapters.copy()
    show["duração"] = show["planned_duration_sec"].apply(fmt_mmss)

    keep = [
        "chapter_index",
        "moment_key",
        "chapter_type",
        "duração",
        "prato",
        "musica",
        "artista",
        "vinho",
    ]

    st.dataframe(show[keep], use_container_width=True, hide_index=True)


def render_band(session_id: str) -> None:
    chapters, idx, row = get_current_row(session_id)

    if chapters.empty or not row:
        st.warning("Sessão sem capítulos.")
        return

    musica = pick_first(row, ["musica", "music_title"], "")
    artista = pick_first(row, ["artista", "music_artist"], "")
    prato = pick_first(row, ["prato"], "")

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-label">Banda</div>
            <div class="hero-title">Etapa {idx}: {esc(musica)}</div>
            <div style="font-size:18px;color:rgba(247,240,232,0.82);">{esc(artista)} · {esc(prato)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Roteiro musical")

    show = chapters.copy()
    show["duração"] = show["planned_duration_sec"].apply(fmt_mmss)

    keep = [
        "chapter_index",
        "moment_key",
        "duração",
        "musica",
        "artista",
        "prato",
        "vinho",
    ]

    st.dataframe(show[keep], use_container_width=True, hide_index=True)

    st.markdown("### Narrativa da etapa atual")
    render_chapter_cards(row)


def page_login(session_id: str) -> None:
    render_top("Login", session_id)

    with st.sidebar:
        st.markdown("### Acesso interno")
        username = st.text_input("Login")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = auth_login(username, password)

            if not user:
                st.warning("Login ou senha incorretos.")
            else:
                st.session_state["user"] = user
                st.rerun()

    render_client(session_id)


def main() -> None:
    app_bootstrap()

    try:
        _ = get_sheet()
    except Exception as e:
        st.error(f"Erro de configuração: {e}")
        return

    session_id = get_default_sid()
    view = safe_text(st.query_params.get("view", "cliente")).lower()
    user = st.session_state.get("user")

    if view not in ["cliente", "banda", "operacao"]:
        view = "cliente"

    with st.sidebar:
        st.markdown("### Visões")
        chosen_view = st.radio(
            "Escolha a visão",
            ["cliente", "banda", "operacao"],
            index=["cliente", "banda", "operacao"].index(view),
        )

        if chosen_view != view:
            st.query_params["view"] = chosen_view
            st.query_params["sid"] = session_id
            st.rerun()

        sessions = list_sessions()

        if not sessions.empty:
            session_options = sessions["session_id"].tolist()
            chosen_sid = st.selectbox(
                "Sessão",
                session_options,
                index=session_options.index(session_id) if session_id in session_options else 0,
            )

            if chosen_sid != session_id:
                st.query_params["sid"] = chosen_sid
                st.query_params["view"] = view
                st.rerun()

        if user:
            st.caption(f"{user.get('username')} · {user.get('role')}")

            if st.button("Sair"):
                logout()

    if view == "cliente":
        render_top("Cliente", session_id)
        render_client(session_id)
        return

    if view == "banda":
        render_top("Banda", session_id)
        render_band(session_id)
        return

    if view == "operacao":
        if not user:
            page_login(session_id)
            return

        role = safe_text(user.get("role", "")).lower()

        if role not in ["admin", "ops", "operacao", "operation", "staff"]:
            st.error("Usuário sem permissão para operação.")
            return

        render_top("Operação", session_id)
        render_operation(session_id)
        return


if __name__ == "__main__":
    main()
