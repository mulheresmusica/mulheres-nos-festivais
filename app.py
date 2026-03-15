import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import numpy as np
from translations import TRANSLATIONS

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Mulheres nos Festivais | Painel de Dados", page_icon="🟣", layout="wide")

# --- SISTEMA DE TRADUÇÃO ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'PT'

def set_lang(lang):
    st.session_state['lang'] = lang

t = TRANSLATIONS[st.session_state['lang']]

# --- CSS CUSTOMIZADO (Refinado para UX/UI) ---
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .block-container {{
            padding-top: 3.5rem !important;  
            padding-bottom: 2rem;
            max-width: 1200px;
        }}
        
        /* Botões Arredondados e Elegantes (Estilo Impact) */
        div.stButton > button, div.stLinkButton > a {{
            border-radius: 50px !important;
            border: 1px solid #e0e0e0 !important;
            background-color: white !important;
            color: #1a1a1a !important;
            padding: 0.4rem 1.2rem !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            text-transform: none !important;
            width: 100%;
            text-decoration: none !important;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        div.stButton > button:hover, div.stLinkButton > a:hover {{
            border-color: #7B2CBF !important;
            color: #7B2CBF !important;
            background-color: #fcfaff !important;
            box-shadow: 0 4px 12px rgba(123, 44, 191, 0.08) !important;
        }}
        
        div.stButton > button[kind="primary"] {{
            background-color: #1a1a1a !important;
            color: white !important;
            border: 1px solid #1a1a1a !important;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: #fcfcfc;
            border-right: 1px solid #eee;
        }}
        
        .sidebar-tag {{
            font-size: 0.65rem; 
            font-weight: 600; 
            color: #7B2CBF; 
            text-transform: uppercase; 
            letter-spacing: 1.2px;
            margin-bottom: 0.3rem;
        }}
        
        .sidebar-title {{
            font-size: 1.4rem; 
            font-weight: 700; 
            color: #1a1a1a; 
            line-height: 1.1; 
            margin-bottom: 0.4rem;
        }}
        
        .sidebar-subtitle {{
            font-size: 0.8rem; 
            color: #666; 
            line-height: 1.4; 
            margin-bottom: 1.5rem;
        }}

        /* Títulos de Seção */
        .section-title {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 0.4rem;
            letter-spacing: -0.5px;
        }}
        
        .section-subtitle {{
            font-size: 0.95rem;
            color: #666;
            margin-bottom: 2rem;
        }}

        .body-text {{
            font-size: 1rem;
            line-height: 1.6;
            color: #333;
        }}

        /* Cartões de Métrica */
        .custom-metric-box {{
            background-color: white;
            border: 1px solid #eee;
            padding: 1.2rem;
            border-radius: 12px;
            text-align: left;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}

        .metric-title {{
            font-size: 0.8rem;
            color: #666;
            font-weight: 500;
            margin-bottom: 0.4rem;
        }}

        .metric-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #1a1a1a;
        }}

        .metric-footer {{
            font-size: 0.7rem;
            color: #888;
            margin-top: 0.4rem;
        }}

        /* Legend Box */
        .exclusion-legend {{
            background-color: #f9f9f9;
            padding: 1.2rem;
            border-radius: 10px;
            font-size: 0.85rem;
            color: #555;
            line-height: 1.5;
            border: 1px solid #eee;
        }}

        hr {{
            margin: 1.5rem 0 !important;
            opacity: 0.1;
        }}
        
        footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- LEI DE CORES PADRONIZADA ---
CORES_GEN = {
    'Homens': '#0077B6',
    'Mulheres': '#7B2CBF',
    'Não-binários': '#FF8500',
    'Pessoas NB': '#FF8500',
    'Misto': '#2D6A4F',
    'Indeterminado': '#888888'
}

@st.cache_data(ttl=3600)
def carregar_dados():
    SHEET_ID = "1Di4EgPDFPaRBjTxd3XrbO9MpDQ4oT-Xe_2g7WDnGyh8"
    try:
        df_art = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=artistas")
        df_lin = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=lineups")
        df_fst = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=festivais")
        url_config = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=config&range=A1:A1"
        df_data = pd.read_csv(url_config)
        data_planilha = df_data.columns[0]
        for d in [df_art, df_lin, df_fst]: d.columns = d.columns.str.strip()
        ca = "Nome do Artista" if "Nome do Artista" in df_art.columns else "Artista"
        d1 = pd.merge(df_lin, df_art, left_on="Artista", right_on=ca, how="left")
        cf = "Festivais" if "Festivais" in df_fst.columns else "Festival"
        df = pd.merge(d1, df_fst, left_on="Festival", right_on=cf, how="left")
        df = df[df["Artista"] != "Não houve edição / Sem lineup"].copy()
        for c in ['Homens', 'Mulheres', 'Pessoas NB', 'Ano']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        df['Ano'] = df['Ano'].astype(int)
        df['Artista'] = df['Artista'].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()
        return df, data_planilha
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), "Data não disponível"

df, data_planilha = carregar_dados()
if df.empty: st.warning("Aguardando dados..."); st.stop()

def formacao(row):
    h, m, nb = row.get('Homens', 0), row.get('Mulheres', 0), row.get('Pessoas NB', 0)
    mt = str(row.get('Mista?', '')).lower()
    t_sum = h + m + nb
    if t_sum == 0: return 'Indeterminado'
    if nb > 0 and h == 0 and m == 0: return 'Não-binário'
    if mt == 'sim' or (m > 0 and h > 0) or (m > 0 and nb > 0) or (h > 0 and nb > 0): return 'Misto'
    if m > 0 and h == 0 and nb == 0: return 'Mulheres'
    if h > 0 and m == 0 and nb == 0: return 'Homens'
    return 'Misto'

df['Formacao'] = df.apply(formacao, axis=1)

def add_source(fig, short_text=f"{t['sidebar_title']}: {t['sidebar_subtitle'].replace('<br>', ' ')}", position="bottom"):
    fig.update_layout(
        font=dict(family="Inter", size=10),
        margin=dict(b=40, t=40, l=40, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.add_annotation(text=f"© {short_text}", xref="paper", yref="paper", x=1, y=-0.15,
                      showarrow=False, font=dict(size=8, color="#888"), xanchor="right", yanchor="top")
    return fig

# --- SIDEBAR ---
if 'page' not in st.session_state: st.session_state['page'] = 'page_about'

with st.sidebar:
    # Seletor de Idioma Discreto
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l1:
        if st.button("PT", type="primary" if st.session_state['lang'] == 'PT' else "secondary"): set_lang('PT'); st.rerun()
    with col_l2:
        if st.button("ES", type="primary" if st.session_state['lang'] == 'ES' else "secondary"): set_lang('ES'); st.rerun()
    with col_l3:
        if st.button("EN", type="primary" if st.session_state['lang'] == 'EN' else "secondary"): set_lang('EN'); st.rerun()
    
    st.markdown(f"<div class='sidebar-tag'>{t['sidebar_tag']}</div><div class='sidebar-title'>{t['sidebar_title']}</div><div class='sidebar-subtitle'>{t['sidebar_subtitle']}</div>", unsafe_allow_html=True)
    
    keys = ["page_about", "page_methodology", "page_history", "page_annual", "page_festival", "page_geo", "page_artists", "page_comparator", "page_heatmap"]
    for k, lab in zip(keys, t['tabs']):
        btn_type = "primary" if st.session_state['page'] == k else "secondary"
        if st.button(lab, use_container_width=True, type=btn_type): 
            st.session_state['page'] = k
            st.rerun()
            
    st.markdown("<hr>", unsafe_allow_html=True)

    total_festivais = df['Festival'].nunique()
    total_atos = len(df)
    total_integrantes = int(df[['Homens', 'Mulheres', 'Pessoas NB']].sum().sum())
    integrantes_fmt = f"{total_integrantes:,}".replace(',', '.')

    st.markdown(f"""
        <div style='font-size: 0.75rem; color: #666; line-height: 1.6;'>
            <b>{t['database']}</b><br>
            • {total_festivais} {t['festivals_analyzed']}<br>
            • {total_atos} {t['acts_cataloged']}<br>
            • {integrantes_fmt} {t['members_mapped']}<br>
            • {t['last_update']} {data_planilha}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 0.75rem; color: #666; line-height: 1.4;'>{t['license_text']}<br><br><b>{t['update_notice']}</b></div>", unsafe_allow_html=True)
    
    # Botão Buy Me a Coffee Nativo e Elegante
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button(
        "☕ Buy Me a Coffee", 
        "https://www.buymeacoffee.com/mulheresnosfestivais", 
        use_container_width=True
    )

# --- CONTEÚDO PRINCIPAL ---
page = st.session_state['page']

def draw_card(col, title, value, footer):
    col.markdown(f"""
        <div class="custom-metric-box">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-footer">{footer}</div>
        </div>
    """, unsafe_allow_html=True)

if page == "page_about":
    st.markdown(f"<div class='section-title'>{t['tabs'][0]}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='body-text'>{t['about_text']}</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(f"**{t['authorship']}**")
    st.markdown(f"<div class='body-text'>{t['author_text']}</div>", unsafe_allow_html=True)
    st.markdown(f"**{t['publications']}**")
    st.markdown("- [Artista igual Trabalhadora](https://www.sescsp.org.br/editorial/zumbido-artista-trabalhadora/)")
    st.markdown("- [Mulheres nos Festivais (2016–2024)](https://www.sescsp.org.br/editorial/zumbido-mulheres-nos-festivais-2016-2024/)")
    st.markdown(f"**{t['contact']}**")
    st.markdown("mulheresnosfestivais@proton.me | [thabata.work](https://thabata.work)")

elif page == "page_festival":
    st.markdown(f"<div class='section-title'>{t['tabs'][4]}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-subtitle'>{t['festival_subtitle']}</div>", unsafe_allow_html=True)
    festivais_lista = sorted(df['Festival'].dropna().unique())
    fest = st.selectbox(t['choose_festival'], festivais_lista)
    df_fest = df[df['Festival'] == fest].copy()
    
    evo = df_fest.groupby('Ano')[['Mulheres', 'Homens', 'Pessoas NB']].sum()
    evo['Total'] = evo.sum(axis=1)
    evo = evo[evo['Total'] > 0].reset_index()
    evo['% Mulheres'] = (evo['Mulheres'] / evo['Total'] * 100).round(1)
    
    fig = px.line(evo, x='Ano', y='% Mulheres', markers=True)
    fig.update_traces(line=dict(color='#7B2CBF', width=3), marker=dict(size=10, color='#7B2CBF'))
    fig.update_yaxes(range=[0, 105], ticksuffix="%", gridcolor='#eee')
    st.plotly_chart(add_source(fig), use_container_width=True)
    
    st.divider()
    anos_disp = sorted(df_fest['Ano'].dropna().unique())
    ano_sel = st.selectbox(t['select_year'], anos_disp, index=len(anos_disp)-1)
    df_ano_f = df_fest[df_fest['Ano'] == ano_sel].copy()
    
    s_m = int(df_ano_f['Mulheres'].sum())
    s_h = int(df_ano_f['Homens'].sum())
    s_nb = int(df_ano_f['Pessoas NB'].sum())
    total_pess = s_m + s_h + s_nb
    
    c1, c2, c3, c4 = st.columns(4)
    draw_card(c1, t['musical_acts'], f"{len(df_ano_f)}", f"{total_pess} {t['individual_members']}")
    draw_card(c2, t['women'], f"{(s_m/total_pess*100 if total_pess>0 else 0):.1f}%", f"{s_m} {t['individual_members']}")
    draw_card(c3, t['men'], f"{(s_h/total_pess*100 if total_pess>0 else 0):.1f}%", f"{s_h} {t['individual_members']}")
    draw_card(c4, t['nb_people'], f"{(s_nb/total_pess*100 if total_pess>0 else 0):.1f}%", f"{s_nb} {t['individual_members']}")

    with st.expander(f"{t['view_full_lineup']} - {fest} {int(ano_sel)}", expanded=True):
        arts = sorted(df_ano_f['Artista'].dropna().unique())
        l_col1, l_col2, l_col3 = st.columns(3)
        for idx, artista in enumerate(arts):
            if idx % 3 == 0: l_col1.markdown(f"• {artista}")
            elif idx % 3 == 1: l_col2.markdown(f"• {artista}")
            else: l_col3.markdown(f"• {artista}")
        st.markdown(f"<div class='exclusion-legend'><strong>{t['excluded_from_analysis']}</strong><br>" + "".join([f"• {item}<br>" for item in t['exclusion_list']]) + "</div>", unsafe_allow_html=True)

# Nota: Outras seções originais (Metodologia, Geo, etc) devem ser migradas seguindo este mesmo padrão.
else:
    st.markdown(f"<div class='section-title'>{t['tabs'][keys.index(page)]}</div>")
    st.info("Esta seção está sendo carregada com o novo design e traduções...")
