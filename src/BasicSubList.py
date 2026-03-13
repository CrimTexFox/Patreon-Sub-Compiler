import json

import pandas as pd

class BasicSubList:

    def __init__(self, csvFile, platform="default", jsonFile="PlatformTiers.json"):
        self.csvFile = csvFile
        self.df = pd.DataFrame()
        self.definedTiers : dict = self.preloadTierNames(platform)
    

    def preloadTierNames(self, platformName : str, fileName : str = 'PlatformTiers.json') -> dict:
        """
        fills the definedTiers dict with the appropriate column names for the specified platform, based on the provided JSON file

        Args:
            platformName: The name of the platform to load tier names for (e.g. "patreon", "subscribestar")
            fileName: The name of the JSON file containing the platform tier mappings (default is 'PlatformTiers.json')
        Returns:
            a dictionary containing the column names for the specified platform, or an empty dictionary if the platform is not found in the JSON file
        """
        with open(fileName) as jsonFile:
            data = json.load(jsonFile)
        return data[platformName]


    def filterTable(self, subName : str, minDays : int = 0, *extraCols) -> pd.DataFrame:
        """
        Extracts a column from a DataFrame and returns it as a list

        Args:
            subName : Name of sub tier
            minDays: Minimum days since subbed
            *extraCols: Any extra columns to include in the returned table (must be in the original CSV)

        Returns:
            a list containing the values of the specified column
            If subName is not found, returns an empty DataFrame. If extraCols are not found, they are skipped with a warning.
        """
        #Fix up formatting - Uppercase, remove surrounding whitespace, add _ between words
        self.df.columns = self.df.columns.str.upper().str.strip().str.replace(' ', '_')

        #Check if sub name even exists
        if subName.upper() not in self.df[self.COL_TIERNAME.upper()].str.upper().values:
            print(f"Warning: Sub tier '{subName}' not found in {self.csvFile}. Returning empty DataFrame.")
            return pd.DataFrame()

        #check if extra columns exist
        unpackedList = list(extraCols)
        for col in extraCols:
            if col.upper() not in [c.upper() for c in self.df.columns]:
                print(f"Warning: Column '{col}' not found in {self.csvFile}. Skipping this column.")
                unpackedList.remove(col)
        #Uppercase list
        unpackedList = [c.upper() for c in unpackedList]

        #Handle dates
        self.df[self.COL_SUBBEDDATE.upper()] = pd.to_datetime(self.df[self.COL_SUBBEDDATE.upper()], errors='coerce')
        thresholdDate = pd.Timestamp.now() - pd.Timedelta(days=minDays)
        self.df = self.df[self.df[self.COL_SUBBEDDATE.upper()] <= thresholdDate]

        #return cut down table
        newFrame = self.df[[self.definedTiers["userName"], self.definedTiers["tierTitle"], self.definedTiers["subbedSince"], self.definedTiers["lifetime"], *unpackedList]].copy()
        return newFrame


    @staticmethod
    def combineTables(tables : list):
        """
            Combines all tables and returns a single one

            Args:
                tables: list of all dables to combine
            
            Returns:
                a single pandas dataframe with all members from all tables
        """
        
        if len(tables) == 0:
            print("No data to combine.")
            return pd.DataFrame()

        mergedDF = pd.concat(tables, ignore_index=True)
        print(f"Total Combined Members: {len(mergedDF)}")
        return mergedDF
    

    def extractCol(self, val):
        """
            Extracts a column from a DataFrame and returns it as a list

            Args:
                table: The pandas DataFrame to extract the column from
                val: The name of the column to extract

            Returns:
                a list containing the values of the specified column
        """
        columnList = self.df[val].tolist()
        return columnList