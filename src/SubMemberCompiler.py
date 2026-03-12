# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta

def compileSubs(csvFile, platform, tierColName, nameColName, dateSubbedColName, grossColName, min_days=0):
    df = pd.read_csv(csvFile, sep=None, engine='python')
    
    # 1. Standardize columns: lowercase and underscores
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    
    # Standardize the input arguments to match the new column format
    tierCol = tierColName.lower().replace(' ', '_')
    nameCol = nameColName.lower().replace(' ', '_')
    dateCol = dateSubbedColName.lower().replace(' ', '_')
    grossCol = grossColName.lower().replace(' ', '_')

    # 2. Logic for 'final_tier' (Checking if tier_title exists first)
    if 'tier_title' in df.columns:
        df['final_tier'] = df[tierCol].fillna(df['tier_title'])
    else:
        df['final_tier'] = df[tierCol]


    ##print(df)
    # 3. Filtering
    # Note: added .str.lower() to the check to be safe
    mask = df['final_tier'].astype(str).str.lower().str.contains('loyal') & \
       df['final_tier'].astype(str).str.lower().str.contains('drone')

    df = df[mask].copy()
    
    if df.empty:
        print(f"Warning: No 'loyaldrone' entries found in {csvFile}")
        return pd.DataFrame() # Return empty instead of crashing

    try:
        # 4. Handle Dates
        # errors='coerce' turns unparseable dates into NaT (Not a Time)
        df[dateCol] = pd.to_datetime(df[dateCol], errors='coerce')
        
        # Calculate the threshold date (Today - min_days)
        threshold_date = datetime.now() - timedelta(days=min_days)
        
        # Filter for entries older than or equal to the min_days requirement
        df = df[df[dateCol] <= threshold_date]
        
        # 5. Extract and Rename
        newdf = df[['final_tier', nameCol, dateCol, grossCol]].copy()
        newdf.columns = ['tier', 'username', 'subbedDate', 'gross']
        newdf['username'] = newdf['username'].astype(str) + f"_{platform}"
        
        print(f"Successfully processed {csvFile} ({len(newdf)} members met the {min_days} day requirement)")
        return newdf
    except KeyError as e:
        print(f"Error in {csvFile}: Column {e} not found.")
        print("Available columns were:", df.columns.tolist())
        return pd.DataFrame()

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
    

def extractCol(table, val):
    """
        Extracts a column from a DataFrame and returns it as a list

        Args:
            table: The pandas DataFrame to extract the column from
            val: The name of the column to extract

        Returns:
            a list containing the values of the specified column
    """
    column_list = table[val].tolist()
    return column_list

def main():
    subStarDF = compileSubs("substarmembers.csv", "S", 'original_tier_title', 'nickname', 'subscribed', 'gross', 30)
    patreonDF = compileSubs("patreonmembers.csv", "P", 'tier', 'name', 'patronage_since_date', 'lifetime amount', 30)
    
    print("\nSubstar:\n",subStarDF)
    print("\nPatreon:\n",patreonDF)
    
    totalDF = combineTables([subStarDF, patreonDF])
    print("\nAll:\n", totalDF)
    
    print("\n"+"-"*50)
    names = extractCol(totalDF, "username")
    print("All Names:")
    print("-"*20)
    for name in names:
        print(name)
    print("-"*50)

if __name__ == "__main__":
    main()