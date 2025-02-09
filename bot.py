import requests
import telebot
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread

# --- UBACI SVOJE KLJUČEVE OVDE ---
TELEGRAM_BOT_TOKEN = "7866226516:AAH5oaNASTchVP9fyCT6aUv5seKbS05XG9g"
NEWS_API_KEY = "2b9b8be151a04a4d960312ad2eb86088"

# --- POVEZUJEMO BOTA ---
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Funkcija za preuzimanje vesti iz Rusije
def get_news(language="en"):
    url = f"https://newsapi.org/v2/everything?q=russia&language={language}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "ok":
        return {"error": f"Greška u preuzimanju vesti: {data.get('message', 'Nepoznata greška')}"}

    articles = data.get("articles", [])
    if not articles:
        return {"news": []}

    news_list = []
    for article in articles[:10]:  # Uzimamo samo 5 vesti
        news_list.append({
            "title": article.get("title", "Bez naslova"),
            "url": article.get("url", "#"),
        })

    return {"news": news_list}

# Komanda /news da korisnik dobije vesti
@bot.message_handler(commands=["news"])
def send_news(message):
    news = get_news()
    if "error" in news:
        bot.send_message(message.chat.id, news["error"])
    else:
        news_text = ""
        for article in news["news"]:
            news_text += f"📰 {article['title']}\n🔗 {article['url']}\n\n"
        bot.send_message(message.chat.id, news_text.strip())

# HTTP server za React aplikaciju
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/news":
            # Preuzimamo vesti na engleskom jeziku za frontend
            news = get_news(language="en")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(news).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def run_http_server():
    server_address = ("", 8080)  # Sluša na portu 8000
    httpd = HTTPServer(server_address, RequestHandler)
    print("HTTP server je pokrenut na http://localhost:8080")
    httpd.serve_forever()

# Pokretanje bota i HTTP servera u odvojenim nitima
if __name__ == "__main__":
    Thread(target=run_http_server).start()
    print("Telegram bot je pokrenut...")
    bot.polling()
