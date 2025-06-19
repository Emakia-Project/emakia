import requests
from bs4 import BeautifulSoup
import time

# --- Function to Fetch Maxnews Articles ---
def get_maxnews_articles():
    main_url = 'https://www.newsmax.com'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.findAll('div', class_='nmNewsfrontHead')

    parsed_articles = []
    for article in articles[:3]:
        a_tag = article.find('a')
        if not a_tag:
            continue

        title = a_tag.text.strip()
        link = a_tag['href']
        if link.startswith('/'):
            link = f'{main_url}{link}'

        try:
            article_response = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            content_div = article_soup.find('div', attrs={'id': 'mainArticleDiv'})
            content = content_div.get_text(strip=True, separator='\n') if content_div else "No content found."

            parsed_articles.append({"title": title, "link": link, "content": content})
        except Exception as e:
            print(f'Error fetching article: {e}')

        time.sleep(1)  
    
    return parsed_articles 