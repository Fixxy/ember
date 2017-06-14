import json
import requests
import sys

def qbLogin(s, user, password):
	try:
		reqLogin = s.post("http://127.0.0.1:8080/login", data={'username':user, 'password':password})
	except:
		print("Something went wrong in reqLogin")
		sys.exit(1)
	print("   " + str(reqLogin.status_code) + " " + str(reqLogin.reason))
	return

def qbSetPreferences(s, hdr, payload):
	json_data = "json={}".format(json.dumps(payload))
	try:
		reqPref = s.post("http://127.0.0.1:8080/command/setPreferences", headers=hdr, data=json_data)
	except:
		print("Something went wrong in reqPref")
		sys.exit(1)
	print("   " + str(reqPref.status_code) + " " + str(reqPref.reason))
	return

def qbAddMagnet(s, hdr, urls):
	try:
		reqAdd = s.post("http://127.0.0.1:8080/command/download", headers=hdr, data={'urls': urls})
	except:
		print("Something went wrong in reqAdd")
		sys.exit(1)
	print("   " + str(reqAdd.status_code) + " " + str(reqAdd.reason))
	return
