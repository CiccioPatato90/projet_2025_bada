Project Documentation
======

XMLParser
-----------


A class for parsing and modifying XML files.

 **Methods:**

* `len_tags(tag_name)`: Returns the count of occurrences of a given tag.

* `find_tag(tag_name)`: Finds and prints all occurrences of a tag.

* `find_tag_coefficients(tag_name)`: Retrieves numerical values from a tag.

* `modify_tag'(tag_name, new_value)` : Modifies XML tag values and updates the file.

**Utility Function:**

* `change_multiple_tags(list_of_tags, dict_of_list_of_values, xml_parser)`: Updates multiple XML tags with new values.

PRNFileParser
-----------

A class for parsing .prn files to extract metadata and structured data.

**Methods:**

* `parse_file()`: Reads the file, extracts metadata, and loads data into a DataFrame.

* `get_metadata()`: Returns extracted metadata.

* `get_dataframe()`: Returns structured data as a pandas DataFrame.

* `get_column_as_array(column_name)`: Retrieves a specific column as an array.

Data Extraction & CSV Handling
---

A script extracts specific altitude-temperature data from .prn files and saves them as CSVs.

**Key Features:**

* Detects altitude and ISA temperature.

* Extracts corresponding table data.

* Saves structured data into CSV format.

* Includes a cleanup function to delete generated CSV files.

from_CSV_to_PTD
---

**Methods**

* `calculate_tas(mach, temperature)`: Computes the True Airspeed (TAS) using Mach number and air temperature.

* `calculate_isa_deviation(altitude_feet, temperature_real)`: Calculates the deviation from International Standard Atmosphere (ISA) temperature at a given altitude.

* `calculate_drag()`: Placeholder function for drag computation.

* `process_file(file_path)`: Processes a given CSV file to extract relevant flight data, apply transformations, and save structured data into categorized CSV files.

**Key features**

* Reads and filters flight data, focusing on cruise conditions.

* Computes derived metrics like TAS and ISA deviation.

* Segments data based on altitude and ISA deviation thresholds.

* Saves structured flight data into categorized CSV files.

* Supports automated batch processing of multiple CSV files.

PTD
---
