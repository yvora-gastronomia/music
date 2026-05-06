import os
import json
import html
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


APP_TITLE = "YVORA Music"
BRAND_BG = "#EFE7DD"
BRAND_BLUE = "#0E2A47"

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
    "vinho",
    "texto_vinho",
]

LIVE_HEADERS = [
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


def escape(value: Any) -> str:
    return html.escape(safe_text(value))


def fmt_mmss(total_seconds: Any) -> str:
    try:
        total_seconds = int(float(total_seconds or 0))
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
            color: {BRAND_BLUE};
            font-family: Georgia, "Times New Roman", serif;
            letter-spacing: 0.5px;
            margin: 0;
          }}

          .divider {{
            height: 1px;
            background: linear-gradient(to right, rgba(14,42,71,0), rgba(14,42,71,0.35), rgba(14,42,71,0));
            margin: 10px 0 14px 0;
          }}

          .meta {{
            color: rgba(14,42,71,0.70);
            font-size: 13px;
          }}

          .hero-card {{
            background: {BRAND_BLUE};
            border-radius: 0 0 36px 36px;
            padding: 36px 52px 44px 52px;
            margin-bottom: 28px;
            color: #F7F0E8;
            box-shadow: 0 18px 50px rgba(14,42,71,0.16);
          }}

          .hero-label {{
            color: rgba(247,240,232,0.72);
            font-size: 13px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 12px;
          }}

          .hero-title {{
            font-family: Georgia, "Times New Roman", serif;
            color: #F7F0E8;
            font-size: 42px;
            line-height: 1.10;
            margin: 0 0 10px 0;
          }}

          .hero-subtitle {{
            color: rgba(247,240,232,0.82);
            font-size: 18px;
            line-height: 1.45;
          }}

          .hero-text {{
            margin-top: 24px;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 27px;
            line-height: 1.48;
            color: rgba(247,240,232,0.94);
          }}

          .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin-top: 8px;
          }}

          .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
            margin-top: 8px;
          }}

          .info-card {{
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(14,42,71,0.10);
            border-radius: 22px;
            padding: 22px 24px;
            min-height: 210px;
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

          .small-card {{
            background: rgba(255,255,255,0.65);
            border: 1px solid rgba(14,42,71,0.14);
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 12px;
          }}

          .small-title {{
            font-family: Georgia, "Times New Roman", serif;
            color: {BRAND_BLUE};
            font-size: 22px;
            margin: 0 0 6px 0;
          }}

          .small-muted {{
            color: rgba(14,42,71,0.72);
            font-size: 14px;
            line-height: 1.55;
          }}

          .pill {{
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background: rgba(14,42,71,0.08);
            color: {BRAND_BLUE};
            font-size:12px;
            margin-right:6px;
            margin-bottom:6px;
          }}

          .ops-current {{
            background: rgba(14,42,71,0.08);
            border: 1px solid rgba(14,42,71,0.18);
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 12px;
          }}

          .stButton > button {{
            border-radius: 999px !important;
          }}

          .yv-badge {{
            display:inline-block;
            padding:4px 10px;
            border-radius:999px;
            background: rgba(14,42,71,0.08);
            color: {BRAND_BLUE};
            font-size:12px;
            margin-right:6px;
          }}

          @media (max-width: 900px) {{
            .hero-card {{
              padding: 28px 24px 34px 24px;
              border-radius: 0 0 28px 28px;
            }}

            .hero-title {{
              font-size: 31px;
            }}

            .hero-subtitle {{
              font-size: 16px;
            }}

            .hero-text {{
              font-size: 22px;
            }}

            .grid-3, .grid-2 {{
              grid-template-columns: 1fr;
              gap: 12px;
            }}

            .info-card {{
              min-height: unset;
              padding: 20px 22px;
            }}

            .info-card p {{
              font-size: 17px;
            }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(subtitle: str) -> None:
    col1, col2 = st.columns([1, 4])
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

    with col1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=90)

    with col2:
        st.markdown(f'<h2 class="yv-title">{escape(APP_TITLE)}</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">{escape(subtitle)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


@st.cache_resource
def get_sheet():
    import gspread
    from google.oauth2.service_account import Credentials

    try:
        sheet_id = st.secrets["google"]["sheet_id"]
    except Exception:
        raise RuntimeError("Falta [google].sheet_id nos Secrets")

    sa_info: Dict[str, Any] = {}
    google_block = st.secrets.get("google", {})

    if google_block.get("service_account_json"):
        sa_info = json.loads(google_block["service_account_json"])
    elif "gcp_service_account" in st.secrets:
        sa_info = dict(st.secrets["gcp_service_account"])
    else:
        raise RuntimeError("Use [google].service_account_json ou [gcp_service_account] nos Secrets.")

    private_key = sa_info.get("private_key", "")

    if not private_key:
        raise RuntimeError("private_key ausente nas credenciais.")

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
        row1 = ws.row_values(1)

        if headers and not row1:
            ws.append_row(headers)

        return ws

    except Exception:
        ws = sh.add_worksheet(title=title, rows=1000, cols=max(12, len(headers) or 12))

        if headers:
            ws.append_row(headers)

        return ws


def ws_read_df(title: str, headers: List[str]) -> pd.DataFrame:
    ws = ws_get_or_create(title, headers)
    values = ws.get_all_values()

    if not values or not values[0]:
        return pd.DataFrame(columns=headers)

    current_headers = values[0]
    rows = values[1:]

    return pd.DataFrame(rows, columns=current_headers)


def ws_replace_all(title: str, headers: List[str], df: pd.DataFrame) -> None:
    ws = ws_get_or_create(title, headers)

    output = [headers]

    for _, row in df.iterrows():
        output.append([safe_text(row.get(h, "")) for h in headers])

    ws.clear()
    ws.update("A1", output)


def normalize_chapters_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=CH_HEADERS)

    for col in CH_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[CH_HEADERS].copy()

    df["chapter_index"] = pd.to_numeric(df["chapter_index"], errors="coerce").fillna(0).astype(int)
    df["planned_duration_sec"] = pd.to_numeric(df["planned_duration_sec"], errors="coerce").fillna(240).astype(int)

    return df.sort_values("chapter_index").reset_index(drop=True)


def list_sessions_sheet() -> pd.DataFrame:
    df = ws_read_df("sessions", SESS_HEADERS)

    if df.empty:
        return df

    for col in SESS_HEADERS:
        if col not in df.columns:
            df[col] = ""

    return df[SESS_HEADERS].copy()


def get_session_row(session_id: str) -> Optional[Dict[str, Any]]:
    df = list_sessions_sheet()

    if df.empty:
        return None

    df["session_id"] = df["session_id"].astype(str)
    match = df[df["session_id"] == session_id]

    if match.empty:
        return None

    return match.iloc[0].to_dict()


def read_chapters(session_id: str) -> pd.DataFrame:
    df = ws_read_df("chapters", CH_HEADERS)
    df = normalize_chapters_df(df)

    if df.empty:
        return df

    df["session_id"] = df["session_id"].astype(str)
    df = df[df["session_id"] == session_id].copy()

    return df.sort_values("chapter_index").reset_index(drop=True)


def get_live_index(session_id: str) -> int:
    df = ws_read_df("live", LIVE_HEADERS)

    if df.empty or "session_id" not in df.columns:
        return 1

    df["session_id"] = df["session_id"].astype(str)
    match = df[df["session_id"] == session_id]

    if match.empty:
        return 1

    try:
        return int(float(match.iloc[0]["current_chapter_index"]))
    except Exception:
        return 1


def set_live_index(session_id: str, idx: int) -> None:
    df = ws_read_df("live", LIVE_HEADERS)

    if df.empty:
        df = pd.DataFrame(columns=LIVE_HEADERS)

    for col in LIVE_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[LIVE_HEADERS].copy()
    df["session_id"] = df["session_id"].astype(str)

    now = utc_now()

    if session_id in df["session_id"].tolist():
        df.loc[df["session_id"] == session_id, "current_chapter_index"] = str(int(idx))
        df.loc[df["session_id"] == session_id, "updated_at_utc"] = now
    else:
        df.loc[len(df)] = [session_id, str(int(idx)), now]

    ws_replace_all("live", LIVE_HEADERS, df)


def upsert_session_status(session_id: str, status: str) -> None:
    df = list_sessions_sheet()

    if df.empty:
        df = pd.DataFrame(columns=SESS_HEADERS)

    for col in SESS_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[SESS_HEADERS].copy()
    df["session_id"] = df["session_id"].astype(str)

    valid_status = status if status in ["draft", "scheduled", "live", "finished", "cancelled"] else "live"

    if session_id in df["session_id"].tolist():
        df.loc[df["session_id"] == session_id, "status"] = valid_status
        df.loc[df["session_id"] == session_id, "updated_at_utc"] = utc_now()
    else:
        df.loc[len(df)] = [
            session_id,
            "YVORA Bossa Nova Experience",
            "Bossa Nova",
            "60",
            valid_status,
            utc_now(),
        ]

    ws_replace_all("sessions", SESS_HEADERS, df)


def auth_login(username: str, password: str) -> Optional[Dict[str, str]]:
    df = ws_read_df("users", USERS_HEADERS)

    if df.empty:
        return None

    u = safe_text(username)
    p = safe_text(password)

    for _, row in df.iterrows():
        active = safe_text(row.get("active", "1")).lower()

        if active in ["0", "false", "não", "nao", "inativo"]:
            continue

        if safe_text(row.get("username", "")) == u and safe_text(row.get("password", "")) == p:
            role = safe_text(row.get("role", "staff")) or "staff"
            return {"username": u, "role": role}

    return None


def logout() -> None:
    st.session_state.pop("user", None)
    st.rerun()


def get_default_sid() -> str:
    qp_sid = safe_text(st.query_params.get("sid", ""))

    if qp_sid:
        return qp_sid

    sessions = list_sessions_sheet()

    if not sessions.empty and "session_id" in sessions.columns:
        return safe_text(sessions.iloc[0]["session_id"])

    return "bossa-nova-yvora"


def get_current_chapter(session_id: str) -> tuple[pd.DataFrame, int, Dict[str, Any]]:
    chapters = read_chapters(session_id)

    if chapters.empty:
        return chapters, 1, {}

    cur_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == cur_idx]

    if current.empty:
        current = chapters.iloc[[0]]
        cur_idx = int(current.iloc[0]["chapter_index"])

    return chapters, cur_idx, current.iloc[0].to_dict()


def render_live_controls(session_id: str, chapters: pd.DataFrame, cur_idx: int) -> None:
    if chapters.empty:
        return

    indexes = chapters["chapter_index"].tolist()

    c1, c2, c3, c4, c5 = st.columns([1.1, 1, 1, 1, 2])

    with c1:
        if st.button("Iniciar evento", use_container_width=True):
            set_live_index(session_id, min(indexes))
            upsert_session_status(session_id, "live")
            st.rerun()

    with c2:
        if st.button("◀ Anterior", use_container_width=True):
            previous_indexes = [i for i in indexes if i < cur_idx]
            new_idx = max(previous_indexes) if previous_indexes else min(indexes)
            set_live_index(session_id, new_idx)
            st.rerun()

    with c3:
        if st.button("Próximo ▶", use_container_width=True):
            next_indexes = [i for i in indexes if i > cur_idx]
            new_idx = min(next_indexes) if next_indexes else max(indexes)
            set_live_index(session_id, new_idx)
            st.rerun()

    with c4:
        if st.button("Voltar início", use_container_width=True):
            set_live_index(session_id, min(indexes))
            st.rerun()

    with c5:
        chosen = st.selectbox(
            "Ir para capítulo",
            indexes,
            index=indexes.index(cur_idx) if cur_idx in indexes else 0,
            key="jump_chapter",
        )

        if chosen != cur_idx:
            set_live_index(session_id, int(chosen))
            st.rerun()


def render_chapter_narratives(row: Dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="grid-3">
          <div class="info-card">
            <h3>Prato</h3>
            <p>{escape(row.get("texto_card_prato", ""))}</p>
          </div>

          <div class="info-card">
            <h3>Música</h3>
            <p>{escape(row.get("texto_card_musica", ""))}</p>
          </div>

          <div class="info-card">
            <h3>Harmonização</h3>
            <p>{escape(row.get("texto_card_harmonizacao", ""))}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    vinho = escape(row.get("vinho", ""))
    texto_vinho = escape(row.get("texto_vinho", ""))

    if vinho or texto_vinho:
        st.markdown(
            f"""
            <div class="small-card" style="margin-top:18px;">
              <div class="small-title">Vinho sugerido</div>
              <div style="font-weight:700; color:{BRAND_BLUE}; margin-bottom:6px;">{vinho}</div>
              <div class="small-muted">{texto_vinho}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_client_view(session_id: str, show_controls: bool = False) -> None:
    session = get_session_row(session_id)

    if not session:
        st.error("Sessão não encontrada na aba sessions.")
        return

    chapters, cur_idx, row = get_current_chapter(session_id)

    if chapters.empty or not row:
        st.warning("Sessão sem capítulos na aba chapters.")
        return

    if show_controls:
        render_live_controls(session_id, chapters, cur_idx)

    subtitle_parts = [
        escape(row.get("artista", "")),
        escape(row.get("prato", "")),
        escape(row.get("moment_key", "")),
    ]
    subtitle = " · ".join([p for p in subtitle_parts if p])

    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-label">Agora tocando</div>
          <h1 class="hero-title">{escape(row.get("musica", ""))}</h1>
          <div class="hero-subtitle">{subtitle}</div>
          <div class="hero-text">{escape(row.get("texto_destaque", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_chapter_narratives(row)


def safe_setlist_df(chapters: pd.DataFrame) -> pd.DataFrame:
    if chapters.empty:
        return chapters

    show = chapters.copy()

    show["planned_duration_sec"] = pd.to_numeric(show["planned_duration_sec"], errors="coerce").fillna(0).astype(int)
    show["duracao"] = show["planned_duration_sec"].apply(fmt_mmss)

    keep = [
        "chapter_index",
        "moment_key",
        "chapter_type",
        "duracao",
        "prato",
        "musica",
        "artista",
        "vinho",
    ]

    return show[[c for c in keep if c in show.columns]].copy()


def page_band_view(session_id: str) -> None:
    render_header("Banda")

    chapters, cur_idx, row = get_current_chapter(session_id)

    if chapters.empty or not row:
        st.warning("Sem capítulos para esta sessão.")
        return

    st.markdown("### Agora")
    st.markdown(
        f"""
        <div class="ops-current">
          <span class="pill">Capítulo {escape(cur_idx)}</span>
          <span class="pill">{escape(row.get("moment_key", ""))}</span>
          <div class="small-title">{escape(row.get("musica", ""))}</div>
          <div class="small-muted">{escape(row.get("artista", ""))}</div>
          <div style="margin-top:8px;"><b>Prato:</b> {escape(row.get("prato", ""))}</div>
          <div style="margin-top:8px; line-height:1.5;">{escape(row.get("texto_card_musica", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Roteiro completo")
    st.dataframe(safe_setlist_df(chapters), use_container_width=True, hide_index=True)


def page_kitchen_view(session_id: str) -> None:
    render_header("Cozinha")

    chapters, cur_idx, row = get_current_chapter(session_id)

    if chapters.empty or not row:
        st.warning("Sem capítulos para esta sessão.")
        return

    st.markdown("### Agora no salão")
    st.markdown(
        f"""
        <div class="ops-current">
          <span class="pill">Capítulo {escape(cur_idx)}</span>
          <span class="pill">{escape(row.get("chapter_type", ""))}</span>
          <div class="small-title">{escape(row.get("prato", ""))}</div>
          <div class="small-muted">{escape(row.get("musica", ""))} · {escape(row.get("artista", ""))}</div>
          <div style="margin-top:10px; line-height:1.55;"><b>Momento:</b> {escape(row.get("moment_key", ""))}</div>
          <div style="margin-top:10px; line-height:1.55;"><b>Vinho:</b> {escape(row.get("vinho", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Narrativa do prato atual")
    st.info(safe_text(row.get("texto_card_prato", "")))

    upcoming = chapters[chapters["chapter_index"] >= cur_idx].copy()
    upcoming = upcoming[["chapter_index", "moment_key", "prato", "musica", "planned_duration_sec"]].copy()
    upcoming["duracao"] = upcoming["planned_duration_sec"].apply(fmt_mmss)
    upcoming = upcoming.drop(columns=["planned_duration_sec"])

    st.markdown("### Próximas etapas")
    st.dataframe(upcoming, use_container_width=True, hide_index=True)


def page_ops_view(session_id: str) -> None:
    render_header("Operação")

    chapters, cur_idx, row = get_current_chapter(session_id)

    if chapters.empty or not row:
        st.warning(f"Timeline não encontrada para a sessão: {session_id}")
        return

    render_live_controls(session_id, chapters, cur_idx)

    st.markdown("### Capítulo atual")
    st.markdown(
        f"""
        <div class="ops-current">
          <span class="pill">Capítulo {escape(cur_idx)}</span>
          <span class="pill">{escape(row.get("chapter_type", ""))}</span>
          <span class="pill">{escape(row.get("moment_key", ""))}</span>
          <div class="small-title">{escape(row.get("musica", ""))}</div>
          <div class="small-muted">{escape(row.get("artista", ""))}</div>
          <div style="margin-top:8px;"><b>Prato/serviço:</b> {escape(row.get("prato", ""))}</div>
          <div style="margin-top:8px;"><b>Vinho:</b> {escape(row.get("vinho", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Narrativas do capítulo")
    render_chapter_narratives(row)

    st.markdown("### Sequência completa")
    st.dataframe(safe_setlist_df(chapters), use_container_width=True, hide_index=True)


def page_login() -> Optional[Dict[str, str]]:
    render_header("Login")

    with st.sidebar:
        st.markdown("### Acesso interno")
        username = st.text_input("Login")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = auth_login(username, password)

            if not user:
                st.warning("Login ou senha incorretos.")
                return None

            st.session_state["user"] = user
            st.rerun()

    return st.session_state.get("user")


def role_can_access(role: str, view: str) -> bool:
    role = safe_text(role).lower()
    view = safe_text(view).lower()

    if role == "admin":
        return True

    allowed = {
        "ops": ["operacao", "cliente", "banda", "cozinha"],
        "operation": ["operacao", "cliente", "banda", "cozinha"],
        "band": ["banda", "cliente"],
        "kitchen": ["cozinha"],
        "client": ["cliente"],
        "staff": ["cliente", "banda", "cozinha"],
    }

    return view in allowed.get(role, [])


def main() -> None:
    app_bootstrap()

    try:
        _ = get_sheet()
    except Exception as e:
        st.error(f"Erro de configuração: {e}")
        st.info("Verifique o sheet_id e as credenciais nos Secrets do Streamlit.")
        return

    user = st.session_state.get("user")
    view = safe_text(st.query_params.get("view", "")).lower()
    sid = get_default_sid()

    path = safe_text(st.query_params.get("path", "")).lower()

    if not view:
        # compatibilidade com alguns links antigos do Streamlit
        raw_path = safe_text(st.experimental_get_query_params().get("view", [""])[0]) if hasattr(st, "experimental_get_query_params") else ""
        view = raw_path.lower()

    # compatibilidade com URLs antigas como /Banda, /Operacao
    current_path = safe_text(st.context.url).lower() if hasattr(st, "context") else ""
    if not view:
        if "/banda" in current_path:
            view = "banda"
        elif "/cozinha" in current_path:
            view = "cozinha"
        elif "/operacao" in current_path or "/operação" in current_path:
            view = "operacao"
        elif "/cliente" in current_path:
            view = "cliente"

    if not view:
        view = "cliente"

    with st.sidebar:
        st.markdown("### Visões YVORA")
        selected_view = st.radio(
            "Escolha a visão",
            ["cliente", "banda", "cozinha", "operacao"],
            index=["cliente", "banda", "cozinha", "operacao"].index(view) if view in ["cliente", "banda", "cozinha", "operacao"] else 0,
        )

        if selected_view != view:
            st.query_params["view"] = selected_view
            st.query_params["sid"] = sid
            st.rerun()

        sessions = list_sessions_sheet()

        if not sessions.empty:
            session_options = sessions["session_id"].tolist()
            chosen_sid = st.selectbox(
                "Sessão",
                session_options,
                index=session_options.index(sid) if sid in session_options else 0,
            )

            if chosen_sid != sid:
                st.query_params["sid"] = chosen_sid
                st.query_params["view"] = view
                st.rerun()

        if user:
            st.markdown(
                f"<span class='yv-badge'>{escape(user.get('username'))}</span>"
                f"<span class='yv-badge'>{escape(user.get('role'))}</span>",
                unsafe_allow_html=True,
            )

            if st.button("Sair"):
                logout()

    # Cliente e banda ficam simples para teste e uso em tela.
    if view == "cliente":
        render_header("Cliente")
        render_client_view(sid, show_controls=False)
        time.sleep(2)
        st.rerun()
        return

    if view == "banda":
        page_band_view(sid)
        time.sleep(2)
        st.rerun()
        return

    # Cozinha e operação exigem login.
    if view in ["cozinha", "operacao"]:
        if not user:
            user = page_login()
            if not user:
                return

        role = safe_text(user.get("role", "")).lower()

        if not role_can_access(role, view):
            st.error("Usuário sem permissão para esta área.")
            return

        if view == "cozinha":
            page_kitchen_view(sid)
        else:
            page_ops_view(sid)

        time.sleep(2)
        st.rerun()
        return


if __name__ == "__main__":
    main()
