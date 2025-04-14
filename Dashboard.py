#%%
import locale
import streamlit as st
import pandas as pd
import plotly.express as px
from babel.dates import format_datetime
from datetime import datetime

st.set_page_config(layout="wide")
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')  # fallback para o padrão do sistema
# %%
# %%
bd = st.secrets['data']['banco']
df_raw = pd.read_excel(bd,None)
df_cobranca_raw = df_raw['Acomp Cobrança']
#%% funções
def abreviar_nome(nome):
    partes = nome.strip().split()
    if len(partes) == 1:
        return partes[0]  # nome único
    return f"{partes[0]} {partes[-1]}"  # primeiro e último
#%% tratamentos
df_cobranca = df_cobranca_raw.copy()
df_cobranca.rename(columns={'Data':'data_hora', 'Descrição':'Tipo Interação'}, inplace=True)
df_cobranca['data'] = df_cobranca['data_hora'].dt.date
df_cobranca['hora'] = df_cobranca['data_hora'].dt.time
df_cobranca['hora_inteira'] = df_cobranca['data_hora'].dt.hour
df_cobranca['hora_inteira'] = df_cobranca['hora_inteira'].astype(str).str.zfill(2) + ':00'
df_cobranca['Nome Operador Abreviado'] = df_cobranca['Nome Operador'].apply(abreviar_nome)
# df_cobranca['Dia da Semana'] = df_cobranca['data_hora'].dt.strftime('%A')
# df_cobranca['MesAno'] = df_cobranca['data_hora'].dt.strftime('%B/%Y').str.capitalize()
df_cobranca['Dia da Semana'] = df_cobranca['data_hora'].apply(lambda x: format_datetime(x, 'EEEE', locale='pt_BR'))
df_cobranca['MesAno'] = df_cobranca['data_hora'].apply(lambda x: format_datetime(x, "MMMM/yyyy", locale='pt_BR').capitalize())
df_cobranca['MesAno_dt'] = df_cobranca['data_hora'].dt.to_period('M').dt.to_timestamp()
df_cobranca['Mes e Ano'] = df_cobranca['data_hora'].dt.strftime('%m/%Y')
df_meses = df_cobranca[['MesAno', 'MesAno_dt']].drop_duplicates().sort_values('MesAno_dt')
meses_disponiveis = df_meses['MesAno'].tolist()
df_cobranca_tratada = df_cobranca.copy()
#%%
#df_cobranca_tratada[df_cobranca_tratada['MesAno'] == 'Abril/2025']
#df_cobranca['hora_inteira'].str.zfill(2) + ':00'
df_cobranca.groupby('Contrato').size().reset_index(name='Quantidade').sort_values('Quantidade', ascending=False).head(15)
#%%funcoes de grafico
def graf_interacoes(coluna, mes_ano=None, operador=None, data=None, ordena_cat=False, n_top=None, tp_filtro=None):
    df = df_cobranca_tratada.copy()

    # Aplica filtro conforme tipo selecionado
    if tp_filtro == "Mês" and mes_ano and mes_ano != "Todos":
        df = df[df['MesAno'] == mes_ano]

    elif tp_filtro == "Data específica" and data:
        df = df[df['data'] == data]

    # Filtro por operador, se houver
    if operador:
        df = df[df['Nome Operador Abreviado'] == operador]

    # Agrupamento
    df = df.groupby(coluna).size().reset_index(name='Quantidade')

    # TOP N, se necessário
    if n_top is not None:
        df = df.head(n_top)

    txt_top = '' if n_top is None else f'TOP {n_top} '

    # Gráfico
    return px.bar(
        df.sort_values(coluna, ascending=True) if ordena_cat else df.sort_values('Quantidade', ascending=False),
        y='Quantidade',
        x=coluna,
        text_auto=True,
        title=f'{txt_top}Interações por {coluna}'
    )

# def graf_interacoes(coluna, mes_ano=None, operador = None, ordena_cat = False,n_top = None):
#     df = df_cobranca_tratada.copy()
#     if mes_ano:
#         df = df_cobranca_tratada[df_cobranca_tratada['MesAno'] == mes_ano].groupby(coluna).size().reset_index(name='Quantidade')
#     if operador:
#         df = df_cobranca_tratada[df_cobranca_tratada['Nome Operador Abreviado'] == operador].groupby(coluna).size().reset_index(name='Quantidade')
#     if mes_ano == None and operador == None:
#         df = df_cobranca_tratada.groupby(coluna).size().reset_index(name='Quantidade')
#     if n_top == None:
#         pass
#     else:
#         df = df.head(n_top)
#     txt_top = '' if n_top == None else f'TOP {n_top} '
#     return px.bar(
#                     df.sort_values(coluna,ascending=True) if ordena_cat else df.sort_values('Quantidade',ascending=False),
#                     y = 'Quantidade',
#                     x = coluna,
#                     text_auto = True,
#                     title = f'{txt_top}Interações por {coluna}'
#                 )
#%%

# #%%
# df_interacoes_colab = df_cobranca_tratada.groupby('Nome Operador Abreviado').size().reset_index(name='Quantidade')
# df_interacoes_dia_sem = df_cobranca_tratada.groupby('Dia da Semana').size().reset_index(name='Quantidade')
# df_interacoes_hora = df_cobranca_tratada.groupby('hora_inteira').size().reset_index(name='Quantidade')
# #%%

# #%% Graficos
# fig_interacoes_dia_sem = px.bar(df_interacoes_dia_sem.sort_values('Quantidade',ascending=False),
#                             y = 'Quantidade',
#                             x = 'Dia da Semana',
#                             text_auto = True,
#                             title = 'Interações por Dia da Semana')

# fig_interacoes_hora = px.bar(df_interacoes_hora.sort_values('Quantidade',ascending=True),
#                             y = 'Quantidade',
#                             x = 'hora_inteira',
#                             text_auto = True,
#                             title = 'Interações por Hora do Dia')

# fig_interacoes_cob = px.bar(df_interacoes_colab.sort_values('Quantidade',ascending=True),
#                             y = 'Nome Operador Abreviado',
#                             x = 'Quantidade',
#                             text_auto = True,
#                             title = 'Interações por Colaborador')
#df_cobranca.head()

#%%

#%%
operadores_disponiveis = sorted(df_cobranca_tratada['Nome Operador Abreviado'].unique())

#%% autenticação
def autenticar_usuario():
    st.markdown("### 🔒 Login obrigatório")
    
    # Texto explicativo
    st.info("Em caso de dúvidas, procurar por **Kely Bemfica**.")

    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            usuarios_validos = st.secrets['login']
            if usuario in usuarios_validos and senha == usuarios_validos[usuario]:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = usuario
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    # # Rodapé com LinkedIn
    # st.markdown(
    #     """<hr style="margin-top: 2rem; margin-bottom: 0.5rem">
    #     <div style='text-align: center; font-size: 0.9em; color: gray;'>
    #         Desenvolvido por <a href='https://www.linkedin.com/in/douglascdsantos' target='_blank'>Douglas Santos</a>
    #     </div>
    #     """, unsafe_allow_html=True
    # )

# Checa se já está logado
if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
    autenticar_usuario()
    st.stop()

# %% elementos graficos
#st.title('Painel de Acompanhamento de Interações da Cobrança')
col1, col2 = st.columns([0.9, 0.1])  # você pode ajustar os tamanhos conforme necessário
with col1:
    st.title("Painel de Acompanhamento de Interações da Cobrança")
    st.write("Supervisor da área Ayslan Santos")

with col2:
    st.image("https://www.omni.com.br/wp-content/themes/omni/assets/images/logos/logo-omni.svg?v=08082023202447", width=100)

# st.metric("Total Interações 2025",df_cobranca_tratada.shape[0])
# Pega o mês atual com base na data de hoje
# mes_atual = pd.to_datetime(datetime.today().strftime("%Y-%m"))

# # Separa os dados
# df_mes_atual = df_cobranca_tratada[df_cobranca_tratada['MesAno'] == mes_atual]
# df_meses_fechados = df_cobranca_tratada[df_cobranca_tratada['MesAno'] < mes_atual]

# # Calcula a média de registros (interações) por mês
# media_fechados = df_meses_fechados.groupby('MesAno').size().mean()
# total_mes_atual = df_mes_atual.shape[0]

# # Formata os números
# media_fechados_fmt = f"{int(media_fechados):,}".replace(",", ".")
# total_mes_atual_fmt = f"{total_mes_atual:,}".replace(",", ".")
#%%
df_copia = df_cobranca_tratada.copy()
df_copia['data_hora'] = pd.to_datetime(df_copia['data_hora'], errors='coerce')

# Cria uma coluna auxiliar com o primeiro dia do mês
df_copia['MesAno_dt'] = df_copia['data_hora'].dt.to_period("M").dt.to_timestamp()

# Mês atual com base na data de hoje
mes_atual = pd.to_datetime(datetime.today().strftime("%Y-%m-01"))

# Filtra meses fechados e mês atual
df_meses_fechados = df_copia[df_copia['MesAno_dt'] < mes_atual]
df_mes_atual = df_copia[df_copia['MesAno_dt'] == mes_atual]

# Calcula médias
media_fechados = df_meses_fechados.groupby('MesAno_dt').size().mean()
total_mes_atual = df_mes_atual.shape[0]

# Formata números com ponto
media_fechados_fmt = f"{int(media_fechados):,}".replace(",", ".")
total_mes_atual_fmt = f"{total_mes_atual:,}".replace(",", ".")

# Exibe os cards
col0, col1, col2 = st.columns(3)
with col0:
    st.metric("Total Interações 2025", f"{df_cobranca_tratada.shape[0]:,}".replace(",", "."))
with col1:
    st.metric("📊 Média de Interações - Meses Fechados", media_fechados_fmt)

with col2:
    st.metric("📈 Interações - Mês Atual", total_mes_atual_fmt)


st.plotly_chart(graf_interacoes('Mes e Ano', ordena_cat=True),
                use_container_width=True,
                config={'displayModeBar': False,  # Remove a barra superior
                        'staticPlot': True        # Torna o gráfico completamente estático
                        }
                )


coluna1, coluna2, _ = st.columns([1, 2, 0.0001])  # a última é "fantasma" só pra alinhar melhor
with coluna1:
    tipo_filtro = st.radio(
        "🔎 deseja filtrar o período por:",
        ["Mês", "Data específica"],
        horizontal=True
    )

    if tipo_filtro == "Mês":
        meses_opcoes = ["Todos"] + meses_disponiveis  # adiciona a opção "Todos" no início
        mes_selecionado = st.selectbox("Selecione o mês:", meses_opcoes)
        data_especifica = None
    else:
        data_especifica = st.date_input("Selecione uma data específica:")
        mes_selecionado = None
#     mes_selecionado = st.segmented_control(
#                                             "Selecione o mês:",
#                                             options=meses_disponiveis,
#                                             format_func=lambda x: x  # opcional se já estiver formatado
#                                         )
# with coluna2:
#     data_especifica = st.date_input("Selecione uma data (opcional):")   
with coluna2:
    operador_selecionado = st.segmented_control(
                                            "Selecione o Operador:",
                                            options=operadores_disponiveis,
                                            format_func=lambda x: x  # opcional se já estiver formatado
                                        )
st.write(f"O mes selecionado é {mes_selecionado if mes_selecionado is not None else 'Todos'}, a Data é {data_especifica if data_especifica is not None else 'Todos'} e operador é {operador_selecionado if operador_selecionado is not None else 'Todos'}")

coluna1, coluna2, coluna3 = st.columns(3)
with coluna1:
#     st.plotly_chart(fig_interacoes_cob, use_container_width=True, config={
#     'displayModeBar': False,  # Remove a barra superior
#     'staticPlot': True        # Torna o gráfico completamente estático
# })
    st.plotly_chart(graf_interacoes('Nome Operador Abreviado', mes_ano = mes_selecionado, data = data_especifica, tp_filtro= tipo_filtro),
                    use_container_width=True,
                    config={'displayModeBar': False,  # Remove a barra superior
                            'staticPlot': True        # Torna o gráfico completamente estático
                            }
                    )
with coluna2:
#     st.plotly_chart(fig_interacoes_dia_sem, use_container_width=True, config={
#     'displayModeBar': False,  # Remove a barra superior
#     'staticPlot': True        # Torna o gráfico completamente estático
# })
    st.plotly_chart(graf_interacoes('Dia da Semana', mes_ano= mes_selecionado, operador= operador_selecionado, data = data_especifica, tp_filtro= tipo_filtro),
                    use_container_width=True,
                    config={'displayModeBar': False,  # Remove a barra superior
                            'staticPlot': True        # Torna o gráfico completamente estático
                            }
                    )
with coluna3:
#     st.plotly_chart(fig_interacoes_hora, use_container_width=True, config={
#     'displayModeBar': False,  # Remove a barra superior
#     'staticPlot': True        # Torna o gráfico completamente estático
# })
    st.plotly_chart(graf_interacoes('hora_inteira', mes_ano= mes_selecionado, data = data_especifica, operador= operador_selecionado, ordena_cat=True, tp_filtro= tipo_filtro),
                    use_container_width=True,
                    config={'displayModeBar': False,  # Remove a barra superior
                            'staticPlot': True        # Torna o gráfico completamente estático
                            }
                    )
coluna1, coluna2, _ = st.columns([1, 2, 0.0001])  # a última é "fantasma" só pra alinhar melhor

with coluna1:
    df_contrato_filtrado = df_cobranca.copy()

    if tipo_filtro == "Mês" and mes_selecionado and mes_selecionado != "Todos":
        df_contrato_filtrado = df_contrato_filtrado[df_contrato_filtrado['MesAno'] == mes_selecionado]

    if tipo_filtro == "Data específica" and data_especifica:
        df_contrato_filtrado = df_contrato_filtrado[df_contrato_filtrado['data'] == data_especifica]

    if operador_selecionado:
        df_contrato_filtrado = df_contrato_filtrado[df_contrato_filtrado['Nome Operador Abreviado'] == operador_selecionado]

    df_contrato_filtrado = (
        df_contrato_filtrado
        .groupby('Contrato')
        .size()
        .reset_index(name='Quantidade')
        .sort_values('Quantidade', ascending=False)
        .head(15)
        .reset_index(drop=True)
    )

    st.markdown("📋 TOP 15 Contratos com maiores interações")
    st.dataframe(df_contrato_filtrado, use_container_width=True)
    # st.plotly_chart(
    #     graf_interacoes('Contrato', mes_ano= mes_selecionado, operador= operador_selecionado, n_top=15),
    #     use_container_width=True,
    #     config={'displayModeBar': False, 'staticPlot': True}
    # )

with coluna2:
    st.plotly_chart(
        graf_interacoes('Tipo Interação', mes_ano= mes_selecionado, data = data_especifica, operador= operador_selecionado, tp_filtro= tipo_filtro),
        use_container_width=True,
        config={'displayModeBar': False, 'staticPlot': True}
    )

# %%
coluna1, coluna2, _ = st.columns([1, 2, 0.0001])  # a última é "fantasma" só pra alinhar melhor
with coluna1:
    # Campo de filtro de contrato (apenas para a tabela final)
    st.markdown("### 🔍 Filtro por Contrato")
    contrato_filtrado = st.text_input("Digite o número do contrato (opcional):", placeholder="Ex: 1.00333.0000683.24")
with coluna2:
    tp_interacao_selecionado = st.segmented_control(
                                            "Selecione o Tipo de Interação:",
                                            options = sorted(df_cobranca_tratada['Tipo Interação'].unique()),
                                            format_func=lambda x: x  # opcional se já estiver formatado
                                        )
# df_filtrado = df_cobranca_tratada.copy()

# if mes_selecionado:
#     df_filtrado = df_filtrado[df_filtrado['MesAno'] == mes_selecionado]

# if operador_selecionado:
#     df_filtrado = df_filtrado[df_filtrado['Nome Operador Abreviado'] == operador_selecionado]

# if tp_interacao_selecionado:
#     df_filtrado = df_filtrado[df_filtrado['Tipo Interação'] == tp_interacao_selecionado]

# if contrato_filtrado:
#     df_filtrado = df_filtrado[df_filtrado['Contrato'].astype(str).str.contains(contrato_filtrado, case=False)]
df_filtrado = df_cobranca_tratada.copy()

if tipo_filtro == "Mês" and mes_selecionado and mes_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['MesAno'] == mes_selecionado]

if tipo_filtro == "Data específica" and data_especifica:
    df_filtrado = df_filtrado[df_filtrado['data'] == data_especifica]

if operador_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Nome Operador Abreviado'] == operador_selecionado]

if contrato_filtrado:
    df_filtrado = df_filtrado[df_filtrado['Contrato'].str.contains(contrato_filtrado, na=False)]

st.markdown("### 📋 Detalhamento das Interações")
st.dataframe(
    df_filtrado[['data_hora', 'Ocorrência', 'Tipo Interação', 'Cliente', 'Nome', 'Contrato','Contato', 'Cod Operador', 'Nome Operador']],
    use_container_width=True
)
#%%
# %%
# # Rodapé com LinkedIn
# st.markdown(
#     """<hr style="margin-top: 2rem; margin-bottom: 0.5rem">
#     <div style='text-align: center; font-size: 0.9em; color: gray;'>
#         Desenvolvido por <a href='https://www.linkedin.com/in/douglascdsantos' target='_blank'>Douglas Santos</a>
#     </div>
#     """, unsafe_allow_html=True
# )
