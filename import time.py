import time
import csv
import random
import concurrent.futures
import requests  # Corrigida a falta de importação
from bs4 import BeautifulSoup

# global headers to be used for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
}

MAX_THREADS = 15

def extract_movie_details(movie_link):
    """Extrai detalhes de um filme da página do IMDb."""
    try:
        time.sleep(random.uniform(0, 0.2))
        response = requests.get(movie_link, headers=headers)
        response.raise_for_status()  # Garante que a resposta é válida

        movie_soup = BeautifulSoup(response.content, 'html.parser')

        if not movie_soup:
            return

        title = date = rating = plot_text = None

        # Encontrando a seção específica
        page_section = movie_soup.find('section', class_='ipc-page-section')

        if page_section:
            divs = page_section.find_all('div', recursive=False)
            if len(divs) > 1:
                target_div = divs[1]

                # Encontrando o título do filme
                title_tag = target_div.find('h1')
                if title_tag:
                    span_title = title_tag.find('span')
                    title = span_title.get_text() if span_title else None

                # Encontrando a data de lançamento
                date_tag = target_div.find('a', href=lambda href: href and 'releaseinfo' in href)
                date = date_tag.get_text().strip() if date_tag else None

        # Encontrando a classificação do filme
        rating_tag = movie_soup.find('div', attrs={'data-testid': 'hero-rating-bar__aggregate-rating__score'})
        rating = rating_tag.get_text().strip() if rating_tag else None

        # Encontrando a sinopse do filme
        plot_tag = movie_soup.find('span', attrs={'data-testid': 'plot-xs_to_m'})
        plot_text = plot_tag.get_text().strip() if plot_tag else None

        if all([title, date, rating, plot_text]):
            print(f"{title} | {date} | {rating} | {plot_text}")

            with open('movies.csv', mode='a', newline='', encoding='utf-8') as file:
                movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                movie_writer.writerow([title, date, rating, plot_text])

    except requests.RequestException as e:
        print(f"Erro ao acessar {movie_link}: {e}")

def extract_movies(soup):
    """Extrai links dos filmes populares no IMDb."""
    try:
        movies_table = soup.find('div', attrs={'data-testid': 'chart-layout-main-column'}).find('ul')
        if not movies_table:
            print("Tabela de filmes não encontrada!")
            return

        movies_table_rows = movies_table.find_all('li')
        movie_links = ['https://imdb.com' + movie.find('a')['href'] for movie in movies_table_rows if movie.find('a')]

        threads = min(MAX_THREADS, len(movie_links))
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(extract_movie_details, movie_links)

    except Exception as e:
        print(f"Erro ao extrair filmes: {e}")

def main():
    """Função principal que inicia a extração dos filmes."""
    start_time = time.time()

    # IMDB Most Popular Movies - 100 filmes
    popular_movies_url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'

    try:
        response = requests.get(popular_movies_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrai os filmes da página
        extract_movies(soup)

    except requests.RequestException as e:
        print(f"Erro ao acessar {popular_movies_url}: {e}")

    end_time = time.time()
    print('Total time taken:', end_time - start_time)

if __name__ == '__main__':
    main()
