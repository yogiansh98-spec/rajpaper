"""Discover Rajasthan results from official sites; publish verified RBSE forms only."""
import json, re, urllib.request
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

ROOT=Path(__file__).resolve().parents[1]/"data"
TODAY=datetime.now(timezone.utc).date().isoformat()
YEAR=int(TODAY[:4])
HOSTS={"rajeduboard.rajasthan.gov.in","rpsc.rajasthan.gov.in","rsmssb.rajasthan.gov.in","rssb.rajasthan.gov.in","police.rajasthan.gov.in"}
SOURCES={
 "RPSC":"https://rpsc.rajasthan.gov.in/results.aspx",
 "RSSB":"https://rsmssb.rajasthan.gov.in/page?menuName=XThs%2FFdacUY%3D&theme=Green",
 "Police":"https://police.rajasthan.gov.in/portal/RecruitmentsResults"
}
class A(HTMLParser):
 def __init__(self): super().__init__();self.href=None;self.parts=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=="a":self.href=dict(attrs).get("href");self.parts=[]
 def handle_data(self,s):
  if self.href is not None:self.parts.append(s.strip())
 def handle_endtag(self,tag):
  if tag=="a" and self.href is not None:
   self.links.append((self.href," ".join(self.parts).strip()));self.href=None

def get(url):
 u=urlparse(url)
 if u.scheme!="https" or u.hostname not in HOSTS:raise ValueError("not official")
 req=urllib.request.Request(url,headers={"User-Agent":"RajResultsBot/0.2 (official public results indexing)"})
 with urllib.request.urlopen(req,timeout=15) as r:
  end=urlparse(r.geturl())
  if end.scheme!="https" or end.hostname not in HOSTS:raise ValueError("unsafe redirect")
  return r.read(2000000).decode("utf-8","replace")

def load(path,default):
 return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def save(path,value):
 output=json.dumps(value,ensure_ascii=False,indent=2)+"\n"
 if not path.exists() or path.read_text(encoding="utf-8")!=output:
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(output,encoding="utf-8");return True
 return False

def identify(url):
 p=urlparse(url).path
 m=re.search(r"/RESULT(SUPP)?(\d{4})/",p,re.I)
 if not m:return None
 year=int(m.group(2))
 if year!=YEAR:return None
 if urlparse(url).hostname!="rajeduboard.rajasthan.gov.in":return None
 if not re.search(r"/Roll_Input\.htm$",p,re.I):return None
 section=p.upper().split("/")[-2]
 types={
 "SEV":("10","10वीं",""),"SCIENCE":("12","12वीं Science","Science"),
 "ARTS":("12","12वीं Arts","Arts"),"COMM":("12","12वीं Commerce","Commerce"),
 "SRS":("12","12वीं",""),"PRAV":("other","प्रवेशिका",""),
 "UPD":("other","वरिष्ठ उपाध्याय","")
 }
 if section not in types:return None
 category,label,stream=types[section]
 kind="revised" if "RL-RWH" in p.upper() else "supplementary" if m.group(1) else "main"
 return {
 "id":f"rbse-{year}-{kind}-{section.lower()}","title":f"RBSE {label} {kind.title() if kind!='main' else ''} Result {year}".replace("  "," "),
 "detail":f"RBSE {label} · {kind}","category":category,"stream":stream,"kind":kind,
 "board":"RBSE","year":year,"announced_on":"","verified_on":TODAY,
 "url":url,"link_type":"roll",
 "keywords":[label,"RBSE","राजस्थान बोर्ड",stream]
 }

def main():
 results_path=ROOT/"results.json";results=load(results_path,[])
 seen={x.get("url") for x in results}
 for year in (YEAR,):
  for prefix,idx in (("RESULT",f"Result{year}.htm"),("RESULTSUPP",f"Result{year}S.htm")):
   page=f"https://rajeduboard.rajasthan.gov.in/{prefix}{year}/{idx}"
   try:
    parser=A();parser.feed(get(page))
    for href,_ in parser.links:
     url=urljoin(page,href)
     p=urlparse(url)
     if p.scheme!="https" or p.hostname!="rajeduboard.rajasthan.gov.in" or not re.search(r"/Roll_Input\.htm$",p.path,re.I):continue
     if url in seen:continue
     entry=identify(url)
     if not entry:continue
     try:
      html=get(url)
      if not re.search(r"<input\b",html,re.I) or not re.search(r"roll\s*[- ]?\s*(?:no|number)|अनुक्रमांक",html,re.I):continue
     except Exception as ex:print("skip unverified form",type(ex).__name__);continue
     results.append(entry);seen.add(url);print("published verified RBSE",entry["title"])
   except Exception as ex:print("source unavailable",page,type(ex).__name__)
 save(results_path,results)
 pending_path=ROOT/"pending-results.json"
 pending={x["url"]:x for x in load(pending_path,[])}
 keywords=re.compile(r"result|merit|selection|selected|shortlist|चयन|परिणाम|नतीजा|रिजल्ट",re.I)
 for board,page in SOURCES.items():
  try:
   parser=A();parser.feed(get(page))
   for href,title in parser.links:
    url=urljoin(page,href);parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in HOSTS or len(title)<14 or not keywords.search(title):continue
    if url==page or not (parsed.path.lower().endswith(".pdf") or "result" in parsed.path.lower()):continue
    if url not in pending:pending[url]={"board":board,"title":title[:240],"url":url,"source_page":page,"first_seen_on":TODAY,"review_status":"pending"}
  except Exception as ex:print("competitive source unavailable",board,type(ex).__name__)
 save(pending_path,list(pending.values())[-400:])
 print("Published results",len(results),"Competitive candidates awaiting review",len(pending))

if __name__=="__main__":main()
