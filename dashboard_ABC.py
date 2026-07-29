import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Monitoramento da Assistência Farmacêutica - Cambé",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNÇÃO DE FORMATAÇÃO NO PADRÃO BRASILEIRO (PT-BR) ---
def formatar_br(valor, e_financeiro=False):
    """
    Formata números para o padrão brasileiro:
    - Milhares separados por ponto (.)
    - Decimais separados por vírgula (,)
    """
    if pd.isna(valor):
        return "-"
    if e_financeiro:
        texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"
    else:
        texto = f"{valor:,.0f}".replace(",", ".")
        return texto

# Carregamento e tratamento dos dados
@st.cache_data
def load_data():
    df = pd.read_excel('dadosABC.xlsx')
    df['Produto'] = df['Produto'].ffill()
    df[['Ano', 'Mês']] = df['ano-mes'].str.split('-', expand=True)
    df['Ano'] = df['Ano'].astype(int)
    df['Mês'] = df['Mês'].astype(int)
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o arquivo 'dadosABC.xlsx'. Certifique-se de que ele está na mesma pasta do script. Erro: {e}")
    st.stop()

# --- BARRA LATERAL ---
st.sidebar.title("📌 Painel de Controle")
st.sidebar.markdown("---")

ref_opcao = st.sidebar.radio(
    "Selecione a referência da análise:",
    ["Volume financeiro", "Volume de movimentação"],
    index=0
)
coluna_analise = "Valor Total Produto Movimento" if ref_opcao == "Volume financeiro" else "Qtde Produto Movimento"
e_financeiro = (ref_opcao == "Volume financeiro")

metodo_analise = st.sidebar.radio(
    "Método de análise:",
    ["Consumo médio", "Acumulado do período"],
    index=1
)

anos_disponiveis = sorted(df_raw['Ano'].unique())
meses_disponiveis = sorted(df_raw['Mês'].unique())

st.sidebar.markdown("### 📅 Período Inicial")
ano_ini = st.sidebar.selectbox("Ano Inicial", anos_disponiveis, index=0)
mes_ini = st.sidebar.selectbox("Mês Inicial", meses_disponiveis, index=0)

st.sidebar.markdown("### 📅 Período Final")
ano_fim = st.sidebar.selectbox("Ano Final", anos_disponiveis, index=len(anos_disponiveis)-1)
mes_fim = st.sidebar.selectbox("Mês Final", meses_disponiveis, index=len(meses_disponiveis)-1)

data_inicio_str = f"{ano_ini}-{mes_ini:02d}"
data_fim_str = f"{ano_fim}-{mes_fim:02d}"

if data_inicio_str > data_fim_str:
    st.sidebar.error("Erro: A data inicial não pode ser maior que a data final.")
    st.stop()

df_filtrado = df_raw[
    (df_raw['ano-mes'] >= data_inicio_str) & 
    (df_raw['ano-mes'] <= data_fim_str)
].copy()

# --- CÁLCULO DINÂMICO DA CURVA ABC (CORRIGIDO) ---
df_abc_calc = df_filtrado.groupby('Produto')[coluna_analise].sum().reset_index()
df_abc_calc = df_abc_calc.sort_values(by=coluna_analise, ascending=False).reset_index(drop=True)
total_geral = df_abc_calc[coluna_analise].sum()

if total_geral > 0:
    df_abc_calc['Percentual'] = df_abc_calc[coluna_analise] / total_geral
    df_abc_calc['Acumulado'] = df_abc_calc['Percentual'].cumsum()
    
    # Pega o percentual anterior para verificar a transição de faixa
    df_abc_calc['Acumulado_Anterior'] = df_abc_calc['Acumulado'].shift(1, fill_value=0)
    
    def classificar_abc_ajustado(row):
        # Se o item (ou os itens anteriores) estão dentro dos 30%
        # ou se é o primeiro item e ele ultrapassou os 30%
        if row['Acumulado_Anterior'] < 0.30:
            return 'Classe A'
        elif row['Acumulado_Anterior'] < 0.70:
            return 'Classe B'
        else:
            return 'Classe C'
            
    df_abc_calc['Classe'] = df_abc_calc.apply(classificar_abc_ajustado, axis=1)
else:
    df_abc_calc['Classe'] = 'Classe C'

mapeamento_classes = dict(zip(df_abc_calc['Produto'], df_abc_calc['Classe']))
df_filtrado['Classe'] = df_filtrado['Produto'].map(mapeamento_classes)

# --- CONFIGURAÇÃO DAS ABAS ---
aba_intro, aba_classe, aba_med = st.tabs([
    "📂 INTRODUÇÃO", 
    "📊 CLASSE DE MEDICAMENTOS", 
    "📈 MEDICAMENTO INDIVIDUAL"
])

# ================= ABA 1: INTRODUÇÃO =================
with aba_intro:
    st.markdown("""
    Este painel interativo foi desenvolvido para subsidiar as análises e decisões da **Comissão de Assistência Farmacêutica**, 
    consolidando dados de movimentação e consumo de medicamentos na rede municipal. A ferramenta transforma registros de 
    distribuição em indicadores visuais e dinâmicos, garantindo maior agilidade no planejamento e na governança dos recursos de saúde.
    """)
    
    st.markdown("### 📅 Período de Análise")
    st.markdown(f"O banco de dados abrange a série histórica selecionada de **{data_inicio_str}** até **{data_fim_str}**.")
    
    st.markdown("### O que você pode analisar aqui:")
    st.markdown("""
    * **Consumo Mensal:** Acompanhe o histórico de distribuição de medicamentos, alternando entre a soma total acumulada ou a média mensal do período selecionado.
    * **Impacto Financeiro:** Visualize o valor total (em R$) dos medicamentos enviados para a rede, permitindo o acompanhamento orçamentário detalhado.
    * **Filtros Personalizados:** Utilize os seletores de período e categorias na barra lateral para segmentar as informações de acordo com a demanda da sua análise.
    """)
    
    st.markdown("### 📊 Classificação Dinâmica (Curva ABC)")
    st.markdown("""
    Para apoiar a tomada de decisões, o painel aplica a metodologia da **Curva ABC** de forma dinâmica sobre os dados consolidados. 
    O sistema ordena os medicamentos em ordem decrescente de relevância e os classifica de acordo com a sua representatividade no impacto total do período filtrado:
    
    * **Classe A (Alto Impacto):** Medicamentos cujas saídas ou custos acumulados respondem por até **30%** do total geral movimentado pela assistência farmacêutica.
    * **Classe B (Médio Impacto):** Medicamentos que, somados aos anteriores, compõem a faixa intermediária de consumo, representando os **40%** seguintes do impacto total.
    * **Classe C (Baixo Impacto):** Medicamentos restantes que apresentam menor volume de movimentação ou menor peso financeiro, equivalentes aos **30% finais** do total acumulado.
    """)

# ================= ABA 2: VISÃO POR CLASSE DE MEDICAMENTOS =================
with aba_classe:
    st.markdown("<h3 style='background-color: #e2e8f0; padding: 8px; text-align: center;'>VISÃO POR CLASSE DE MEDICAMENTO</h3>", unsafe_allow_html=True)
    
    classe_selecionada = st.selectbox("Selecione a classe:", ["Classe A", "Classe B", "Classe C"])
    
    df_classe = df_filtrado[df_filtrado['Classe'] == classe_selecionada]
    
    if df_classe.empty:
        st.warning(f"Sem movimentações para a {classe_selecionada} no período selecionado.")
    else:
        if metodo_analise == "Consumo médio":
            df_top_med = df_classe.groupby('Produto')[coluna_analise].mean().reset_index()
            titulo_grafico_1 = f"Top Medicamentos ({classe_selecionada}) - Média Mensal"
        else:
            df_top_med = df_classe.groupby('Produto')[coluna_analise].sum().reset_index()
            titulo_grafico_1 = f"Top Medicamentos ({classe_selecionada}) - Total Acumulado"
            
        df_top_10 = df_top_med.sort_values(by=coluna_analise, ascending=False).head(10).copy()
        
        df_top_10['Valor_Formatado'] = df_top_10[coluna_analise].apply(lambda x: formatar_br(x, e_financeiro))
        
        fig_barras = px.bar(
            df_top_10,
            x=coluna_analise,
            y='Produto',
            orientation='h',
            text='Valor_Formatado',
            title=titulo_grafico_1,
            labels={coluna_analise: f"{ref_opcao}", 'Produto': 'Medicamento'},
            color_discrete_sequence=['#2e7d32']
        )
        fig_barras.update_traces(textposition='auto')
        fig_barras.update_layout(
            yaxis={'categoryorder': 'total ascending'}, 
            height=450,
            separators=',.'
        )
        st.plotly_chart(fig_barras, use_container_width=True)
        
        df_serie_classe = df_classe[df_classe['Produto'].isin(df_top_10['Produto'])]
        df_serie_agrupada = df_serie_classe.groupby(['ano-mes', 'Produto'])[coluna_analise].sum().reset_index()
        
        fig_linha = px.line(
            df_serie_agrupada,
            x='ano-mes',
            y=coluna_analise,
            color='Produto',
            title=f"Série Mensal de Saídas dos Principais Medicamentos da {classe_selecionada}",
            labels={'ano-mes': 'Período (Ano-Mês)', coluna_analise: f"{ref_opcao}"},
            markers=True
        )
        fig_linha.update_layout(
            height=450, 
            separators=',.',
            legend=dict(orientation="h", yanchor="bottom", y=-0.6, xanchor="left", x=0)
        )
        st.plotly_chart(fig_linha, use_container_width=True)

# ================= ABA 3: VISÃO POR MEDICAMENTO INDIVIDUAL =================
with aba_med:
    st.markdown("<h3 style='background-color: #e2e8f0; padding: 8px; text-align: center;'>VISÃO POR MEDICAMENTO INDIVIDUAL</h3>", unsafe_allow_html=True)
    
    lista_medicamentos = sorted(df_filtrado['Produto'].unique())
    med_selecionado = st.selectbox("Selecione o medicamento:", lista_medicamentos)
    
    df_u_med = df_filtrado[df_filtrado['Produto'] == med_selecionado]
    
    if df_u_med.empty:
        st.warning("Nenhum dado encontrado para o medicamento selecionado no período.")
    else:
        total_acumulado_med = df_u_med[coluna_analise].sum()
        media_mensal_med = df_u_med[coluna_analise].mean()
        classe_atual_med = df_u_med['Classe'].iloc[0] if 'Classe' in df_u_med.columns else "N/A"
        
        col_metrica, col_grafico_linha = st.columns([1, 2])
        
        with col_metrica:
            st.markdown("#### Meta & Indicadores")
            valor_exibido = total_acumulado_med if metodo_analise == "Acumulado do período" else media_mensal_med
            label_exibida = "Total Acumulado" if metodo_analise == "Acumulado do período" else "Consumo Médio Mensal"
            
            st.metric(
                label=f"{label_exibida} ({ref_opcao})",
                value=formatar_br(valor_exibido, e_financeiro)
            )
            
            st.markdown(f"**Classificação Atual:** `{classe_atual_med}`")
            st.caption("A classificação muda dinamicamente dependendo do intervalo de tempo escolhido na barra lateral.")
            
        with col_grafico_linha:
            df_serie_med = df_u_med.sort_values(by='ano-mes')
            
            fig_linha_med = px.line(
                df_serie_med,
                x='ano-mes',
                y=coluna_analise,
                title=f"Série Histórica: {med_selecionado}",
                labels={'ano-mes': 'Meses', coluna_analise: f"{ref_opcao}"},
                markers=True,
                color_discrete_sequence=['#0288d1']
            )
            fig_linha_med.update_layout(height=350, separators=',.')
            st.plotly_chart(fig_linha_med, use_container_width=True)
