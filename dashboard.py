import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# --- Configurações Iniciais ---
pio.renderers.default = "svg"
st.set_page_config(layout="wide")

# --- Funções de Carregamento e Processamento de Dados ---
@st.cache_data
def load_and_preprocess_data():
    """Carrega, trata e retorna o DataFrame."""
    df = pd.read_csv("supermarket_sales.csv", sep=";", decimal=",")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Month"] = df["Date"].apply(lambda x: str(x.year) + "-" + str(x.month))

    # Renomeando as colunas para português
    df.rename(columns={
        "Invoice ID": "ID da Fatura",
        "Branch": "Filial",
        "City": "Cidade",
        "Customer type": "Tipo de Cliente",
        "Gender": "Gênero",
        "Product line": "Linha de Produto",
        "Unit price": "Preço Unitário",
        "Quantity": "Quantidade",
        "Tax 5%": "Imposto 5%",
        "Total": "Total",
        "Date": "Data",
        "Time": "Hora",
        "Payment": "Pagamento",
        "cogs": "CMV",
        "gross margin percentage": "Margem Bruta %",
        "gross income": "Lucro Bruto",
        "Rating": "Avaliação",
        "Month": "Mês"
    }, inplace=True)

    # Traduzindo as formas de pagamento
    df["Pagamento"].replace({
        "Ewallet": "Carteira Digital",
        "Credit card": "Cartão de Crédito",
        "Cash": "Dinheiro"
    }, inplace=True)

    return df

@st.cache_data
def filter_dataframe(df, month, city, gender, customer_type):
    """Filtra o DataFrame com base nos seletores da barra lateral."""
    df_filtered = df[df["Mês"] == month]
    if city:
        df_filtered = df_filtered[df_filtered["Cidade"].isin(city)]
    if gender:
        df_filtered = df_filtered[df_filtered["Gênero"].isin(gender)]
    if customer_type:
        df_filtered = df_filtered[df_filtered["Tipo de Cliente"].isin(
            customer_type)]
    return df_filtered


# --- Carregar Dados ---
df = load_and_preprocess_data()

# --- Layout do Dashboard ---
st.markdown("<h1><span style='color:#F63366'>Dashboard de Vendas do Supermercado📈</span></h1>",
            unsafe_allow_html=True)
st.markdown("""
## Análise de Vendas

Este painel apresenta uma análise detalhada das vendas do supermercado, permitindo visualizar o faturamento diário, por tipo de produto, por filial e por forma de pagamento. Além disso, também é possível avaliar a satisfação dos clientes através das avaliações dadas às filiais.
""")
st.markdown("---")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("Configurações")
month = st.sidebar.selectbox("Mês", df["Mês"].unique())
city = st.sidebar.multiselect(
    "Filial", df["Cidade"].unique(), default=df["Cidade"].unique())
gender = st.sidebar.multiselect("Gênero", df["Gênero"].unique())
customer_type = st.sidebar.multiselect(
    "Tipo de Cliente", df["Tipo de Cliente"].unique())

df_filtered = filter_dataframe(df, month, city, gender, customer_type)

# --- KPIs ---
st.subheader("Indicadores de Desempenho")
col1, col2, col3 = st.columns(3)
faturamento_total = df_filtered["Total"].sum()
quantidade_vendas = df_filtered["ID da Fatura"].count()
lucro_bruto = df_filtered["Lucro Bruto"].sum()
col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
col2.metric("Quantidade de Vendas", quantidade_vendas)
col3.metric("Lucro Bruto", f"R$ {lucro_bruto:,.2f}")

st.markdown("---")

col_prod1, col_prod2 = st.columns(2)
produto_mais_vendido = df_filtered.groupby("Linha de Produto")[
    "Quantidade"].sum().idxmax()
produto_mais_lucrativo = df_filtered.groupby(
    "Linha de Produto")["Lucro Bruto"].sum().idxmax()
col_prod1.metric("Produto Mais Vendido", produto_mais_vendido)
col_prod2.metric("Produto Mais Lucrativo", produto_mais_lucrativo)

st.markdown("---")

# --- Gráficos (Seções por Tema) ---

# Seção 1: Faturamento e Desempenho
st.subheader("Análise de Faturamento e Desempenho")
col_fat1, col_fat2 = st.columns(2)

# Gráfico 1: Faturamento por Dia
fig_date = px.bar(
    df_filtered,
    x="Data",
    y="Total",
    color="Cidade",
    title="Faturamento por Dia",
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_date.update_layout(
    xaxis_title="Data",
    yaxis_title="Faturamento (R$)",
    barmode="group",
    title_font_size=24, title_font_color="#333333"
)
fig_date.update_traces(marker_line_color='black',
                       marker_line_width=1.0, opacity=1.0)
col_fat1.plotly_chart(fig_date, use_container_width=True)

# Gráfico 2: Faturamento por Filial
city_total = df_filtered.groupby("Cidade")[["Total"]].sum().reset_index()
fig_city = px.bar(
    city_total,
    x="Cidade",
    y="Total",
    title="Faturamento por Filial",
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_city.update_layout(
    title_font_size=24, title_font_color="#333333"
)
col_fat2.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")

# Seção 2: Análise por Categoria e Pagamento
st.subheader("Análise por Categoria e Pagamento")
col_cat1, col_cat2 = st.columns(2)

# Gráfico 3: Faturamento por Tipo de Produto
fig_prod = px.bar(
    df_filtered,
    x="Total",
    y="Linha de Produto",
    color="Cidade",
    title="Faturamento por Tipo de Produto",
    orientation="h",
    color_discrete_sequence=px.colors.qualitative.Plotly
)

fig_prod.update_layout(
    xaxis_title="Faturamento (R$)",
    yaxis_title="Linha de Produto",
    barmode="group",
    title_font_size=24, title_font_color="#333333"
)
col_cat1.plotly_chart(fig_prod, use_container_width=True)

# Gráfico 4: Faturamento por Tipo de Pagamento
fig_kind = px.pie(
    df_filtered,
    values="Total",
    names="Pagamento",
    title="Faturamento por Tipo de Pagamento",
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_kind.update_traces(textposition='inside', textinfo='percent+label')
fig_kind.update_layout(
    title_font_size=24, title_font_color="#333333"
)
col_cat2.plotly_chart(fig_kind, use_container_width=True)

st.markdown("---")

# Seção 3: Satisfação do Cliente
# Gráfico 5: Avaliação das Filiais
st.subheader("Satisfação do Cliente")
col_rat, _ = st.columns([1, 1])

fig_rating_df = df_filtered.groupby(
    "Cidade")[["Avaliação"]].mean().reset_index()
fig_rating = px.bar(
    fig_rating_df,
    y="Avaliação",
    x="Cidade",
    title="Avaliação das Filiais",
    color_discrete_sequence=px.colors.qualitative.Plotly
)
fig_rating.update_layout(
    xaxis_title="Filial",
    yaxis_title="Avaliação Média",
    title_font_size=24, title_font_color="#333333"
)
col_rat.plotly_chart(fig_rating, use_container_width=True)

st.markdown("""
### Observações:
- O painel oferece uma visão completa do desempenho de vendas, com **indicadores-chave (KPIs)** no topo para um resumo rápido.
- Os **gráficos de faturamento** permitem analisar o desempenho diário, por filial, por categoria de produto e por forma de pagamento.
- Os indicadores de **produto mais vendido** e **mais lucrativo** destacam os itens que impulsionam o volume de vendas e a rentabilidade do negócio.
- Utilize os **filtros da barra lateral** para segmentar a análise por mês, filial, gênero e tipo de cliente, obtendo insights mais específicos.
- O gráfico de **avaliação das filiais** auxilia a entender a satisfação geral dos clientes.
""")