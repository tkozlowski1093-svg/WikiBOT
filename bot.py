import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i jestem gotów do pracy!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    # Bot informuje, że rozpoczął pracę
    await ctx.send(f'🔍 Przeszukuję zakamarki forum Balmory w poszukiwaniu: **{zapytanie}**...')
    
    # 1. Zmieniamy tekst na format linku (np. spacje na %20) i tworzymy link do wyszukiwarki forum
    query = urllib.parse.quote(zapytanie)
    search_url = f"https://forum.balmora.pl/search/?q={query}"
    
    # 2. Udajemy prawdziwą przeglądarkę, by forum nas nie zablokowało za bycie botem
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # Pytamy wyszukiwarkę o wyniki
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Szukamy linku do pierwszego tematu w wynikach wyszukiwania
        # Zazwyczaj linki do tematów zawierają słowo "topic" (temat)
        wyniki = soup.find_all('a', href=True)
        znaleziony_link = None
        
        for link in wyniki:
            if '/topic/' in link['href']: 
                znaleziony_link = link['href']
                break # Znaleźliśmy pierwszy lepszy temat, przerywamy szukanie
                
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, nie znalazłem na forum żadnego tematu pasującego do tego zapytania.')
            return

        # 4. Wchodzimy w znaleziony temat, aby pobrać tekst i obrazek
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        # Próbujemy znaleźć treść pierwszego posta (tag 'article' lub 'div' - zależy od forum)
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap')
        
        if post:
            # Wyciągamy sam tekst, ale skracamy go do 1000 znaków, żeby nie zalać Discorda ścianą tekstu
            tekst = post.get_text(separator="\n", strip=True)[:1000] 
            
            # Szukamy pierwszego zdjęcia wrzuconego w poście
            obrazek = post.find('img')
            
            # Budujemy ostateczną wiadomość do wysłania na Discord
            odpowiedz = f"**Znalazłem odpowiedź na forum!**\n🔗 Źródło: {znaleziony_link}\n\n**Fragment:**\n{tekst}...\n\n"
            
            if obrazek and obrazek.get('src'):
                # Jeśli znaleziono obrazek i nie jest to emotikonka (zazwyczaj mają mały rozmiar/specyficzną nazwę), dodajemy go
                if "emoticons" not in obrazek.get('src'):
                    odpowiedz += f"**Screen z poradnika:**\n{obrazek['src']}"
                
            await ctx.send(odpowiedz)
        else:
            # Znalazło temat, ale strona ma inną budowę i bot nie umie wyciąć samego tekstu
            await ctx.send(f'Znalazłem temat, ale nie potrafię z niego wyciągnąć samego tekstu. Oto link, sprawdź sam: {znaleziony_link}')

    except Exception as e:
        await ctx.send('Wybacz, Mości Panie. Napotkałem techniczny błąd podczas analizy strony.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
