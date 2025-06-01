import pandas as pd
import argparse
import os
import geopandas as gpd

def proclehdata(mainfile, auxfile, state, parindx=11):

    # read in the lehdod data
    main = pd.read_csv(mainfile)
    aux = pd.read_csv(auxfile)

    # Create a column called tract and populate it with census tract id
    if state == "al":
        main["tract"] = "0" + main["w_geocode"].astype(str).str[:parindx]
        aux["tract"] = "0" + aux["w_geocode"].astype(str).str[:parindx]
    else:
        main["tract"] = main["w_geocode"].astype(str).str[:parindx]
        aux["tract"] = aux["w_geocode"].astype(str).str[:parindx]

    # Aggregate the data by census tract
    main_ = main.groupby("tract").agg({"SE03": lambda x: x.sum()})
    aux_ = aux.groupby("tract").agg({"SE03": lambda x: x.sum()})

    # Reset row index back to integers
    main_.reset_index(inplace=True)
    aux_.reset_index(inplace=True)

    # merge main and aux SEO3 data
    df = pd.merge(main_, aux_, on="tract", how="left")

    df["SE03_y"] = df["SE03_y"].astype(str)

    for id, ii in df.iterrows():
        if ii["SE03_y"] == "nan":
            df.loc[id, "total"] = ii["SE03_x"]
        else:
            df.loc[id, "total"] = ii["SE03_x"] + int(float(ii["SE03_y"]))

    # QC to ensure that the total in the raw data is the same as the processed data
    maintotal = main["SE03"].sum()
    auxtotal = aux["SE03"].sum()
    totalmainaux = maintotal + auxtotal

    # renaming of column
    df.rename(columns={"SE03_x": "HSresidence",
              "SE03_y": "HSoutreisdence", "total": "HStotal"}, inplace=True)

    # QC to ensure that the total in the raw data is the same as the processed data
    if df["HStotal"].sum() == totalmainaux:
        return df
    else:
        return f"Sum of aux, main SEO3: {totalmainaux} and the processed data: {df["HStotal"].sum()} does not match...."


def procblks(csvfiles, state, parindx=11):
    # reading in the files
    blkfile = pd.read_csv(csvfiles)

    # Create a column called tract and populate it with census tract id
    if state == "al":
        blkfile["tract"] = "0" + blkfile["w_geocode"].astype(str).str[:parindx]
    else:
        blkfile["tract"] = blkfile["w_geocode"].astype(str).str[:parindx]

    # Aggregate the data by census tract
    blkfile_ = blkfile.groupby("tract").agg({"CR02": lambda x: x.sum()})

    # reset row index back to integers
    blkfile_.reset_index(inplace=True)

    # renaming of column
    blkfile_.rename(columns={"CR02": "HSblk"}, inplace=True)

    # QC to ensure that the total in the raw data is the same as the processed data
    if blkfile["CR02"].sum() == blkfile_["HSblk"].sum():
        return blkfile_
    else:
        return "Sum of original blk highpaying job not equal to the total of processed highpaying job"


def procwc(mainfile, state, parindx=11):
    # reading in the files
    workers = pd.read_csv(mainfile)

    # Create a column called tract and populate it with census tract id
    if state == "al":
        workers["tract"] = "0" + workers["h_geocode"].astype(str).str[:parindx]
    else:
        workers["tract"] = workers["h_geocode"].astype(str).str[:parindx]

    # Aggregate the data by census tract
    workers_ = workers.groupby("tract").agg({"S000": lambda x: x.sum()})

    # reset row index back to integers
    workers_.reset_index(inplace=True)

    # renaming of column
    workers_.rename(columns={"S000": "low_workers"}, inplace=True)

    # QC to ensure that the total in the raw data is the same as the processed data
    if workers["S000"].sum() == workers_["low_workers"].sum():
        return workers_
    else:
        return "Sum of original low-paying works is not equal to processed data"


def processedlehdata(mainfile, auxfile, csvfiles, folderpath, shapefile, state, parindx=11):
    lehdata = proclehdata(mainfile, auxfile, state, parindx)
    blkhs = procblks(csvfiles, state, parindx)
    workers = procwc(mainfile, state, parindx)
    rshapef = gpd.read_file(shapefile).to_crs("epsg:4269")
    rshapef["lon"] = rshapef.loc[:]["geometry"].x
    rshapef["lat"] = rshapef.loc[:]["geometry"].y

    listwant = ["GEOID", "lon", "lat"]

    rshapef.drop([ii for ii in list(rshapef.columns.values)
                 if ii not in listwant], axis=1, inplace=True)

    if type(lehdata) != str and type(blkhs) != str and type(workers) != str:
        df1 = pd.merge(rshapef, lehdata, left_on="GEOID",
                       right_on="tract", how="left")
        df2 = pd.merge(df1, blkhs, left_on="GEOID",
                       right_on="tract", how="left")
        df3 = pd.merge(df2, workers, left_on="GEOID",
                       right_on="tract", how="left")
        df3.drop(["tract_x", "tract_y", "tract"], axis=1, inplace=True)

        df3.to_csv(os.path.join(folderpath, f'{os.path.split(
            mainfile)[1][:5]}_processed.csv'), index=False)
    else:
        print(lehdata)
        print(blkhs)
        print(workers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="process some files and arguments")
    parser.add_argument("--mainfile", type=str,
                        help="path to the main lehd file")
    parser.add_argument("--auxfile", type=str,
                        help="path to the aux file from lehd")
    parser.add_argument("--parindx", type=int,
                        help="integer used to index the w_geocode id")
    parser.add_argument("--folderpath", type=str,
                        help="path to the folder to store the processed data")
    parser.add_argument("--csvfiles", type=str,
                        help="path to residence workers")
    parser.add_argument("--shapefile", type=str,
                        help="path to centroid shapefile for the respective states")
    parser.add_argument("--state", type=str, help="specifying state")

    parsed_args = parser.parse_args()

    processedlehdata(parsed_args.mainfile, parsed_args.auxfile, parsed_args.csvfiles, parsed_args.folderpath,
                     parsed_args.shapefile, parsed_args.state, parsed_args.parindx)