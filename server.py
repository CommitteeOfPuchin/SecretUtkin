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
		data = ['T_Unknown' if not x.startswith('K') else x for x in data]

	else:
		data = ['T_Unknown' if x != wss[websocket][1] else x for x in data]

	return data


def console_output(ws, message):
	print('[%s]: %s' % (ws.remote_address[0], message))


async def hello(websocket, path):
	console_output(websocket, 'Client connected.')
	
	if len(wss) == 10:
		websocket.close()
		return
		
	wss[websocket] = (await websocket.recv(), "T_Unknown")
	console_output(websocket, 'Client nickname is "%s".' % wss[websocket][0])
	print('[Debug]: %s' % repr(wss))
		
	await websocket.send('hs.default')
	await asyncio.sleep(0.1)
	with open('Cards/T_Placeholder.png', "rb") as image_file:
		await websocket.send(base64.b64encode(image_file.read()))
	await asyncio.sleep(0.1)
	console_output(websocket, 'Client got default data.')

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
		await ws.send(repr([wss[websocket][0], 'T_Unknown']))
		await asyncio.sleep(0.1)
	console_output(websocket, 'Client sent to the others')

	await websocket.send('hs.ended')

	try:
		while websocket.open:
			cmd = await websocket.recv()

			if cmd == "data.request":
				path = await websocket.recv()
				try:
					with open('Cards/%s.png' % path, "rb") as image_file:
						await websocket.send(base64.b64encode(image_file.read()))
				except:
					await websocket.send('')
	except websockets.exceptions.ConnectionClosed:
		console_output(websocket, 'Client disconnected. Reason: "%s"' % websocket.close_reason)

		for ws in wss.keys():
			if ws == websocket:
				continue
			await ws.send('player.leave')
			await asyncio.sleep(0.1)
			await ws.send(str(list(wss.keys()).index(websocket)))
		console_output(websocket, 'Client purged from others.')

		del wss[websocket]

		print('[Debug]: %s' % wss)
	else:
		pass

start_server = websockets.serve(hello, '0.0.0.0', 6999)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().create_task(wakeup())
asyncio.get_event_loop().create_task(con())

try:
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
	pass
