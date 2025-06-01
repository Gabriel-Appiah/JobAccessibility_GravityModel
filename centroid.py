import geopandas as gpd
import argparse
import os


def centroidgdp(shapefile, statename, path, cord):
    geodata = gpd.read_file(shapefile)  # read the shapefile using geopandas
    geodata = geodata.to_crs(cord)

    geodatacopy = geodata.copy()  # make a copy of the shapefile

    # create columan containing the centroid of census tract
    geodatacopy["geometry"] = geodata.centroid

    # save the shapefile
    return geodatacopy.to_file(os.path.join(path, statename))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process some files and arguments")
    parser.add_argument("--shapefile", type=str,
                        help="path to census tract shapefile")
    parser.add_argument("--statename", type=str,
                        help="Name of state for savingfile")
    parser.add_argument("--path", type=str,
                        help="path for saving shapefile")
    parser.add_argument("--cord", type=str,
                        help="for projected coordinate system")

    parsed_args = parser.parse_args()

    centroidgdp(parsed_args.shapefile, parsed_args.statename,
                parsed_args.path, parsed_args.cord)