import discord
from discord.ext import commands
import os
from bs4 import BeautifulSoup
import google.generativeai as genai
import cloudscraper
import urllib.parse

# Konfiguracja AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Tworzymy specjalnego "włamywacza", który omija błąd 403 (Cloudflare) na Balmorze
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})

@bot.event
async def on_ready():
    print(f'Mości Panie, {bot.user} jest gotów do dynamicznego przeszukiwania całego forum Balmory!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🔍 Włączam omijanie zapór. Przeszukuję całe forum Balmory o: **{zapytanie}**...')
    
    try:
        # 1. Szukamy linku przez wyszukiwarkę (używając Cloudscrapera, by uniknąć blokad)
        query = urllib.parse.quote(f"site:forum.balmora.pl {zapytanie}")
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        
        ddg_response = scraper.get(search_url)
        soup = BeautifulSoup(ddg_response.text, 'html.parser')
        
        znaleziony_link = None
        
        # Wyciągamy pierwszy link prowadzący na Balmorę
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'uddg=' in href:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'uddg' in qs:
                    href = qs['uddg'][0]
            if 'forum.balmora.pl' in href and '/topic/' in href:
                znaleziony_link = href
                break
                
        if not znaleziony_link:
            await ctx.send('Niestety, Mości Panie, na forum nie ma żadnego tematu odpowiadającego na to zapytanie.')
            return

        # 2. Wchodzimy bezpośrednio w znaleziony temat na Balmorze (omijając 403)
        forum_response = scraper.get(znaleziony_link)
        forum_soup = BeautifulSoup(forum_response.text, 'html.parser')
        
        # Szukamy postów (szeroki zakres klas dla silnika Invision)
        posty = forum_soup.find_all(['div', 'article'], class_=['cPost_contentWrap', 'ipsComment_content', 'ipsType_normal'])
        
        pelny_tekst = ""
        pierwszy_obrazek_url = None
        
        for post in posty:
            pelny_tekst += post.get_text(separator="\n", strip=True) + "\n"
            
            # Pobieramy pierwszy merytoryczny obrazek (np. mapę/screen)
            if not pierwszy_obrazek_url:
                obrazek = post.find('img')
                if obrazek and obrazek.get('src'):
                    src = obrazek.get('src')
                    if 'emoticons' not in src and 'profile' not in src and 's.gravatar.com' not in src:
                        pierwszy_obrazek_url = src
                        
        if not pelny_tekst or len(pelny_tekst) < 50:
            await ctx.send(f'Przełamałem zaporę, ale temat wydaje się pusty. Sprawdź ręcznie: {znaleziony_link}')
            return

        # 3. AI analizuje przeczytany tekst i generuje konkretną odpowiedź
        prompt = f"""
        Jesteś inteligentnym asystentem graczy na serwerze Balmora (Metin2). 
        Gracz pyta o: "{zapytanie}"
        
        Z forum Balmory pobrano "w locie" następujący poradnik/dyskusję:
        {pelny_tekst[:8000]}
        
        Na podstawie WYŁĄCZNIE powyższego tekstu odpowiedz graczowi krótko, naturalnie i samymi konkretami.
        Nie podawaj linków i nie zaczynaj od "Według tekstu". 
        Jeżeli w tym tekście nie ma żadnej odpowiedzi na to pytanie, powiedz po prostu, że forumowicze o tym nie wspomnieli.
        """
        
        ai_odpowiedz = model.generate_content(prompt).text
        
        # Wysyłamy gotową odpowiedź
        await ctx.send(ai_odpowiedz)
        
        # Opcjonalnie wysyłamy wyciągnięty z tematu screen
        if pierwszy_obrazek_url:
            if pierwszy_obrazek_url.startswith('//'):
                pierwszy_obrazek_url = 'https:' + pierwszy_obrazek_url
            await ctx.send(f"**Załącznik z forum:** {pierwszy_obrazek_url}")
            
    except Exception as e:
        await ctx.send('Napotkałem silny opór ze strony magicznych zapór Balmory. Spróbuj zadać pytanie inaczej.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
