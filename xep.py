import asyncio
import json
import sys
import traceback

@asyncio.coroutine
def start(host, port):
    reader, writer = yield from asyncio.open_connection(host, port)
    def send_message(obj):
        if isinstance(obj, str):
            text = obj
        elif isinstance(obj, bytes):
            text = obj.decode('utf-8', 'replace')
        else:
            text = str(obj)
        writer.write(json.dumps({
            "Type": "message",
            "Data": {
                "body": text
            }
            }).encode('utf-8') + b'\n'
        )
    while True:
        line = yield from reader.readline() 
        msg = json.loads(line.decode('utf-8', 'ignore'))
        if msg['Type'] == 'ping':
            print("ping received")
            writer.write(json.dumps({
                "Type": "pong"
                }).encode('utf-8') + b'\n'
            )
        elif msg['Type'] == 'message':
            print("msg : {}".format(msg))
            body = msg['Data']['body']
            if body.startswith('py>'):
                try:
                    exec(body[3:])
                except BaseException as e:
                    send_message(traceback.format_exc())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(sys.argv[1], sys.argv[2]))
    loop.close()
