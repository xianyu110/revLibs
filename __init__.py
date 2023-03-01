import asyncio
from EdgeGPT import Chatbot


async def main():
    bot = Chatbot(cookiePath='./cookies.json')
    # bot = Chatbot()
    print(await bot.ask(prompt="Hello world"))
    await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
