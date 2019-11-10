import urllib.request
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

top_level_url = "http://localhost:8080/requests/status.xml"
password_mgr.add_password(None, top_level_url, '', 'foo')

handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

opener = urllib.request.build_opener(handler)



#This sets up the https connection
#req = urllib.request.Request('http://localhost:8080/requests/status.xml')
#req.add_header('Authorization', 'Basic :foo')


with opener.open(top_level_url) as f:
    print(f.read().decode('utf-8'))

