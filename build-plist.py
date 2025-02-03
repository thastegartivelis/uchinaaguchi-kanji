import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib.request
import csv

substitutionlist = []
with urllib.request.urlopen('https://docs.google.com/spreadsheets/d/1jexNjSt_RQ2IhARen8P3EJTjIFGO7VcdPNU1-ZzqgJk/export?gid=1190944708&format=csv') as f:
    reader = csv.DictReader(f.read().decode('utf-8').splitlines()) #.read().decode('utf-8'))
    for row in reader:
        for hiragana in row['hiragana'].split(';'):
            for kanji in [val for val in row['kanji representation'].split(';') if val != '']:
                substitutionlist.append({'substitution': kanji, 'reading': hiragana})

plist = ET.Element('plist', version="1.0")
array = ET.SubElement(plist, 'array')
for substitution in substitutionlist:
    dict = ET.SubElement(array, 'dict')
    ET.SubElement(dict, 'key').text = "phrase"
    ET.SubElement(dict, 'string').text = substitution['substitution']
    ET.SubElement(dict, 'key').text = "shortcut"
    ET.SubElement(dict, 'string').text = substitution['reading']

xmlstring = ET.tostring(plist, xml_declaration=None)
xmlstring = minidom.parseString(xmlstring).toprettyxml(indent="\t").removeprefix('<?xml version="1.0" ?>\n')

with open('transformations.plist', 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
    f.write(xmlstring)
