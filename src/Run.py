# -*- coding: utf-8 -*-
from BasicSubList import BasicSubList

from gui.GUI_Practice import MainWindow
from PySide6.QtWidgets import QApplication

def main():
    #create objects
    patreonList = BasicSubList("patreonmembers.csv", platform="patreon")
    substarList = BasicSubList("substarmembers.csv", platform="subscribestar")

    #get all tables
    allTables = []
    allTables.append(patreonList.filterTable("Loyal Drones"))
    allTables.append(substarList.filterTable("Loyal Drones"))

    #generate a final table
    combinedTable = BasicSubList.combineTables(allTables)
    combinedNameCol = BasicSubList.extractCol(combinedTable, "username")

    # Create and run GUI with the data
    MainWindow.runApp(combinedNameCol)
    



if __name__ == "__main__":
    main()