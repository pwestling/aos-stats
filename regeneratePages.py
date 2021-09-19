import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
import os
import re
import inflect
from multiprocessing import Process

def get_nav_contents(label, page, navClass, exclusions):
    try:
        nav_element = page.find("div", attrs={"class": navClass}).find_next_sibling()
        result = [link["href"] for link in nav_element.find_all("a") if
                  link["href"] not in exclusions and link.get_text() not in exclusions]
        return result
    except:
        print(f"Could not get nav contents for {label}")


def getattr(cells, index):
    i = 0
    reali = 0
    while i <= index:
        curr = cells[reali]
        reali = reali + 1
        if curr.get("colspan"):
            i = i + int(curr.get("colspan"))
        else:
            i = i + 1
    val = cells[reali - 1].contents[0]
    if isinstance(val, NavigableString):
        return str(val)
    else:
        return "*"

def getstat(link, contents, name, append=""):
    match = re.search('ws' + name + '(Ct)?">(?P<value>[0-9-]+)?(?P<aster><img[^>]*asterix[^>]*>)?', contents)
    if not match:
        return None
    gd = match.groupdict()
    if gd["aster"]:
        return "*"
    else:
        try:
            int(gd["value"])
            return gd["value"] + append
        except:
            return gd["value"]

def colorize(colorstr, s):
    return f"[{colorstr}]{s}[-]"


def space(size, els):
    result = ""
    temp = f"{{:<{size}s}}"
    for el in els:
        result = result + temp.format(el)
    return result


def extract_unit_page(faction_name, unit_name, scroll, outdir):
    contents = requests.get(f"https://wahapedia.ru{scroll}").text
    soup = BeautifulSoup(contents, features="html.parser")
    date = datetime(2020,12,5)
    warscroll_name = str(soup.find("h3", class_="wsHeader").get_text())
    outname = os.path.join(outdir, f"{date.strftime('%Y-%m-%d')}-{unit_name}.markdown")

    print(f"Writing warscroll for {warscroll_name} to {outname}")

    move = getstat(unit_name, contents, "Move", '"')

    if not move:
        print(f"{warscroll_name} is not a unit")
        return

    wounds = getstat(unit_name, contents, "Wounds")
    save = getstat(unit_name, contents, "Save", "+")
    brave = getstat(unit_name, contents, "Bravery")

    target = soup.find("td", class_="wsHeaderCellName_RangedWeapons")
    if not target:
        target = soup.find("td", class_="wsHeaderCellName_MeleeWeapons")
    weapon_table = target.parent.parent
    weapon_rows = weapon_table.find_all(class_="wsDataRow")


    weapons = []
    for row in weapon_rows:
        result = {}
        if "wsDataCell" in row["class"] or "wsLastDataCell" in row["class"]:
            weapons.append(result)
            cells = list(row.contents)
            result["name"] = getattr(cells, 1)
            result["range"] = getattr(cells, 2)
            result["attacks"] = getattr(cells, 3)
            result["tohit"] = getattr(cells, 4)
            result["towound"] = getattr(cells, 5)
            result["rend"] = getattr(cells, 6)
            result["damage"] = getattr(cells, 7)





    statheader = colorize("56f442", space(6, ["M", "W", "B", "Sa"]))
    stats = space(6, [move, wounds, brave, save])
    weaponheader = colorize("e85545", "Weapons")
    weaponlines = []
    for weapon in weapons:
        weaponlines.append(
            "[c6c930]{name}[-]\n{range:<6} A:{attacks:<4} H:{tohit:<4} W:{towound:<4} R:{rend:<4} D:{damage:<4}".format(
                **weapon))

    block = "\n".join([statheader, stats, weaponheader, "\n".join(weaponlines)])

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
    tags: [{faction_name}]
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

    with open(outname, "w") as out:
        out.write(template)


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__))
    indexPageResponse = requests.get("https://wahapedia.ru/aos3/the-rules/matched-play-games/")
    indexPage = indexPageResponse.text
    indexPageTree = BeautifulSoup(indexPage, features="html.parser")

    factionListTree = indexPageTree.find("div", attrs={"class": "NavBtn_Factions"}).find_next_sibling(
        attrs={"class": "NavDropdown-content"})

    exclude = {'/aos3/factions/endless-spells', '/aos3/factions/legion-of-the-first-prince'}

    factionLinks = get_nav_contents("Factions", indexPageTree, "NavBtn_Factions", exclude)
    all_processes = []
    for faction in factionLinks:
        factionName = faction.split('/')[-1]
        print(f"Processing faction {factionName}")
        factionIndexPage = BeautifulSoup(requests.get(f"https://wahapedia.ru{faction}").text, features="html.parser")
        scrollLinks = get_nav_contents(factionName, factionIndexPage, "NavBtn_Datasheets", {"Warscrolls collated"})
        for scroll in scrollLinks:
            unitName = scroll.split('/')[-1]
            print(f"Processing scroll {unitName}")
            p = Process(target=extract_unit_page, args=(factionName, unitName, scroll, os.path.join(script_dir, "aosttsscrolls/_posts")))
            p.start()
            all_processes.append(p)

    [p.join() for p in all_processes]