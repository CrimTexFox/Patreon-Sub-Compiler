import BasicSubList

def main():
    #create objects
    patreonList = BasicSubList("PatreonSubs.csv", platform="patreon")
    substarList = BasicSubList("SubstarSubs.csv", platform="subcribestar")

    #get all tables
    allTables = []
    allTables.append(patreonList.filter)

    #generate a final table
    BasicSubList.combineTables();


if __name__ == "__main__":
    main()