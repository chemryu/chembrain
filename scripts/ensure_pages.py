"""Enable Actions-based Pages using the workflow's scoped token; no personal key."""
import json,os,urllib.request,urllib.error
from pathlib import Path
api='https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/pages'
headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'Chembrain-Pages-Preview'}
def request(method,body=None):
 req=urllib.request.Request(api,method=method,headers=headers,data=json.dumps(body).encode() if body else None)
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
def main():
 try:
  try:site=request('GET')
  except urllib.error.HTTPError as e:
   if e.code!=404:raise
   site=request('POST',{'build_type':'workflow'})
  if site.get('build_type')!='workflow':site=request('PUT',{'build_type':'workflow'})
  result={'status':'configured','html_url':site.get('html_url'),'build_type':site.get('build_type')};code=0
 except urllib.error.HTTPError as e:
  try:message=json.load(e).get('message','Pages API request rejected')
  except Exception:message='Pages API request rejected'
  result={'status':'blocked','http_status':e.code,'message':str(message)[:1000]};code=1
 except Exception as e:result={'status':'unavailable','error_type':type(e).__name__};code=1
 Path('pages-config.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));return code
if __name__=='__main__':raise SystemExit(main())
