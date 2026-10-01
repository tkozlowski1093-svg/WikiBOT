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
    print(f'Mości Panie, zalogowałem się jako {bot.user} i czytam bezpośrednie zwoje!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🧠 Analizuję poradnik o bossach na Balmorze w poszukiwaniu: **{zapytanie}**...')
    
    # Skoro znamy dokładny adres najlepszego poradnika na forum, wchodzimy w niego bezpośrednio
    docelowy_link = "https://forum.balmora.pl/topic/16388-bossy-czyli-co-ile-się-respią-co-z-nich-dropi-co-potrzeba-by-je-ubić-czyli-wszystko-o-bossach/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(docelowy_link, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Invision Power Board (silnik Balmory) trzyma treść postów w klasie cPost_contentWrap lub ipsComment_content
        posty = soup.find_all(['div', 'article'], class_=['cPost_contentWrap', 'ipsComment_content'])
        
        pelny_tekst = ""
        pierwszy_obrazek_url = None
        
        for post in posty:
            # Zbieramy tekst ze wszystkich postów w tym poradniku
            pelny_tekst += post.get_text(separator="\n", strip=True) + "\n"
            
            # Szukamy pierwszego sensownego screena z mapą/bosem
            if not pierwszy_obrazek_url:
                obrazek = post.find('img')
                if obrazek and obrazek.get('src'):
                    src = obrazek.get('src')
                    if 'emoticons' not in src and 'profile' not in src and 's.gravatar.com' not in src:
                        pierwszy_obrazek_url = src

        if not pelny_tekst:
            await ctx.send('Niestety, nie udało się odczytać treści z tego poradnika.')
            return

        # Wysyłamy tekst do Gemini, żeby wybrało interesujący gracza fragment
        prompt = f"""
        Jesteś botem informacyjnym serwera Balmora (Metin2). 
        Gracz pyta o: "{zapytanie}"
        
        Oto pełna treść poradnika z forum na temat bossów:
        {pelny_tekst[:10000]}
        
        Na podstawie tego tekstu udziel dokładnej, zwięzłej i przyjemnej w odbiorze odpowiedzi na pytanie gracza (np. podaj czas respu, lokalizację lub drop, o który pyta). 
        Nie dawaj żadnych linków ani odnośników. Pisz samymi konkretami. Jeśli w tekście nie ma odpowiedzi na to konkretne pytanie, napisz, że brak danych w poradniku.
        """
        
        ai_odpowiedz = model.generate_content(prompt).text
        
        # Wysyłamy odpowiedź tekstową od AI
        await ctx.send(ai_odpowiedz)
        
        # Jeśli znaleziono screen/mapę w poradniku, wysyłamy go jako drugi komunikat
        if pierwszy_obrazek_url:
            await ctx.send(f"Oto zrzut ekranu / mapa z poradnika:\n{pierwszy_obrazek_url}")

    except Exception as e:
        await ctx.send('Wystąpił błąd podczas bezpośredniego czytania zwojów.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
