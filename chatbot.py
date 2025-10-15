import re
import sqlite3  # Opcional para persistência

# Configurações
SENHA_DONO = "dono123"  # Mude para algo seguro
ESTOQUE_INICIAL = [
    {"modelo": "Honda Civic", "ano": 2023, "preco": 120000, "disponivel": True},
    {"modelo": "Toyota Corolla", "ano": 2022, "preco": 110000, "disponivel": True},
    {"modelo": "Ford F-150", "ano": 2023, "preco": 250000, "disponivel": False},
    {"modelo": "Volkswagen Gol", "ano": 2021, "preco": 80000, "disponivel": True},
]

# Inicializar estoque (em memória ou SQLite)
estoque = {carro["modelo"]: carro for carro in ESTOQUE_INICIAL}

# Função para inicializar SQLite (opcional - descomente para usar)
def init_db():
    conn = sqlite3.connect('concessionaria.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS estoque
                 (modelo TEXT PRIMARY KEY, ano INTEGER, preco REAL, disponivel BOOLEAN)''')
    # Inserir dados iniciais se tabela vazia
    for carro in ESTOQUE_INICIAL:
        c.execute("INSERT OR IGNORE INTO estoque VALUES (?, ?, ?, ?)",
                  (carro["modelo"], carro["ano"], carro["preco"], carro["disponivel"]))
    conn.commit()
    conn.close()

# Função para carregar estoque do DB (opcional)
def load_from_db():
    global estoque
    conn = sqlite3.connect('concessionaria.db')
    c = conn.cursor()
    c.execute("SELECT * FROM estoque")
    rows = c.fetchall()
    estoque = {row[0]: {"modelo": row[0], "ano": row[1], "preco": row[2], "disponivel": bool(row[3])} for row in rows}
    conn.close()

# Função para salvar no DB (opcional)
def save_to_db(carro, action="update"):
    conn = sqlite3.connect('concessionaria.db')
    c = conn.cursor()
    if action == "add":
        c.execute("INSERT OR REPLACE INTO estoque VALUES (?, ?, ?, ?)",
                  (carro["modelo"], carro["ano"], carro["preco"], carro["disponivel"]))
    elif action == "remove":
        c.execute("DELETE FROM estoque WHERE modelo=?", (carro["modelo"],))
    elif action == "update":
        c.execute("UPDATE estoque SET disponivel=? WHERE modelo=?", (carro["disponivel"], carro["modelo"]))
    conn.commit()
    conn.close()

# Descomente as linhas abaixo para usar SQLite
# init_db()  # Inicializa o DB na primeira execução
# load_from_db()  # Carrega o estoque do DB

def processar_comando(pergunta):
    pergunta = pergunta.lower().strip()
    
    # Verificar disponibilidade de modelo
    if re.search(r'(possuimos|disponivel|temos|estoque)\s+(o\s+)?(\w+\s+)?(\w+)', pergunta):
        modelo_match = re.search(r'(possuimos|disponivel|temos|estoque)\s+(o\s+)?(.+?)(?:\?|$)', pergunta)
        if modelo_match:
            modelo = modelo_match.group(3).strip().title()
            if modelo in estoque:
                carro = estoque[modelo]
                status = "disponível" if carro["disponivel"] else "indisponível (vendido ou reservado)"
                return f"O {modelo} {carro['ano']} está {status}. Preço: R$ {carro['preco']:,}."
            else:
                return f"Desculpe, não temos o modelo '{modelo}' no estoque atual."
        return "Qual modelo de carro você quer verificar? Ex: 'Possuímos o Honda Civic disponível?'"
    
    # Listar todo o estoque
    elif any(palavra in pergunta for palavra in ['listar', 'todo estoque', 'inventario', 'carros disponiveis']):
        disponiveis = [m for m, c in estoque.items() if c["disponivel"]]
        total = len(estoque)
        valor_total = sum(c["preco"] for c in estoque.values())
        if disponiveis:
            lista = ", ".join([f"{m} {estoque[m]['ano']}" for m in disponiveis])
            return f"Carros disponíveis: {lista}. Total no estoque: {total} carros. Valor total: R$ {valor_total:,}."
        return f"Estoque vazio! Total: {total} carros. Valor total: R$ {valor_total:,}."
    
    # Adicionar carro novo
    elif 'adicionar' in pergunta or 'novo carro' in pergunta:
        try:
            # Extrair dados da pergunta (simples, assume formato: "Adicionar Honda Civic 2023 120000")
            partes = re.split(r'\s+', pergunta)
            if len(partes) >= 5:
                modelo = ' '.join(partes[1:3]).title()  # Ex: Honda Civic
                ano = int(partes[3])
                preco = float(partes[4])
                disponivel = True
                novo_carro = {"modelo": modelo, "ano": ano, "preco": preco, "disponivel": disponivel}
                estoque[modelo] = novo_carro
                # save_to_db(novo_carro, "add")  # Se usando DB
                return f"Carro adicionado: {modelo} {ano} por R$ {preco:,} (disponível)."
            return "Formato: 'Adicionar [modelo] [ano] [preco]'. Ex: 'Adicionar Honda Civic 2023 120000'"
        except (ValueError, IndexError):
            return "Erro ao adicionar. Use o formato correto."
    
    # Remover carro (venda)
    elif 'remover' in pergunta or 'vender' in pergunta:
        modelo_match = re.search(r'(remover|vender)\s+(.+?)(?:\?|$)', pergunta)
        if modelo_match:
            modelo = modelo_match.group(2).strip().title()
            if modelo in estoque:
                del estoque[modelo]
                # save_to_db({"modelo": modelo}, "remove")  # Se usando DB
                return f"Carro {modelo} removido do estoque (vendido!)."
            return f"Modelo '{modelo}' não encontrado."
        return "Qual modelo remover? Ex: 'Remover Honda Civic'"
    
    # Atualizar disponibilidade (ex: marcar como vendido)
    elif 'vender' in pergunta or 'indisponivel' in pergunta:
        modelo_match = re.search(r'(vender|indisponivel)\s+(.+?)(?:\?|$)', pergunta)
        if modelo_match:
            modelo = modelo_match.group(2).strip().title()
            if modelo in estoque:
                estoque[modelo]["disponivel"] = False
                # save_to_db(estoque[modelo], "update")  # Se usando DB
                return f"{modelo} marcado como indisponível (vendido)."
            return f"Modelo '{modelo}' não encontrado."
    
    # Consultar preço ou ano específico
    elif re.search(r'(preco|ano|detalhes)\s+(de\s+)?(.+?)(?:\?|$)', pergunta):
        modelo = re.search(r'(preco|ano|detalhes)\s+(de\s+)?(.+?)(?:\?|$)', pergunta).group(3).strip().title()
        if modelo in estoque:
            carro = estoque[modelo]
            return f"{modelo}: Ano {carro['ano']}, Preço R$ {carro['preco']:,}, Disponível: {'Sim' if carro['disponivel'] else 'Não'}."
        return f"Modelo '{modelo}' não encontrado."
    
    # Estatísticas gerais
    elif 'estatisticas' in pergunta or 'total' in pergunta:
        total_carros = len(estoque)
        disponiveis = sum(1 for c in estoque.values() if c["disponivel"])
        valor_total = sum(c["preco"] for c in estoque.values())
        valor_disponivel = sum(c["preco"] for c in estoque.values() if c["disponivel"])
        return f"Estatísticas: {total_carros} carros no total ({disponiveis} disponíveis). Valor total: R$ {valor_total:,}. Valor disponível: R$ {valor_disponivel:,}."
    
    # Ajuda
    elif 'ajuda' in pergunta or 'como usar' in pergunta:
        return """Comandos disponíveis:
- 'Possuimos [modelo] disponivel?' (ex: Honda Civic)
- 'Listar estoque' ou 'Carros disponíveis'
- 'Adicionar [modelo] [ano] [preco]' (ex: Adicionar Honda Civic 2023 120000)
- 'Remover [modelo]' ou 'Vender [modelo]'
- 'Preço de [modelo]' ou 'Ano de [modelo]'
- 'Estatísticas'
- 'Sair' para encerrar."""
    
    else:
        return "Não entendi. Digite 'ajuda' para ver comandos. Ex: 'Possuímos o Civic disponível?'"

def main():
    print("=== Chatbot de Assistência para Concessionária ===")
    print("Bem-vindo, dono! Digite sua senha para acessar:")
    senha = input("Senha: ")
    if senha != SENHA_DONO:
        print("Senha incorreta. Acesso negado.")
        return
    
    print("Acesso liberado! Faça perguntas sobre o estoque. Digite 'sair' para encerrar.")
    
    while True:
        pergunta = input("\nVocê: ")
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            print("Bot: Obrigado! Até logo.")
            break
        resposta = processar_comando(pergunta)
        print(f"Bot: {resposta}")

if __name__ == "__main__":
    main() 
