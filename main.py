from Server import Proxy
from database import ProxyDataBase
import asyncio


def get_client_data(session):
    while True:
        is_reg = input('Have you already registered? [y/n] >> ').lower()
        if is_reg == 'y':
            login = input('Enter your login >> ')
            password = input('Enter your password >> ')
            break
        elif is_reg == 'n':
            login = input('Enter your login >> ')
            while True:
                password = input('Enter your password >> ')
                conf_password = input('Confirm your password >> ')
                if password == conf_password:
                    session.add_user(login, password)
                    break
                else:
                    print('Passwords are different')
            break
        else:
            print('Please answer correctly')
    return login, password


async def main():
    with ProxyDataBase() as session:
        login, password = get_client_data(session)
        if session.is_user_registered(login, password):
            print('Successfully auth')
            async with Proxy('localhost', 2048) as proxy:
                await proxy.on_close()
        else:
            print("You don't have access to proxy")

if __name__ == "__main__":
    asyncio.run(main())
