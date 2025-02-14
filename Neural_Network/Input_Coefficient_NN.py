from symtable import Class

from utils.XML_Parser import XMLParser
import numpy as np

class Input_Coefficient_NN:
    def __init__(self,xml_parser,tags):
        self.xml_parser = xml_parser
        self.tags = tags
    def create(self):
        max_len = max(len(self.xml_parser.find_tag_coefficients(tag)) for tag in self.tags)
        dummy_targets = np.full((max_len, len(self.tags)), np.nan)
        # Remplir avec les vraies valeurs
        for j, tag in enumerate(self.tags):
            coeffs = self.xml_parser.find_tag_coefficients(tag)
            dummy_targets[:len(coeffs), j] = coeffs  # Remplit les valeurs connues
        return dummy_targets