import asyncio
from asyncio.exceptions import CancelledError
from Request import Request, logger
from options import DOMAINS_BLACK_LIST


class Proxy:
    """
    A proxy class supporting http and https
    usage "async with Proxy(...):
    """
    def __init__(self, host: str, port: int):
        """
        :param host: Proxy host
        :param port: Proxy port
        """
        self.__server = None
        self.__host: str = host
        self.__port: int = port

    async def __read_request(self, reader, writer):
        try:
            # Формируем запрос
            async with Request(reader) as request:
                is_baned_domain = request.host in DOMAINS_BLACK_LIST
                if request.method == 'CONNECT':
                    await request.handle_connection(reader, writer, is_baned_domain)
                else:
                    await request.handle_request(reader, writer, is_baned_domain)
        except Exception as e:
            logger.exception(f'Exception: {e}')

    async def __start_server(self):
        try:
            self.__server = await asyncio.start_server(self.__read_request, self.__host, self.__port)
            print(f'Proxy started at port: {self.__port}')
            async with self.__server:
                await self.__server.serve_forever()
        except CancelledError:
            logger.error('The Proxy has been disabled')

    async def __aenter__(self):
        await self.__start_server()
        return self

    async def __aexit__(self, *args):
        self.__server.close()

    async def on_close(self, timeout=600.0):
        """
        The function monitors connections to the server; if there are none, the server shuts down
        :param timeout:
        :return:
        """
        pass

