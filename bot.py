import discord
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i maskuję się jako przeglądarka!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🧠 Podszywam się pod przeglądarkę i czytam poradnik o: **{zapytanie}**...')
    
    docelowy_link = "https://forum.balmora.pl/topic/16388-bossy-czyli-co-ile-się-respią-co-z-nich-dropi-co-potrzeba-by-je-ubić-czyli-wszystko-o-bossach/"
    
    # Bardzo bogate nagłówki, które oszukują zabezpieczenia forum (Cloudflare / Invision)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://forum.balmora.pl/',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(docelowy_link, headers=headers)
        
        if response.status_code != 200:
            await ctx.send(f'Ojej, forum odrzuciło nas z kodem błędu: {response.status_code}')
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Szukamy zawartości postów na silniku forum
        posty = soup.find_all(['div', 'article'], class_=['cPost_contentWrap', 'ipsComment_content', 'ipsType_normal'])
        
        pelny_tekst = ""
        pierwszy_obrazek_url = None
        
        for post in posty:
            pelny_tekst += post.get_text(separator="\n", strip=True) + "\n"
            
            if not pierwszy_obrazek_url:
                obrazek = post.find('img')
                if obrazek and obrazek.get('src'):
                    src = obrazek.get('src')
                    if 'emoticons' not in src and 'profile' not in src and 's.gravatar.com' not in src:
                        pierwszy_obrazek_url = src

        if not pelny_tekst or len(pelny_tekst) < 100:
            await ctx.send('Strona się załadowala, ale wciąż jest pusta. Prawdopodobnie wymagane jest ominięcie ochrony JS.')
            return

        # Przekazanie do AI
        prompt = f"""
        Jesteś botem informacyjnym serwera Balmora (Metin2). 
        Gracz pyta o: "{zapytanie}"
        
        Oto pełna treść pobrana z poradnika na forum:
        {pelny_tekst[:10000]}
        
        Na podstawie tego tekstu udziel dokładnej, zwięzłej odpowiedzi na pytanie gracza (np. czas respu, drop lub lokalizacja). 
        Żadnych linków, żadnych wstępów. Same fakty po polsku. Jeśli nie ma informacji na ten temat, napisz to krótko.
        """
        
        ai_odpowiedz = model.generate_content(prompt).text
        
        await ctx.send(ai_odpowiedz)
        
        if pierwszy_obrazek_url:
            await ctx.send(f"Oto zrzut ekranu / mapa z poradnika:\n{pierwszy_obrazek_url}")

    except Exception as e:
        await ctx.send('Wystąpił błąd krytyczny przy pobieraniu danych.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
