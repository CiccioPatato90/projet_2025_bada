Project Documentation
==========

This documentation describes the key modules and functions in the aircraft performance processing pipeline. The system is divided into three main parts: data processing and performance calculations, optimization of XML coefficients, and custom performance functions from the BADA4 library.

---

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

## 1. ptd.py

**Purpose:**  
`ptd.py` processes input CSV files containing aircraft performance data, computes performance metrics using modified BADA functions, and saves the results into output CSV files.

### **Key Components:**

- **Constants:**
  - `SIGNIFICANT_DIGITS`: Precision used for rounding error metrics.
  - `BADA_VERSION`: Aircraft model version (set to `"DUMMY"` for testing).
  - `INPUT_DIR`: Directory where parsed CSV input files reside (i.e., `ptd_inputs`).
  - `OUTPUT_DIR`: Directory for saving the output CSV result files (i.e., `ptd_results`).

- **Helper Functions:**
  - `calculate_rmse(value1, value2)`:  
    - **Description:** Computes the Root Mean Square Error (RMSE) between two values.  
    - **Returns:** Rounded RMSE value using `SIGNIFICANT_DIGITS`.
    
  - `calculate_relative_error(value1, value2)`:  
    - **Description:** Computes the relative error (percentage) between two values.  
    - **Returns:** Rounded relative error.

- **Aircraft Initialization:**
  - The module loads all aircraft data using `Bada4Parser.parseAll` from the folder `reference_dummy_extracted`.  
  - A `Bada4Aircraft` instance is created using the parsed data with the aircraft name `"Dummy-TWIN-plus"`.

- **Data Processing:**
  - Input CSV files matching the pattern `Altitude_*_ISA_*.csv` (stored in `ptd_inputs`) are processed in a loop.
  - For each file:
    - The file is read into a Pandas DataFrame.
    - Altitude and ISA temperature deviation values are extracted using the utility function `extract_altitude_and_isa` from `utils/regex_parser.py`.
    - For every row in the CSV:
      - Aircraft parameters (mass, CAS, roll, Mach, drag and fuel values from the PRN file) are extracted.
      - Two performance calculations are performed:
        - **Using SKYCONSEIL model:**  
          `PTD_cruise_SKYCONSEIL([mass], [altitude_extracted], cas, isa_extracted)`
        - **Using BEAM model:**  
          `PTD_cruise_BEAM_SKYCONSEIL(mass, altitude_extracted, cas, isa_extracted, 0, roll, mach)`
      - The computed values (drag and fuel) are compared to the values from the PRN file.
    - RMSE and relative error metrics are calculated and appended to the results.
  - Finally, the results DataFrame is saved to the `ptd_results` directory with a filename prefixed by `results_`.

---

## 2. optimizerV2.py

**Purpose:**  
`optimizerV2.py` optimizes XML coefficients used in the BADA performance models. The goal is to minimize the RMSE between the calculated performance values and observed values from the input CSV files.

### **Key Components:**

- **XML and Aircraft Reinitialization:**
  - `reinit_bada_xml()`:  
    - **Description:** Re-parses the XML configuration and reinitializes the `Bada4Aircraft` instance using data from `reference_dummy_extracted`.  
    - **Returns:** A new `Bada4Aircraft` object.
  
- **XML Coefficient Update:**
  - `update_xml_coefficients(coefficients, tags, xml_parser)`:  
    - **Description:** Iterates through the given XML tags, updates each tag with the corresponding coefficients, and applies modifications via `xml_parser.modify_tag()`.
  
- **Cost Function for Optimization:**
  - `rmse_cost_function(coefficients, tags, csv_files, xml_parser, optimise_for)`:  
    - **Description:**  
      - Updates XML coefficients using `update_xml_coefficients()`.
      - Reinitializes the aircraft object.
      - For each CSV file, calculates predicted values using the corresponding PTD function (depending on whether optimizing for `drag`, `fuel`, or `fuel_beam`).
      - Computes the RMSE between observed values (from CSV) and predicted values.
    - **Returns:** The average RMSE across all CSV files.

- **Optimization Routines:**
  - `optimize_mode(optimise_for, xml_parser, csv_files)`:  
    - **Description:** Optimizes individual coefficients for a specific performance mode (`drag`, `fuel`, or `fuel_beam`) using SciPy’s `minimize` with the BFGS method.
    - **Process:**  
      - Retrieves initial guess coefficients using `xml_parser.find_tag_coefficients()`.
      - Minimizes the RMSE cost function.
    - **Output:** Prints and returns the optimal coefficients and minimized RMSE.
  
  - `optimize_mode_joint(optimise_for, xml_parser, csv_files)`:  
    - **Description:** Performs joint optimization for multiple coefficients at the same time (e.g., optimizing both drag and fuel coefficients together).
    - **Process:**  
      - Concatenates initial guesses from multiple XML tags.
      - Uses the BFGS method to minimize the RMSE cost function.
    - **Output:** Prints the optimal coefficients per tag and the minimized RMSE.

---

## 3. Custom Functions from bada4.py

**Purpose:**  
The default `ptd_cruise` function from the BADA library has been overwritten to better suit the SkyConseil requirements. Two functions are implemented:

### **3.1 PTD_cruise_SKYCONSEIL**

- **Description:**  
  A custom implementation for calculating cruise phase performance data using the SKYCONSEIL model.  
- **Parameters:**  
  - `massList`: List of aircraft mass values (kg).  
  - `altitudeList`: List of aircraft altitudes (ft).  
  - `cas`: Calibrated Air Speed (kt) taken directly from the input (bypassing ARPM speed calculations).  
  - `DeltaTemp`: Deviation from ISA temperature (K).
- **Process:**  
  - For each mass and altitude:
    - Converts altitude from feet to meters.
    - Retrieves atmospheric properties (temperature, pressure, density) based on altitude and temperature deviation.
    - Converts CAS to TAS and then computes Mach number.
    - Calculates drag and thrust based on CL (lift coefficient) and CD (drag coefficient) computations.
    - Computes fuel flow by evaluating a custom fuel flow function (`ff`).
  - **Returns:**  
    - A list (CRList) containing computed drag values and fuel flow values.
  
### **3.2 PTD_cruise_BEAM_SKYCONSEIL**

- **Description:**  
  A specialized function implementing the BEAM fuel model for cruise performance calculations using formulas derived from the Eurocontrol paper.
- **Parameters:**  
  - `mass`: Aircraft mass (kg).  
  - `altitude`: Altitude (ft).  
  - `cas`: Calibrated Air Speed (kt).  
  - `isa`: ISA temperature deviation (°C).  
  - `gamma`: Flight path angle (radians, usually set to 0 for cruise).  
  - `phi`: Bank angle (radians) used in fuel flow estimation.  
  - `Mach`: Mach number of the aircraft.
- **Process:**  
  - Retrieves BEAM-specific fuel and drag coefficients from the aircraft configuration (`AC.beam_fuel_coeffs` and `AC.beam_drag_coeffs`).
  - Converts altitude to meters and computes atmospheric properties.
  - Converts CAS to TAS.
  - Calculates drag using a combination of dynamic pressure and aircraft-specific drag terms (including a high-order Mach term).
  - Computes fuel flow based on the BEAM model:  
    \( \text{fuel\_flow} = f5 \times \Big(f0 - f1 \times \text{altitude} + (f2 + f3 \times \text{TAS} - f4 \times \text{TAS}^2) \times D \Big) \)
- **Returns:**  
  - The computed fuel flow (kg/s).

---

## 4. Additional Context

- **Integration with XML Files:**  
  The XML file (stored in `reference_dummy_extracted/dummy_TWIN_plus/dummy_TWIN_plus.xml`) contains aircraft-specific coefficients. For the system to work properly, the content of the original `bada4.py` must be replaced with the customized version from `utils/bada4.txt`.

- **Workflow Summary:**  
  1. **Data Parsing:** Convert raw data from the `reference_skyconseiil` folder into structured CSV files (using `from_CSV_for_PRN` and regex extraction).
  2. **Performance Calculation:** Run `ptd.py` to compute performance metrics based on current XML coefficients.
  3. **Optimization:** Execute `optimizerV2.py` to adjust XML coefficients for improved accuracy.
  4. **Visualization:** Re-run `ptd.py` (if needed) and visualize results using dedicated visualization scripts (`visualize2D.py` and/or `visualize3D.py`).

---

This comprehensive documentation should help new users understand the roles of each file and function within the project. For more details or code-level specifics, please refer directly to the source files.
=======
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

