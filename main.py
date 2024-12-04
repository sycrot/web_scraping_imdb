import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Verificar os Termos de Uso
def verificar_termos_imdb():
    url_termos = "https://www.imdb.com/conditions"
    response = requests.get(url_termos)
    if response.status_code == 200:
        termos = BeautifulSoup(response.text, 'html.parser').get_text()
        if "web scraping" in termos.lower() or "prohibited" in termos.lower():
            print("Raspagem de dados não permitida segundo os Termos de Uso do IMDb.")
            return False
        print("Raspagem permitida ou não restrita explicitamente nos Termos de Uso.")
        return True
    else:
        print("Não foi possível acessar os Termos de Uso.")
        return False

# Raspagem de dados
def raspagem_imdb():
    url = "https://www.imdb.com/chart/moviemeter/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"})
    if response.status_code != 200:
        print(f"Erro ao acessar o IMDb: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    filmes = []

    # Selecionar os elementos da tabela de filmes populares
    linhas = soup.select('ul.ipc-metadata-list li')
    for linha in linhas:
        # Extração de título
        titulo = linha.select_one('.ipc-title__text').get_text(strip=True)

        # Extração de nota
        nota_tag = linha.select_one('.ipc-rating-star--rating')
        nota = float(nota_tag.get_text(strip=True)) if nota_tag else None

        # Extração do total de votos
        total_votos_tag = linha.select_one('.ipc-rating-star--voteCount')
        total_votos = total_votos_tag.get_text(strip=True)  if total_votos_tag else None

        # Extração de data de lançamento
        ano_lancamento = linha.select_one('.cli-title-metadata span:first-child').get_text(strip=True)

        filmes.append({"Título": titulo, "Nota": nota, "Total de Votos": total_votos, "Ano de Lançamento": ano_lancamento})
    
    return filmes

# Tratamento de dados
def tratar_dados(filmes):
    df = pd.DataFrame(filmes)

    # Substituir valores ausentes
    df['Nota'].fillna("Sem nota", inplace=True)
    df['Ano de Lançamento'].fillna("Sem data", inplace=True)
    df['Total de Votos'].fillna("Sem votos", inplace=True)

    return df

# Salva dados em csv
if __name__ == "__main__":
    if verificar_termos_imdb():
        filmes = raspagem_imdb()
        if filmes:
            df = tratar_dados(filmes)
            print(df.head());
            
            df.to_csv("filmes_mais_populares_imdb.csv", index=False)
