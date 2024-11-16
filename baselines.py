import json

from thefuzz import fuzz, process


data = json.load(open('actors.db', 'r',encoding='utf-8'))['items']

# tech, form, level, baseline
baselines = []

for i in data:
  level = i['data']['baseLevel']
  if level is None:
    level = 0
  baselines.append((i['data']['technique']['value'], i['data']['form']['value'], level, i['name']))  
      
data = None

def get_baseline(technique, form, max_level=1000):

  if (technique == ''):
    return '';

  if (form == ''):
    return '';

  if len(technique) > 2: technique = technique[:2]
  technique = technique.lower()
  if len(form) > 2: form = form[:2]
  form = form.lower()

  msg = ''
  results = []
  for i in baselines:
    if (i[2] <= max_level) and (technique == i[0]) and (form == i[1]):
      results.append(i)

  results.sort()

  msg = msg + "== **" + technique.capitalize() + form.capitalize() + "** ==\n"

  for r in results:
    if r[2] == 0:
      level = "General"
    else:
      level = "Level " + str(r[2])
    msg = msg + "**" + level + "**: " + r[3] + '\n'

  return msg
  
