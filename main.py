import asyncio
import json
import time
import aiohttp
import websockets
import sys
import os

# CONFIGURATION - Use variáveis de ambiente ou edite aqui
TOKEN = os.getenv("DISCORD_TOKEN", "SEU_TOKEN_AQUI")
CATEGORY_ID = os.getenv("CATEGORY_ID", "SEU_CATEGORY_ID_AQUI")
RESPONSE_MSG = os.getenv("RESPONSE_MSG", "Olá! Como posso ajudar você hoje?")

# API URLS
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
API_BASE = "https://discord.com/api/v10"

class MaxPerformanceBot:
    def __init__(self, token, category_id, message):
        self.token = token
        self.category_id = str(category_id)
        self.message = message
        self.session = None
        self.processed = set()
        self.last_sequence = None
        
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.payload = json.dumps({"content": self.message}).encode('utf-8')

    async def start(self):
        # Conector ultra-agressivo
        connector = aiohttp.TCPConnector(
            limit=0,
            ttl_dns_cache=600,
            use_dns_cache=True,
            force_close=False,
            enable_cleanup_closed=True
        )
        
        async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
            self.session = session
            # Aquecimento instantâneo
            try: await session.get(f"{API_BASE}/users/@me")
            except: pass
            
            await self.connect_gateway()

    async def connect_gateway(self):
        async with websockets.connect(GATEWAY_URL, max_size=None, ping_interval=None) as ws:
            print(f"[*] MODO MÁXIMO ATIVO")
            
            cat_id = self.category_id
            json_loads = json.loads
            create_task = asyncio.create_task

            async for message in ws:
                # DETECÇÃO ULTRA-RÁPIDA
                if cat_id in message and '"t":"CHANNEL_CREATE"' in message:
                    try:
                        data = json_loads(message)
                        if data.get('t') == 'CHANNEL_CREATE':
                            d = data['d']
                            if str(d.get('parent_id')) == cat_id:
                                cid = d['id']
                                # PROTEÇÃO ABSOLUTA CONTRA DUPLICATAS
                                if cid not in self.processed:
                                    self.processed.add(cid)
                                    # DISPARO ÚNICO E INSTANTÂNEO
                                    create_task(self.fire(cid))
                    except: pass

                # Manutenção mínima do gateway
                if '"op":10' in message:
                    data = json_loads(message)
                    interval = data["d"]["heartbeat_interval"] / 1000
                    create_task(self.heartbeat(ws, interval))
                    await self.identify(ws)
                elif '"s":' in message:
                    try:
                        data = json_loads(message)
                        self.last_sequence = data.get("s", self.last_sequence)
                        if data.get("t") == "READY":
                            print(f"[*] ON: {data['d']['user']['username']}")
                    except: pass

    async def fire(self, cid):
        """Disparo único e máximo de velocidade."""
        url = f"{API_BASE}/channels/{cid}/messages"
        start = time.perf_counter()
        
        try:
            async with self.session.post(url, data=self.payload) as resp:
                lat = (time.perf_counter() - start) * 1000
                if resp.status == 200:
                    print(f"[+] SHOT! {lat:.2f}ms")
                elif resp.status == 404:
                    # Retry único para propagação
                    await asyncio.sleep(0.08)
                    async with self.session.post(url, data=self.payload) as r:
                        if r.status == 200:
                            lat2 = (time.perf_counter() - start) * 1000
                            print(f"[+] RETRY WIN! {lat2:.2f}ms")
                elif resp.status == 429:
                    print(f"[-] RATE LIMIT")
                else:
                    print(f"[-] ERR {resp.status}")
        except Exception as e:
            print(f"[-] EXC: {e}")

    async def identify(self, ws):
        await ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {"os": "Windows", "browser": "Chrome", "device": ""},
                "compress": False,
                "large_threshold": 50,
                "intents": 513  # GUILDS + GUILD_MESSAGES
            }
        }))

    async def heartbeat(self, ws, interval):
        while True:
            await asyncio.sleep(interval)
            try: await ws.send(json.dumps({"op": 1, "d": self.last_sequence}))
            except: break

if __name__ == "__main__":
    bot = MaxPerformanceBot(TOKEN, CATEGORY_ID, RESPONSE_MSG)
    try: asyncio.run(bot.start())
    except KeyboardInterrupt: pass
