import json, time
from deluge_client import DelugeRPCClient

def dwnTorrent(magnet, hash, dir):
	client = DelugeRPCClient('127.0.0.1', 58846, 'localclient', 'ea721c8753060acee794819a83ffafce544a18f3') #home pc
	#client = DelugeRPCClient('127.0.0.1', 58846, 'localclient', '813725b1fb8a18f15f8c9e36224347fb6d37e538') #pc at work
	
	# let's see if we can connect to the deluge daemon
	try:
		client.connect()
	except:
		return
	
	path = ''
	torrent = client.call('core.get_torrent_status', hash, [])
	
	if torrent:
		percent = float(torrent[b'file_progress'][0]*100)
		msg = 'already in deluge ({0})'.format(percent)
	else:
		client.call('core.add_torrent_magnet', magnet, {'download_location':dir})
		msg = 'not found, adding to deluge'
		
		#waiting for the files to appear
		while not (client.call('core.get_torrent_status', hash, [])[b'files']):
			time.sleep(2)
		else:
			path = client.call('core.get_torrent_status', hash, [])[b'files'][0][b'path']
			path = path.replace(b'/',b'\\').decode('utf-8')
	
	client.disconnect()
	return path