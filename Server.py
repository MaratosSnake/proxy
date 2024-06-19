import asyncio
from asyncio.exceptions import CancelledError
from Request import Request, logger
from options import DOMAINS_BLACK_LIST


class Proxy:
    """
    A proxy class supporting http and https
    """
    def __init__(self, host: str, port: int, args: list):
        """
        :param host: Proxy host
        :param port: Proxy port
        """
        self.__server = None
        self.__host: str = host
        self.__port: int = port
        self.__args = set(args) if args else None
        self.__active_connections = 0
        self.__lock = asyncio.Lock()
        print(f'Additional filtering: {self.__args}')
        print(f'Base filtering: {DOMAINS_BLACK_LIST}')

    async def __read_request(self, reader, writer):
        async with self.__lock:
            self.__active_connections += 1
        try:
            # Формируем запрос
            async with (Request(reader) as request):
                is_baned_domain: bool = request.host in DOMAINS_BLACK_LIST or (request.host in self.__args if self.__args else False)
                if request.method == 'CONNECT':
                    await request.handle_connection(reader, writer, is_baned_domain)
                else:
                    await request.handle_request(reader, writer, is_baned_domain)
        except Exception as e:
            logger.exception(f'Exception: {e}')
        finally:
            async with self.__lock:
                self.__active_connections -= 1
                if self.__active_connections == 0:
                    self.__stop_server()

    async def __start_server(self):
        try:
            self.__server = await asyncio.start_server(self.__read_request, self.__host, self.__port)
            print(f'Proxy started at port: {self.__port}')
            async with self.__server:
                await self.__server.serve_forever()
        except CancelledError:
            logger.error('The Proxy has been disabled')

    def __stop_server(self):
        if self.__server:
            self.__server.close()
            asyncio.create_task(self.__server.wait_closed())
            logger.info('Proxy server stopped as there are no active connections.')
            asyncio.get_running_loop().stop()

    async def __aenter__(self):
        await self.__start_server()
        return self

    async def __aexit__(self, *args):
        pass

    async def on_close(self, timeout=600.0):
        """
        The function monitors connections to the server; if there are none, the server shuts down
        :param timeout:
        :return:
        """
        pass

