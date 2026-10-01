import discord
from discord.ext import commands
import os
from bs4 import BeautifulSoup
import google.generativeai as genai
from playwright.async_api import async_playwright

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i uruchamiam ukrytą przeglądarkę!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    await ctx.send(f'🧠 Uruchamiam ukrytą przeglądarkę, by ominąć zabezpieczenia Balmory i szukam: **{zapytanie}**...')
    
    docelowy_link = "https://forum.balmora.pl/topic/16388-bossy-czyli-co-ile-się-respią-co-z-nich-dropi-co-potrzeba-by-je-ubić-czyli-wszystko-o-bossach/"
    
    try:
        # Uruchamiamy przeglądarkę w tle, która oszukuje filtry antybotowe
        async with async_playwright() as p:
            # Używamy przeglądarki Chromium w trybie niewidocznym (headless)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
            
            # Wchodzimy na stronę i czekamy aż JavaScript i ochrona Cloudflare się zweryfikują
            await page.goto(docelowy_link, timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            # Pobieramy pełny kod HTML wyrenderowanej strony
            html_content = await page.content()
            await browser.close()

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Wyciąganie postów
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
            await ctx.send('Strona się otworzyła, ale treść jest pusta.')
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
        await ctx.send('Wystąpił błąd krytyczny podczas pracy przeglądarki w chmurze.')
        print(f"Błąd: {e}")

bot.run(os.environ.get('DISCORD_TOKEN'))
