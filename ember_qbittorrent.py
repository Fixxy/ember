import json
import requests

def qbLogin(s, user, password):
	try:
		reqLogin = s.post("http://127.0.0.1:8080/login", data={'username':user, 'password':password})
	except reqLogin.exceptions.RequestException as e:
		print(e)
		sys.exit(1)
	print("   " + str(reqLogin.status_code) + " " + str(reqLogin.reason))
	return

def qbSetPreferences(s, hdr, payload):
	json_data = "json={}".format(json.dumps(payload))
	try:
		reqPref = s.post("http://127.0.0.1:8080/command/setPreferences", headers=hdr, data=json_data)
	except reqPref.exceptions.RequestException as e:
		print(e)
		sys.exit(1)
	print("   " + str(reqPref.status_code) + " " + str(reqPref.reason))
	return

def qbAddMagnet(s, hdr, urls):
	try:
		reqAdd = s.post("http://127.0.0.1:8080/command/download", headers=hdr, data={'urls': urls})
	except reqAdd.exceptions.RequestException as e:
		print(e)
		sys.exit(1)
	print("   " + str(reqAdd.status_code) + " " + str(reqAdd.reason))
	return
