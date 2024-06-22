import os
from dotenv import load_dotenv
from typing import Final

from discord import Intents, Client, Message, FFmpegPCMAudio
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

intents: Intents = Intents.default()
intents.message_content = True
intents.voice_states = True


client: Client = Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as a start bot {client.user}")


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("(Message was empty because intents were not enabled probably)")
        return

    if is_private := user_message[0] == "?":
        user_message = user_message[1:]
    try:
        response: str = get_response(user_message)
        (
            await message.author.send(response)
            if is_private
            else await message.channel.send(response)
        )
    except Exception as e:
        print(e)


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    # starting message with ? will send the response in private
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)
    print(f"{username} in {channel} said: {user_message}")

    await send_message(message, user_message)

if __name__ == "__main__":
    client.run(TOKEN)
