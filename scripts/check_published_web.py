"""Check actual Pages HTTP publication against the triggering source marker."""
import json,sys,time,urllib.request
from urllib.parse import urlsplit
url=sys.argv[1].rstrip('/')+'/';expected=sys.argv[2]
p=urlsplit(url)
if p.scheme!='https' or not p.hostname.endswith('.github.io'):raise SystemExit('Expected a GitHub Pages HTTPS URL')
for attempt in range(12):
 try:
  def get(path):
   with urllib.request.urlopen(urllib.request.Request(url+path+'?build='+expected,headers={'Cache-Control':'no-cache'}),timeout=10) as r:return r.read()
  assert json.loads(get('version.json'))['commit']==expected
  assert b'<html lang="en"' in get('')
  data=json.loads(get('library.json'));assert data['schema_version']==1 and data['chemicals'] and data['reactions']
  print('PAGES_HTTP_PASS: exact-source marker, HTML and compact library available over public HTTPS');break
 except Exception as error:
  if attempt==11:raise SystemExit('Pages HTTP verification unavailable or stale: '+type(error).__name__)
  time.sleep(4)
