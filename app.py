import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import numpy as np

st.set_page_config(page_title="Mulheres nos Festivais | Painel de Dados", page_icon="🟣", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 6.5rem !important;  
            padding-bottom: 2rem;
        }
        
        .section-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 0 !important;  
            margin-bottom: 0.2rem;
            border-bottom: 2px solid #444;
            padding-bottom: 0.4rem;
            display: inline-block;
        }
        
        header[data-testid="stHeader"] {
            height: 2rem;  
            background: transparent;
        }
        
        /* Resto do CSS permanece igual... */
        
        footer {visibility: hidden;}
        
        [data-testid="stSidebar"] > div:first-child {padding-top: 1.5rem;}
        
        .sidebar-tag {font-size: 0.7rem; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 1.5px;}
        .sidebar-title {
            font-size: 1.6rem; 
            font-weight: 700; 
            color: #1a1a1a; 
            line-height: 1.2; 
            margin-top: 6px;
            margin-bottom: 4px;
        }
        .sidebar-subtitle {font-size: 0.95rem; color: #555; line-height: 1.4; margin-bottom: 20px;}
        
        .section-subtitle {font-size: 0.9rem; color: #666; margin-bottom: 1.2rem; margin-top: 0.3rem;}
        .body-text {font-size: 0.95rem; line-height: 1.7; color: #333;}
        .body-text p {margin-bottom: 0.9rem;}
        .pp-tooltip {border-bottom: 1px dashed #666; cursor: help;}
        .info-box {background-color: #f8f9fa; border-left: 4px solid #666; padding: 1rem; margin: 1rem 0; border-radius: 4px;}
        .trans-box {background-color: #f3e5f5; border-left: 4px solid #9c27b0; padding: 1rem; margin: 1rem 0; border-radius: 4px;}
    </style>
""", unsafe_allow_html=True)

# --- LEI DE CORES PADRONIZADA ---
CORES_GEN = {
    'Homens': '#0077B6',      # Azul Vibrante
    'Mulheres': '#7B2CBF',    # Roxo Vibrante
    'Não-binários': '#FF8500', # Laranja Brilhante
    'Pessoas NB': '#FF8500',  # Variante para NB
    'Misto': '#2D6A4F',       # Verde
    'Indeterminado': '#888888'
}

@st.cache_data(ttl=3600)
def carregar_dados():
    SHEET_ID = "1Di4EgPDFPaRBjTxd3XrbO9MpDQ4oT-Xe_2g7WDnGyh8"
    try:
        df_art = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=artistas")
        df_lin = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=lineups")
        df_fst = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=festivais")
        for d in [df_art, df_lin, df_fst]: d.columns = d.columns.str.strip()
        ca = "Nome do Artista" if "Nome do Artista" in df_art.columns else "Artista"
        d1 = pd.merge(df_lin, df_art, left_on="Artista", right_on=ca, how="left")
        cf = "Festivais" if "Festivais" in df_fst.columns else "Festival"
        df = pd.merge(d1, df_fst, left_on="Festival", right_on=cf, how="left")
        df = df[df["Artista"] != "Não houve edição / Sem lineup"].copy()
        for c in ['Homens', 'Mulheres', 'Pessoas NB', 'Ano']: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        df['Ano'] = df['Ano'].astype(int)
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = carregar_dados()
if df.empty: st.warning("Aguardando dados..."); st.stop()

def formacao(row):
    h, m, nb = row.get('Homens', 0), row.get('Mulheres', 0), row.get('Pessoas NB', 0)
    mt = str(row.get('Mista?', '')).lower()
    t = h + m + nb
    if t == 0: return 'Indeterminado'
    if nb > 0 and h == 0 and m == 0: return 'Não-binário'
    if mt == 'sim' or (m > 0 and h > 0) or (m > 0 and nb > 0) or (h > 0 and nb > 0): return 'Misto'
    if m > 0 and h == 0 and nb == 0: return 'Mulheres'
    if h > 0 and m == 0 and nb == 0: return 'Homens'
    return 'Misto'

df['Formacao'] = df.apply(formacao, axis=1)

def add_source(fig, short_text="Lima Arruda, 2026", position="top"):
    if position == "top":
        fig.update_layout(margin=dict(b=30, t=60, l=60, r=20))
        fig.add_annotation(text=f"© {short_text}", xref="paper", yref="paper", x=0.99, y=0.96,
                          showarrow=False, font=dict(size=8, color="#888"), xanchor="right", yanchor="top")
    else:
        fig.update_layout(margin=dict(b=25, t=50, l=60, r=20))
        fig.add_annotation(text=f"© {short_text}", xref="paper", yref="paper", x=0.99, y=0.01,
                          showarrow=False, font=dict(size=7, color="#777"), xanchor="right", yanchor="bottom")
    return fig

if 'page' not in st.session_state: st.session_state['page'] = 'page_about'
TABS = ["Sobre o Projeto", "Metodologia", "Evolução Histórica", "Panorama Anual", "Visão por Festival", "Panorama Regional", "Panorama Artístico", "Comparador", "Heatmap Temporal"]
SOURCE_LONG = "Mulheres nos Festivais: quem ocupa os palcos brasileiros?"

with st.sidebar:
    st.markdown(f"<div class='sidebar-tag'>Painel de Dados</div><div class='sidebar-title'>Mulheres nos Festivais</div><div class='sidebar-subtitle'>Quem ocupa os palcos brasileiros?<br>2016 — 2026</div>", unsafe_allow_html=True)
    keys = ["page_about", "page_methodology", "page_history", "page_annual", "page_festival", "page_geo", "page_artists", "page_comparator", "page_heatmap"]
    for k, lab in zip(keys, TABS):
        btn_type = "primary" if st.session_state['page'] == k else "secondary"
        if st.button(lab, use_container_width=True, type=btn_type): st.session_state['page'] = k; st.rerun()
    st.markdown("<hr style='margin: 15px 0; opacity: 0.3;'>", unsafe_allow_html=True)
    st.caption("A democratização destes dados é parte fundamental deste projeto. Você pode compartilhar, copiar e redistribuir este conteúdo em qualquer suporte ou formato, desde que atribua o crédito apropriadamente à autora e indique o link desta plataforma. — [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.pt)")
    st.markdown("<hr style='margin: 15px 0; opacity: 0.3;'>", unsafe_allow_html=True)
    
    # Código para renderizar o botão oficial do Buy Me a Coffee
    button_html = """
    <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" 
            data-name="bmc-button" data-slug="mulheresnosfestivais" data-color="#3D2B56" 
            data-emoji="☕" data-font="Cookie" data-text="Buy Me a Coffee" data-outline-color="#ffffff" 
            data-font-color="#ffffff" data-coffee-color="#FFDD00"></script>
    """
    
    # Centraliza o botão na sidebar
    components.html(f"<div style='display: flex; justify-content: center;'>{button_html}</div>", height=70)
page = st.session_state['page']

if page == "page_about":
    st.markdown(f"<div class='section-title'>{TABS[0]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'></div>", unsafe_allow_html=True)
    
    # Texto principal
    st.markdown("""
    <div class='body-text'>
    Coletar, sistematizar e disseminar dados que exponham as lacunas e desigualdades históricas na indústria musical, especialmente nos palcos dos principais festivais brasileiros, tem sido o foco deste estudo ao longo da última década.<br><br>
    
    Embora existam avanços, a disparidade de gênero continua sendo uma realidade latente. Isso reforça a urgência de ações efetivas e, sobretudo, consistentes, para que um cenário musical brasileiro verdadeiramente inclusivo se consolide.<br><br>
    
    Este painel tem como missão evidenciar a desigualdade de oportunidades e de postos de trabalho no mercado de festivais, com olhar atento às mulheres que fazem da música e do palco sua profissão. Concebido como um projeto vivo, este espaço de consulta para pesquisas e profissionais do mercado é expandido gradualmente, integrando novos festivais à medida que consolidam sua trajetória e amostragem no cenário nacional.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Autoria
    st.markdown("**Autoria**")
    st.markdown("""
    <div class='body-text' style='margin-bottom: 1.5rem;'>
    Todos os dados foram coletados e organizados pela pesquisadora musical <b>Thabata Lima Arruda</b>.
    </div>
    """, unsafe_allow_html=True)
    
    # Publicações
    st.markdown("**Publicações**")
    st.markdown("""
    - [Artista igual Trabalhadora: histórias, dados e perspectivas sobre as mulheres nos palcos brasileiros](https://www.sescsp.org.br/editorial/zumbido-artista-trabalhadora/)
    - [Mulheres nos Festivais: quem ocupa os palcos brasileiros? (2016–2024)](https://www.sescsp.org.br/editorial/zumbido-mulheres-nos-festivais-2016-2024/)
    - [Presença feminina nos festivais brasileiros de 2019](https://www.sescsp.org.br/editorial/a-presenca-feminina-nos-festivais-brasileiros-de-2019/)
    - [Presença feminina nos festivais brasileiros (2016–2018)](https://www.sescsp.org.br/editorial/a-presenca-feminina-nos-festivais-brasileiros-de-2016-a-2018/)
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contato
    st.markdown("**Contato**")
    st.markdown("mulheresnosfestivais@proton.me")
    st.markdown("[thabata.work](https://thabata.work)")
        

elif page == "page_methodology":
    st.markdown(f"<div class='section-title'>{TABS[1]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Critérios de amostragem e classificação</div>", unsafe_allow_html=True)
    
    with st.expander("Seleção dos festivais"):
        st.markdown("""
        <div class='body-text'>
        Foram selecionados festivais para a análise de todas as regiões do Brasil de médio a grande porte com edições realizadas entre 2016 e 2026. Nove dos eventos analisados primariamente surgiram após a pandemia e enquanto 21 tiveram início em 2016 ou antes. Além disso, todos os festivais incluídos no estudo realizaram, no mínimo, quatro edições, o que garante uma amostragem mais consistente.<br><br>

        Vale destacar que alguns festivais deixaram de acontecer, especialmente após a pandemia, enquanto outros já apresentavam edições irregulares antes desse período. O número de festivais analisados anualmente seguiu uma média ajustada, levando em conta tanto os cancelamentos quanto a inclusão de novos eventos. Essa abordagem busca garantir uma avaliação equilibrada das tendências de participação feminina ao longo do tempo.<br><br>

        A expansão da base de dados (tanto festivais, quanto artistas) ocorre de forma incremental. Atualmente, novos eventos estão sendo catalogados e inseridos gradualmente, priorizando festivais que consolidam o critério metodológico de ao menos quatro edições realizadas.
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("Programações"):
        st.markdown("""
        <div class='body-text'>
        Para contabilizar todas as atrações artísticas de cada edição, foi analisada a programação completa de cada festival. As informações foram obtidas diretamente de fontes oficiais, como redes sociais dos eventos ou produtoras, sites e matérias da imprensa publicadas próximas à data do evento.
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("Atos musicais e suas categorias"):
        st.markdown("""
        <div class='body-text'>
        No contexto deste estudo, um <b>ato musical</b> refere-se a qualquer performance ao vivo durante o festival, seja por artista solo (incluindo DJs), duo ou grupo musical, abrangendo tanto apresentações principais quanto secundárias.<br><br>

        <b>Foram excluídos da análise:</b>
        <ul>
        <li>Atos não musicais (artistas visuais, teatro, comediantes, VJs, palestras, etc.);</li>
        <li>Atos não anunciados publicamente antes do festival (showcases, participações surpresas, etc.);</li>
        <li>Grandes formações com dificuldade para identificar integrantes oficiais (cortejos, orquestras, big bands, etc.);</li>
        <li>Artistas anônimos, sem registros disponíveis na imprensa ou redes sociais;</li>
        <li>Artistas que se apresentaram mais de uma vez com o mesmo nome ou projeto, sendo contabilizados uma única vez;</li>
        <li>Jam sessions, batalhas de rimas, regentes e apresentações de aparelhagem.</li>
        </ul><br>

        Os atos musicais de cada festival foram classificados em três categorias:
        <ul>
        <li><b>Mulheres:</b> solistas e grupos compostos exclusivamente por mulheres e/ou pessoas não-binárias.</li>
        <li><b>Homens:</b> solistas e grupos formados apenas por homens.</li>
        <li><b>Grupos mistos:</b> bandas com pelo menos uma mulher ou pessoa não-binária na formação oficial.</li>
        </ul><br>

        As porcentagens foram calculadas com base no número de atrações de cada categoria em relação ao total de atrações de cada ano, multiplicando o valor por 100. Isso facilita a comparação da participação de cada grupo ao longo do tempo e a identificação de tendências nos line-ups.
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("Integrantes Individuais e suas categorias"):
        st.markdown("""
        <div class='body-text'>
        Além da categorização dos atos musicais, também foi realizada a categorização dos <b>integrantes individuais</b> de cada ato musical. Essa abordagem metodológica foi essencial para aprofundar a análise sobre a disparidade de gênero nos festivais, uma vez que os integrantes de cada grupo foram contabilizados individualmente.<br><br>

        Consideram-se integrantes individuais quem é parte de duos, grupos ou bandas, excluindo artistas contratados apenas para apresentações pontuais ou turnês temporárias, bem como profissionais não-músicos, como produtores ou dançarinos. As fontes para identificar os integrantes incluem sites oficiais, redes sociais, fotos promocionais e matérias jornalísticas, e foram consultadas de acordo com o ano de cada festival, levando em consideração que as formações dos grupos/bandas podem mudar ao longo do tempo.<br><br>

        A classificação dos integrantes seguiu três categorias:
        <ul>
        <li><b>Mulheres</b></li>
        <li><b>Homens</b></li>
        <li><b>Pessoas não-binárias</b> (incluindo identidades como queer, gênero fluido, agênero etc.)</li>
        </ul><br>

        É importante destacar que mulheres trans são mulheres, e homens trans, homens. A categorização é baseada na identidade de gênero autodeclarada ou nos pronomes utilizados, obtidos em fontes confiáveis. Suposições foram evitadas, e esforços consideráveis foram feitos para não presumir as identidades de gênero durante o levantamento. Para artistas com múltiplos pronomes, foram feitas pesquisas adicionais para garantir precisão.<br><br>

        <b>Critérios de classificação baseado nos pronomes:</b>
        <ul>
        <li>Ela/dela (she/her) → <b>Mulher</b></li>
        <li>Ele/dele (he/him) → <b>Homem</b></li>
        <li>Elu/delu, they/them → <b>Não-binário</b></li>
        <li>She/they, they/she → <b>Mulher</b> (se não houver mais informações)</li>
        <li>He/they, they/he → <b>Homem</b> (se não houver mais informações)</li>
        </ul><br>

        Esse método assegurou uma categorização precisa e ética, respeitando a diversidade de gênero na música.
        </div>
        """, unsafe_allow_html=True)

elif page == "page_history":
    st.markdown(f"<div class='section-title'>{TABS[2]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Participação percentual de Integrantes Individuais por gênero</div>", unsafe_allow_html=True)
    
    evo = df.groupby('Ano')[['Mulheres', 'Homens', 'Pessoas NB']].sum()
    evo['Total'] = evo.sum(axis=1)
    for c in ['Mulheres', 'Homens', 'Pessoas NB']: 
        evo[f'% {c}'] = (evo[c] / evo['Total'] * 100).round(1)
    evo = evo.reset_index()
    
    fig = go.Figure()
    
    # 1. HOMENS (Azul)
    fig.add_trace(go.Scatter(
        x=evo['Ano'], y=evo['% Homens'], mode='lines+markers', name='Homens', 
        line=dict(color=CORES_GEN['Homens'], width=2.5, dash='dash'),
        marker=dict(size=7, symbol='diamond'), hovertemplate='Homens: %{y:.1f}%<extra></extra>'
    ))

    # 2. MULHERES (Roxo)
    fig.add_trace(go.Scatter(
        x=evo['Ano'], y=evo['% Mulheres'], mode='lines+markers', name='Mulheres', 
        line=dict(color=CORES_GEN['Mulheres'], width=3),
        marker=dict(size=8), hovertemplate='Mulheres: %{y:.1f}%<extra></extra>'
    ))
    
    # 3. PESSOAS NB (Laranja)
    fig.add_trace(go.Scatter(
        x=evo['Ano'], y=evo['% Pessoas NB'], mode='lines+markers', name='Não-binários', 
        line=dict(color=CORES_GEN['Pessoas NB'], width=2.5, dash='dot'),
        marker=dict(size=7, symbol='square'), hovertemplate='Não-binários: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        height=420, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(dtick=1, gridcolor='#eee'), yaxis=dict(range=[0, 100], ticksuffix="%", gridcolor='#eee'),
        plot_bgcolor='white', paper_bgcolor='white'
    )
    
    fig = add_source(fig, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
    st.plotly_chart(fig, use_container_width=True)

# --- PÁGINA 4: PANORAMA ANUAL ---
elif page == "page_annual":
    st.markdown(f"<div class='section-title'>{TABS[3]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Consolidado anual e ranking de festivais</div>", unsafe_allow_html=True)
    
   
    st.markdown("""
        <style>
            .custom-metric-box {
                background-color: #f8f9fa;
                border: 1px solid #eee;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                height: 100%;
            }
            .metric-title { font-size: 0.85rem; color: #666; margin-bottom: 8px; font-weight: 500; }
            .metric-value { font-size: 1.6rem; font-weight: 800; color: #000; line-height: 1.2; }
            .metric-footer { font-size: 0.8rem; color: #888; margin-top: 4px; }
        </style>
    """, unsafe_allow_html=True)

    try:
   
        anos = sorted(df['Ano'].unique())
        st.markdown("**Ano**")
        ano = st.selectbox("Selecione o ano:", anos, index=len(anos)-1, label_visibility="collapsed")
        d = df[df['Ano'] == ano].copy()
        
       
        for col in ['Mulheres', 'Homens', 'Pessoas NB']:
            if col in d.columns:
                d[col] = pd.to_numeric(d[col], errors='coerce').fillna(0)
        
        total_atos = len(d)
        soma_m = int(d['Mulheres'].sum())
        soma_h = int(d['Homens'].sum())
        soma_nb = int(d['Pessoas NB'].sum())
        total_ints = soma_m + soma_h + soma_nb

       
        d.columns = d.columns.str.strip()
        col_trans_name = "Pessoas Trans" 
        
        soma_trans = 0
        if col_trans_name in d.columns:
           
            soma_trans = len(d[d[col_trans_name].astype(str).str.lower().str.strip() == 'sim'])
        
        pct_trans = (soma_trans / total_ints * 100) if total_ints > 0 else 0


        def draw_card(col, titulo, valor, sub):
            col.markdown(f"""
                <div class="custom-metric-box">
                    <div class="metric-title">{titulo}</div>
                    <div class="metric-value">{valor}</div>
                    <div class="metric-footer">{sub}</div>
                </div>
            """, unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        draw_card(c1, "Atos Musicais", f"{total_atos}", "Projetos no ano")
        draw_card(c2, "Total Integrantes", f"{total_ints}", "Pessoas no palco")
        
        pm = (soma_m / total_ints * 100) if total_ints > 0 else 0
        ph = (soma_h / total_ints * 100) if total_ints > 0 else 0
        pnb = (soma_nb / total_ints * 100) if total_ints > 0 else 0
        
        draw_card(c3, "Mulheres", f"{pm:.1f}%", f"{soma_m} integrantes")
        draw_card(c4, "Homens", f"{ph:.1f}%", f"{soma_h} integrantes")
        draw_card(c5, "Pessoas NB", f"{pnb:.1f}%", f"{soma_nb} integrantes")
        
        st.markdown("<br>", unsafe_allow_html=True)

      
        if soma_trans > 0:
            st.info(f"""
                **Diversidade Trans:** identificamos a presença de **{soma_trans}** pessoas autodeclaradas trans nos palcos de {ano}. 
                Isso representa **{pct_trans:.1f}%** do total de **{total_ints}** integrantes individuais analisados neste ano.
            """)
        else:
            st.warning(f"Informação: Não foram identificados artistas mapeados como 'Sim' na coluna 'Pessoa Trans' para o ano de {ano}.")

        st.divider()
        
        # --- 4. RANKING DE REPRESENTATIVIDADE ---
        st.markdown("**Ranking de representatividade (Mulheres + Não-binárias)**")
        
        r = d.groupby('Festival')[['Mulheres', 'Homens', 'Pessoas NB']].sum()
        r['Total'] = r.sum(axis=1)
        r = r[r['Total'] > 0]
        r['% Fem+NB'] = ((r['Mulheres'] + r['Pessoas NB']) / r['Total'] * 100).round(1)
        r = r.sort_values('% Fem+NB', ascending=False).reset_index()
        
        if len(r) >= 3:
            cols = st.columns(3)
            for i, (_, row) in enumerate(r.head(3).iterrows()):
                delta_val = row['% Fem+NB'] - 50
                with cols[i]:
                    st.metric(
                        label=f"#{i+1} {row['Festival'][:22]}", 
                        value=f"{row['% Fem+NB']:.1f}%", 
                        delta=f"{delta_val:+.1f} p.p. vs paridade" if abs(delta_val) > 0.5 else "paridade"
                    )
        
        def cor_ranking(v):
            try:
                n = float(str(v).replace('%',''))
                if n >= 50: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif n >= 35: return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
                else: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            except: return ''
        
        disp = r[['Festival', '% Fem+NB']].copy()
        disp['Representatividade (Fem+NB)'] = disp['% Fem+NB'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            disp[['Festival', 'Representatividade (Fem+NB)']].style.map(cor_ranking, subset=['Representatividade (Fem+NB)']),
            use_container_width=True, hide_index=True, height=400
        )

    except Exception as e:
        st.error(f"Erro ao carregar panorama anual: {e}")

# --- PÁGINA 5: RAIO-X POR FESTIVAL ---
elif page == "page_festival":

    st.markdown(f"<div class='section-title'>{TABS[4]}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-subtitle'>Dados detalhados por festival/edição</div>", unsafe_allow_html=True)
    
   
    st.markdown("""
        <style>
            .custom-metric-box {
                background-color: #f8f9fa;
                border: 1px solid #eee;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                height: 100%;
            }
            .metric-title { font-size: 0.8rem; color: #666; margin-bottom: 5px; font-weight: 500; }
            .metric-value { font-size: 1.4rem; font-weight: 800; color: #000; line-height: 1.1; }
            .metric-footer { font-size: 0.75rem; color: #888; margin-top: 2px; }
            .exclusion-legend { 
                background-color: #f9f9f9; 
                padding: 25px; 
                border-radius: 5px; 
                border: 1px solid #eee; 
                font-size: 0.85rem; 
                color: #555;
                margin-top: 35px;
                line-height: 1.6;
            }
        </style>
    """, unsafe_allow_html=True)

  
    festivais_lista = sorted(df['Festival'].dropna().unique())
    fest = st.selectbox("Escolha um Festival:", festivais_lista)
    df_fest = df[df['Festival'] == fest].copy()
    
   
    evo = df_fest.groupby('Ano')[['Mulheres', 'Homens', 'Pessoas NB']].sum()
    evo['Total'] = evo.sum(axis=1)
    evo = evo[evo['Total'] > 0].reset_index()
    evo['% Mulheres'] = (evo['Mulheres'] / evo['Total'] * 100).round(1)
    
    st.markdown(f"**Evolução da presença feminina: {fest}**")
    fig = px.line(evo, x='Ano', y='% Mulheres', markers=True)
    fig.update_traces(line=dict(color='#7B2CBF', width=3), marker=dict(size=10, color='#7B2CBF'))
    
    
    fig.update_xaxes(
        dtick=1, 
        tickformat='d', 
        showgrid=False
    )
    
    fig.update_yaxes(range=[0, 105], ticksuffix="%", gridcolor='#eee')
    fig.update_layout(
        height=320, 
        margin=dict(t=20, b=50, l=10, r=10), 
        plot_bgcolor='white',
        hovermode="x unified"
    )
    fig.add_hline(y=50, line_dash="dot", line_color="#ccc")
    
  
    fig = add_source(fig, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
    
    st.divider()
    
 
    st.markdown("**Análise por Edição**")
    anos_disp = sorted(df_fest['Ano'].dropna().unique())
    
    col_sel, col_btn = st.columns([1, 1])
    with col_sel:
        ano_sel = st.selectbox("Selecione o Ano:", anos_disp, index=len(anos_disp)-1, label_visibility="collapsed")
    
    df_ano = df_fest[df_fest['Ano'] == ano_sel].copy()
    
 
    link_fonte = None
    if 'Cartaz' in df_ano.columns:
        valid_links = df_ano['Cartaz'].dropna().unique()
        if len(valid_links) > 0 and str(valid_links[0]).startswith('http'):
            link_fonte = str(valid_links[0])

    with col_btn:
        if link_fonte:
            st.link_button("Fonte", link_fonte, use_container_width=True)
        else:
            st.button("Fonte Indisponível", disabled=True, use_container_width=True)

   
    total_atos = len(df_ano)
    for c in ['Mulheres', 'Homens', 'Pessoas NB', 'Pessoas Trans']:
        if c in df_ano.columns:
            df_ano[c] = pd.to_numeric(df_ano[c], errors='coerce').fillna(0)

    s_m = int(df_ano['Mulheres'].sum())
    s_h = int(df_ano['Homens'].sum())
    s_nb = int(df_ano['Pessoas NB'].sum())
    total_pess = s_m + s_h + s_nb
    
    s_trans = 0
    if 'Pessoa Trans' in df_ano.columns:
        if df_ano['Pessoa Trans'].dtype in [np.float64, np.int64]:
            s_trans = int(df_ano['Pessoa Trans'].sum())
        else:
            s_trans = len(df_ano[df_ano['Pessoas Trans'].astype(str).str.lower().str.strip() == 'sim'])

    def draw_fest_card(col, title, value, footer):
        col.markdown(f"""
            <div class="custom-metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-footer">{footer}</div>
            </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    draw_fest_card(c1, "Atos Musicais", f"{total_atos}", f"{total_pess} pessoas")
    
    pm = (s_m / total_pess * 100) if total_pess > 0 else 0
    ph = (s_h / total_pess * 100) if total_pess > 0 else 0
    pnb = (s_nb / total_pess * 100) if total_pess > 0 else 0
    
    draw_fest_card(c2, "Mulheres", f"{pm:.1f}%", f"{s_m} integrantes")
    draw_fest_card(c3, "Homens", f"{ph:.1f}%", f"{s_h} integrantes")
    draw_fest_card(c4, "Pessoas NB", f"{pnb:.1f}%", f"{s_nb} integrantes")

    if s_trans > 0:
        pct_t = (s_trans / total_pess * 100) if total_pess > 0 else 0
        st.info(f"**Diversidade Trans:** esta edição contou com {s_trans} integrante(s) trans ({pct_t:.1f}% do palco).")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. LINEUP E LEGENDA
    with st.expander(f"Ver Lineup Completo - {fest} {int(ano_sel)}", expanded=True):
        arts = sorted(df_ano['Artista'].dropna().unique())
        l_col1, l_col2, l_col3 = st.columns(3)
        for idx, artista in enumerate(arts):
            if idx % 3 == 0: l_col1.markdown(f"• {artista}")
            elif idx % 3 == 1: l_col2.markdown(f"• {artista}")
            else: l_col3.markdown(f"• {artista}")
            
        st.markdown(f"""
            <div class="exclusion-legend">
                <strong>Foram excluídos da análise:</strong><br>
                • Atos não musicais (artistas visuais, teatro, comediantes, VJs, palestras, etc)<br>
                • Atos não anunciados publicamente antes do festival (showcases, participações surpresas, etc)<br>
                • Grandes formações com dificuldade para identificar integrantes oficiais (cortejos, orquestras, etc)<br>
                • Artistas anônimos ou sem registros disponíveis na imprensa/redes sociais<br>
                • Artistas contabilizados uma única vez mesmo que apresentados em múltiplos projetos com o mesmo nome<br>
                • Jam sessions, batalhas de rimas e apresentações de aparelhagem.
            </div>
        """, unsafe_allow_html=True)




elif page == "page_geo":
    st.markdown(f"<div class='section-title'>{TABS[5]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Distribuição geográfica e indicadores regionais dos festivais</div>", unsafe_allow_html=True)
    
    anos = sorted(df['Ano'].unique())
    st.markdown("**Ano**")
    ano_geo = st.selectbox("Selecione o ano:", anos, index=len(anos)-1, label_visibility="collapsed")
    df_geo = df[df['Ano'] == ano_geo]
    
    if 'Estado' not in df_geo.columns or df_geo['Estado'].isna().all():
        st.info("Dados de localização não disponíveis.")
        st.stop()
    
    reg = df_geo.groupby('Estado').agg({
        'Festival': 'nunique',
        'Mulheres': 'sum', 'Homens': 'sum', 'Pessoas NB': 'sum'
    }).reset_index()
    reg['Total'] = reg[['Mulheres', 'Homens', 'Pessoas NB']].sum(axis=1)
    reg['% Fem+NB'] = ((reg['Mulheres'] + reg['Pessoas NB']) / reg['Total'] * 100).round(1)
    reg = reg.sort_values('Festival', ascending=False)
    
    cv, ct = st.columns([3, 2])
    with cv:
        fig = px.scatter(reg, x='Estado', y='% Fem+NB', size='Festival',
                        color='% Fem+NB', color_continuous_scale='Purp',
                        size_max=45, range_color=[15, 55])
        fig.update_traces(marker=dict(line=dict(width=1, color='white')))
        fig.update_layout(height=350, xaxis_tickangle=-30, plot_bgcolor='white')
        fig.add_hline(y=50, line_dash="dot", line_color="#666", opacity=0.4)
        fig = add_source(fig, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
        st.plotly_chart(fig, use_container_width=True)
    
    with ct:
        st.markdown("**Indicadores por estado**")
        st.dataframe(
            reg[['Estado', 'Festival', '% Fem+NB']].rename(
                columns={'Festival': 'Festivais', '% Fem+NB': '% Fem+NB'}
            ).style.format({'% Fem+NB': '{:.1f}%'}),
            use_container_width=True, hide_index=True, height=280
        )

# --- PÁGINA 7: PANORAMA ARTÍSTICO ---
elif page == "page_artists":
    st.markdown(f"<div class='section-title'>{TABS[6]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Análise detalhada por tipo de ato e formação</div>", unsafe_allow_html=True)
    
    st.markdown("**Ano**")
    anos = sorted(df['Ano'].unique())
    ano_sel = st.selectbox("Selecione o ano:", anos, index=len(anos)-1, label_visibility="collapsed")
    da = df[df['Ano'] == ano_sel].copy()
    
    t1, t2, t3, t4 = st.tabs(["Atos Musicais", "Grupos", "Solistas", "Recorrência"])
    
    CORES_PIE = {'Solista': '#3D2B56', 'Duo': '#94A3B8', 'Grupo': '#2D6A4F', 'Banda': '#1B4332'}
    CORES_GEN_ART = {
        'Homens': CORES_GEN['Homens'], 
        'Mulheres': CORES_GEN['Mulheres'], 
        'Misto': CORES_GEN['Misto'], 
        'Não-binárie': CORES_GEN['Pessoas NB']
    }

    with t1:
        st.markdown("### Atos Musicais")
        st.caption("Performances ao vivo durante o festival, seja por artista solo (incluindo DJs), duo ou grupo musical, abrangendo tanto apresentações principais quanto secundárias.")
        
        tp = da['Tipo'].value_counts().reset_index()
        tp.columns = ['Tipo', 'N']
        fig = px.pie(tp, values='N', names='Tipo', hole=0.4, color='Tipo', color_discrete_map=CORES_PIE)
        fig.update_traces(textposition='outside', textinfo='label+percent')
        fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=50),
                          legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5))
        
        fig = add_source(fig, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.markdown("### Grupos")
        st.caption("Duo ou grupo musical. Categorias: Mulheres (exclusivamente mulheres e/ou pessoas NB), Homens (apenas homens) e Grupos mistos (pelo menos uma mulher ou pessoa NB na formação).")
        
        grupos = da[da['Tipo'] != 'Solista'].copy()
        if len(grupos) > 0:
            rs = grupos['Formacao'].value_counts()
            total_g = len(grupos)
            
            c1, c2, c3 = st.columns(3)
            def draw_card_g(col, title, val_abs, total):
                pct = (val_abs/total*100) if total > 0 else 0
                col.markdown(f"""
                    <div style="background-color: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.8rem; color: #666;">{title}</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #000;">{pct:.1f}%</div>
                        <div style="font-size: 0.75rem; color: #888;">{int(val_abs)} grupos</div>
                    </div>
                """, unsafe_allow_html=True)

            draw_card_g(c1, "Só Homens", rs.get('Homens', 0), total_g)
            draw_card_g(c2, "Só Mulheres", rs.get('Mulheres', 0), total_g)
            draw_card_g(c3, "Grupos Mistos", rs.get('Misto', 0), total_g)

            st.markdown("<br>**Evolução histórica da formação de grupos**", unsafe_allow_html=True)
            ev_g = df[df['Tipo'] != 'Solista'].groupby(['Ano', 'Formacao']).size().unstack(fill_value=0).reset_index()
            fig_g = go.Figure()

            for f_name in ['Homens', 'Mulheres', 'Misto']:
                if f_name in ev_g.columns:
                    fig_g.add_trace(go.Scatter(x=ev_g['Ano'], y=ev_g[f_name], name=f_name, mode='lines+markers',
                                             line=dict(color=CORES_GEN.get(f_name), width=3),
                                             hovertemplate=f'{f_name}: %{{y}}<extra></extra>'))
            fig_g.update_layout(height=350, hovermode='x unified', plot_bgcolor='white', xaxis=dict(dtick=1))
            fig_g = add_source(fig_g, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            st.info("Sem grupos catalogados para este ano.")

    with t3:
        st.markdown("### Solistas")
        st.caption("Atos musicais onde a comunicação é compreendida como artista solo. Categorias: Mulheres (mulheres + pessoas NB) e Homens.")
        
        solistas = da[da['Tipo'] == 'Solista'].copy()
        if len(solistas) > 0:
            def gs(r):
                if r['Mulheres']==1 and r['Homens']==0: return 'Mulheres'
                if r['Homens']==1 and r['Mulheres']==0: return 'Homens'
                if r['Pessoas NB']==1: return 'Mulheres' # Seguindo sua regra: Mulheres = mulheres + NB
                return 'Outros'
            
            solistas['Gênero_Simpl'] = solistas.apply(gs, axis=1)
            rs_s = solistas['Gênero_Simpl'].value_counts()
            total_s = len(solistas)

            cs1, cs2 = st.columns(2)
            def draw_card_s(col, title, val_abs, total):
                pct = (val_abs/total*100) if total > 0 else 0
                col.markdown(f"""
                    <div style="background-color: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.8rem; color: #666;">{title}</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #000;">{pct:.1f}%</div>
                        <div style="font-size: 0.75rem; color: #888;">{int(val_abs)} artistas</div>
                    </div>
                """, unsafe_allow_html=True)

            draw_card_s(cs1, "Homens", rs_s.get('Homens', 0), total_s)
            draw_card_s(cs2, "Mulheres (+ NB)", rs_s.get('Mulheres', 0), total_s)

            st.markdown("<br>**Evolução histórica de solistas**", unsafe_allow_html=True)

            df_sol = df[df['Tipo'] == 'Solista'].copy()
            df_sol['G_Hist'] = df_sol.apply(gs, axis=1)
            ev_s = df_sol.groupby(['Ano', 'G_Hist']).size().unstack(fill_value=0).reset_index()
            
            fig_s = go.Figure()
            for g_name in ['Homens', 'Mulheres']:
                if g_name in ev_s.columns:
                    fig_s.add_trace(go.Scatter(x=ev_s['Ano'], y=ev_s[g_name], name=g_name, mode='lines+markers',
                                             line=dict(color=CORES_GEN.get(g_name), width=3),
                                             hovertemplate=f'{g_name}: %{{y}}<extra></extra>'))
            fig_s.update_layout(height=350, hovermode='x unified', plot_bgcolor='white', xaxis=dict(dtick=1))
            fig_s = add_source(fig_s, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
            st.plotly_chart(fig_s, use_container_width=True)
        else:
            st.info("Sem solistas catalogados para este ano.")

    with t4:
        st.markdown("### Recorrência")
        st.caption(f"Artistas que aparecem em múltiplos festivais diferentes no ano de {int(ano_sel)}.")
        
        rec = da.groupby('Artista').agg({'Festival': 'nunique'}).reset_index()
        rec = rec[rec['Festival'] >= 2].sort_values('Festival', ascending=False).head(15)
        
        if len(rec) > 0:
            fig_r = px.bar(rec, x='Festival', y='Artista', orientation='h', 
                         color='Festival', color_continuous_scale='Blues')
            fig_r.update_layout(height=450, yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            fig_r.update_xaxes(dtick=1)
            fig_r = add_source(fig_r, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "bottom")
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("Nenhum artista com múltiplas aparições em festivais diferentes neste ano.")
# --- PÁGINA 9: COMPARADOR ---
elif page == "page_comparator":
    st.markdown(f"<div class='section-title'>{TABS[8]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Compare a representatividade entre dois festivais</div>", unsafe_allow_html=True)
    
    fests = sorted(df['Festival'].dropna().unique())
    c1, c2 = st.columns(2)
    with c1: f1 = st.selectbox("Festival A:", fests, index=0)
    with c2: f2 = st.selectbox("Festival B:", fests, index=1 if len(fests)>1 else 0)
    
    def get_evo(f_name):
        d_f = df[df['Festival'] == f_name].copy()

        for col in ['Mulheres', 'Homens', 'Pessoas NB']:
            d_f[col] = pd.to_numeric(d_f[col], errors='coerce').fillna(0)
        
        ev = d_f.groupby('Ano')[['Mulheres', 'Homens', 'Pessoas NB']].sum()
        ev['Total'] = ev.sum(axis=1)

        ev['% Repr'] = ((ev['Mulheres'] + ev['Pessoas NB']) / ev['Total'] * 100).round(1)
        return ev.reset_index()

    df_f1 = get_evo(f1)
    df_f2 = get_evo(f2)
    
    fig = go.Figure()
    
    # Festival A
    fig.add_trace(go.Scatter(
        x=df_f1['Ano'], y=df_f1['% Repr'], name=f1,
        mode='lines+markers', line=dict(color='#C75B39', width=3),
        hovertemplate='%{y:.1f}%'
    ))
    
    # Festival B
    fig.add_trace(go.Scatter(
        x=df_f2['Ano'], y=df_f2['% Repr'], name=f2,
        mode='lines+markers', line=dict(color='#2E5A6B', width=3, dash='dash'),
        hovertemplate='%{y:.1f}%'
    ))
    
    fig.update_layout(
        height=450,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        plot_bgcolor='white',
        xaxis=dict(dtick=1, tickformat='d', gridcolor='#eee'), # 'd' força ano inteiro
        yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor='#eee', title="Representatividade (Fem + NB)")
    )
    fig.add_hline(y=50, line_dash="dot", line_color="#ccc", annotation_text="paridade")
    
    fig = add_source(fig, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "top")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Situação na edição mais recente")
    m1, m2 = st.columns(2)
    
    def draw_comp_card(col, fest_name, data):
        if not data.empty:
            ultimo = data.iloc[-1]
            col.markdown(f"""
                <div style="background-color: #f8f9fa; border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.85rem; color: #666; font-weight: 500;">{fest_name} ({int(ultimo['Ano'])})</div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: #000;">{ultimo['% Repr']:.1f}%</div>
                    <div style="font-size: 0.8rem; color: #888;">Representatividade Fem + NB</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            col.info(f"Sem dados para {fest_name}")

    draw_comp_card(m1, f1, df_f1)
    draw_comp_card(m2, f2, df_f2)

elif page == "page_heatmap":
    st.markdown(f"<div class='section-title'>{TABS[8]}</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Matriz temporal: representação feminina</div>", unsafe_allow_html=True)
    
    h = df.groupby(['Festival', 'Ano'])[['Mulheres', 'Homens', 'Pessoas NB']].sum()
    h['Total'] = h.sum(axis=1)
    h['Pct'] = (h['Mulheres'] / h['Total'] * 100).round(1)
    h = h.reset_index()
    
    pv = h.pivot(index='Festival', columns='Ano', values='Pct')
    
    fig = go.Figure(data=go.Heatmap(
        z=pv.values,
        x=[str(int(c)) for c in pv.columns],
        y=pv.index,
        colorscale=[
            [0.0, '#F2F0F7'], # Roxo clarinho
            [0.5, '#9D4EDD'], # Roxo médio
            [1.0, '#7B2CBF']  # Roxo vibrante (Mulheres)
        ],
        zmin=0, zmax=50,
        colorbar=dict(title="%<br>Mulheres", ticksuffix="%"),
        hovertemplate="%{y}<br>Ano: %{x}<br>Mulheres: %{z:.1f}%<extra></extra>",
        text=[[f"{v:.0f}" if pd.notna(v) else "" for v in r] for r in pv.values],
        texttemplate="%{text}",
        textfont={"size": 8, "color": "#444"}
    ))
    
    fig.update_layout(
        height=max(500, len(pv) * 28),
        yaxis=dict(autorange="reversed", tickfont_size=10),
        xaxis=dict(tickfont_size=10),
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=150, r=20, t=50, b=40)
    )
    fig = add_source(fig, "Mulheres nos Festivais: quem ocupa os palcos brasileiros? Lima Arruda, 2026", "bottom")
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Intensidade do roxo indica proximidade da paridade (50%). Células vazias = dados ausentes.")

st.markdown("<hr style='margin: 2rem 0 1rem; opacity: 0.3;'>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.75rem; line-height: 1.6;'>
    {SOURCE_LONG}<br>
    Thabata Lima Arruda, 2026 · mulheresnosfestivais@proton.me<br>
    Última atualização de dados: {datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")} </br>
    Uso livre para fins informativos e de pesquisa, mediante citação obrigatória de fonte e autoria. <br>
<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.pt">CC BY-NC-SA 4.0</a>
</div>
""", unsafe_allow_html=True)
