#%%
import locale
import streamlit as st
import pandas as pd
import plotly.express as px
from babel.dates import format_datetime
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
df_cobranca['hora_inteira'] = df_cobranca['hora_inteira'].astype(str)
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
#df_cobranca['MesAno'].unique()
#%%funcoes de grafico
def graf_interacoes(coluna, mes_ano=None, operador = None, ordena_cat = False,n_top = None):
    df = df_cobranca_tratada.copy()
    if mes_ano:
        df = df_cobranca_tratada[df_cobranca_tratada['MesAno'] == mes_ano].groupby(coluna).size().reset_index(name='Quantidade')
    if operador:
        df = df_cobranca_tratada[df_cobranca_tratada['Nome Operador Abreviado'] == operador].groupby(coluna).size().reset_index(name='Quantidade')
    # if mes_ano == None and operador == None:
    #     df = df_cobranca_tratada.groupby(coluna).size().reset_index(name='Quantidade')
    # elif mes_ano != None and operador == None:
    #     df = df_cobranca_tratada.query('MesAno == @mes_ano').groupby(coluna).size().reset_index(name='Quantidade')
    # elif mes_ano == None and operador != None:
    #     df = df_cobranca_tratada.query('`Nome Operador Abreviado` == @operador').groupby(coluna).size().reset_index(name='Quantidade')
    # elif mes_ano != None and operador != None:
    #     df = df_cobranca_tratada.query('MesAno == @mes_ano and `Nome Operador Abreviado` == @operador').groupby(coluna).size().reset_index(name='Quantidade')
    # # else:
    # #     df = df_cobranca_tratada.query('MesAno == @mes_ano').groupby(coluna).size().reset_index(name='Quantidade')
    if mes_ano == None and operador == None:
        df = df_cobranca_tratada.groupby(coluna).size().reset_index(name='Quantidade')
    if n_top == None:
        pass
    else:
        df = df.head(n_top)
    txt_top = '' if n_top == None else f'TOP {n_top} '
    return px.bar(
                    df.sort_values(coluna,ascending=True) if ordena_cat else df.sort_values('Quantidade',ascending=False),
                    y = 'Quantidade',
                    x = coluna,
                    text_auto = True,
                    title = f'{txt_top}Interações por {coluna}'
                )
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

operadores_disponiveis = sorted(df_cobranca_tratada['Nome Operador Abreviado'].unique())

# %% elementos graficos
st.title('Painel de Acompanhamento de Interações da Cobrança')
st.metric("Total Interações",df_cobranca_tratada.shape[0])
st.plotly_chart(graf_interacoes('Mes e Ano', ordena_cat=True),
                use_container_width=True,
                config={'displayModeBar': False,  # Remove a barra superior
                        'staticPlot': True        # Torna o gráfico completamente estático
                        }
                )
coluna1, coluna2, _ = st.columns([1, 2, 0.0001])  # a última é "fantasma" só pra alinhar melhor
with coluna1:
    mes_selecionado = st.segmented_control(
                                            "Selecione o mês:",
                                            options=meses_disponiveis,
                                            format_func=lambda x: x  # opcional se já estiver formatado
                                        )
with coluna2:
    operador_selecionado = st.segmented_control(
                                            "Selecione o Operador:",
                                            options=operadores_disponiveis,
                                            format_func=lambda x: x  # opcional se já estiver formatado
                                        )
st.write(f"O mes selecionado é {mes_selecionado if mes_selecionado is not None else 'Todos'} e operador é {operador_selecionado if operador_selecionado is not None else 'Todos'}")

coluna1, coluna2, coluna3 = st.columns(3)
with coluna1:
#     st.plotly_chart(fig_interacoes_cob, use_container_width=True, config={
#     'displayModeBar': False,  # Remove a barra superior
#     'staticPlot': True        # Torna o gráfico completamente estático
# })
    st.plotly_chart(graf_interacoes('Nome Operador Abreviado', mes_selecionado),
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
    st.plotly_chart(graf_interacoes('Dia da Semana',mes_selecionado, operador_selecionado),
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
    st.plotly_chart(graf_interacoes('hora_inteira',mes_selecionado, operador_selecionado),
                    use_container_width=True,
                    config={'displayModeBar': False,  # Remove a barra superior
                            'staticPlot': True        # Torna o gráfico completamente estático
                            }
                    )
coluna1, coluna2, _ = st.columns([1, 2, 0.0001])  # a última é "fantasma" só pra alinhar melhor

with coluna1:
    st.plotly_chart(
        graf_interacoes('Contrato', mes_selecionado, operador_selecionado, n_top=15),
        use_container_width=True,
        config={'displayModeBar': False, 'staticPlot': True}
    )

with coluna2:
    st.plotly_chart(
        graf_interacoes('Tipo Interação', mes_ano= mes_selecionado, operador= operador_selecionado),
        use_container_width=True,
        config={'displayModeBar': False, 'staticPlot': True}
    )

# %%

df_filtrado = df_cobranca_tratada.copy()

if mes_selecionado:
    df_filtrado = df_filtrado[df_filtrado['MesAno'] == mes_selecionado]

if operador_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Nome Operador Abreviado'] == operador_selecionado]

st.markdown("### 📋 Detalhamento das Interações")
st.dataframe(df_filtrado, use_container_width=True)
