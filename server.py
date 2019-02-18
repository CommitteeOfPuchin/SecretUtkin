import asyncio
import websockets
import time
import base64


async def wakeup():
	while True:
		await asyncio.sleep(1)


async def hello(websocket, path):
	print('%s connected' % websocket.remote_address[0])
	while True:
		t = input().split()

		with open("Avatars/%s.png" % t[1], "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())

		await websocket.send('user %s' % t[0])
		await websocket.send(encoded_string)
		print('%s | %s' % (websocket.remote_address[0], t))


start_server = websockets.serve(hello, '0.0.0.0', 6999)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().create_task(wakeup())
try:
	asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
	pass
