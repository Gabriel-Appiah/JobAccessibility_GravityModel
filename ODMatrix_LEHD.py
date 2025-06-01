import pandas as pd

def odmatrixclean(ODMatrixcsv, pdf3csv):
    # Make copies of input DataFrames
    pdf3_ = pdf3csv.copy()
    ODMatrix_ = ODMatrixcsv.copy()

    # Get list of centroids (census tracts with SE data)
    coordinates = set(pdf3_["ID_"])

    # Select only census tracts in ODMatrix that have SE data
    ODMatrix_ = ODMatrix_[ODMatrix_["ID"].isin(coordinates)]

    # Select census tracts in SE data for which we have travel time
    pdf3_ = pdf3_[pdf3_["ID_"].isin(set(ODMatrix_["ID"]))]

    # Get the list of relevant columns to keep in ODMatrix
    valid_columns = set(ODMatrix_["origin"])  # Origin census tracts
    valid_columns.add("ID")  # Keep 'ID' column for sorting
    valid_columns.add("origin")  # Keep 'origin' column

    # Drop unnecessary columns in one step
    ODMatrix_ = ODMatrix_[
        [col for col in ODMatrix_.columns if col in valid_columns]]

    # Sort and reset index for proper alignment
    ODMatrix_ = ODMatrix_.sort_values(by="ID").reset_index(drop=True)
    pdf3_ = pdf3_.sort_values(by="ID_").reset_index(drop=True)

    newdata = pd.merge(pdf3_, ODMatrix_, left_on="ID_",
                       right_on="ID", how="left")

    # Save a copy before dropping 'ID' while keeping 'origin'
    origdata = ODMatrix_.drop(columns=["ID"])  # Keep 'origin' column only

    # Drop 'ID' and 'origin' in final cleaned ODMatrix
    ODMatrix_.drop(columns=["ID", "origin"], inplace=True)

    return ODMatrix_, pdf3_, origdata, newdata