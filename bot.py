import os
import time
import asyncio
import requests
import random
import sys
from datetime import datetime, timedelta
from discord.ext import tasks, commands
from discord import Message

print(r'''
                      .^!!^.
                  .:~7?7!7??7~:.
               :^!77!~:..^^~7?J?!^.
           .^!7??!^..  ..^^^^^~JJJJ7~:.
           7?????: ...^!7?!^^^~JJJJJJJ?.
           7?????:...^???J7^^^~JJJJJJJJ.
           7?????:...^??7?7^^^~JJJJJJJ?.
           7?????:...^~:.^~^^^~JJJJJJJ?.
           7?????:.. .:^!7!~^^~7?JJJJJ?.
           7?????:.:~JGP5YJJ?7!^^~7?JJ?.
           7?7?JY??JJ5BBBBG5YJJ?7!~7JJ?.
           7Y5GBBYJJJ5BBBBBBBGP5Y5PGP5J.
           ^?PBBBP555PBBBBBBBBBBBB#BPJ~
              :!YGB#BBBBBBBBBBBBGY7^
                 .~?5BBBBBBBBPJ~.
                     :!YGGY7:
                        ..

 🚀 join channel Airdrop Sambil Rebahan : https://t.me/kingfeeder
''')

# === Konfigurasi ===
DISCORD_USER_TOKEN = "TOKEN KAMU"
CHANNEL_ID = # Channel ID yang jadi Target
INTERVAL_MIN = 1
INTERVAL_MAX = 3
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma:2b"

# === State ===
next_reply_time = datetime.now()
pending_message = None
has_printed_wait = False

client = commands.Bot(command_prefix="!", self_bot=True)

# === AI RESPONSE ===
async def get_ai_reply(prompt):
    try:
        crypto_prompt = (
            "You are a real human chatting casually.\n"
            "Reply naturally.\n\n"

            "STRICT RULES:\n"
            "- Max 7 words\n"
            "- One sentence only\n"
            "- No explanations\n"
            "- No introductions\n"
            "- No meta phrases\n"
            "- No quotes\n"
            "- No emojis\n\n"

            "FORBIDDEN:\n"
            "sure, here's, here is, as an ai, in conclusion, this sentence\n\n"

            "STYLE:\n"
            "casual, short, direct, sometimes like 'yeah', 'true', 'same'\n\n"

            f"Message: {prompt}\n"
            "Reply:"
        )

        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": crypto_prompt,
            "stream": False
        })

        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    except Exception as e:
        print(f"[❌] Error Ollama: {e}")
        return ""

# === READY ===
@client.event
async def on_ready():
    print(f"[✅] Login sebagai {client.user}")
    reply_loop.start()
    auto_restart.start()

# === LISTEN MESSAGE ===
@client.event
async def on_message(message: Message):
    global pending_message

    if message.channel.id != CHANNEL_ID:
        return

    if message.author.id == client.user.id:
        return

    pending_message = message

# === MAIN LOOP ===
@tasks.loop(seconds=10)
async def reply_loop():
    global pending_message, next_reply_time, has_printed_wait

    if not pending_message:
        has_printed_wait = False
        return

    now = datetime.now()

    if now < next_reply_time:
        if not has_printed_wait:
            remaining = int((next_reply_time - now).total_seconds() // 60)
            print(f"[⏳] Menunggu {remaining} menit sebelum balas...")
            has_printed_wait = True
        return

    has_printed_wait = False

    # === Retry AI biar gak aneh ===
    banned_phrases = [
        "sure",
        "here's",
        "here is",
        "as an ai",
        "in conclusion",
        "this sentence"
    ]

    reply = ""

    for _ in range(3):
        reply = await get_ai_reply(pending_message.content)

        if reply and not any(p in reply.lower() for p in banned_phrases) and reply.count("\n") < 2:
            break

    if not reply:
        reply = random.choice(["yeah true", "same here", "lol true"])

    # === Kirim reply (FITUR REPLY DISCORD) ===
    try:
        await pending_message.reply(
            reply,
            mention_author=False
        )

        print(f"[✅] Balas ke {pending_message.author.name}: {reply}")

        wait_minutes = random.randint(INTERVAL_MIN, INTERVAL_MAX)
        next_reply_time = datetime.now() + timedelta(minutes=wait_minutes)
        pending_message = None

    except Exception as e:
        print(f"[❌] Gagal kirim: {e}")

# === AUTO RESTART ===
@tasks.loop(hours=2)
async def auto_restart():
    print(f"[♻️] Restart pada {datetime.now().strftime('%H:%M:%S')}")
    python = sys.executable
    os.execv(python, [python] + sys.argv)

@auto_restart.before_loop
async def before_auto_restart():
    await client.wait_until_ready()
    await asyncio.sleep(2 * 60 * 60)

# === RUN ===
client.run(DISCORD_USER_TOKEN)
