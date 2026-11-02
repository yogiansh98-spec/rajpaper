"""Discover candidate official PDF links without publishing unverified metadata."""
import json, re, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

SOURCES = [
  "https://rpsc.rajasthan.gov.in/previousquestionpapers.aspx",
  "https://rssb.rajasthan.gov.in/questionpapers",
]
ALLOWED = {"rpsc.rajasthan.gov.in", "rssb.rajasthan.gov.in"}
class Links(HTMLParser):
  def __init__(self): super().__init__(); self.links=[]; self.href=None; self.label=[]
  def handle_starttag(self,tag,attrs):
    if tag=="a": self.href=dict(attrs).get("href"); self.label=[]
  def handle_data(self,data):
    if self.href is not None: self.label.append(data.strip())
  def handle_endtag(self,tag):
    if tag=="a" and self.href: self.links.append((self.href," ".join(self.label).strip())); self.href=None

candidates={}
for source in SOURCES:
  try:
    req=urllib.request.Request(source,headers={"User-Agent":"RajPaperBot/0.1 (public exam-paper index; respectful polling)"})
    with urllib.request.urlopen(req,timeout=15) as resp: html=resp.read(3_000_000).decode("utf-8","replace")
    parser=Links(); parser.feed(html)
    for href,label in parser.links:
      url=urljoin(source,href)
      parsed=urlparse(url)
      if parsed.scheme!="https" or parsed.hostname not in ALLOWED or not re.search(r"\\.pdf$",parsed.path,re.I): continue
      candidates[url]={"source_page":source,"title_hint":label[:160],"pdf_url":url,"status":"needs_review"}
  except Exception as e:
    print(f"Source unavailable: {source}: {type(e).__name__}")
path=Path(__file__).resolve().parents[1]/"data"/"candidates.json"
old={x["pdf_url"]:x for x in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else {}
old.update(candidates)
path.write_text(json.dumps(sorted(old.values(),key=lambda x:x["pdf_url"]),ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
print(f"Queued {len(old)} candidate links; no automatic publication.")
