import logging
import os.path
from typing import Optional

import IO_files_util
import pandas as pd
from util import safe_read_csv

logger = logging.getLogger(__name__)

_COMPARATORS: dict[str, str] = {
    "not equals": "!=",
    "equals": "==",
    "greater than": ">",
    "greater than or equals": ">=",
    "less than": "<",
    "less than or equals": "<=",
}


def listToString(s: list, sep: str) -> str:
    return sep.join(s)


def get_comparator(phrase: str) -> str:
    return _COMPARATORS.get(phrase, "")


def select_csv(files: list, cols: Optional[list] = None):
    for file in files:
        yield safe_read_csv(file, cols)


def get_cols(dfs: list, headers: list):
    if len(headers) != len(dfs):
        return "Unmatching number of dataframes and headers"
    for df, header in zip(dfs, headers):
        yield df[header]


def append(outputDir: str, operation_results_text_list: list) -> str:
    files = []
    headers = []
    for i, s in enumerate(operation_results_text_list):
        files.append(s.split(",")[0])
        headers.append(s.split(",")[1])
        tempHeaders = str(headers[i])
        if " " in tempHeaders:
            tempHeaders = "`" + tempHeaders + "`"

    outputFilename = IO_files_util.generate_output_file_name(
        files[0],
        os.path.dirname(files[0]),
        outputDir,
        ".csv",
        "append",
        "",
        "",
        "",
        "",
        False,
        True,
    )

    data_files = list(select_csv(files))
    if not data_files:
        return ""
    data_cols = list(get_cols(data_files, headers))
    if not data_cols:
        return ""
    sep = ","
    df_append = pd.concat(data_cols, axis=0)
    df_append.to_csv(
        outputFilename,
        encoding="utf-8",
        header=[listToString(headers, sep)],
        index=False,
    )
    return outputFilename


def concat(dfs: list, separator: str) -> pd.DataFrame:
    s = pd.DataFrame
    for i, df in enumerate(dfs):
        if i == 0:
            s = df.astype(str) + separator
        elif i != len(dfs) - 1:
            s = s + df.astype(str) + separator
        else:
            s = s + df.astype(str)
    return s


def concatenate(outputDir: str, operation_results_text_list: list) -> str:
    files = []
    headers = []
    sep = []
    for i, s in enumerate(operation_results_text_list):
        files.append(s.split(",")[0])
        headers.append(s.split(",")[1])
        tempHeaders = str(headers[i])
        if " " in tempHeaders:
            tempHeaders = "`" + tempHeaders + "`"
            headers = [tempHeaders]
        if i == 0:
            sep = s.split(",")[2]

    outputFilename = IO_files_util.generate_output_file_name(
        files[0],
        os.path.dirname(files[0]),
        outputDir,
        ".csv",
        "concatenate",
        "",
        "",
        "",
        "",
        False,
        True,
    )

    data_files = list(select_csv(files))
    if not data_files:
        return ""
    data_cols = list(get_cols(data_files, headers))
    if not data_cols:
        return ""
    df_concat = concat(data_cols, sep)
    df_concat.to_csv(
        outputFilename,
        header=[listToString(headers, sep)],
        encoding="utf-8",
        index=False,
    )
    return outputFilename


def export_csv_to_csv_txt(
    outputDir: str,
    operation_results_text_list: list,
    export_type: str = ".csv",
    cols: Optional[list] = None,
) -> str:
    files = []
    headers = []
    sign_var = []
    value_var = []
    and_or = []
    for i, s in enumerate(operation_results_text_list):
        files.append(s.split(",")[0])
        headers.append(s.split(",")[1])
        tempHeaders = str(headers[i])
        if " " in tempHeaders:
            tempHeaders = "`" + tempHeaders + "`"
        headers.append(tempHeaders)
        sign_var.append(s.split(",")[2])
        value_var.append(s.split(",")[3])
        and_or.append(s.split(",")[4])

    outputFilename = IO_files_util.generate_output_file_name(
        files[0], "", outputDir, export_type, "extract", "", "", "", "", False, True
    )

    data_files = list(select_csv(files, cols))
    if not data_files:
        return ""
    if not operation_results_text_list:
        raise Exception("Missing fields")
    queryStr = ""
    if len(data_files) <= 1:
        data_files = data_files * len(headers)
    df_list = []
    value: str
    header: str
    for sign, value, cond, header, df in zip(sign_var, value_var, and_or, headers, data_files):
        if sign == "''" and value == "''":
            df_list.append(df[[header]])
        else:
            if sign == "":
                raise Exception("Missing sign condition")
            if "'" not in value and not value.isdigit():
                value = "'" + value + "'"
            if sign == "=":
                sign = "=="
            if sign == "<>":
                sign = "!="
            if queryStr == "":
                queryStr = header + sign + value
            else:
                queryStr = queryStr + " " + cond + " " + header + sign + value
    result = df.query(queryStr, engine="python")
    df_list.append(result)
    df_extract = df_list[0]
    for index, _df_ex in enumerate(df_list):
        if operation_results_text_list[index].split(",")[4] in ["and", "''"]:
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how="inner", right_index=True, left_index=True)
        elif operation_results_text_list[index].split(",")[4] == "or":
            if index == len(df_list) - 1:
                continue
            df_extract = df_extract.merge(df_list[index + 1], how="outer", right_index=True, left_index=True)
        elif operation_results_text_list[index].split(",")[4] == "" and index != len(df_list) - 1:
            raise Exception("Missing and/or condition")
    if export_type == ".csv":
        df_extract.to_csv(outputFilename, encoding="utf-8", index=False)
    else:
        text = df_extract.to_csv(encoding="utf-8", index=False)
        text = text.replace(",", " ")
        with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as text_file:
            text_file.write(text)
    return outputFilename


def put_csv(lst: list) -> list:
    return [item.strip().strip("[]'") for item in lst if item.endswith(".csv")]


def put_param(lst: list) -> list:
    return [item.strip().strip("[]'") for item in lst if not item.endswith(".csv")]


def drop_suffixCol(df: pd.DataFrame) -> pd.DataFrame:
    for c in df.columns:
        if c.endswith("_"):
            df = df.drop(columns=[c])
    return df


def MERGE(outputDir: str, operation_results_text_list) -> str:
    df = pd.DataFrame()
    operation_results_text_list = str(operation_results_text_list)
    ip = operation_results_text_list.split("][")
    tp = []
    for item in ip:
        for t in item.split(","):
            tp.append(t)
    csv_lst = list(dict.fromkeys(put_csv(tp)))
    param_lst = list(dict.fromkeys(put_param(tp)))

    size = len(csv_lst)
    try:
        df1 = safe_read_csv(csv_lst[0])
        df2 = safe_read_csv(csv_lst[1])
        df = pd.merge(df1, df2, on=param_lst, how="inner", suffixes=("", "_"))
        df = drop_suffixCol(df)
        if size > 2:
            for i in range(2, size):
                tdf = safe_read_csv(csv_lst[i])
                df = pd.merge(df, tdf, on=param_lst, how="inner", suffixes=("", "_"))
                df = drop_suffixCol(df)
    except (ValueError, TypeError) as err:
        raise FileNotFoundError(f"Error merging files: {err}") from err

    outputFilename = IO_files_util.generate_output_file_name(
        csv_lst[0],
        os.path.dirname(csv_lst[0]),
        outputDir,
        ".csv",
        "merge",
        "",
        "",
        "",
        "",
        False,
        True,
    )
    df.to_csv(outputFilename, encoding="utf-8", index=False)
    return outputFilename
