import asyncio
from Request import Request
import aiohttp


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
        self._server = None
        self._addresses = None
        self._host: str = host
        self._port: int = port

    async def _forward(self, source_reader, dst_writer):
        while True:
            data = await source_reader.read(8192)
            if not data:
                break
            dst_writer.write(data)
            await dst_writer.drain()

    async def read_request(self, reader, writer):
        try:
            # Формируем запрос
            async with Request(reader) as request:
                if request.method == 'CONNECT':
                    target_reader, target_writer = await asyncio.open_connection(request.host, request.port)
                    writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                    await writer.drain()
                    await asyncio.gather(
                        self._forward(reader, target_writer),
                        self._forward(target_reader, writer),
                    )
                    target_writer.close()
                    await target_writer.wait_closed()
                else:
                    # async with aiohttp.ClientSession() as session:
                    #     async with session.request(request.method, request.url, headers=request.headers, allow_redirects=False) as response:
                    #         headers_answer = response.headers
                    #         response_text = await response.read()

                    target_reader, target_writer = await asyncio.open_connection(request.host, request.port)
                    writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                    await writer.drain()
                    resp = await request.send_request(target_reader, target_writer)
                    print(resp)

        except Exception as e:
            print(f"Error in read_request: {e} {request.method}")

    async def start_server(self):
        self._server = await asyncio.start_server(self.read_request, self._host, self._port)
        self._addresses = ', '.join(str(sock.getsockname()) for sock in self._server.sockets)
        print(f'Connection on {self._addresses}')
        async with self._server:
            await self._server.serve_forever()

    async def __aenter__(self):
        await self.start_server()

    async def __aexit__(self):
        self._server.close()


async def main():
    async with Proxy('localhost', 2005):
        print('Hello World!')

if __name__ == "__main__":
    asyncio.run(main())
