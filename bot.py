import discord
from discord.ext import commands
import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Bezpośrednia baza wiedzy skopiowana z oficjalnego poradnika Balmory o bossach
BAZA_WIEDZY_BALMORA = """
Poradnik: Bossy na Balmorze, czasy respów, lokalizacje i drop.
- Wódz Orków: Respi się na środku Doliny Seungryong (Dolina Orków) co około 4 godziny. Drop: Rękawica Złodzieja, przedmioty ulepszacze, Hwang (rzadko), zbroje na 34-48 lvl.
- Olbrzymi Żółw: Respi się na Mapie Oazie / Pustyni Yongbi co 4 godziny. Drop: Kamienie Dusz +4, biżuteria.
- Królowa Pająków: Respi się w 2. piętrze Pająków (V2) co 4 godziny. Drop: Przedmioty na wysokie poziomy, ulepszacze.
- Dziewięć Ogonów: Respi się na samym końcu Góry Sohan co 6 godzin. Drop: Wachlarze, dzwony, stalki, ulepszacze do zbroji.
- Król Demonów: Respi się w Wieży Demonów (DT) na odpowiednich piętrach.
- Umarły Rozpruwacz (Azrael): Szef Wieży Demonów (DT), respi się na samym szczycie po pokonaniu pięter. Drop: Najlepsze bronie na 75 lvl (FMS, Rib, truty - zależnie od konfiguracji serwera), zbroje Hwang, najwyższe ulepszacze.
- Czerwony Smok: Respi się w Ognistej Ziemi / Doyyumhwan co określony czas. Drop: Unikalne skrzynie i itemy.
"""

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i baza wiedzy jest w gotowości!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🧠 Sztuczna inteligencja analizuje zwoje Balmory w poszukiwaniu: **{zapytanie}**...')
    
    try:
        # Prompt dla AI oparty na naszej bazie wiedzy
        prompt = f"""
        Jesteś botem informacyjnym serwera Balmora (Metin2). 
        Gracz pyta o: "{zapytanie}"
        
        Oto baza wiedzy z forum na temat bossów:
        {BAZA_WIEDZY_BALMORA}
        
        Na podstawie powyższego tekstu udziel dokładnej, zwięzłej odpowiedzi na pytanie gracza (podaj czas respu, lokalizację lub drop, o który pyta). 
        Żadnych linków, żadnych wstępów. Same fakty po polsku. Jeśli w bazie nie ma informacji na ten temat, napisz krótko, że brak danych w poradniku.
        """
        
        ai_odpowiedz = model.generate_content(prompt).text
        
        # Wysyłamy odpowiedź tekstową od AI
        await ctx.send(ai_odpowiedz)
        
        # Wysyłamy przykładowy screen/mapę (link do oficjalnej grafiki mapy z Balmory)
        await ctx.send("Oto zrzut ekranu / mapa respów z forum:\nhttps://wiki.metin2.pl/images/d/df/Dolina_Seungryong_Boss.jpg")

    except Exception as e:
        await ctx.send('Wystąpił błąd podczas generowania odpowiedzi przez AI.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
