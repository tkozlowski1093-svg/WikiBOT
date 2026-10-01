import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
from googlesearch import search

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i jestem gotów do pracy!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🔍 Wzywam magię Google do przeszukania forum Balmory o: **{zapytanie}**...')
    
    # Narzucamy Google wyszukiwanie TYLKO na forum.balmora.pl
    zapytanie_z_filtrem = f"site:forum.balmora.pl {zapytanie}"
    znaleziony_link = None
    
    try:
        # Pobieramy tylko 1, najlepszy wynik z Google
        for wynik in search(zapytanie_z_filtrem, num_results=1, lang="pl"):
            znaleziony_link = wynik
            break
            
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, Google nie znalazło żadnego pasującego tematu na Balmorze.')
            return

        # Skoro mamy link z Google, wchodzimy prosto na forum pobrać treść
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        # Przeszukujemy tagi, w których fora zazwyczaj trzymają treść wpisów
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap') or temat_soup.find('div', class_='ipsType_normal')
        
        if post:
            # Skracamy tekst
            tekst = post.get_text(separator="\n", strip=True)[:1000]
            
            # Szukamy obrazków (ignorując emotikony i awatary profilowe)
            obrazek = post.find('img')
            obrazek_url = None
            if obrazek and obrazek.get('src') and 'emoticons' not in obrazek.get('src') and 'profile' not in obrazek.get('src'):
                obrazek_url = obrazek.get('src')
                
            odpowiedz = f"**Znalazłem odpowiedź!**\n🔗 Link: {znaleziony_link}\n\n**Fragment:**\n{tekst}...\n"
            
            if obrazek_url:
                odpowiedz += f"\n**Screen z forum:**\n{obrazek_url}"
                
            await ctx.send(odpowiedz)
        else:
            await ctx.send(f'Znalazłem temat, ale skrypt nie potrafi przebić się przez kod strony do tekstu. Zajrzyj sam: {znaleziony_link}')

    except Exception as e:
        await ctx.send('Wybacz, Mości Panie. Napotkaliśmy blokadę lub błąd po stronie Google.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
