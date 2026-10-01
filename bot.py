import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i ukrywam linki przed graczami!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🧠 Przeszukuję kroniki Balmory i układam odpowiedź na temat: **{zapytanie}**...')
    
    zapytanie_z_filtrem = f"site:forum.balmora.pl/topic {zapytanie}"
    znaleziony_link = None
    
    try:
        url = "https://lite.duckduckgo.com/lite/"
        data = {"q": zapytanie_z_filtrem}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        ddg_response = requests.post(url, data=data, headers=headers)
        ddg_soup = BeautifulSoup(ddg_response.text, 'html.parser')
        
        for a in ddg_soup.find_all('a', href=True):
            href = a['href']
            if 'uddg=' in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in qs:
                    href = qs['uddg'][0]
            
            if 'forum.balmora.pl/topic/' in href:
                znaleziony_link = href
                break
                
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, nie znalazłem informacji na ten temat na forum.')
            return

        # Pobieramy treść z forum
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap')
        
        if post:
            surowy_tekst = post.get_text(separator="\n", strip=True)[:3000]
            
            # Instrukcja dla AI – żadnych linków, tylko czysta wiedza
            prompt = f"""
            Jesteś pomocnym asystentem graczy Metin2 na serwerze Balmora. 
            Gracz zadał następujące pytanie: "{zapytanie}"
            
            Oto surowy tekst pobrany z forum Balmory:
            {surowy_tekst}
            
            Na podstawie powyższego tekstu, sformułuj zwięzłą, przyjazną i konkretną odpowiedź na pytanie gracza.
            Wypisz same fakty, bez żadnych wstępów typu "według forum" i bez podawania jakichkolwiek linków czy adresów stron.
            Jeśli w tekście nie ma informacji do odpowiedzi, napisz po prostu, że nie posiadasz takich danych.
            """
            
            ai_odpowiedz = model.generate_content(prompt).text
            
            # Szukanie screena (jeśli gracz pytał o bossa/metina)
            obrazek = post.find('img')
            obrazek_url = None
            if obrazek and obrazek.get('src') and 'emoticons' not in obrazek.get('src') and 'profile' not in obrazek.get('src'):
                obrazek_url = obrazek.get('src')
                
            # Wysyłamy samą treść i opcjonalnie sam obrazek (bez brzydkich linków tekstowych)
            await ctx.send(ai_odpowiedz)
            
            if obrazek_url:
                await ctx.send(obrazek_url)
                
        else:
            await ctx.send('Przeanalizowałem forum, ale struktura strony uniemożliwia odczytanie treści.')

    except Exception as e:
        await ctx.send('Wystąpił błąd podczas przetwarzania żądania.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
