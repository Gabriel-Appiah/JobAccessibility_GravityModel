import pandas as pd
import argparse


def countyzctacroswallk(csvpath):
    gacroswalk = pd.read_csv(csvpath)
    gacroswalk.drop([0], axis=0, inplace=True)

    countyzecta = {}

    for id, ii in gacroswalk.iterrows():
        dic = {"countyfips": ii["county"], "afact": float(ii["afact"])}

        if ii["zcta"] not in countyzecta:
            countyzecta[ii["zcta"]] = []
        countyzecta[ii["zcta"]].append(dic)

    singlecounty = []
    multipcounty = []

    for ii in countyzecta:
        if len(countyzecta[ii]) == 1:
            dic = {"county": countyzecta[ii][0]["countyfips"], "zctacod": ii}
            singlecounty.append(dic)
        else:
            maxcheck = []
            for iv in countyzecta[ii]:
                maxcheck.append(iv["afact"])

            maxafact = max(maxcheck)

            for aiv in countyzecta[ii]:
                if aiv["afact"] == maxafact:
                    dic = {"county": aiv["countyfips"], "zctacod": ii}
                    multipcounty.append(dic)

    finalcroswalk = singlecounty+multipcounty

    df = pd.DataFrame(finalcroswalk)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process some files and arguments")
    parser.add_argument("--csvpath", type=str,
                        help="path to county zcta crosswalk")

    parsed_args = parser.parse_args()
    countyzctacroswallk(parsed_args.csvpath)