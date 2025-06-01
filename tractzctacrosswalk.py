import pandas as pd
import argparse


def tractzcta(csvpath):
    cbtozcta = pd.read_csv(csvpath)
    cbtozcta.drop([0], axis=0, inplace=True)
    cbtozcta["tract"] = cbtozcta["tract"].str.replace(".", "", regex=False)
    cbtozcta["couttract"] = cbtozcta["county"]+cbtozcta["tract"]

    zctdata = {}
    for id, ii in cbtozcta.iterrows():
        dic = {"couttract": ii["couttract"], "afact": float(
            ii["afact"]), "zctcode": ii["zcta"]}

        if ii["couttract"] not in zctdata:
            zctdata[ii["couttract"]] = []
        zctdata[ii["couttract"]].append(dic)
    singletract = []
    multipcounty = []

    for ii in zctdata:
        if len(zctdata[ii]) == 1:
            dic = {"couttract": ii, "zctacode": zctdata[ii][0]["zctcode"]}
            singletract.append(dic)
        else:
            maxcheck = []
            for iv in zctdata[ii]:
                maxcheck.append(iv["afact"])
            maxafact = max(maxcheck)

            for aiv in zctdata[ii]:
                if aiv["afact"] == maxafact:
                    dic = {"couttract": ii, "zctacode": aiv["zctcode"]}
                    multipcounty.append(dic)
    finalcrosswalk = singletract+multipcounty

    df = pd.DataFrame(finalcrosswalk)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process some files and arguments") 
    parser.add_argument("--csvpath", type=str,
                        help="path to county zcta crosswalk")

    parsed_args = parser.parse_args()
    tractzcta(parsed_args.csvpath)
