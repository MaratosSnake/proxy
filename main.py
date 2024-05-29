import asyncio
import aiohttp

async def main():
    try:
        server = await asyncio.start_server(read_request, 'localhost', 1945)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Connection on {addrs}')
        async with server:
            await server.serve_forever()
    except Exception as e:
        print(f"Error in main: {e}")

async def read_request(reader, writer):
    try:
        headers = {}
        data = []
        while True:
            new_line = await reader.readline()
            data.append(new_line.decode())
            if new_line == b'\r\n':
                break
            elif ':' in new_line.decode():
                split_line = new_line.decode().split(':')
                headers[split_line[0]] = split_line[1].strip()

        request_line = data[0].rstrip('\r\n')
        request_parts = request_line.split(' ')
        method, path, http_version = request_parts[0], request_parts[1], request_parts[2]

        print(method, path, http_version)

        if method == 'CONNECT':
            host, port = path.split(':')
            port = int(port)
            target_reader, target_writer = await asyncio.open_connection(host, port)

            writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            await writer.drain()

            async def forward(src_reader, dst_writer):
                while True:
                    data = await src_reader.read(8192)
                    if not data:
                        break
                    dst_writer.write(data)
                    await dst_writer.drain()

            await asyncio.gather(
                forward(reader, target_writer),
                forward(target_reader, writer),
            )

            target_writer.close()
            await target_writer.wait_closed()
        else:
            url = f"http://{headers['Host']}{path}"
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, allow_redirects=False) as response:
                    headers_answer = response.headers
                    response_text = await response.read()

            status_line = f"HTTP/1.1 {response.status} {response.reason}\r\n".encode()
            writer.write(status_line)

            # Отправка заголовков
            for header, value in headers_answer.items():
                if header.lower() == 'transfer-encoding':
                    continue
                writer.write(f"{header}: {value}\r\n".encode())
            writer.write(b"\r\n")

            # Отправка тела ответа
            writer.write(response_text)
            await writer.drain()
    except Exception as e:
        print(f"Error in read_request: {e}")

asyncio.run(main())
