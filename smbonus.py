import json
import sys
import html2text

from thefuzz import fuzz, process

data = []

## TODO - Auto-load from https://raw.githubusercontent.com/Xzotl42/arm5e-compendia/refs/heads/main/data/aspects.json
with open('aspects.json', 'r', encoding='utf-8') as f:
  data = json.load(f)

def search_sm_name(query):
  if query == '': return ''
  
  result, score = process.extractOne(query, data.keys(), scorer=fuzz.token_set_ratio)

  item = data[result]
  if item is None:
    return ''

  #print(f"Top match: {result}, Score: {score}")
  #print(process.extract(query, names))
  #print(json.dumps(item, indent=4, sort_keys=True))

  msg = "Searching Shape & Material Bonus for " + query + "\n"
  msg = msg + "**" + item['name'] + "**\n"
  for i in item['effects'].values():
    msg = msg + "**" + i['name'] + "**: +" + str(i['bonus']) + "\n"

  return msg

def search_sm_bonus(query):
  if query == '': return ''
  
  bonus_names = []
  for item in data.values():
    for i in item['effects'].values():
      bonus_names.append((i['name'], item))

  result, score = process.extractOne(query, bonus_names, scorer=fuzz.token_set_ratio)

  item = result[1]
  if item is None:
    return ''

  #print(f"Top match: {result}, Score: {score}")
  #print(process.extract(query, names))
  #print(json.dumps(result, indent=4, sort_keys=True))

  msg = "Shape & Material Bonus looking for a bonus for " + query + "\n"
  msg = msg + "**" + result[1]['name'] + "**\n"
  for i in item['effects'].values():
    msg = msg + "**" + i['name'] + "**: +" + str(i['bonus']) + "\n"

  return msg

print(search_sm_name('tree'))
print(search_sm_bonus('corpus'))