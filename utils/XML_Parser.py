import xml.etree.ElementTree as ET

class XMLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()

    def len_tags(self, tag_name):
        return len(self.root.findall(f".//{tag_name}"))

    def find_tag(self, tag_name):
        elements = self.root.findall(f".//{tag_name}")
        for elem in elements:
            print(f"Found: {elem.tag} -> {elem.text}")
        return elements

    def find_tag_coefficients(self, tag_name):
        elements = self.root.findall(f".//{tag_name}")
        res = []
        for elem in elements:
            print(f"Found: {elem.tag} -> {elem.text}")
            res.append(float(elem.text))
        return res

    def modify_tag(self, tag_name, new_value):
        elements = self.root.findall(f".//{tag_name}")
        if not elements:
            print(f"No {tag_name} tag found.")
            return

        if len(new_value) != len(elements):
            print(f"Error: For {tag_name} provided {len(new_value)} values, but found {len(elements)} elements.")
            return

        for elem, new_value in zip(elements, new_value):
            elem.text = str(new_value)

        self.tree.write(self.file_path, encoding="utf-8", xml_declaration=True)
        print(f"Updated {tag_name} to {new_value}")


def change_multiple_tags(list_of_tags, dict_of_list_of_values, xml_parser):
    for tag in list_of_tags:
        print(f"Tag: {tag}")
        if dict_of_list_of_values[tag] is None:
            tab = xml_parser.find_tag(tag)
            new_values = [None] * len(tab)
            for i in range(len(tab)):
                new_values[i] = round(float(tab[i].text))  # here if you want to change based on the value found in the doc or just do nothing
            xml_parser.modify_tag(tag, new_values)
            xml_parser.find_tag(tag)
        else:
            tab = xml_parser.find_tag(tag)
            xml_parser.modify_tag(tag, dict_of_list_of_values[tag])
            xml_parser.find_tag(tag)