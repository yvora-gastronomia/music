import os
import json
import time
import re
import html
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

APP_TITLE = "Yvora Music"
BRAND_BG = "#EFE7DD"
BRAND_BLUE = "#0E2A47"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def fmt_mmss(total_seconds: Any) -> str:
    try:
        total_seconds = int(float(total_seconds or 0))
    except Exception:
        total_seconds = 0
    total_seconds = max(total_seconds, 0)
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m:02d}:{s:02d}"


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    value = str(value)
    if value.lower() == "nan":
        return ""
    return value.strip()


def pick_first(row: Dict[str, Any], cols: List[str], default: str = "") -> str:
    for col in cols:
        value = safe_text(row.get(col, ""))
        if value:
            return value
    return default


def app_bootstrap() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.markdown(
        f"""
        <style>
          html, body, [class*="css"] {{ background: {BRAND_BG} !important; }}

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

          .mobile-wrap {{
            max-width: 1180px;
            margin: 0 auto;
          }}

          .show-card {{
            background: rgba(255,255,255,0.55);
            border: 1px solid rgba(14,42,71,0.14);
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 14px;
          }}

          .hero-card {{
            background: {BRAND_BLUE};
            border-radius: 0 0 34px 34px;
            padding: 34px 52px 42px 52px;
            margin-bottom: 28px;
            color: #F7F0E8;
            box-shadow: 0 18px 50px rgba(14,42,71,0.16);
          }}

          .hero-label {{
            color: rgba(247,240,232,0.72);
            font-size: 13px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 10px;
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

          .show-h1 {{
            font-family: Georgia, "Times New Roman", serif;
            color: {BRAND_BLUE};
            font-size: 22px;
            margin: 0 0 6px 0;
          }}

          .show-muted {{
            color: rgba(14,42,71,0.70);
            font-size: 13px;
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

          .wine-card {{
            background: rgba(255,255,255,0.70);
            border: 1px solid rgba(14,42,71,0.10);
            border-radius: 22px;
            padding: 20px 24px;
            margin-top: 18px;
            box-shadow: 0 12px 34px rgba(14,42,71,0.06);
          }}

          .wine-card h3 {{
            font-family: Georgia, "Times New Roman", serif;
            color: {BRAND_BLUE};
            font-size: 22px;
            margin: 0 0 8px 0;
          }}

          .wine-name {{
            font-weight: 700;
            color: {BRAND_BLUE};
            margin-bottom: 6px;
          }}

          .wine-text {{
            color: rgba(52,43,35,0.78);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 17px;
            line-height: 1.55;
          }}

          .stButton > button {{
            padding: 0.20rem 0.60rem !important;
            min-height: 2.0rem !important;
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
            .mobile-wrap {{
              max-width: 560px;
            }}

            .hero-card {{
              padding: 26px 24px 34px 24px;
              border-radius: 0 0 28px 28px;
            }}

            .hero-title {{
              font-size: 31px;
            }}

            .hero-subtitle {{
              font-size: 16px;
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
        st.markdown(f'<h2 class="yv-title">{APP_TITLE}</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="meta">{html.escape(subtitle)}</div>', unsafe_allow_html=True)

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
        ws = sh.add_worksheet(title=title, rows=5000, cols=max(12, len(headers) or 12))
        if headers:
            ws.append_row(headers)
        return ws


def ws_read_df(title: str) -> pd.DataFrame:
    ws = ws_get_or_create(title, [])
    values = ws.get_all_values()
    if not values or not values[0]:
        return pd.DataFrame()
    header = values[0]
    rows = values[1:]
    return pd.DataFrame(rows, columns=header)


def ws_append_row(title: str, headers: List[str], row: List[Any]) -> None:
    ws = ws_get_or_create(title, headers)
    ws.append_row([("" if v is None else str(v)) for v in row])


def ws_replace_session_rows(title: str, headers: List[str], session_id: str, new_rows: List[List[Any]]) -> None:
    ws = ws_get_or_create(title, headers)
    allv = ws.get_all_values()

    if not allv:
        ws.append_row(headers)
        allv = [headers]

    header = allv[0]

    for h in headers:
        if h not in header:
            header.append(h)

    kept = [header]
    idx_key = header.index("session_id")

    for r in allv[1:]:
        if not r:
            continue
        r = r + [""] * (len(header) - len(r))
        if r[idx_key] != session_id:
            kept.append(r)

    ws.clear()
    ws.append_rows(kept)

    if new_rows:
        ws.append_rows([["" if v is None else str(v) for v in row] for row in new_rows])


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

LIVE_HEADERS = ["session_id", "current_chapter_index", "updated_at_utc"]

HIST_HEADERS = [
    "ts_utc",
    "session_id",
    "chapter_index",
    "moment_key",
    "music_title",
    "music_artist",
    "link_context_input",
    "ai_story_text",
    "ai_music_alternatives",
    "ai_experience_actions",
    "ai_notes",
]


def auth_login(username: str, password: str) -> Optional[Dict[str, str]]:
    df = ws_read_df("users")
    if df.empty:
        return None

    u = safe_text(username)
    p = safe_text(password)

    for _, r in df.iterrows():
        active = safe_text(r.get("active", "1"))
        if active in ["0", "False", "false", "não", "nao"]:
            continue

        if safe_text(r.get("username", "")) == u and safe_text(r.get("password", "")) == p:
            role = safe_text(r.get("role", "staff")) or "staff"
            return {"username": u, "role": role}

    return None


def logout() -> None:
    st.session_state.pop("user", None)
    st.rerun()


def list_sessions_sheet() -> pd.DataFrame:
    df = ws_read_df("sessions")
    if df.empty:
        return df

    if "updated_at_utc" in df.columns:
        df = df.sort_values("updated_at_utc", ascending=False)

    return df


def get_session_row(session_id: str) -> Optional[Dict[str, Any]]:
    df = list_sessions_sheet()
    if df.empty or "session_id" not in df.columns:
        return None

    m = df[df["session_id"] == session_id]
    if m.empty:
        return None

    return m.iloc[0].to_dict()


def upsert_session(session_id: str, title: str, genre: str, total_min: int, status: str) -> None:
    ws = ws_get_or_create("sessions", SESS_HEADERS)
    values = ws.get_all_values()

    if not values:
        ws.append_row(SESS_HEADERS)
        values = [SESS_HEADERS]

    header = values[0]

    for h in SESS_HEADERS:
        if h not in header:
            header.append(h)

    idx_key = header.index("session_id")
    found = None

    for i, r in enumerate(values[1:], start=2):
        if len(r) > idx_key and r[idx_key] == session_id:
            found = i
            break

    valid_status = status if status in ["draft", "scheduled", "live", "finished", "cancelled"] else "draft"

    row = {
        "session_id": session_id,
        "title": title,
        "genre": genre,
        "total_duration_min": str(int(total_min)),
        "status": valid_status,
        "updated_at_utc": utc_now().isoformat(),
    }

    out = [row.get(h, "") for h in header]

    if found:
        ws.update(f"A{found}", [out])
    else:
        ws.append_row(out)


def read_chapters(session_id: str) -> pd.DataFrame:
    df = ws_read_df("chapters")

    if df.empty or "session_id" not in df.columns:
        return pd.DataFrame()

    df = df[df["session_id"] == session_id].copy()

    if df.empty:
        return df

    if "chapter_index" not in df.columns:
        df["chapter_index"] = range(len(df))

    if "planned_duration_sec" not in df.columns:
        df["planned_duration_sec"] = 300

    for col in CH_HEADERS:
        if col not in df.columns:
            df[col] = ""

    df["chapter_index"] = pd.to_numeric(df["chapter_index"], errors="coerce").fillna(0).astype(int)

    return df.sort_values("chapter_index").reset_index(drop=True)


def save_chapters(session_id: str, df: pd.DataFrame) -> None:
    rows = []

    for _, r in df.iterrows():
        row = {
            "session_id": session_id,
            "chapter_index": int(pd.to_numeric(r.get("chapter_index", 0), errors="coerce") or 0),
            "moment_key": r.get("moment_key", "aquecimento"),
            "chapter_type": r.get("chapter_type", "music"),
            "planned_duration_sec": int(pd.to_numeric(r.get("planned_duration_sec", 300), errors="coerce") or 300),
            "prato": r.get("prato", ""),
            "musica": r.get("musica", r.get("music_title", "")),
            "artista": r.get("artista", r.get("music_artist", "")),
            "texto_card_prato": r.get("texto_card_prato", ""),
            "texto_card_musica": r.get("texto_card_musica", ""),
            "texto_card_harmonizacao": r.get("texto_card_harmonizacao", ""),
            "texto_destaque": r.get("texto_destaque", ""),
            "music_title": r.get("music_title", r.get("musica", "")),
            "music_artist": r.get("music_artist", r.get("artista", "")),
            "link_context_input": r.get("link_context_input", ""),
            "ai_story_text": r.get("ai_story_text", ""),
            "ai_music_alternatives": r.get("ai_music_alternatives", ""),
            "ai_experience_actions": r.get("ai_experience_actions", ""),
            "ai_notes": r.get("ai_notes", ""),
            "updated_at_utc": utc_now().isoformat(),
            "vinho": r.get("vinho", ""),
            "texto_vinho": r.get("texto_vinho", ""),
        }

        rows.append([row.get(h, "") for h in CH_HEADERS])

    ws_replace_session_rows("chapters", CH_HEADERS, session_id, rows)


def get_live_index(session_id: str) -> int:
    df = ws_read_df("live")

    if df.empty or "session_id" not in df.columns:
        return 1

    m = df[df["session_id"] == session_id]

    if m.empty:
        return 1

    try:
        return int(m.iloc[0]["current_chapter_index"])
    except Exception:
        return 1


def set_live_index(session_id: str, idx: int) -> None:
    ws = ws_get_or_create("live", LIVE_HEADERS)
    values = ws.get_all_values()

    if not values:
        ws.append_row(LIVE_HEADERS)
        values = [LIVE_HEADERS]

    header = values[0]
    idx_key = header.index("session_id")
    found = None

    for i, r in enumerate(values[1:], start=2):
        if len(r) > idx_key and r[idx_key] == session_id:
            found = i
            break

    row = {
        "session_id": session_id,
        "current_chapter_index": str(int(idx)),
        "updated_at_utc": utc_now().isoformat(),
    }

    out = [row.get(h, "") for h in header]

    if found:
        ws.update(f"A{found}", [out])
    else:
        ws.append_row(out)


def gemini_available() -> bool:
    return False


def gemini_generate(payload: Dict[str, str]) -> Dict[str, str]:
    return {
        "story_text": "",
        "music_alternatives": "",
        "experience_actions": "",
        "notes": "",
    }


def append_gemini_history(row: Dict[str, Any]) -> None:
    return None


def render_client_view(session_id: str, show_controls: bool = False) -> None:
    sess = get_session_row(session_id)

    if not sess:
        st.error("Sessão não encontrada na planilha.")
        return

    ch = read_chapters(session_id)

    if ch.empty:
        st.warning("Sessão sem capítulos na planilha.")
        return

    cur_idx = get_live_index(session_id)
    cur = ch[ch["chapter_index"] == cur_idx]

    if cur.empty:
        cur = ch.iloc[[0]]
        cur_idx = int(cur.iloc[0]["chapter_index"])

    row = cur.iloc[0].to_dict()

    if show_controls:
        c1, c2, c3 = st.columns([1, 1, 3])

        with c1:
            if st.button("◀ Anterior", use_container_width=True):
                indexes = ch["chapter_index"].tolist()
                previous_indexes = [i for i in indexes if i < cur_idx]
                new_idx = max(previous_indexes) if previous_indexes else min(indexes)
                set_live_index(session_id, new_idx)
                st.rerun()

        with c2:
            if st.button("Próximo ▶", use_container_width=True):
                indexes = ch["chapter_index"].tolist()
                next_indexes = [i for i in indexes if i > cur_idx]
                new_idx = min(next_indexes) if next_indexes else max(indexes)
                set_live_index(session_id, new_idx)
                st.rerun()

        with c3:
            st.caption(f"Capítulo ao vivo: {cur_idx}")

    musica = pick_first(row, ["musica", "music_title"], "Ao vivo")
    artista = pick_first(row, ["artista", "music_artist"], "")
    prato = pick_first(row, ["prato"], "")

    texto_prato = pick_first(row, ["texto_card_prato"], "")
    texto_musica = pick_first(row, ["texto_card_musica"], "")
    texto_harmonizacao = pick_first(row, ["texto_card_harmonizacao"], "")
    texto_destaque = pick_first(row, ["texto_destaque"], "A conexão desta etapa aparece aqui.")

    vinho = pick_first(row, ["vinho"], "")
    texto_vinho = pick_first(row, ["texto_vinho"], "")

    momento = pick_first(row, ["moment_key"], "")

    musica_html = html.escape(musica)
    artista_html = html.escape(artista)
    prato_html = html.escape(prato)
    momento_html = html.escape(momento)

    texto_prato_html = html.escape(texto_prato)
    texto_musica_html = html.escape(texto_musica)
    texto_harmonizacao_html = html.escape(texto_harmonizacao)
    texto_destaque_html = html.escape(texto_destaque)

    vinho_html = html.escape(vinho)
    texto_vinho_html = html.escape(texto_vinho)

    st.markdown('<div class="mobile-wrap">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-label">Agora tocando</div>
          <h1 class="hero-title">{musica_html}</h1>
          <div class="hero-subtitle">
            {artista_html}
            {f' · {prato_html}' if prato_html else ''}
            {f' · {momento_html}' if momento_html else ''}
          </div>
          <div style="margin-top:24px; font-family: Georgia, 'Times New Roman', serif; font-size:28px; line-height:1.48;">
            {texto_destaque_html}
          </div>
        </div>

        <div class="info-grid">
          <div class="info-card">
            <h3>Prato</h3>
            <p>{texto_prato_html}</p>
          </div>

          <div class="info-card">
            <h3>Música</h3>
            <p>{texto_musica_html}</p>
          </div>

          <div class="info-card">
            <h3>Harmonização</h3>
            <p>{texto_harmonizacao_html}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if vinho_html or texto_vinho_html:
        st.markdown(
            f"""
            <div class="wine-card">
              <h3>Vinho sugerido</h3>
              <div class="wine-name">{vinho_html}</div>
              <div class="wine-text">{texto_vinho_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def safe_setlist_df(ch: pd.DataFrame) -> pd.DataFrame:
    if ch.empty:
        return ch

    show = ch.copy()

    if "planned_duration_sec" not in show.columns:
        show["planned_duration_sec"] = 0

    show["planned_duration_sec"] = pd.to_numeric(show["planned_duration_sec"], errors="coerce").fillna(0).astype(int)

    keep = [
        c
        for c in [
            "chapter_index",
            "moment_key",
            "chapter_type",
            "planned_duration_sec",
            "prato",
            "musica",
            "artista",
            "vinho",
            "music_title",
            "music_artist",
        ]
        if c in show.columns
    ]

    show = show[keep].copy()
    show["planned_duration_sec"] = show["planned_duration_sec"].apply(fmt_mmss)

    if "musica" not in show.columns and "music_title" in show.columns:
        show["musica"] = show["music_title"]

    if "artista" not in show.columns and "music_artist" in show.columns:
        show["artista"] = show["music_artist"]

    show = show.drop(columns=[c for c in ["music_title", "music_artist"] if c in show.columns])

    return show.rename(columns={"planned_duration_sec": "duração"})


def page_login() -> None:
    render_header("Login único")
    st.write("Use o mesmo link para Cliente, Banda e Operação.")

    with st.sidebar:
        st.markdown("### Acesso interno")
        u = st.text_input("Login")
        p = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            user = auth_login(u, p)

            if not user:
                st.warning("Login ou senha incorretos.")
            else:
                st.session_state["user"] = user
                st.success(f"Logado como {user['role']}")
                st.rerun()

    qp_sid = st.query_params.get("sid", "")
    df = list_sessions_sheet()

    if qp_sid:
        render_client_view(qp_sid)
        time.sleep(2)
        st.rerun()
    elif not df.empty:
        st.subheader("Cliente")
        sid = st.selectbox("Escolha a sessão", df["session_id"].tolist(), key="public_sid")
        render_client_view(sid)
        time.sleep(2)
        st.rerun()
    else:
        st.info("Sem sessões ainda. Faça login como admin para criar a primeira.")


def page_band() -> None:
    render_header("Banda")
    df = list_sessions_sheet()

    if df.empty:
        st.info("Sem sessões.")
        return

    sid = st.selectbox("Sessão", df["session_id"].tolist(), key="band_sid")
    ch = read_chapters(sid)

    if ch.empty:
        st.warning("Sem capítulos.")
        return

    st.dataframe(safe_setlist_df(ch), use_container_width=True, hide_index=True)

    st.subheader("Cliente")
    render_client_view(sid, show_controls=False)


def page_admin() -> None:
    render_header("Operação")

    st.subheader("Criar sessão")

    with st.form("create_session"):
        sid = st.text_input("session_id", value=datetime.now().strftime("%Y%m%d-1900"))
        title = st.text_input("Título", value="Yvora Music Session")
        genre = st.text_input("Gênero", value="Bossa Nova")
        total = st.number_input("Duração total (min)", min_value=45, max_value=240, value=60, step=5)
        ok = st.form_submit_button("Criar")

    if ok:
        upsert_session(sid, title, genre, int(total), "draft")

        base = []

        for i in range(15):
            base.append(
                {
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
                    "music_title": "",
                    "music_artist": "",
                    "link_context_input": "",
                    "ai_story_text": "",
                    "ai_music_alternatives": "",
                    "ai_experience_actions": "",
                    "ai_notes": "",
                    "vinho": "",
                    "texto_vinho": "",
                }
            )

        save_chapters(sid, pd.DataFrame(base))
        set_live_index(sid, 1)
        st.success("Sessão criada e gravada no Google Sheets.")
        st.rerun()

    sess_df = list_sessions_sheet()

    if sess_df.empty:
        st.info("Sem sessões.")
        return

    sid2 = st.selectbox("Sessão", sess_df["session_id"].tolist(), key="adm_sid")
    ch = read_chapters(sid2)

    if ch.empty:
        st.warning("Sem capítulos.")
        return

    st.subheader("Resumo")
    st.dataframe(safe_setlist_df(ch), use_container_width=True, hide_index=True)

    st.subheader("Editar capítulos")

    edit_cols = [
        c
        for c in [
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
            "link_context_input",
        ]
        if c in ch.columns
    ]

    edited = st.data_editor(ch[edit_cols], use_container_width=True, hide_index=True, num_rows="dynamic")

    c1, c2 = st.columns([1, 2])

    with c1:
        if st.button("Salvar alterações"):
            full = ch.copy()

            for col in edit_cols:
                full[col] = edited[col]

            save_chapters(sid2, full)
            st.success("Capítulos salvos.")
            st.rerun()

    with c2:
        st.caption("As narrativas, pratos, músicas e vinhos são lidos diretamente da planilha. A IA não é usada nesta versão.")

    st.subheader("Controle ao vivo")
    render_client_view(sid2, show_controls=True)


def main():
    app_bootstrap()

    try:
        _ = get_sheet()
    except Exception as e:
        st.error(f"Erro de configuração: {e}")
        st.info("O app aceita [google].service_account_json ou [gcp_service_account] nos Secrets.")
        return

    user = st.session_state.get("user")
    qp_sid = st.query_params.get("sid", "")

    with st.sidebar:
        st.markdown("### Navegação")

        if user:
            st.markdown(
                f"<span class='yv-badge'>{html.escape(user.get('username'))}</span><span class='yv-badge'>{html.escape(user.get('role'))}</span>",
                unsafe_allow_html=True,
            )

            if st.button("Sair"):
                logout()

    if not user:
        page_login()
        return

    role = user.get("role", "")

    if role == "admin":
        page = st.sidebar.radio("Área", ["Operação", "Banda", "Cliente"], index=0)

        if page == "Operação":
            page_admin()
        elif page == "Banda":
            page_band()
        else:
            render_header("Cliente")
            df = list_sessions_sheet()

            if df.empty:
                st.info("Sem sessões.")
            else:
                sid = qp_sid or st.selectbox("Sessão", df["session_id"].tolist(), key="admin_public_sid")
                render_client_view(sid, show_controls=True)

    elif role == "band":
        page_band()

    else:
        render_header("Cliente")
        sid = qp_sid

        if not sid:
            df = list_sessions_sheet()

            if df.empty:
                st.info("Sem sessões.")
                return

            sid = st.selectbox("Sessão", df["session_id"].tolist(), key="staff_public_sid")

        render_client_view(sid)


if __name__ == "__main__":
    main()
