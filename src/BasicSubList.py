# -*- coding: utf-8 -*-
import json

import pandas as pd

class BasicSubList:

    def __init__(self, csvFile, platform="default", jsonFile="data\PlatformColNames.Json"):
        self.csvFile = csvFile
        self.df = pd.DataFrame()
        self.definedTiers : dict = self.preloadTierNames(platform, jsonFile)
        self.defaultTiers : dict = self.preloadTierNames("default", jsonFile)
    

    def preloadTierNames(self, platformName : str, fileName : str) -> dict:
        """
        fills the definedTiers dict with the appropriate column names for the specified platform, based on the provided JSON file

        Args:
            platformName: The name of the platform to load tier names for (e.g. "patreon", "subscribestar")
            fileName: The name of the JSON file containing the platform tier mappings (default is 'PlatformTiers.json')
        Returns:
            a dictionary containing the column names for the specified platform, or an empty dictionary if the platform is not found in the JSON file
        """
        try:
            with open(fileName) as jsonFile:
                data = json.load(jsonFile)
            return data[platformName]
        except FileNotFoundError as e:
            print(f"FATAL ERROR: Predefined Tiers file not found: {e}")
        except Exception as e:
            print(f"Error: cannot excract tier table for platform: {platformName}: {e}")


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
        #Load CSV if not already loaded
        if self.df.empty:
            self.df = pd.read_csv(self.csvFile, sep=None, engine='python')

        #Fix up formatting - Uppercase, remove surrounding whitespace, add _ between words
        self.df.columns = self.df.columns.astype(str).str.upper().str.strip().str.replace(' ', '_')

        #Check if sub name even exists
        if subName.upper() not in self.df[self.definedTiers["tierColName"].upper()].str.upper().values:
            print(f"Warning: Sub tier '{subName}' not found in {self.csvFile}. Returning empty DataFrame.")
            return pd.DataFrame()
        
        try:
            self.df = self.df[self.df[self.definedTiers["tierColName"].upper()].str.upper() == subName.upper()]
        except Exception as e:
            print(f"Error: failed to isolate {subName}: {e}")

        #Filter by active subscription status if the platform defines a status column
        statusCol = self.definedTiers.get("subStateName", "").strip()
        activeLabel = self.definedTiers.get("subStateActiveLabel", "").strip()
        if statusCol and activeLabel:
            statusColUpper = statusCol.upper().replace(' ', '_')
            if statusColUpper in self.df.columns:
                self.df = self.df[self.df[statusColUpper].str.strip().str.upper() == activeLabel.upper()]
            else:
                print(f"Warning: Status column '{statusCol}' not found in {self.csvFile}. Skipping active status filter.")

        #check if extra columns exist
        unpackedList = list(extraCols)
        for col in extraCols:
            if col.upper() not in [c.upper() for c in self.df.columns]:
                print(f"Warning: Column '{col}' not found in {self.csvFile}. Skipping this column.")
                unpackedList.remove(col)
        #Uppercase list
        unpackedList = [c.upper() for c in unpackedList]

        #Handle dates
        try:
            self.df[self.definedTiers["dateSubbedColName"].upper()] = pd.to_datetime(self.df[self.definedTiers["dateSubbedColName"].upper()], errors='coerce')
            thresholdDate = pd.Timestamp.now() - pd.Timedelta(days=minDays)
            self.df = self.df[self.df[self.definedTiers["dateSubbedColName"].upper()] <= thresholdDate]
        except Exception as e:
            print(f"Error: problem in isolating desired dates: {e}")

        #rename columns to standard names
        try:
            renameMap = {
                self.definedTiers["nameColName"].upper(): self.defaultTiers["nameColName"].upper(),
                self.definedTiers["tierColName"].upper(): self.defaultTiers["tierColName"].upper(),
                self.definedTiers["dateSubbedColName"].upper(): self.defaultTiers["dateSubbedColName"].upper(),
                self.definedTiers["grossColName"].upper(): self.defaultTiers["grossColName"].upper()
            }
            #Drop any existing columns that would conflict with the new names
            conflicting = [col for col in renameMap.values() if col in self.df.columns and col not in renameMap]
            self.df = self.df.drop(columns=conflicting)
            self.df.rename(columns=renameMap, inplace=True)
        except Exception as e:
            print("Error: failed to rename primary columns to default names") 

        #stamp names with platform header
        self.df[self.defaultTiers['nameColName'].upper()] = self.df[self.defaultTiers['nameColName'].upper()].apply(lambda x: f'{self.definedTiers["header"]} - {x}')

        #return cut down table
        newFrame = self.df[[self.defaultTiers["nameColName"].upper(), self.defaultTiers["tierColName"].upper(), self.defaultTiers["dateSubbedColName"].upper(), self.defaultTiers["grossColName"].upper(), *unpackedList]].copy()
        return newFrame


    @staticmethod
    def combineTables(tables : list) -> pd.DataFrame:
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

        mergedDF = pd.concat([c for c in tables], ignore_index=True)
        print(f"Total Combined Members: {len(mergedDF)}")
        return mergedDF
    

    @staticmethod
    def extractCol(table, val)->pd.DataFrame:
        """
            Extracts a column from a DataFrame and returns it as a list

            Args:
                table: The pandas DataFrame to extract the column from
                val: The name of the column to extract

            Returns:
                a list containing the values of the specified column
        """
        if val.upper() not in table.columns:
            raise ValueError(f"{val} not found in table. Existing columns: {table.columns}")
        
        columnList = table[val.upper()].tolist()
        return columnList