import json
import sys
import html2text

from thefuzz import fuzz, process

virtues = []
flaws = []

with open('virtues.db', 'r', encoding='utf-8') as f:
    for line in f:
        virtues.append(json.loads(line.strip()))

with open('flaws.db', 'r', encoding='utf-8') as f:
    for line in f:
        flaws.append(json.loads(line.strip()))

def search_virtue(query):
    return search_virtue_flaw(virtues, query)

def search_flaw(query):
    return search_virtue_flaw(flaws, query)

def search_virtue_flaw(data, query):

    if query == '': return ''

    names = []
    for i in data:
        names.append(i['name'])

    result, score = process.extractOne(query, names, scorer=fuzz.token_set_ratio)

    item = next((i for i in data if i['name'] == result), None)
    if item is None:
        return ''

    #print(f"Top match: {result}, Score: {score}, Index: {line}")
    #print(process.extract(query, names))
    #print(json.dumps(item, indent=4, sort_keys=True))

    name = item['name']
    description = item['system']['description']
    item_type = item['system']['type']
    impact = item['system']['impact']['value']
    source = item['system']['source']
    source_page = item['system']['page']

    text_maker = html2text.HTML2Text()
    text_maker.body_width = 0
    description = text_maker.handle(description).strip()

    if len(description) > 1500:
        description = description[:1500] + " (...)"

    msg = ''
    msg = msg + "**" + name + "**\n" 
    msg = msg + "*" + impact.capitalize() + ", " + item_type.capitalize() + "*\n"
    msg = msg + description + "\n"
    msg = msg + "*Src: " + source + " p." + str(source_page) + "*"

    return msg

#print(search_virtue(sys.argv[1]))