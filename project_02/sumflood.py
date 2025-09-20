#!/usr/bin/env python3
import sys

import pandas as pd

SUBDISTRICT_CSV = "result.csv"
SUMFLOOD_CSV = "resources/sumflood.csv"

ADMIN_SUBDISTRICT_NAME_COL = "TAM_NAM_T"
ADMIN_PROVINCE_NAME_COL = "PROV_NAM_T"
LDD_SUBDISTRICT_NAME_COL = "ตำบล"
LDD_PROVINCE_NAME_COL = "จังหวัด"


class MergerException(Exception):
    def __init__(self, message, nested_exception=None):
        super().__init__(message)
        self.message = message
        self.nested_exception = nested_exception


def load_sumflood_csv(csv_file):
    try:
        sumflood = pd.read_csv(csv_file, encoding="utf-8")
    except FileNotFoundError as e:
        raise MergerException(f"Specified CSV file '{csv_file}' cannot be found.", e)

    try:
        # Fill the province column for the rows with the missing values
        sumflood[LDD_PROVINCE_NAME_COL] = sumflood[LDD_PROVINCE_NAME_COL].ffill()
        # Remove the prefix of the provinces and obtain only the names of the provinces
        province_replacements = {
            "จ.": "",
        }
        sumflood[LDD_PROVINCE_NAME_COL] = sumflood[LDD_PROVINCE_NAME_COL].replace(
            province_replacements, regex=True
        )

        # Remove the prefix of the subdistricts and obtain only the names of the subdistricts
        subdistrict_replacements = {
            "ต.": "",
            "แขวง": "",
            "ตำบล": "",
        }
        sumflood[LDD_SUBDISTRICT_NAME_COL] = sumflood[LDD_SUBDISTRICT_NAME_COL].replace(
            subdistrict_replacements, regex=True
        )
    except KeyError as e:
        raise MergerException(f"Column {str(e)} of LDD file does not exist", e)
    return sumflood


def load_subdistrict_csv(csv_file):
    try:
        subdistricts = pd.read_csv(csv_file, encoding="utf-8")
    except FileNotFoundError as e:
        raise MergerException(f"Specified CSV file '{csv_file}' cannot be found.")

    try:
        # Remove the prefix of the provinces and obtain only the names of the provinces
        province_replacements = {
            "จ.": "",
        }
        subdistricts[ADMIN_PROVINCE_NAME_COL] = subdistricts[
            ADMIN_PROVINCE_NAME_COL
        ].replace(province_replacements, regex=True)

        # Remove the prefix of the subdistricts and obtain only the names of the subdistricts
        replacements = {
            "ต.": "",
            "แขวง": "",
            "ตำบล": "",
        }
        subdistricts[ADMIN_SUBDISTRICT_NAME_COL] = subdistricts[
            ADMIN_SUBDISTRICT_NAME_COL
        ].replace(replacements, regex=True)
    except KeyError as e:
        raise MergerException(f"Column {str(e)} of subdistrict file does not exist", e)
    return subdistricts


def main():
    subdistricts = None
    sumflood = None
    try:
        subdistricts = load_subdistrict_csv(SUBDISTRICT_CSV)
        sumflood = load_sumflood_csv(SUMFLOOD_CSV)
    except MergerException as e:
        print(f"Error: {e.message}")
        sys.exit(-1)

    # Left join on the columns - The subdistrict and the province of a row need to match in both dataframes
    result = pd.merge(
        subdistricts,
        sumflood,
        left_on=[ADMIN_SUBDISTRICT_NAME_COL, ADMIN_PROVINCE_NAME_COL],
        right_on=[LDD_SUBDISTRICT_NAME_COL, LDD_PROVINCE_NAME_COL],
        how="left",
        indicator=True,
    )
    result.to_csv("final.csv", encoding="utf-8")
    result_unique = result.drop_duplicates(
        subset=[ADMIN_SUBDISTRICT_NAME_COL, ADMIN_PROVINCE_NAME_COL]
    )
    result_subdistricts_count = result_unique.shape[0]

    unmatched = result[result["_merge"] == "left_only"]
    unmatched_unique = unmatched.drop_duplicates(
        subset=[ADMIN_SUBDISTRICT_NAME_COL, ADMIN_PROVINCE_NAME_COL]
    )
    unmatched_subdistricts_count = unmatched_unique.shape[0]

    total_subdistricts_count = result_subdistricts_count + unmatched_subdistricts_count
    result_subdistricts_percent = (
        result_subdistricts_count / total_subdistricts_count
    ) * 100
    unmatched_subdistricts_percent = (
        unmatched_subdistricts_count / total_subdistricts_count
    ) * 100
    print(
        f"Subdistricts with information:    {result_subdistricts_count} ({result_subdistricts_percent:.2f}%)"
    )
    print(
        f"Subdistricts with NO information: {unmatched_subdistricts_count} ({unmatched_subdistricts_percent:.2f}%)"
    )
    print(f"Total subdistricts:               {total_subdistricts_count}")


if __name__ == "__main__":
    main()
