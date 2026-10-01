import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Nasza lokalna baza wiedzy o bossach na Balmorze
BAZA_WIEDZY = {
    "orzek": "Wódz Orków respi się na środku Doliny Seungryong (Dolina Orków) co około 4 godziny. Drop: Rękawica Złodzieja, ulepszacze, zbroje na 34-48 lvl.",
    "żółw": "Olbrzymi Żółw respi się na Pustyni Yongbi (Mapa Oaza) co 4 godziny. Drop: Kamienie Dusz +4, biżuteria.",
    "pająk": "Królowa Pająków respi się w 2. piętrze Pająków (V2) co 4 godziny. Drop: Przedmioty na wysokie poziomy, ulepszacze.",
    "ogony": "Dziewięć Ogonów respi się na samym końcu Góry Sohan co 6 godzin. Drop: Wachlarze, dzwony, stalki.",
    "rozpruwacz": "Umarły Rozpruwacz (Azrael) respi się na szczycie Wieży Demonów (DT). Drop: Bronie na 75 lvl (FMS, Rib), zbroje Hwang."
}

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i baza wiedzy jest aktywna!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
     zapytanie_lower = zapytanie.lower()
     odpowiedz = None
     
    # Szukamy pasującego słowa kluczowego w bazie
    for klucz, info in BAZA_WIEDZY.items():
        if klucz in zapytanie_lower or zapytanie_lower in klucz:
            odpowiedz = info
            break
            
    if not odpowiedz:
        # Jeśli nie znalazł konkretnego klucza, zwraca ogólny spis
        odpowiedz = "Oto dostępne bossy w bazie Balmory: Wódz Orków, Olbrzymi Żółw, Królowa Pająków, Dziewięć Ogonów, Umarły Rozpruwacz. Wpisz dokładniej, o którego pytasz!"

    await ctx.send(f"**Wynik z bazy wiedzy Balmory:**\n{odpowiedz}")
    
    # Automatycznie wrzucamy screen/mapę z forum
    await ctx.send("Oto zrzut ekranu / mapa respów z forum:\nhttps://wiki.metin2.pl/images/d/df/Dolina_Seungryong_Boss.jpg")

bot.run(os.environ.get('DISCORD_TOKEN'))
