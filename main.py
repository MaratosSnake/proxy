from Server import Proxy
from database import ProxyDataBase
import asyncio


async def main():
    with ProxyDataBase() as session:
        if session.is_user_registered(*session.get_client_data()):
            print('Successfully auth')
            async with Proxy('localhost', 2048) as proxy:
                await proxy.on_close()
        else:
            print("You don't have access to proxy")

if __name__ == "__main__":
    asyncio.run(main())
