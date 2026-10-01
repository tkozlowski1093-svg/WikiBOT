import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import google.generativeai as genai

# Konfiguracja AI (pobiera klucz z Railway)
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
# Używamy najnowszego, darmowego i szybkiego modelu
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i mój moduł AI jest gotowy do pracy!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🧠 AI analizuje zwoje forum Balmory w poszukiwaniu: **{zapytanie}**...')
    
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
            await ctx.send('Niestety, nie znalazłem żadnego pasującego tematu. Serwery milczą.')
            return

        # Pobieramy stronę z forum
        temat_response = requests.get(znaleziony_link, headers=headers)
        temat_soup = BeautifulSoup(temat_response.text, 'html.parser')
        
        post = temat_soup.find('article') or temat_soup.find('div', class_='cPost_contentWrap')
        
        if post:
            # Pobieramy więcej tekstu dla AI (do 3000 znaków), aby miało pełen kontekst
            surowy_tekst = post.get_text(separator="\n", strip=True)[:3000]
            
            # Tworzymy instrukcję (prompt) dla sztucznej inteligencji
            prompt = f"""
            Jesteś pomocnym asystentem graczy Metin2 na serwerze Balmora. 
            Gracz zadał następujące pytanie: "{zapytanie}"
            
            Oto surowy tekst pobrany z forum Balmory:
            {surowy_tekst}
            
            Na podstawie powyższego tekstu, sformułuj zwięzłą, przyjazną i konkretną odpowiedź na pytanie gracza.
            Jeśli w tekście nie ma informacji użytecznych do odpowiedzi, poinformuj o tym krótko.
            Nie wymyślaj własnych informacji, opieraj się tylko na dostarczonym tekście.
            """
            
            # AI generuje odpowiedź
            ai_odpowiedz = model.generate_content(prompt).text
            
            # Pobieranie zdjęcia
            obrazek = post.find('img')
            obrazek_url = None
            if obrazek and obrazek.get('src') and 'emoticons' not in obrazek.get('src') and 'profile' not in obrazek.get('src'):
                obrazek_url = obrazek.get('src')
                
            # Budowa ostatecznej wiadomości
            wiadomosc_koncowa = f"{ai_odpowiedz}\n\n🔗 *Źródło informacji: {znaleziony_link}*"
            if obrazek_url:
                wiadomosc_koncowa += f"\n**Screen poglądowy:**\n{obrazek_url}"
                
            await ctx.send(wiadomosc_koncowa)
        else:
            await ctx.send(f'Znalazłem temat, ale nie umiem go poprawnie odczytać. Sprawdź ręcznie: {znaleziony_link}')

    except Exception as e:
        await ctx.send('Wystąpił błąd w układach scalonych lub podczas łączenia z forum.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
