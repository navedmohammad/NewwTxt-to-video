import os
import sys
import time
import asyncio
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pyrogram.errors import FloodWait

bot = Client("bot",
             bot_token="7054832669:AAGDS-LhvS14dy3yejqMfEJOVl3arknQAps",
             api_id=20483216,
             api_hash="2518170d3dd939b3f2893cb0aae805c4")

# Dictionary to track user states
user_states = {}

async def listen(chat_id, bot):
    """
    Custom function to wait for the next message from the user in the specified chat.
    """
    future = asyncio.get_event_loop().create_future()
    async def _listener(client, message):
        if not future.done():
            future.set_result(message)
            bot.remove_handler(_listener)  # Remove handler after getting the message

    bot.add_handler(_listener)
    return await future

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"Hello [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nPress /vastavik")

@bot.on_message(filters.command("stop"))
async def stop(bot: Client, m: Message):
    await m.reply_text("STOPPED🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["vastavik"]))
async def vastavik(bot: Client, m: Message):
    editable = await m.reply_text('Send TXT file for download')
    input_msg: Message = await listen(editable.chat.id, bot)
    file_path = await input_msg.download()
    await input_msg.delete()

    try:
        with open(file_path, "r") as f:
            content = f.read()
        links = [line.split("://", 1) for line in content.split("\n") if line]
        os.remove(file_path)
    except Exception as e:
        await m.reply_text("Invalid file input.")
        os.remove(file_path)
        return

    await editable.edit(f"Total links found are {len(links)}\n\nSend the starting point (initial is 1)")
    start_msg: Message = await listen(editable.chat.id, bot)
    start_index = int(start_msg.text)
    await start_msg.delete()

    await editable.edit("Enter Batch Name")
    batch_msg: Message = await listen(editable.chat.id, bot)
    batch_name = batch_msg.text
    await batch_msg.delete()

    await editable.edit("Enter resolution (e.g., 720)")
    res_msg: Message = await listen(editable.chat.id, bot)
    resolution = res_msg.text
    await res_msg.delete()

    resolution_dict = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    res = resolution_dict.get(resolution, "UN")

    await editable.edit("Enter A Highlighter Otherwise send 👉Co👈 ")
    highlighter_msg: Message = await listen(editable.chat.id, bot)
    highlighter = highlighter_msg.text
    await highlighter_msg.delete()
    MR = highlighter if highlighter != 'Co' else "️ ⁪⁬⁮⁮⁮"

    await editable.edit("Now send the Thumb URL\nEg: https://telegra.ph/file/0633f8b6a6f110d34f044.jpg\n\nor Send no")
    thumb_msg: Message = await listen(editable.chat.id, bot)
    thumb_url = thumb_msg.text
    await thumb_msg.delete()
    await editable.delete()

    thumb_path = None
    if thumb_url.startswith("http://") or thumb_url.startswith("https://"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb_path = "thumb.jpg"

    count = start_index
    try:
        for i in range(start_index - 1, len(links)):
            url = "https://" + links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)
            elif 'videos.classplusapp' in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'YOUR_ACCESS_TOKEN'}).json()['url']
            elif '/master.mpd' in url:
                id = url.split("/")[-2]
                url = f"https://d26g5bnklkwsh4.cloudfront.net/{id}/master.m3u8"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'

            if "youtu" in url:
                ytf = f"b[height<={resolution}][ext=mp4]/bv[height<={resolution}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={resolution}]/bv[height<={resolution}]+ba/b/bv+ba"

            cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            cc = f'Vid_id  » {str(count).zfill(3)}\nTitle  » {name1} {res} {MR}.mkv\nBatch » {batch_name}\n\n'
            cc1 = f'Vid_id  » {str(count).zfill(3)}\nTitle » {name1} {MR}.pdf\nBatch » {batch_name}\n\n'

            if "drive" in url:
                try:
                    downloaded_file = await helper.download(url, name)
                    await bot.send_document(chat_id=m.chat.id, document=downloaded_file, caption=cc1)
                    count += 1
                    os.remove(downloaded_file)
                    time.sleep(1)
                except FloodWait as e:
                    await m.reply_text(str(e))
                    time.sleep(e.x)
                    continue
            elif ".pdf" in url:
                try:
                    cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                    count += 1
                    os.remove(f'{name}.pdf')
                except FloodWait as e:
                    await m.reply_text(str(e))
                    time.sleep(e.x)
                    continue
            else:
                prog = await m.reply_text(f"Downloading:-\n\nName :- {name}\nQuality - {resolution}\n\nUrl :- {url}")
                res_file = await helper.download_video(url, cmd, name)
                await prog.delete()
                await helper.send_vid(bot, m, cc, res_file, thumb_path, name, prog)
                count += 1
                time.sleep(1)

    except Exception as e:
        await m.reply_text(f"Error: {str(e)}")
    await m.reply_text("Done")

bot.run()
