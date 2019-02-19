import asyncio
import websockets
import time
import base64
from aioconsole import ainput

wss = {}

async def wakeup():
	while True:
		await asyncio.sleep(1)

async def con():
	while True:
		line = await ainput()
		line = line.split()
		
		with open("Avatars/%s.png" % line[1], "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())
		
		for ws in wss:
			if ws.closed:
				print('fuck')
			await ws.send('user %s' % line[0])
			await ws.send(encoded_string)
			print('Server -> %s | %s' % (ws.remote_address[0], line))


def avaGen(websocket):
	data = [a[1] for a in wss.values()]
	if wss[websocket][1].startswith('K'):
		data = ['T_Unknown.png' if not x.startswith('K') else x for x in data]

	else:
		data = ['T_Unknown.png' if x != wss[websocket][1] else x for x in data]

	for i, path in enumerate(data):
		with open('Cards/%s' % path, "rb") as image_file:
			data[i] = base64.b64encode(image_file.read())
	return data


async def hello(websocket, path):
	print('%s connected' % websocket.remote_address[0])
	
	if len(wss) == 10:
		websocket.close()
		return
		
	wss[websocket] = (await websocket.recv(), "T_Unknown.png")
	print(wss)
		
	await websocket.send('hs.default')
	await asyncio.sleep(0.1)
	await websocket.send(T_Placeholder)
	await asyncio.sleep(0.1)
	print(1)

	await websocket.send('hs.you')
	await asyncio.sleep(0.1)
	await websocket.send(str(list(wss.keys()).index(websocket)))

	await websocket.send('hs.players')
	await asyncio.sleep(0.1)
	await websocket.send(repr([a[0] for a in wss.values()]))
	await asyncio.sleep(0.1)
	await websocket.send(repr(avaGen(websocket)))

	for ws in wss.keys():
		if ws == websocket:
			continue

		await ws.send('player.join')
		await ws.send(repr([wss[websocket][0], T_Unknown]))
		await asyncio.sleep(0.1)
	print(2)

	closed = False
	while not closed:
		await websocket.wait_closed()
		closed = websocket.closed

	print('%s disconnected' % websocket.remote_address[0])
	print('Reason: %s' % websocket.close_reason)

	for ws in wss.keys():
		if ws == websocket:
			continue
		await ws.send('player.leave')
		await asyncio.sleep(0.1)
		await ws.send(str(list(wss.keys()).index(websocket)))
	print(3)

	del wss[websocket]

	print(wss)

start_server = websockets.serve(hello, '0.0.0.0', 6999)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().create_task(wakeup())
asyncio.get_event_loop().create_task(con())

with open('Cards/T_Placeholder.png', "rb") as image_file:
	T_Placeholder = base64.b64encode(image_file.read())

with open('Cards/T_Unknown.png', "rb") as image_file:
	T_Unknown = base64.b64encode(image_file.read())

try:
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
	pass
