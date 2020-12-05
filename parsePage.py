import os
import sys
import re
from bs4 import BeautifulSoup, NavigableString


fname = sys.argv[1]
contents = open(fname, "r").read()

def getstat(name):
  match = re.search('ws'+name+'(?P<isvar>Ct)?">(?P<value>[0-9]+)?', contents)
  gd = match.groupdict()
  if gd["isvar"]:
    return "*"
  else:
    return gd["value"]

move = getstat("Move")
wounds = getstat("Wounds")
save = getstat("Save")
brave = getstat("Bravery")

soup = BeautifulSoup(contents, features="html.parser")
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

print("\n".join([statheader,stats, weaponheader, "\n".join(weaponlines)]))

# template = "="[56f442]M    W    B     Sa[-]"&CHAR(10)&H13&I13&J13&K13&CHAR(10)&"[e85545]Weapons[-]"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,query(AOSWeapons!A:J,"select I where A = """&A13&""" label I ''"))&CHAR(10)&"[dc61ed]Abilities[-]"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,query(AOSAbilities!A:K,"select F where A = """&A13&""" label F ''")) 
