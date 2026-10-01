import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i jestem gotów do pracy!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🔍 Przeszukuję kroniki forum Balmory o: **{zapytanie}**...')
    
    # Filtr wymuszający szukanie tylko na Balmorze
    zapytanie_z_filtrem = f"site:forum.balmora.pl {zapytanie}"
    znaleziony_link = None
    
    try:
        # Używamy bezpiecznego, wewnętrznego API DuckDuckGo, które omija blokady
        with DDGS() as ddgs:
            wyniki = list(ddgs.text(zapytanie_z_filtrem, max_results=1))
            if wyniki:
                znaleziony_link = wyniki[0]['href']
            
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, nie znalazłem żadnego pasującego tematu na forum.')
            return

        # Bot wchodzi w znaleziony link na forum
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        # Szukanie treści posta na forum
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap')
        
        if post:
            tekst = post.get_text(separator="\n", strip=True)[:1000]
            
            # Pobieranie pierwszego sensownego obrazka
            obrazek = post.find('img')
            obrazek_url = None
            if obrazek and obrazek.get('src') and 'emoticons' not in obrazek.get('src') and 'profile' not in obrazek.get('src'):
                obrazek_url = obrazek.get('src')
                
            odpowiedz = f"**Znalazłem odpowiedź!**\n🔗 Link: {znaleziony_link}\n\n**Fragment:**\n{tekst}...\n"
            if obrazek_url:
                odpowiedz += f"\n**Screen:**\n{obrazek_url}"
                
            await ctx.send(odpowiedz)
        else:
            await ctx.send(f'Znalazłem temat, ale ma on nietypową budowę. Sprawdź sam: {znaleziony_link}')

    except Exception as e:
        await ctx.send('Wybacz, Mości Panie. Wystąpił błąd podczas przeszukiwania zwojów.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
