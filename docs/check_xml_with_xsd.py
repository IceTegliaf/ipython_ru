#!/usr/bin/python
from lxml import etree


xmlschema_doc = etree.parse("ipython_dox.xsd")
xmlschema = etree.XMLSchema(xmlschema_doc)

f = open("ipython_dox.xml")
doc = etree.parse(f)

print xmlschema.assertValid(doc)

f.close()

