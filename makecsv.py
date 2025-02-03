import csv
import json
from itertools import product
import re

fieldnames = ["id", "hiragana", "definition (JP)"]
forbiddens = ["'", "?", "ʔ", "’"]
rows = []
# See https://stackoverflow.com/a/72427628
hira_start = int("3041", 16)
hira_end = int("3096", 16)
kata_start = int("30a1", 16)
kata_end = int("30f6", 16)

kata_to_hira = dict()
for i in range(kata_start, kata_end+1):
    kata_to_hira[chr(i)] = chr(i-kata_start+hira_start)

alternatives = {
    "ふぃ": "ひ",
    "ふぇ": "へ",
    "ぁ": "ゎ",
    "フィ": "ひ",
    "フェ": "へ",
    "ァ": "ゎ",
}

def includeAlternatives(words):
    ret = []
    modifiedWords = []
    for word in words:
        modifiedWords.append(word)
        if word.endswith('ゆん') or word.endswith('ユン'):
            modifiedWords.append(re.sub(r'(?:ゆん|ユン)$', 'いん', word, count=1))
    for word in modifiedWords:
        options = []
        i = 0
        while i < len(word):
            replaced = False
            for key, value in alternatives.items():
                if word[i:i+len(key)] == key:
                    options.append((key, value))
                    i += len(key)
                    replaced = True
                    break
            if not replaced:
                options.append((word[i],))
                i += 1
        permutations = [''.join(p) for p in product(*options)]
        ret += permutations
    return ret

with open('./okinawa_01.json') as f:
    words = json.load(f)

with open('./katsuyou_jiten.json') as f:
    conjugated = json.load(f)

print('words')
for i in words:
    if len(i['phonetics']['pronunciation']['HEIMIN']['kana']) > 0:
        original = ';'.join([rep for rep in includeAlternatives(i['phonetics']['pronunciation']['HEIMIN']['kana']+i['phonetics']['pronunciation'].get('SHIZOKU', {'kana': []})['kana']) if not any(forbidden in rep for forbidden in forbiddens)])
        for k, v in kata_to_hira.items():
            if (k in original):
                original = original.replace(k, v)
        rows.append({'id': 'word-' + str(i['id']), 'hiragana': original, 'definition (JP)': ''.join([''.join([meaning['yamato'] for meaning in meanings if 'yamato' in meaning]) for meanings in i['meaning']])})

print('conjugations')

for i in conjugated:
    rows.append({'id': 'conj-' + str(i['id']) + '-index', 'hiragana': ';'.join(includeAlternatives(i['index'])), 'definition (JP)': i['yamato']})
    for k, v in i.get('conjugation', {}).items():
        rows.append({'id': 'conj-' + str(i['id']) + '-' + k, 'hiragana': ';'.join(includeAlternatives([v])), 'definition (JP)': i['yamato']})

with open('data.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
