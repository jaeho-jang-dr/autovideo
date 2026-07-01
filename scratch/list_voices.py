import asyncio
import edge_tts

async def main():
    voices = await edge_tts.VoicesManager.create()
    ko_voices = voices.find(Language="ko")
    for v in ko_voices:
        print(f"Name: {v['Name']}, ShortName: {v['ShortName']}, Gender: {v['Gender']}")

if __name__ == "__main__":
    asyncio.run(main())
