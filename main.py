from Server import Proxy
import asyncio


async def main():
    async with Proxy('localhost', 2048) as proxy:
        await proxy.on_close()

if __name__ == "__main__":
    asyncio.run(main())