import os
import discord
from discord.ext import commands, tasks
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading
import requests

# 환경변수로부터 설정값 가져오기
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
VOICE_CHANNEL_ID = int(os.getenv("DISCORD_VC_ID"))

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

current_voice_members = []
winners = []
excluded_names = ["달해나"]  # 제외할 닉네임 목록

@bot.event
async def on_ready():
    print(f"✅ 봇 로그인됨: {bot.user.name}")
    update_voice_members.start()

@tasks.loop(seconds=5)
async def update_voice_members():
    global current_voice_members
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ GUILD_ID를 찾을 수 없습니다.")
        return
    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if channel and channel.members:
        current_voice_members = [
            m.display_name for m in channel.members
            if not m.bot and m.display_name not in excluded_names
        ]
    else:
        current_voice_members = []

@bot.command(name="로테")
async def open_roulette(ctx):
    url = "https://your-railway-app-name.up.railway.app/"  # 배포된 주소로 수정
    await ctx.send(f"📺 룰렛 페이지: {url}")

@bot.command(name="내전")
async def pinball_member_list(ctx):
    if not current_voice_members:
        await ctx.send("⚠ 현재 채널에 참가자가 없습니다.")
        return
    name_list = ", ".join(current_voice_members)
    link = "https://bluedell.com/%ED%95%80%EB%B3%BC-%EB%9E%9C%EB%8D%A4-%EC%88%AB%EC%9E%90-%EB%BD%91%EA%B8%B0-%EA%B3%B5%EB%BD%91%EA%B8%B0/"
    await ctx.send(f"👥 현재 내전 참가자:\n`{name_list}`\n\n📍 추첨 링크: {link}")

@bot.command(name="ㅎ")
async def show_winners(ctx):
    try:
        res = requests.get("https://your-railway-app-name.up.railway.app/winners")
        data = res.json()
        if data:
            await ctx.send("🏆 당첨자 목록: " + ", ".join(data))
        else:
            await ctx.send("❗ 아직 당첨자가 없습니다!")
    except:
        await ctx.send("⚠ 당첨자 목록을 불러오지 못했습니다.")

# Flask 앱 설정
app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route("/")
def serve_roulette():
    return render_template("roulette.html")

@app.route("/names", methods=["GET"])
def get_names():
    return jsonify(current_voice_members)

@app.route("/winner", methods=["POST"])
def post_winner():
    data = request.get_json()
    name = data.get("name")
    if name and name not in winners:
        winners.append(name)
        print(f"✅ 당첨자 등록됨: {name}")
        return jsonify({"status": "ok", "message": f"{name} saved"})
    return jsonify({"status": "error", "message": "Invalid or duplicate"}), 400

@app.route("/winners", methods=["GET"])
def get_winners():
    return jsonify(winners)

# Flask 실행 함수
def run_flask():
    app.run(host="0.0.0.0", port=5000)

# 메인 실행
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
