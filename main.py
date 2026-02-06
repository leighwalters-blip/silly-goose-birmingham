import asyncio
from engine.game import Game


async def main():
    game = Game()
    await game.run()

asyncio.run(main())
