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
    await ctx.send(f'🔍 Przeszukuję księgi Balmory w poszukiwaniu: **{zapytanie}**...')
    
    # Krok 1: Szukamy linku do forum przez wyszukiwarkę z ograniczeniem site:
    zapytanie_z_filtrem = f"site:forum.balmora.pl {zapytanie}"
    query = urllib.parse.quote(zapytanie_z_filtrem)
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # Pobieramy wyniki wyszukiwania
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        znaleziony_link = None
        
        # Wyciągamy czysty link z przekierowań DuckDuckGo
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Szukamy linków, które prowadzą konkretnie do tematów na Balmorze
            if 'uddg=' in href and 'forum.balmora.pl/topic/' in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in qs:
                    znaleziony_link = qs['uddg'][0]
                    break
                    
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, nie znalazłem na forum żadnego tematu pasującego do tego zapytania.')
            return

        # Krok 2: Wchodzimy bezpośrednio pod znaleziony link na forum Balmory
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        # Fora takie jak Balmora często trzymają główny post w znaczniku 'article'
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap')
        
        if post:
            # Pobieramy tekst (maksymalnie 1000 znaków)
            tekst = post.get_text(separator="\n", strip=True)[:1000]
            
            # Pobieramy pierwszy obrazek (pomijamy emotikony z forum)
            obrazek = post.find('img')
            obrazek_url = None
            if obrazek and obrazek.get('src') and 'emoticons' not in obrazek.get('src'):
                obrazek_url = obrazek.get('src')
                
            odpowiedz = f"**Znalazłem odpowiedź!**\n🔗 Źródło: {znaleziony_link}\n\n**Fragment poradnika:**\n{tekst}...\n"
            
            if obrazek_url:
                odpowiedz += f"\n**Screen ze strony:**\n{obrazek_url}"
                
            await ctx.send(odpowiedz)
        else:
            await ctx.send(f'Znaleziono temat, ale jego budowa utrudnia wyciągnięcie tekstu. Zobacz samodzielnie: {znaleziony_link}')

    except Exception as e:
        await ctx.send('Wybacz, Mości Panie. Napotkałem problem techniczny przy analizie zwojów.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
