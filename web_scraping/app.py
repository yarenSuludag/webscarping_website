from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

def scrape_books():
    # Temel URL
    base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
    
    # Tüm kitapları depolayacak liste
    all_books = []

    # İlk 5 sayfadan veri çekelim (isteğe göre artırılabilir)
    for page_num in range(1, 50):
        url = base_url.format(page_num)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        books = soup.find_all('article', class_='product_pod')
        
        for book in books:
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text
            availability = book.find('p', class_='instock availability').text.strip()
            image_url = book.find('img')['src']
            full_image_url = f'https://books.toscrape.com/{image_url}'
            all_books.append({'Title': title, 'Price': price, 'Availability': availability, 'Image': full_image_url})
    
    # Verileri bir DataFrame olarak döndür
    df = pd.DataFrame(all_books)
    return df

@app.route('/')
def index():
    # Web scraping ile kitapları çek
    df = scrape_books()

    # Arama ve Filtreleme için kullanıcı girdilerini al
    search_query = request.args.get('search', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort_by = request.args.get('sort_by', '')

    # Arama filtresi
    if search_query:
        df = df[df['Title'].str.contains(search_query, case=False)]
    
    # Fiyat aralığı filtresi
    if min_price:
        df = df[df['Price'].apply(lambda x: float(x[1:])) >= float(min_price)]
    if max_price:
        df = df[df['Price'].apply(lambda x: float(x[1:])) <= float(max_price)]
    
    # Sıralama
    if sort_by == 'price_asc':
        df = df.sort_values('Price', key=lambda x: x.apply(lambda y: float(y[1:])))
    elif sort_by == 'price_desc':
        df = df.sort_values('Price', key=lambda x: x.apply(lambda y: float(y[1:])), ascending=False)
    elif sort_by == 'title_asc':
        df = df.sort_values('Title')
    elif sort_by == 'title_desc':
        df = df.sort_values('Title', ascending=False)

    books = df.to_dict('records')
    return render_template('index.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)
