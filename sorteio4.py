
import sqlite3
import streamlit as st
import pandas as pd
import random
import time

# Conexão com o banco de dados SQLite
def init_db():
    conn = sqlite3.connect('cadastro04.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            numero TEXT NOT NULL
        )
    ''')
    c.execute('CREATE TABLE IF NOT EXISTS sorteio (id INTEGER PRIMARY KEY AUTOINCREMENT, vencedor TEXT, numero TEXT)')
    conn.commit()
    conn.close()

# Função para adicionar um novo usuário
def add_usuario(nome, numero):
    conn = sqlite3.connect('cadastro04.db')
    c = conn.cursor()
    c.execute('INSERT INTO usuarios (nome, numero) VALUES (?, ?)', (nome, numero))
    conn.commit()
    conn.close()

# Função para obter todos os usuários
def get_usuarios():
    conn = sqlite3.connect('cadastro04.db')
    df = pd.read_sql_query('SELECT * FROM usuarios', conn)
    conn.close()
    return df

# Função para realizar o sorteio
def realizar_sorteio(usuarios):
    vencedores = random.sample(usuarios.index.tolist(), 2)
    resultado = []

    for v in vencedores:
        vencedor = usuarios.iloc[v]
        resultado.append(vencedor)

        conn = sqlite3.connect('cadastro04.db')
        c = conn.cursor()
        c.execute('INSERT INTO sorteio (vencedor, numero) VALUES (?, ?)', (vencedor['nome'], vencedor['numero']))
        conn.commit()
        conn.close()

    return resultado

# Função para excluir o histórico de sorteios
def excluir_historico():
    conn = sqlite3.connect('cadastro04.db')
    c = conn.cursor()
    c.execute('DELETE FROM sorteio')
    conn.commit()
    conn.close()

# Função para excluir todos os usuários
def excluir_usuarios():
    conn = sqlite3.connect('cadastro04.db')
    c = conn.cursor()
    c.execute('DELETE FROM usuarios')
    conn.commit()
    conn.close()

# Função para mostrar um contador regressivo em uma única linha
def contador_regressivo(segundos):
    contador_placeholder = st.empty()  # Cria um espaço vazio para o contador
    for i in range(segundos, 0, -1):
        contador_placeholder.write(f"Contagem regressiva: {i} segundos")
        time.sleep(1)
    contador_placeholder.write("Sorteio iniciado!")  # Mensagem após a contagem

# Inicializa o banco de dados
init_db()

# Chave PIX (exemplo fictício)
pix_key = "4b1229d4-ea65-4dbd-a3e7-b1ca62569072"
senha_cadastro = "1286"

# Interface do Streamlit
st.title("Sorteio do PIX")
st.subheader("O bilhete para esta rodada custa apenas 10 reais\nPrêmio: 25 reais.")
st.write("Você só estará concorrendo\nse tiver feito o pagamento do bilhete.")
st.write("Só assim poderá receber o seu prêmio.")
st.write(f"Para se cadastrar, pague o seu bilhete nesta chave PIX: {pix_key}")

# Cadastro de usuário
senha = st.text_input("Digite a senha para liberar o cadastro:", type="password")
nome = st.text_input("Digite seu nome:")
if st.button("Cadastrar"):
    if senha == senha_cadastro and nome:
        # Gera um número de 3 dígitos
        numero = f"{random.randint(0, 999):03d}"
        add_usuario(nome, numero)
        st.success(f"Cadastro realizado com sucesso! O número do seu bilhete é: {numero}")

        # Verifica quantos usuários estão cadastrados
        usuarios = get_usuarios()
        total_cadastrados = len(usuarios)
        faltando = max(0, 10 - total_cadastrados)

        st.write(f"Total de cadastrados: {total_cadastrados}. Faltam {faltando} para o sorteio.")
        
        # Realiza o sorteio se houver 10 cadastrados
        if total_cadastrados >= 10:
            st.write("Iniciando o sorteio...")
            contador_regressivo(10)  # Chama a função do contador
            vencedores = realizar_sorteio(usuarios)
            vencedores_info = ", ".join([f"{v['nome']} (número: {v['numero']})" for v in vencedores])
            st.success(f"Os ganhadores foram: {vencedores_info}.")

    elif senha != senha_cadastro:
        st.error("Senha incorreta! Tente novamente.")
    else:
        st.error("Por favor, insira um nome válido.")

# Mostra os usuários cadastrados em tabela
if st.button("Ver Usuários Cadastrados"):
    usuarios = get_usuarios()
    if not usuarios.empty:
        usuarios_formatados = usuarios.copy()
        usuarios_formatados['info'] = usuarios_formatados.apply(lambda row: f"{row['nome']} (bilhete: {row['numero']})", axis=1)
        st.table(usuarios_formatados[['info']])
    else:
        st.write("Nenhum usuário cadastrado.")

# Mostrar histórico de sorteios em tabela
if st.button("Ver Histórico de Sorteios"):
    conn = sqlite3.connect('cadastro04.db')
    sorteios = pd.read_sql_query('SELECT * FROM sorteio', conn)
    conn.close()
    if not sorteios.empty:
        sorteios_formatados = sorteios.copy()
        
        # Agrupar por sorteios
        vencedores_formatados = sorteios_formatados.apply(
            lambda row: f"O primeiro ganhador foi {row['vencedor']}, com o bilhete {row['numero']}." if row.name == 0 
            else f"E o segundo ganhador foi {row['vencedor']}, com o bilhete {row['numero']}.", axis=1
        )
        
        st.table(vencedores_formatados)
    else:
        st.write("Nenhum sorteio realizado ainda.")

# Excluir histórico de sorteios
senha_exclusao_historico = st.text_input("Digite a senha para excluir o histórico de sorteios:", type="password")
if st.button("Excluir Histórico"):
    if senha_exclusao_historico == "1285":
        excluir_historico()
        st.success("Histórico de sorteios excluído com sucesso!")
    else:
        st.error("Senha incorreta! Não foi possível excluir o histórico.")

# Excluir todos os usuários
senha_exclusao_usuarios = st.text_input("Digite a senha para excluir todos os usuários:", type="password")
if st.button("Excluir Usuários"):
    if senha_exclusao_usuarios == "1285":
        excluir_usuarios()
        st.success("Todos os usuários foram excluídos com sucesso!")
    else:
        st.error("Senha incorreta! Não foi possível excluir os usuários.")