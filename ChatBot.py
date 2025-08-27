# APRENDIZADO SUPERVISIONADO E NÃO SUPERVISIONADO
import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

#TAREFA 1
def limpar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\d+', '', texto)
    texto = texto.strip()
    return texto

mensagens = [
    "Quero fazer um pedido",
    "Preciso falar com o suporte",
    "Quais promoções vocês têm hoje?",
    "Qual o horário de funcionamento?",
    "Meu produto veio com defeito",
    "Posso pagar com cartão de crédito?",
    # +4 mensagens
    "Vocês entregam no fim de semana?",
    "Quero cancelar meu pedido",
    "Tem frete grátis acima de quanto?",
    "Onde acompanho meu pedido?"
]
rotulos = [
    "pedido", "suporte", "promoção", "informação", "suporte", "pagamento",
    "informação", "pedido", "informação", "pedido"
]

mensagens_limpas = [limpar_texto(m) for m in mensagens]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(mensagens_limpas)

modelo = MultinomialNB()
modelo.fit(X, rotulos)

while True:
    nova_mensagem = input("\nDigite uma mensagem (ou 'sair' para encerrar): ")
    if nova_mensagem.lower() == "sair":
        break
    nova_mensagem_limpa = limpar_texto(nova_mensagem)
    X_novo = vectorizer.transform([nova_mensagem_limpa])
    predicao = modelo.predict(X_novo)
    print(f"Intenção prevista: {predicao[0]}")

#TAREFA 2

frases = [
    "Quando abre matrícula?",
    "Como vejo minhas notas?",
    "Vai ter evento semana que vem?",
    "Qual o horário da biblioteca?",
    "Preciso trancar a matrícula",
    "Quais disciplinas estão disponíveis?",
    "Onde retiro meu diploma?",
    "Como faço a rematrícula online?"
]
rotulos = [
    "matricula", "notas", "eventos", "biblioteca",
    "matricula", "matricula", "informação", "matricula"
]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(frases)

modelo = MultinomialNB()
modelo.fit(X, rotulos)

print("--- TAREFA 2 ---")
while True:
    nova_frase = input("\nDigite uma frase (ou 'sair' para encerrar): ")
    if nova_frase.lower() == "sair":
        break
    nova_frase_limpa = vectorizer.transform([nova_frase])
    predicao = modelo.predict(nova_frase_limpa)
    print(f"Intenção prevista: {predicao[0]}")
    
#TAREFA 3

print("--- TAREFA 3 ---")
dados_entregas = np.array([
    [5, 2],
    [2, 1],
    [10, 4],
    [7, 3],
    [1, 1]
])
tempos_entrega = np.array([30, 15, 55, 40, 10])

modelo_entrega = LinearRegression()
modelo_entrega.fit(dados_entregas, tempos_entrega)

pedido_novo = np.array([[8, 2]])
tempo_previsto = modelo_entrega.predict(pedido_novo)
print(f"Tempo de entrega previsto para o novo pedido: {tempo_previsto[0]:.2f} minutos")

#TAREFA 4

print("\n--- TAREFA 4 ---")
mensagens_cluster = [
    "Quero pedir pizza",
    "Qual o valor da pizza grande?",
    "Preciso de suporte no aplicativo",
    "O app está travando",
    "Vocês têm sobremesas?",
    "Meu pedido está atrasado",
    # +3 mensagens
    "Quais sabores de pizza vocês têm?",
    "Onde fica a loja mais próxima?",
    "Quero falar com atendente"
]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(mensagens_cluster)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X)

for i, msg in enumerate(mensagens_cluster):
    print(f"'{msg}' => Cluster {kmeans.labels_[i]}")
