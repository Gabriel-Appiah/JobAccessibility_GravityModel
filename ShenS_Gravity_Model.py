
import numpy as np
import pandas as pd

"""
Implementing Shen's Gravity Model Using Numpy library
"""
def distance_decay_(c, beta):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.exp(c * (-beta))


def calculate_accessibility_index_shen(C, O, D, beta, threshold):
    """
    Calculate the accessibility index based on the Shen method.

    Parameters:
        C (ndarray): Distance matrix (n x n).
        O (ndarray): Attraction at location j (n,).
        D (ndarray): Demand at location k (n,).
        beta (ndarray): Decay parameter for each origin (n,).
        threshold (float): Maximum distance to consider.

    Returns:
        tuple: Accessibility index (A), denominator values (F), and decay matrix.
    """
    # Validate input dimensions
    n = C.shape[0]

    # A = np.zeros(n)

    if C.shape != (n, n) or O.shape != (n,) or D.shape != (n,) or beta.shape != (n,):
        raise ValueError("Input arrays have incompatible shapes.")

    # Apply threshold mask
    threshold_mask = (C <= threshold)

    # Compute decay matrix (element-wise decay)
    decay_matrix = distance_decay_(C, beta[:, np.newaxis]) * threshold_mask

    # Calculate F[j] values (denominator)
    F = np.sum(D[:, np.newaxis] * decay_matrix, axis=0)

    # valid_F = F > np.finfo(float).eps

    F[F == 0] = np.finfo(float).eps  # Avoid division by zero

    # Calculate accessibility index A[i]
    # if np.any(valid_F):
    # A[valid_F] = np.sum((O/F[valid_F]) * decay_matrix[:, valid_F], axis=1)

    A = np.sum((O / F) * decay_matrix, axis=1)
    # A[np.isnan(A)] = 0

    return A, F, decay_matrix



"""
Implementation of Schen's Gravity Model using Pandas library

"""


def create_centroid_str(row):
    return "(" + str(row["lon"]) + ", " + str(row["lat"]) + ")"


def createID(row):
    return "(" + str(float(round(row["lon"], 7))) + ", " + str(float(round(row["lat"], 7))) + ")"

def lon(df):
    return round(float(df["origin"].split(",")[0][1:]), 7)


def lon_(df):
    return round(float(df["destination"].split(",")[0][1:]), 7)


def lat(df):
    return round(float(df["origin"].split(",")[1][:-1]), 7)


def lat_(df):
    return round(float(df["destination"].split(",")[1][:-1]), 7)


def creatIDOD(df):
    df["lon"] = df.apply(lon, axis=1)
    df["lat"] = df.apply(lat, axis=1)
    df["ID"] = df.apply(create_centroid_str, axis=1)
    df.drop(["lon", "lat"], axis=1, inplace=True)
    return df


def creatIDODdest(df):
    df["lon"] = df.apply(lon_, axis=1)
    df["lat"] = df.apply(lat_, axis=1)
    df["ID"] = df.apply(create_centroid_str, axis=1)
    df.drop(["lon", "lat"], axis=1, inplace=True)
    return df

def access_datproces(ODmatrix, LEHD, urbanbeta, ruralbeta, rurdf, urdf, accesstype="HStotal"):
    # read in the data
    OD = pd.read_csv(ODmatrix)
    LEHD_ = pd.read_csv(LEHD)
    rur = pd.read_csv(rurdf)
    urb = pd.read_csv(urdf)

    OD["total"] = OD.iloc[:, 1:].sum(axis=1)  # Calculate the total duration

    # Select only census tract with nonzero travel time
    OD = OD[OD["total"] != 0]

    OD.drop("total", axis=1)  # Dropping the total

    # create an ID by reducing the origin lon lat to 7 decimal places
    OD = creatIDOD(OD)

    # filter only records with HStotal and HSblk values
    LEHD_ = LEHD_[LEHD_[accesstype] > 0]

    # create an ID by reducing the origin lon lat or 7 decimal places
    LEHD_["ID"] = LEHD_.apply(createID, axis=1)

    # filter out only census tract for which we have LEHD data for
    OD_ = OD[OD["ID"].isin(set(LEHD_["ID"]))]

    valid_columns = set(OD_["origin"])
    valid_columns.add("origin")

    # drop columns in the ODmatrix
    OD_ = OD_[[col for col in OD_.columns if col in valid_columns]]

    # converting ODmatrix from wide to long
    OD2 = OD_.melt(id_vars="origin", var_name="destination",
                   value_name="duration")

    OD2_ = creatIDOD(OD2)  # Create an ID for the long data
    rur = creatIDOD(rur)  # Create an ID for the rural OD
    urb = creatIDOD(urb)  # Create an ID for the urban OD

    # populating the betas to the OD
    OD2_.loc[OD2_["ID"].isin(set(rur["ID"])), "beta"] = ruralbeta
    OD2_.loc[OD2_["ID"].isin(set(urb["ID"])), "beta"] = urbanbeta

    # creating a mask for the travel threshold
    OD2_["mask"] = np.where(OD2_["duration"] > 30, 0, 1)

    # computing decaymatrix using exponential function
    OD2_["decay"] = np.exp(-OD2_["beta"] * OD2_["duration"]) * OD2_["mask"]

    # filting only census tract in ODmatrix
    LEHDnew = LEHD_[LEHD_["ID"].isin(set(OD2_["ID"]))]

    # merge OD2 matrix to LEHDnew on ID
    ODLEHDmerge = pd.merge(OD2_, LEHDnew, on="ID", how="inner")

    # calculate the demand for each destinaiton
    ODLEHDmerge["dmatrix"] = ODLEHDmerge["decay"] * ODLEHDmerge["low_workers"]

    F = ODLEHDmerge.groupby(["destination"]).agg({"dmatrix": lambda x: x.sum(
        skipna=True)})  # Aggregate demand for each destination

    F.reset_index(inplace=True)  # reset index

    # Select origin OD matrix for computing acc
    newOD = ODLEHDmerge.iloc[:, :7]

    # update the IDs for the matrix using the destination ID
    newOD = creatIDODdest(newOD)

    # merge it gain with LEHD based on the destination
    newOD_ = pd.merge(newOD, LEHDnew, on="ID", how="inner")

    # merge it with the F(demand)
    newOD2 = pd.merge(newOD_, F, on="destination", how="inner")

    # calculate accessibility to each destination
    newOD2["acc"] = (newOD2[accesstype]/newOD2["dmatrix"]) * newOD2["decay"]

    accessbility = newOD2.groupby("origin").agg(
        # aggregate accessibility by origin
        {"acc": lambda x: x.sum(skipna=True)})

    accessbility.reset_index(inplace=True)

    return accessbility