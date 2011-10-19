#!/usr/bin/python
from lxml import etree


xmlschema_doc = etree.parse("dox.xsd")
xmlschema = etree.XMLSchema(xmlschema_doc)

f = open("example_dox.xml")
doc = etree.parse(f)

print xmlschema.assertValid(doc)

f.close()

