import os
import sys
import re
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import inflect


fname = sys.argv[1]
faction = re.search(r"faction-indexes/([a-z-]+)", fname).group(1)
post_dir = sys.argv[2]
contents = open(fname, "r").read()


soup = BeautifulSoup(contents, features="html.parser")
date = datetime.now().strftime("%Y-%m-%d")
warscroll_name = str(soup.find("h3", class_="wsHeader").string)
tagname = os.path.basename(fname)
outname = os.path.join(post_dir,f"{date}-{tagname}.markdown")

print(f"Writing warscroll for {warscroll_name} to {outname}")

def getstat(name, append=""):
  match = re.search('ws'+name+'(Ct)?">(?P<value>[0-9-]+)?(?P<aster><img[^>]*asterix[^>]*>)?', contents)
  if not match:
    print(f"File {fname} is a battalion")
    exit(0)
  gd = match.groupdict()
  if gd["aster"]:
    return "*"
  else:
    try:
      int(gd["value"])
      return gd["value"]+append
    except:
      return gd["value"]

move = getstat("Move")
wounds = getstat("Wounds")
save = getstat("Save")
brave = getstat("Bravery")


target = soup.find("td", class_="wsHeaderCellName_RangedWeapons")
if not target:
  target = soup.find("td", class_="wsHeaderCellName_MeleeWeapons")
weapon_table = target.parent.parent  
weapon_rows = weapon_table.find_all(class_="wsDataRow")

def getattr(cells, index):
  val = cells[index].contents[0]
  if isinstance(val, NavigableString):
    return str(val)
  else:
    return "*" 
weapons = []
for row in weapon_rows:
  result = {}
  if len(row.contents) == 8:
    weapons.append(result)
    cells = list(row.contents)
    result["name"] = getattr(cells, 1)
    result["range"] = getattr(cells, 2)
    result["attacks"] = getattr(cells, 3)
    result["tohit"] = getattr(cells, 4)
    result["towound"] = getattr(cells, 5)
    result["rend"] = getattr(cells, 6)
    result["damage"] = getattr(cells, 7)
  
def colorize(colorstr, s):
  return f"[{colorstr}]{s}[-]"

def space(size, els):
  result = ""
  temp = f"{{:<{size}s}}"
  for el in els:
    result = result + temp.format(el)
  return result

statheader = colorize("56f442", space(6, ["M","W","B","Sa"]))
stats = space(6, [move,wounds,brave,save])
weaponheader = colorize("e85545", "Weapons")
weaponlines = []
for weapon in weapons:
  weaponlines.append("[c6c930]{name}[-]\n{range:<6} A:{attacks:<4} H:{tohit:<4} W:{towound:<4} R:{rend:<4} D:{damage:<4}".format(**weapon))

block = "\n".join([statheader,stats, weaponheader, "\n".join(weaponlines)])

wound_count = f"{wounds}/{wounds}"
try:
  if int(wounds) <= 1:
    wound_count = ""
except:
  pass
p = inflect.engine()

unit_name = p.singular_noun(warscroll_name)
unit_name = unit_name if unit_name else warscroll_name

template = f"""---
layout: post
title:  "{warscroll_name}"
date:   {date}
source: Wahapedia
tags: [{faction}]
---

**{warscroll_name}**

**Stat Block**
```
{wound_count} {unit_name}
```

```
{block}
```


"""


out = open(outname, "w")
out.write(template)