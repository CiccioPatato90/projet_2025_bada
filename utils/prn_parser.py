import pandas as pd


class PRNFileParser:
    def __init__(self, file_path):
        """
        Initializes the PRNFileParser with the file path.

        Parameters:
            file_path (str): Path to the .txt file.
        """
        self.file_path = file_path
        self.metadata = {}
        self.dataframe = None

    def parse_file(self):
        """
        Reads the .txt file, extracts metadata and table data,
        and stores them in class attributes.
        """
        table_data = []
        columns = []

        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()

                # Extract metadata from a single line with ';'
                if ";" in line and ":" in line and not columns:
                    parts = line.split(";")
                    for part in parts:
                        key, value = part.split(":")
                        self.metadata[key.strip()] = value.strip()

                # Extract column headers
                elif ";" in line and not table_data:
                    columns = [col.strip() for col in line.split(";")]

                # Extract data rows
                elif columns and line:
                    values = [float(val) for val in line.split()]
                    table_data.append(values)

        # Convert table data to DataFrame
        self.dataframe = pd.DataFrame(table_data, columns=columns)

    def get_metadata(self):
        """
        Returns the metadata as a dictionary.
        """
        return self.metadata

    def get_dataframe(self):
        """
        Returns the table data as a pandas DataFrame.
        """
        return self.dataframe

    def get_column_as_array(self, column_name):

        if self.dataframe is None:
            raise ValueError("The dataframe is not loaded. Call parse_file() first.")

        if column_name not in self.dataframe.columns:
            raise ValueError(f"Column '{column_name}' not found in the DataFrame.")

        return self.dataframe[column_name].to_list()


