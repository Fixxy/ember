import json, time
from deluge_client import DelugeRPCClient

video_formats = ('.webm', '.mkv', '.flv', '.avi', '.mov', '.wmv', '.mp4')

dHost = '127.0.0.1'
dPort = 58846
dUser = 'localclient'
dPass = '813725b1fb8a18f15f8c9e36224347fb6d37e538' #work
#dPass = 'ea721c8753060acee794819a83ffafce544a18f3' #pc at home

def dwnTorrent(magnet, hash, dir):
	client = DelugeRPCClient(dHost, dPort, dUser, dPass)
	try:
		client.connect()
	except:
		return
	
	path = ''
	torrent = client.call('core.get_torrent_status', hash, [])
	
	if torrent:
		percent = float(torrent[b'file_progress'][0]*100)
		#msg = 'already in deluge ({0})'.format(percent)
	else:
		client.call('core.add_torrent_magnet', magnet, {'download_location':dir})
		#msg = 'not found, adding to deluge'
		
		#waiting for the files to appear
		while not (client.call('core.get_torrent_status', hash, [])[b'files']):
			time.sleep(2)
		else:
			files = client.call('core.get_torrent_status', hash, [])[b'files']
			
			for format in video_formats:
				for file in files:
					if format in file[b'path'].decode('utf-8'):
						path = file[b'path'].replace(b'/',b'\\').decode('utf-8')
	
	client.disconnect()
	return path
	
def get_progress(hash):
	client = DelugeRPCClient(dHost, dPort, dUser, dPass)
	try:
		client.connect()
	except ValueError as err:
		if ('already-connected SSLSocket' in str(err)):
			pass
	
	torrent = client.call('core.get_torrent_status', hash, [])
	percent = float(torrent[b'progress'])

	client.disconnect()
	return ('%.2f' % percent)