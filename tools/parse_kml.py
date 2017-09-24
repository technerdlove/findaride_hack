#!/usr/bin/python3

import json
import sys
from xml.etree import ElementTree
import xml


def recurse_print(node, indent=""):
    if node.tag == "value":
        print(indent, "value is", node.text)
    else:
        print(indent, node.tag, node.attrib)
    new_indent = indent + "  "
    for child in node:
        recurse_print(child, new_indent)


def print_tag(node, tag_name, out, print_values=False):
    if print_values and node.tag == "value":
        out.send(node.text)
    elif node.tag == "Data" and node.attrib.get("name") == tag_name:
        print_values = True

    for child in node:
        print_tag(child, tag_name, out, print_values)

def recurse_placemarks(node, get_name, placemark=None):
    if node.tag.endswith("Placemark"):
        placemark = node

    if placemark:
        name = get_name(node)
        if name:
            ElementTree.SubElement(placemark, "name").text = name

    for child in node:
        recurse_placemarks(child, get_name, placemark)

# TODO: can get namespace from xml
def add_name_to_placemarks(filename, namespace, get_name):
    # register_namespace prevents python from prepending ns0
    ElementTree.register_namespace('', namespace)
    tree = ElementTree.parse(filename)
    root = tree.getroot()

    recurse_placemarks(root, get_name)

    out = "./out.xml"
    ElementTree.ElementTree(root).write(out)
    print("Wrote to ", out)


def main():
    def _shuttle_name(node):
        if (node.tag.endswith("Data") and
            node.attrib and
            node.attrib.get("name") == "shuttlenam"):
            for child in node:
                if child.tag == "value":
                    return child.text
        return None

    add_name_to_placemarks("../data/King_County_Community_Shuttles.kml",
                           "http://earth.google.com/kml/2.2",
                           _shuttle_name)


def boop():
    results = []
    def get_shuttlenames():
        while True:
            name = (yield)
            results.append('"shuttlenam": "{}"'.format(name))
    out = get_shuttlenames()
    next(out)
    print_tag(root, "shuttlenam", out)
    out.close()

    for result in sorted(results):
        print(result)

if __name__ == "__main__":
    main()
