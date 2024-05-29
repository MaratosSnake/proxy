from re import search

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
            elif ':' in new_line.decode():
                split_line = new_line.decode().split(':')
                self.headers[split_line[0]] = split_line[1].strip()
        self.method, self.path, self.http_version = data[0].rstrip('\r\n').split(' ')[:3]
        if 'http' in self.path:
            self.host = self.headers['Host']
            if self.path.count(':') > 1:
                self.port = 80
                self.path = '/' + self.path.replace('http://','').split(':')[1].replace(self.port, '')
            else:
                self.port = 80
                self.path = self.path.split('//')[1].repalce(self.host,'')
        else:
            self.host = self.path.split(':')[0]
            self.port = int(self.path.split(':')[1])

    async def __aenter__(self):
        await self._set()
        return self

    async def __aexit__(self, *args):
        print(f'{self.method} {self.path} {self.http_version}')

    async def send_request(self, reader, writer) -> str:
        #sending
        request = f"""{self.method} {self.path} {self.http_version}\r\nHost: {self.host}\r\n\r\n"""
        writer.write(request.encode())
        await writer.drain()

        response = await reader.read(1024)
        writer.close()
        await writer.wait_closed()

        return response.encode()

