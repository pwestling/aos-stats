import os

factions = open("factions.txt", "r").readlines()

for faction in factions:
  os.mkdir(os.path.basename(faction))
  os.chdir(os.path.basename(faction))
  os.system("wget)
