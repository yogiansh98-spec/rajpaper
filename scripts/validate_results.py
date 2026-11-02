"""Fail closed if result listings contain bad, unsafe or duplicated records."""
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter

root=Path(__file__).resolve().parents[1]
items=json.loads((root/"data/results.json").read_text(encoding="utf-8"))
assert isinstance(items,list),"results must be a list"
allowed={"rajeduboard.rajasthan.gov.in","rpsc.rajasthan.gov.in","rssb.rajasthan.gov.in","rsmssb.rajasthan.gov.in","police.rajasthan.gov.in","www.police.rajasthan.gov.in","recruitment.rajasthan.gov.in"}
seen_ids=set()
seen_urls=set()
for index,item in enumerate(items):
    assert isinstance(item,dict),f"item {index} must be object"
    for key in ("id","title","board","url","kind","category","year"):
        assert item.get(key) not in (None,""),f"item {index} missing {key}"
    assert item["id"] not in seen_ids,f"duplicate id {item['id']}"
    assert item["url"] not in seen_urls,f"duplicate URL {item['url']}"
    seen_ids.add(item["id"])
    seen_urls.add(item["url"])
    address=urlparse(item["url"])
    assert address.scheme=="https" and address.hostname in allowed and not address.username and not address.password and not address.fragment, f"unsafe URL {index}"
    assert item["board"] in ("RBSE","RPSC","RSSB","Police"),f"invalid board {index}"
    assert isinstance(item["year"],int) and 2000<=item["year"]<=date.today().year+1
    assert item["kind"] in ("main","revised","supplementary","provisional","merit","cutoff","other")
    assert item.get("link_type","roll") in ("roll","pdf","result_page")
    if item["board"]=="RBSE":
        assert address.hostname=="rajeduboard.rajasthan.gov.in"
    if item.get("announced_on"):
        d=date.fromisoformat(item["announced_on"])
        assert d<=date.today(),f"future announcement {index}"
    if item.get("updated_on"):
        assert date.fromisoformat(item["updated_on"])<=date.today()
print(f"PASS: {len(items)} unique official result URLs; no unsafe or future entries")
