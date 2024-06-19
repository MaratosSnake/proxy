from Server import Proxy
from database import ProxyDataBase
from proxy_logger import logger
import asyncio
import argparse


async def main(args: list[str] = None):
    with ProxyDataBase() as session:
        if session.is_user_registered(*session.get_client_data()):
            print('Successfully auth')
            async with Proxy('localhost', 2048, args) as proxy:
                await proxy.on_close()
        else:
            print("You don't have access to proxy")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', nargs='+', help='Domains to block', required=False)
    parser.add_argument('-f', help='Get domains to block from file', required=False)
    domains_to_block: list[str] = parser.parse_args().a
    if parser.parse_args().ffile:
        try:
            with open(parser.parse_args().f) as file:
                if domains_to_block:
                    domains_to_block.append(file.readline().strip())
                else:
                    domains_to_block = [file.readline().strip(), ]
        except Exception as e:
            logger.error(f'Error occurred in opening file\nError: {e}')
    asyncio.run(main(domains_to_block))
