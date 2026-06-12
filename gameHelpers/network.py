import asyncio
import json
import socket

class gameServer:
    def __init__(self, port=5555):
        self.port             = port
        self.prServer         = None
        self.clients          = {}
        self.prNextId         = 1
        self.prMessageQueues  = {}

    async def start(self):
        self.prServer = await asyncio.start_server(
            self.prHandleClient, '0.0.0.0', self.port
        )
        hostIp = socket.gethostbyname(socket.gethostname())
        print(f"network: [host] server started on {hostIp}:{self.port}")
        return hostIp, self.port

    async def prHandleClient(self, reader, writer):
        clientId                       = self.prNextId
        self.prNextId                 += 1
        queue                          = asyncio.Queue()
        self.prMessageQueues[clientId] = queue
        self.clients[clientId]         = {"reader": reader, "writer": writer, "name": f"Player {clientId}"}

        try:
            await self.prSend(writer, {"type": "welcome", "id": clientId})
            while True:
                data = await asyncio.wait_for(reader.readline(), timeout=None)
                if not data:
                    break
                msg                    = json.loads(data.decode().strip())
                print(f"network: [host <- client] {msg.get('type', '?')}")
                if msg.get("type") == "join":
                    self.clients[clientId]["name"] = msg.get("name", f"Player {clientId}")
                    await self.prBroadcastPlayerList()
                await queue.put(msg)
        except (asyncio.CancelledError, ConnectionError, json.JSONDecodeError):
            pass
        finally:
            self.prMessageQueues.pop(clientId, None)
            self.clients.pop(clientId, None)
            await self.prBroadcastPlayerList()

    async def prSend(self, writer, msg):
        data = json.dumps(msg) + "\n"
        print(f"network: [host -> client] {msg.get('type', '?')}")
        writer.write(data.encode())
        await writer.drain()

    async def prBroadcastPlayerList(self):
        players = [{"id": 0, "name": "host"}] + [
            {"id": cid, "name": info["name"]}
            for cid, info in self.clients.items()
        ]
        await self.broadcast({"type": "playerList", "players": players})

    async def broadcast(self, msg):
        for cid, info in list(self.clients.items()):
            try:
                await self.prSend(info["writer"], msg)
            except Exception:
                pass

    async def getMessages(self):
        msgs = []
        for cid, queue in list(self.prMessageQueues.items()):
            while not queue.empty():
                m = await queue.get()
                m["prFrom"] = cid
                msgs.append(m)
        return msgs

    def getPlayerList(self):
        return [{"id": 0, "name": "host"}] + [
            {"id": cid, "name": info["name"]}
            for cid, info in self.clients.items()
        ]

    async def stop(self):
        for info in list(self.clients.values()):
            try:
                info["writer"].close()
            except Exception:
                pass
        self.clients.clear()
        self.prMessageQueues.clear()
        if self.prServer:
            self.prServer.close()
            await self.prServer.wait_closed()


class gameClient:
    def __init__(self, host="127.0.0.1", port=5555, name="Player"):
        self.host            = host
        self.port            = port
        self.name            = name
        self.reader          = None
        self.writer          = None
        self.playerId        = None
        self.prMessageQueue  = asyncio.Queue()
        self.prRunning       = False

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.prRunning           = True
            asyncio.create_task(self.prReadLoop())
            await self.send({"type": "join", "name": self.name})
            return True
        except (ConnectionRefusedError, OSError) as e:
            print(f"network.py: [CLIENT]: failed to connect to {self.host}:{self.port} - {e}")
            return False

    async def prReadLoop(self):
        try:
            while self.prRunning:
                data = await self.reader.readline()
                if not data:
                    break
                msg = json.loads(data.decode().strip())
                print(f"network: [client <- host] {msg}")
                if msg.get("type") == "welcome":
                    self.playerId = msg["id"]
                await self.prMessageQueue.put(msg)
        except (asyncio.CancelledError, ConnectionError):
            pass
        finally:
            self.prRunning = False

    async def send(self, msg):
        if self.writer is None:
            return
        data = json.dumps(msg) + "\n"
        print(f"network: [client -> host] {msg}")
        self.writer.write(data.encode())
        await self.writer.drain()

    async def getMessages(self):
        msgs = []
        while not self.prMessageQueue.empty():
            msgs.append(await self.prMessageQueue.get())
        return msgs

    async def disconnect(self):
        self.prRunning = False
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
