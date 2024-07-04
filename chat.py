import asyncio
from edge_tts import list_voices

async def get_available_voices():
    voices = await list_voices()
    return [voice["ShortName"] for voice in voices]

voices = asyncio.run(get_available_voices())

for i in voices:
    if "en" in i:
        print(i)

