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
    await ctx.send(f'🔍 Analizuję zwoje forum Balmory w poszukiwaniu: **{zapytanie}**...')
    
    zapytanie_z_filtrem = f"site:forum.balmora.pl/topic {zapytanie}"
    znaleziony_link = None
    
    try:
        # Pytamy tekstową wersję DuckDuckGo (Lite), która nie blokuje botów
        url = "https://lite.duckduckgo.com/lite/"
        data = {"q": zapytanie_z_filtrem}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        ddg_response = requests.post(url, data=data, headers=headers)
        ddg_soup = BeautifulSoup(ddg_response.text, 'html.parser')
        
        # Przeszukujemy wszystkie linki na stronie wyników
        for a in ddg_soup.find_all('a', href=True):
            href = a['href']
            
            # Wyszukiwarki często "chowają" prawdziwy link w parametrze przekierowania (uddg=)
            if 'uddg=' in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in qs:
                    href = qs['uddg'][0]
            
            # Bierzemy tylko i wyłącznie bezpośrednie linki do tematów na Balmorze
            if 'forum.balmora.pl/topic/' in href:
                znaleziony_link = href
                break
                
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, nie znalazłem żadnego pasującego tematu. Serwery milczą.')
            return

        # Wejście bezpośrednio na wyłowiony link z forum
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        # Szukanie bloku z tekstem (Balmora zazwyczaj używa <article>)
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap')
        
        if post:
            tekst = post.get_text(separator="\n", strip=True)[:1000]
            
            # Pobranie pierwszego zdjęcia (z pominięciem awatarów i emotek)
            obrazek = post.find('img')
            obrazek_url = None
            if obrazek and obrazek.get('src') and 'emoticons' not in obrazek.get('src') and 'profile' not in obrazek.get('src'):
                obrazek_url = obrazek.get('src')
                
            odpowiedz = f"**Znalazłem odpowiedź!**\n🔗 Link: {znaleziony_link}\n\n**Fragment:**\n{tekst}...\n"
            if obrazek_url:
                odpowiedz += f"\n**Screen z forum:**\n{obrazek_url}"
                
            await ctx.send(odpowiedz)
        else:
            await ctx.send(f'Znalazłem temat, ale ma on nietypową budowę tekstu. Sprawdź ręcznie: {znaleziony_link}')

    except Exception as e:
        await ctx.send('Wybacz, Mości Panie. Zabezpieczenia sieciowe odrzuciły nasze żądanie.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
