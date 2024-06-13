import asyncio
from proxy_logger import logger


class Request:
    """
    A class that includes all information about the request
    :argument reader: The reader

    Usage:
    async with Request(reader) as request:
    """

    def __init__(self, reader):
        self.headers: dict = {}
        self.method: str | None = None
        self.path: str | None = None
        self.http_version: str | None = None
        self.host: str | None = None
        self.port: int | None = None
        self.reader = reader

    async def _set(self):
        data = []
        while True:
            new_line = await self.reader.readline()
            data.append(new_line.decode())
            if new_line == b'\r\n':
                break
            elif ': ' in new_line.decode():
                split_line = new_line.decode().split(':')
                self.headers[split_line[0]] = split_line[1].strip()
        self.method, self.path, self.http_version = data[0].rstrip('\r\n').split(' ')[:3]
        if 'http' in self.path:
            self.host = self.headers['Host']
            if self.path.count(':') > 1:
                self.port = int(self.path.replace('http://', '').split(':')[1].split('/')[0])
                self.path = self.path.replace('http://', '').split(':')[1].replace(str(self.port), '')
            else:
                self.port = 80
                self.path = self.path.split('//')[1].replace(self.host, '')
        else:
            self.host = self.path.split(':')[0]
            self.port = int(self.path.split(':')[1])

    def __str__(self):
        return f'{self.method} - {self.path} - {self.http_version} - {self.host}:{self.port}'

    async def __aenter__(self):
        await self._set()
        logger.info(self)
        return self

    async def __aexit__(self, *args):
        print(self)

    async def _forward(self, source_reader, dst_writer):
        while True:
            try:
                data = await asyncio.wait_for(source_reader.read(8192), timeout=60.0)
                if not data:
                    break
                dst_writer.write(data)
                await dst_writer.drain()
            except (asyncio.TimeoutError, ConnectionResetError, BrokenPipeError, Exception):
                break

    async def handle_connection(self, client_reader, client_writer, is_baned_domain: bool):
        if is_baned_domain:
            response = (
                "HTTP/1.1 403 Forbidden\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n\r\n"
                "<html><body><h1>403 Forbidden</h1><p>Доступ к этому сайту запрещен.</p></body></html>\r\n"
            )
            client_writer.write(response.encode())
            await client_writer.drain()
            client_writer.close()
            logger.info(f"Access to {self.host} is forbidden")
            return
        try:
            target_reader, target_writer = await asyncio.open_connection(self.host, self.port)
            client_writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            await client_writer.drain()
            await asyncio.gather(
                self._forward(client_reader, target_writer),
                self._forward(target_reader, client_writer),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f'error in CONNECT: {e}')
        finally:
            client_writer.close()
            if target_writer:
                target_writer.close()

    async def handle_request(self, client_reader, client_writer, is_baned_domain: bool):
        if is_baned_domain:
            response = (
                "HTTP/1.1 403 Forbidden\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n\r\n"
                "<html><body><h1>403 Forbidden</h1><p>Доступ к этому сайту запрещен.</p></body></html>\r\n"
            )
            client_writer.write(response.encode())
            await client_writer.drain()
            client_writer.close()
            logger.info(f"Access to {self.host} is forbidden")
            return
        try:
            dst_reader, dst_writer = await asyncio.open_connection(self.host, self.port)
            # Отправка запроса
            request = f"{self.method} {self.path} {self.http_version}\r\n"
            dst_writer.write(request.encode())
            for header, value in self.headers.items():
                if header.lower() == 'transfer-encoding':
                    continue
                dst_writer.write(f'{header}: {value}\r\n'.encode())
            dst_writer.write(b'\r\n')
            await dst_writer.drain()

            await asyncio.gather(
                self._forward(client_reader, dst_writer),
                self._forward(dst_reader, client_writer),
                return_exceptions=True
            )
            logger.info(self)
        except Exception as e:
            logger.error(f'Error in handling HTTP: {e} | Request: {self}')
        finally:
            client_writer.close()
            if dst_writer:
                 dst_writer.close()
