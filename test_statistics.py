import pandas as pd
import geopandas as gpd
from scipy.stats import shapiro, ttest_ind, wilcoxon, mannwhitneyu
import argparse


def cleaningdata(ga, va, dc, md, al, la, ms, countygeopath):
    georgia = pd.read_csv(ga)
    Virginia = pd.read_csv(va)
    DC = pd.read_csv(dc)
    maryland = pd.read_csv(md)

    alabama = pd.read_csv(al)

    alabama.loc[:, "county"].astype(int)
    alabama.loc[:, "fips"] = str(0) + alabama.loc[:, "county"].astype(str)

    alabama.drop(["county"], axis=1, inplace=True)
    alabama.rename(columns={"fips": "county"}, inplace=True)

    louisiana = pd.read_csv(la)
    mississippi = pd.read_csv(ms)

    accessdata = pd.concat([georgia, Virginia, DC, maryland, alabama, louisiana,
                           mississippi], axis=0)
    # accessdata = pd.read_csv(accessdatapath)
    # countygeo = pd.read_csv(countygeopath).drop(["Unnamed: 0"], axis=1)
    countygeo = gpd.read_file(countygeopath)

    # calculate percent blk tanf recipients

    countygeo["blkpercent"] = countygeo["blk_recipi"] / \
        countygeo["recipients"] * 100

    # drop irrelevant columns before the merge
    countygeo.drop(['recipients', 'blk_recipi', 'blk_child_', 'blk_fams', 'cc_rec',
                    'cc_med', 'cc_total', 'hous_rec', 'fs_rec', 'transpa_me', 'transpa_to'], axis=1, inplace=True)
    accessdata["county"] = accessdata["county"].astype(str)
    # merge access data to countygeo data

    mergedata = pd.merge(accessdata, countygeo,
                         left_on="county", right_on="GEOID", how="right")

    # Select data for only the specified year

    # mergedata = mergedata[mergedata["year"] == year]

    # select black majority and minority.

    blackmajority = mergedata[mergedata["blkpercent"] > 50]["accindx"]
    blackminority = mergedata[mergedata["blkpercent"] <= 50]["accindx"]

    return blackmajority, blackminority, mergedata


def stasticstest(blackmajority, blackminority):

    shapiro_resultblackma = shapiro(blackmajority.dropna())
    shapiro_resultblackmi = shapiro(blackminority.dropna())
    if shapiro_resultblackma.pvalue > 0.05 and shapiro_resultblackmi > 0.05:
        t_test_result = ttest_ind(
            blackmajority.dropna(), blackminority.dropna())
        mannwhitneyuresult = "Data is normally distributed"
    else:
        t_test_result = "Data is not normally distributed"
        mannwhitneyuresult = mannwhitneyu(
            blackmajority.dropna(), blackminority.dropna(), alternative='two-sided')

    return t_test_result, mannwhitneyuresult


def implementstatistics(ga, va, dc, md, al, la, ms, countygeopath):
    blackmajority, blackminority, mergedata = cleaningdata(ga, va, dc, md, al, la, ms,
                                                           countygeopath)

    t_test, mannwhitneyresult = stasticstest(blackmajority, blackminority)

    return t_test, mannwhitneyresult, mergedata, blackmajority, blackminority


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process some files and arguments")
    parser.add_argument("--countygeopath", type=str,
                        help="paths to the county geodata in csv format")
    parser.add_argument("--year", type=str, help="Year of analysis")
    parser.add_argument("--ga", type=str,
                        help="paths to the accessdata csv file")
    parser.add_argument("--va", type=str,
                        help="paths to the accessdata csv file")
    parser.add_argument("--dc", type=str,
                        help="paths to the accessdata csv file")
    parser.add_argument("--md", type=str,
                        help="paths to the accessdata csv file")
    parser.add_argument("--al", type=str,
                        help="paths to the accessdata csv file")
    parser.add_argument("--la", type=str,
                        help="paths to the accessdata csv file")
    parser.add_argument("--ms", type=str,
                        help="paths to the accessdata csv file")

    parsed_args = parser.parse_args()

    implementstatistics(parsed_args.ga, parsed_args.va, parsed_args.dc, parsed_args.md,
                        parsed_args.al, parsed_args.la, parsed_args.ms,
                        parsed_args.countygeopath)
