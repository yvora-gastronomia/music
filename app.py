import os
import json
import html
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

APP_TITLE = "Yvora Music"
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

SERVICE_NOTES_HEADERS = [
    "session_id",
    "chapter_index",
    "view",
    "nota",
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
            font-size: 12px;
          }}

          .client-wrap {{
            max-width: 1180px;
            margin: 0 auto;
          }}

          .hero-card {{
            background: {BRAND_BLUE};
            border-radius: 0 0 36px 36px;
            padding: 38px 56px 46px 56px;
            margin-bottom: 30px;
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
            font-size: 28px;
            line-height: 1.48;
            color: rgba(247,240,232,0.94);
          }}

          .info-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin-top: 8px;
          }}

          .info-card {{
            background: rgba(255,255,255,0.70);
            border: 1px solid rgba(14,42,71,0.10);
            border-radius: 22px;
            padding: 22px 24px;
            min-height: 230px;
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
            background: rgba(255,255,255,0.62);
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
            color: rgba(14,42,71,0.70);
            font-size: 13px;
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
            padding: 0.25rem 0.75rem !important;
            min-height: 2.1rem !important;
            border-radius: 999px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
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
            .client-wrap {{
              max-width: 560px;
            }}

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

            .info-grid {{
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
        try:
            sa_info = json.loads(google_block["service_account_json"])
        except Exception as e:
            raise RuntimeError(f"google.service_account_json inválido: {e}")
    elif "gcp_service_account" in st.secrets:
        try:
            sa_info = dict(st.secrets["gcp_service_account"])
        except Exception as e:
            raise RuntimeError(f"[gcp_service_account] inválido: {e}")
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

    df["planned_duration_sec"] = (
        pd.to_numeric(df["planned_duration_sec"], errors="coerce")
        .fillna(300)
        .astype(int)
    )

    return df.sort_values("chapter_index").reset_index(drop=True)


def list_sessions_sheet() -> pd.DataFrame:
    df = ws_read_df("sessions", SESS_HEADERS)

    if df.empty:
        return df

    for col in SESS_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[SESS_HEADERS].copy()

    if "updated_at_utc" in df.columns:
        df = df.sort_values("updated_at_utc", ascending=False)

    return df


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


def read_service_notes(session_id: str, view: str = "") -> pd.DataFrame:
    df = ws_read_df("service_notes", SERVICE_NOTES_HEADERS)

    if df.empty:
        return pd.DataFrame(columns=SERVICE_NOTES_HEADERS)

    for col in SERVICE_NOTES_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df = df[SERVICE_NOTES_HEADERS].copy()
    df["session_id"] = df["session_id"].astype(str)
    df["chapter_index"] = pd.to_numeric(df["chapter_index"], errors="coerce").fillna(0).astype(int)
    df = df[df["session_id"] == session_id].copy()

    if view:
        df = df[df["view"].astype(str).str.lower() == view.lower()].copy()

    return df


def get_service_note(session_id: str, chapter_index: int, view: str = "cozinha") -> str:
    df = read_service_notes(session_id, view)

    if df.empty:
        return ""

    match = df[df["chapter_index"] == int(chapter_index)]

    if match.empty:
        return ""

    return safe_text(match.iloc[0].get("nota", ""))


def save_chapters(session_id: str, edited_session_df: pd.DataFrame) -> None:
    all_df = ws_read_df("chapters", CH_HEADERS)
    all_df = normalize_chapters_df(all_df)

    if all_df.empty:
        all_df = pd.DataFrame(columns=CH_HEADERS)

    all_df["session_id"] = all_df["session_id"].astype(str)
    kept = all_df[all_df["session_id"] != session_id].copy()

    edited_session_df = normalize_chapters_df(edited_session_df)
    edited_session_df["session_id"] = session_id

    final_df = pd.concat([kept, edited_session_df], ignore_index=True)
    final_df = final_df[CH_HEADERS].copy()

    ws_replace_all("chapters", CH_HEADERS, final_df)


def get_live_index(session_id: str) -> int:
    df = ws_read_df("live", LIVE_HEADERS)

    if df.empty or "session_id" not in df.columns:
        return 0

    df["session_id"] = df["session_id"].astype(str)
    match = df[df["session_id"] == session_id]

    if match.empty:
        return 0

    try:
        return int(float(match.iloc[0]["current_chapter_index"]))
    except Exception:
        return 0


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


def upsert_session(session_id: str, title: str, genre: str, total_min: int, status: str) -> None:
    df = list_sessions_sheet()

    if df.empty:
        df = pd.DataFrame(columns=SESS_HEADERS)

    df["session_id"] = df["session_id"].astype(str)

    valid_status = status if status in ["draft", "scheduled", "live", "finished", "cancelled"] else "draft"

    row = {
        "session_id": session_id,
        "title": title,
        "genre": genre,
        "total_duration_min": str(int(total_min)),
        "status": valid_status,
        "updated_at_utc": utc_now(),
    }

    if session_id in df["session_id"].tolist():
        for col, value in row.items():
            df.loc[df["session_id"] == session_id, col] = value
    else:
        df.loc[len(df)] = [row.get(h, "") for h in SESS_HEADERS]

    ws_replace_all("sessions", SESS_HEADERS, df[SESS_HEADERS])


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


def require_login_for_view(view: str) -> bool:
    return view in ["operacao", "cozinha"]


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


def render_login_box() -> Optional[Dict[str, str]]:
    with st.sidebar:
        st.markdown("### Acesso")
        username = st.text_input("Login")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = auth_login(username, password)

            if not user:
                st.warning("Login ou senha incorretos.")
                return None

            st.session_state["user"] = user
            st.success(f"Logado como {user['role']}")
            st.rerun()

    return st.session_state.get("user")


def get_default_sid() -> str:
    qp_sid = safe_text(st.query_params.get("sid", ""))

    if qp_sid:
        return qp_sid

    sessions = list_sessions_sheet()

    if not sessions.empty and "session_id" in sessions.columns:
        return safe_text(sessions.iloc[0]["session_id"])

    return "bossa-nova-yvora"


def get_current_row(session_id: str) -> Optional[Dict[str, Any]]:
    chapters = read_chapters(session_id)

    if chapters.empty:
        return None

    cur_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == cur_idx]

    if current.empty:
        current = chapters.iloc[[0]]

    return current.iloc[0].to_dict()


def render_client_view(session_id: str, show_controls: bool = False) -> None:
    session = get_session_row(session_id)

    if not session:
        st.error("Sessão não encontrada na aba sessions.")
        return

    chapters = read_chapters(session_id)

    if chapters.empty:
        st.warning("Sessão sem capítulos na aba chapters.")
        return

    cur_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == cur_idx]

    if current.empty:
        current = chapters.iloc[[0]]
        cur_idx = int(current.iloc[0]["chapter_index"])

    row = current.iloc[0].to_dict()

    if show_controls:
        render_live_controls(session_id, chapters, cur_idx)

    musica = escape(row.get("musica", "Ao vivo"))
    artista = escape(row.get("artista", ""))
    prato = escape(row.get("prato", ""))
    momento = escape(row.get("moment_key", ""))

    texto_prato = escape(row.get("texto_card_prato", ""))
    texto_musica = escape(row.get("texto_card_musica", ""))
    texto_harmonizacao = escape(row.get("texto_card_harmonizacao", ""))
    texto_destaque = escape(row.get("texto_destaque", "") or row.get("texto_card_harmonizacao", ""))
    vinho = escape(row.get("vinho", ""))
    texto_vinho = escape(row.get("texto_vinho", ""))

    subtitle_parts = [p for p in [artista, prato, momento] if p]
    subtitle = " · ".join(subtitle_parts)

    st.markdown('<div class="client-wrap">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-label">Agora tocando</div>
          <h1 class="hero-title">{musica}</h1>
          <div class="hero-subtitle">{subtitle}</div>
          <div class="hero-text">{texto_destaque}</div>
        </div>

        <div class="info-grid">
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

    if vinho or texto_vinho:
        st.markdown(
            f"""
            <div class="small-card" style="margin-top:18px;">
              <div class="small-title">Vinho sugerido</div>
              <div style="font-weight:700; color:{BRAND_BLUE}; margin-bottom:6px;">{vinho}</div>
              <div class="small-muted" style="font-size:15px; line-height:1.55;">{texto_vinho}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_live_controls(session_id: str, chapters: pd.DataFrame, cur_idx: int) -> None:
    c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
    indexes = chapters["chapter_index"].tolist()

    with c1:
        if st.button("◀ Anterior", use_container_width=True):
            previous_indexes = [i for i in indexes if i < cur_idx]
            new_idx = max(previous_indexes) if previous_indexes else min(indexes)
            set_live_index(session_id, new_idx)
            st.rerun()

    with c2:
        if st.button("Próximo ▶", use_container_width=True):
            next_indexes = [i for i in indexes if i > cur_idx]
            new_idx = min(next_indexes) if next_indexes else max(indexes)
            set_live_index(session_id, new_idx)
            st.rerun()

    with c3:
        if st.button("Atualizar", use_container_width=True):
            st.rerun()

    with c4:
        st.caption(f"Capítulo ao vivo: {cur_idx}")


def safe_setlist_df(chapters: pd.DataFrame) -> pd.DataFrame:
    if chapters.empty:
        return chapters

    show = chapters.copy()

    show["planned_duration_sec"] = (
        pd.to_numeric(show["planned_duration_sec"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

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

    chapters = read_chapters(session_id)

    if chapters.empty:
        st.warning("Sem capítulos.")
        return

    cur_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == cur_idx]
    current_row = current.iloc[0].to_dict() if not current.empty else chapters.iloc[0].to_dict()

    st.markdown("### Agora")
    st.markdown(
        f"""
        <div class="ops-current">
          <span class="pill">Capítulo {escape(current_row.get("chapter_index", ""))}</span>
          <span class="pill">{escape(current_row.get("moment_key", ""))}</span>
          <div class="small-title">{escape(current_row.get("musica", ""))}</div>
          <div class="small-muted">{escape(current_row.get("artista", ""))}</div>
          <div style="margin-top:8px;"><b>Prato:</b> {escape(current_row.get("prato", ""))}</div>
          <div style="margin-top:8px; line-height:1.5;">{escape(current_row.get("texto_card_musica", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Roteiro completo")
    st.dataframe(safe_setlist_df(chapters), use_container_width=True, hide_index=True)


def page_kitchen_view(session_id: str) -> None:
    render_header("Cozinha")

    chapters = read_chapters(session_id)

    if chapters.empty:
        st.warning("Sem capítulos.")
        return

    cur_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == cur_idx]

    if current.empty:
        current = chapters.iloc[[0]]
        cur_idx = int(current.iloc[0]["chapter_index"])

    row = current.iloc[0].to_dict()
    note = get_service_note(session_id, cur_idx, "cozinha")

    st.markdown("### Agora no salão")
    st.markdown(
        f"""
        <div class="ops-current">
          <span class="pill">Capítulo {escape(cur_idx)}</span>
          <span class="pill">{escape(row.get("chapter_type", ""))}</span>
          <div class="small-title">{escape(row.get("prato", ""))}</div>
          <div class="small-muted">{escape(row.get("musica", ""))} · {escape(row.get("artista", ""))}</div>
          <div style="margin-top:10px; line-height:1.55;"><b>Nota de serviço:</b> {escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upcoming = chapters[chapters["chapter_index"] >= cur_idx].copy()
    upcoming = upcoming[["chapter_index", "moment_key", "prato", "musica", "planned_duration_sec"]].copy()
    upcoming["duracao"] = upcoming["planned_duration_sec"].apply(fmt_mmss)
    upcoming = upcoming.drop(columns=["planned_duration_sec"])

    st.markdown("### Próximas etapas")
    st.dataframe(upcoming, use_container_width=True, hide_index=True)


def page_ops_view(session_id: str) -> None:
    render_header("Controle operacional")

    chapters = read_chapters(session_id)

    if chapters.empty:
        st.warning("Sem capítulos.")
        return

    cur_idx = get_live_index(session_id)
    current = chapters[chapters["chapter_index"] == cur_idx]

    if current.empty:
        current = chapters.iloc[[0]]
        cur_idx = int(current.iloc[0]["chapter_index"])

    row = current.iloc[0].to_dict()

    render_live_controls(session_id, chapters, cur_idx)

    st.markdown("### Capítulo atual")
    st.markdown(
        f"""
        <div class="ops-current">
          <span class="pill">Capítulo {escape(cur_idx)}</span>
          <span class="pill">{escape(row.get("chapter_type", ""))}</span>
          <div class="small-title">{escape(row.get("musica", ""))}</div>
          <div class="small-muted">{escape(row.get("artista", ""))}</div>
          <div style="margin-top:8px;"><b>Prato:</b> {escape(row.get("prato", ""))}</div>
          <div style="margin-top:8px;"><b>Vinho:</b> {escape(row.get("vinho", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Sequência")
    st.dataframe(safe_setlist_df(chapters), use_container_width=True, hide_index=True)

    st.markdown("### Visualização do cliente")
    render_client_view(session_id, show_controls=False)


def page_admin() -> None:
    render_header("Admin")

    sessions = list_sessions_sheet()

    st.subheader("Criar sessão")

    with st.form("create_session"):
        sid = st.text_input("session_id", value=datetime.now().strftime("%Y%m%d-1900"))
        title = st.text_input("Título", value="Yvora Music Session")
        genre = st.text_input("Gênero", value="Bossa Nova")
        total = st.number_input("Duração total em minutos", min_value=30, max_value=240, value=60, step=5)
        submitted = st.form_submit_button("Criar sessão")

    if submitted:
        upsert_session(sid, title, genre, int(total), "draft")

        base = pd.DataFrame(
            [
                {
                    "session_id": sid,
                    "chapter_index": i + 1,
                    "moment_key": "momento",
                    "chapter_type": "music",
                    "planned_duration_sec": 240,
                    "prato": "",
                    "musica": "",
                    "artista": "",
                    "texto_card_prato": "",
                    "texto_card_musica": "",
                    "texto_card_harmonizacao": "",
                    "texto_destaque": "",
                    "vinho": "",
                    "texto_vinho": "",
                }
                for i in range(15)
            ]
        )

        save_chapters(sid, base)
        set_live_index(sid, 1)

        st.success("Sessão criada.")
        st.rerun()

    sessions = list_sessions_sheet()

    if sessions.empty:
        st.info("Sem sessões.")
        return

    sid = st.selectbox("Sessão", sessions["session_id"].tolist(), key="admin_sid")
    chapters = read_chapters(sid)

    if chapters.empty:
        st.warning("Esta sessão ainda não possui capítulos.")
        return

    area = st.radio("Área admin", ["Controle operacional", "Editar capítulos", "Banda", "Cozinha", "Cliente"], horizontal=True)

    if area == "Controle operacional":
        page_ops_view(sid)

    elif area == "Banda":
        page_band_view(sid)

    elif area == "Cozinha":
        page_kitchen_view(sid)

    elif area == "Cliente":
        render_header("Cliente")
        render_client_view(sid, show_controls=True)

    else:
        st.subheader("Editar capítulos")
        edited = st.data_editor(
            chapters[CH_HEADERS],
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "texto_card_prato": st.column_config.TextColumn("texto_card_prato", width="large"),
                "texto_card_musica": st.column_config.TextColumn("texto_card_musica", width="large"),
                "texto_card_harmonizacao": st.column_config.TextColumn("texto_card_harmonizacao", width="large"),
                "texto_destaque": st.column_config.TextColumn("texto_destaque", width="large"),
                "texto_vinho": st.column_config.TextColumn("texto_vinho", width="large"),
            },
        )

        if st.button("Salvar alterações"):
            save_chapters(sid, edited)
            st.success("Alterações salvas.")
            st.rerun()


def page_login(default_view: str, session_id: str) -> None:
    render_header("Login")

    st.info("Entre com o usuário correspondente à área.")

    user = render_login_box()

    if not user:
        return

    role = safe_text(user.get("role", "")).lower()

    if role_can_access(role, default_view):
        st.rerun()
    else:
        st.warning("Este usuário não tem acesso a esta área.")


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

    if not view:
        view = ""

    with st.sidebar:
        st.markdown("### Navegação")

        if user:
            st.markdown(
                f"<span class='yv-badge'>{escape(user.get('username'))}</span>"
                f"<span class='yv-badge'>{escape(user.get('role'))}</span>",
                unsafe_allow_html=True,
            )

            if st.button("Sair"):
                logout()

    if view in ["cliente", "banda"]:
        if view == "cliente":
            render_header("Cliente")
            render_client_view(sid, show_controls=False)
        else:
            page_band_view(sid)
        time.sleep(2)
        st.rerun()
        return

    if view in ["cozinha", "operacao"]:
        if not user:
            page_login(view, sid)
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

    if not user:
        render_header("Login único")

        with st.sidebar:
            st.markdown("### Acesso interno")
            username = st.text_input("Login")
            password = st.text_input("Senha", type="password")

            if st.button("Entrar"):
                logged = auth_login(username, password)

                if not logged:
                    st.warning("Login ou senha incorretos.")
                else:
                    st.session_state["user"] = logged
                    st.success(f"Logado como {logged['role']}")
                    st.rerun()

        sessions = list_sessions_sheet()

        if not sessions.empty:
            st.subheader("Cliente")
            sid_public = st.selectbox("Escolha a sessão", sessions["session_id"].tolist(), key="public_sid")
            render_client_view(sid_public)
            time.sleep(2)
            st.rerun()
        else:
            st.info("Sem sessões.")
        return

    role = safe_text(user.get("role", "")).lower()

    if role == "admin":
        page_admin()

    elif role in ["ops", "operation"]:
        page_ops_view(sid)

    elif role == "band":
        page_band_view(sid)

    elif role == "kitchen":
        page_kitchen_view(sid)

    else:
        render_header("Cliente")
        render_client_view(sid)


if __name__ == "__main__":
    main()
