#%%
import locale
import streamlit as st
import pandas as pd
import plotly.express as px
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
df_cobranca.rename(columns={'Data':'data_hora'}, inplace=True)
df_cobranca['data'] = df_cobranca['data_hora'].dt.date
df_cobranca['hora'] = df_cobranca['data_hora'].dt.time
df_cobranca['hora_inteira'] = df_cobranca['data_hora'].dt.hour
df_cobranca['hora_inteira'] = df_cobranca['hora_inteira'].astype(str)
df_cobranca['Nome Operador Abreviado'] = df_cobranca['Nome Operador'].apply(abreviar_nome)
df_cobranca['Dia da Semana'] = df_cobranca['data_hora'].dt.strftime('%A')
df_cobranca['MesAno'] = df_cobranca['data_hora'].dt.strftime('%B/%Y').str.capitalize()
meses_disponiveis = df_cobranca['MesAno'].sort_values().unique().tolist()

df_cobranca_tratada = df_cobranca.copy()
#%%
#df_cobranca['MesAno'].unique()
#%%funcoes de grafico
def graf_interacoes(coluna, mes_ano=None):
    if mes_ano == None:
        df = df_cobranca_tratada.groupby(coluna).size().reset_index(name='Quantidade')
    else:
        df = df_cobranca_tratada.query('MesAno == @mes_ano').groupby(coluna).size().reset_index(name='Quantidade')
    return px.bar(
                    df.sort_values('Quantidade',ascending=False),
                    y = 'Quantidade',
                    x = coluna,
                    text_auto = True,
                    title = f'Interações por {coluna}'
                )


#%%
df_interacoes_colab = df_cobranca_tratada.groupby('Nome Operador Abreviado').size().reset_index(name='Quantidade')
df_interacoes_dia_sem = df_cobranca_tratada.groupby('Dia da Semana').size().reset_index(name='Quantidade')
df_interacoes_hora = df_cobranca_tratada.groupby('hora_inteira').size().reset_index(name='Quantidade')
#%%

#%% Graficos
fig_interacoes_dia_sem = px.bar(df_interacoes_dia_sem.sort_values('Quantidade',ascending=False),
                            y = 'Quantidade',
                            x = 'Dia da Semana',
                            text_auto = True,
                            title = 'Interações por Dia da Semana')

fig_interacoes_hora = px.bar(df_interacoes_hora.sort_values('Quantidade',ascending=True),
                            y = 'Quantidade',
                            x = 'hora_inteira',
                            text_auto = True,
                            title = 'Interações por Hora do Dia')

fig_interacoes_cob = px.bar(df_interacoes_colab.sort_values('Quantidade',ascending=True),
                            y = 'Nome Operador Abreviado',
                            x = 'Quantidade',
                            text_auto = True,
                            title = 'Interações por Colaborador')
#df_cobranca.head()

#%%



# %% elementos graficos
st.title('Painel de Acompanhamento de Interações da Cobrança')
st.metric("Total Interações",df_cobranca_tratada.shape[0])

coluna1, coluna2, coluna3 = st.columns(3)
with coluna1:
    st.plotly_chart(fig_interacoes_cob)
with coluna2:
    st.plotly_chart(fig_interacoes_dia_sem)
with coluna3:
    st.plotly_chart(fig_interacoes_hora)

mes_selecionado = st.segmented_control(
                                        "Selecione o mês:",
                                        options=meses_disponiveis,
                                        format_func=lambda x: x  # opcional se já estiver formatado
                                      )
st.write(f'O mes selecionado é {mes_selecionado}')

st.plotly_chart(graf_interacoes('Nome Operador Abreviado',mes_selecionado))




# %%
