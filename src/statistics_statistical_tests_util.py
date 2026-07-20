import sys
import GUI_util
import IO_libraries_util

if IO_libraries_util.install_all_Python_packages(GUI_util.window, "statistics_statistical_tests_util",
        ['os', 'tkinter', 'pandas', 'numpy', 'scipy']) == False:
    sys.exit(0)

import os
import math
import tkinter.messagebox as mb
import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations

import IO_files_util
import IO_csv_util
import charts_util
import GUI_IO_util
import IO_user_interface_util


# ---------------------------------------------------------------------------
#  Private helpers
# ---------------------------------------------------------------------------

def _validate_csv_input(inputFilename):
    if not inputFilename or not inputFilename.endswith('.csv'):
        mb.showwarning(title='File type error',
                       message='The input file\n\n' + str(inputFilename) +
                       '\n\nis not a csv file.\n\nPlease, select a csv file and try again.')
        return None
    try:
        df = pd.read_csv(inputFilename, encoding='utf-8', on_bad_lines='skip')
    except:
        try:
            df = pd.read_csv(inputFilename, encoding='ISO-8859-1', on_bad_lines='skip')
        except Exception as e:
            mb.showwarning(title='Data encoding error',
                           message='Could not read the input file\n\n' + inputFilename +
                           '\n\nError: ' + str(e))
            return None
    return df


def _save_results_csv(results_df, inputFilename, inputDir, outputDir, label):
    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, '.csv', '', label)
    results_df.to_csv(outputFilename, index=False, encoding='utf-8')
    return outputFilename


def _append_chart_files(filesToOpen, outputFiles):
    if outputFiles is not None:
        if isinstance(outputFiles, str):
            filesToOpen.append(outputFiles)
        else:
            filesToOpen.extend(outputFiles)


def _mann_kendall_test(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    s = 0
    for k in range(n - 1):
        for j in range(k + 1, n):
            diff = x[j] - x[k]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1

    unique, counts = np.unique(x, return_counts=True)
    tied_groups = counts[counts > 1]
    var_s = (n * (n - 1) * (2 * n + 5)) / 18.0
    for t in tied_groups:
        var_s -= (t * (t - 1) * (2 * t + 5)) / 18.0

    if s > 0:
        z = (s - 1) / math.sqrt(var_s) if var_s > 0 else 0
    elif s < 0:
        z = (s + 1) / math.sqrt(var_s) if var_s > 0 else 0
    else:
        z = 0

    p_value = 2.0 * stats.norm.sf(abs(z))
    tau = s / (n * (n - 1) / 2.0)

    slopes = []
    for k in range(n - 1):
        for j in range(k + 1, n):
            if j != k:
                slopes.append((x[j] - x[k]) / (j - k))
    slope = np.median(slopes) if slopes else 0.0
    intercept = np.median(x - slope * np.arange(n))

    if p_value < 0.05:
        trend = 'increasing' if tau > 0 else 'decreasing'
    else:
        trend = 'no significant trend'

    return {'tau': tau, 'p_value': p_value, 'slope': slope,
            'intercept': intercept, 'trend': trend, 'z': z, 'S': s}


def _dunns_test(groups, group_labels):
    all_values = np.concatenate(groups)
    n_total = len(all_values)
    ranks = stats.rankdata(all_values)

    group_ranks = []
    idx = 0
    for g in groups:
        group_ranks.append(ranks[idx:idx + len(g)])
        idx += len(g)

    k = len(groups)
    num_comparisons = k * (k - 1) // 2

    tied_groups_counts = np.unique(ranks, return_counts=True)[1]
    tie_correction = np.sum(tied_groups_counts ** 3 - tied_groups_counts) / (12.0 * (n_total - 1))

    results = []
    for (i, j) in combinations(range(k), 2):
        n_i = len(groups[i])
        n_j = len(groups[j])
        mean_rank_i = np.mean(group_ranks[i])
        mean_rank_j = np.mean(group_ranks[j])
        diff = mean_rank_i - mean_rank_j

        se = math.sqrt(((n_total * (n_total + 1) / 12.0) - tie_correction) *
                       (1.0 / n_i + 1.0 / n_j))

        z_val = diff / se if se > 0 else 0
        p_val = 2.0 * stats.norm.sf(abs(z_val))
        p_adj = min(p_val * num_comparisons, 1.0)

        results.append({
            'Group A': group_labels[i],
            'Group B': group_labels[j],
            'Mean Rank A': round(mean_rank_i, 4),
            'Mean Rank B': round(mean_rank_j, 4),
            'Z statistic': round(z_val, 4),
            'p-value': round(p_val, 6),
            'p-value (Bonferroni)': round(p_adj, 6),
            'Significant (alpha=0.05)': 'Yes' if p_adj < 0.05 else 'No'
        })

    return results


# ---------------------------------------------------------------------------
#  1. Chi-Square Test for Independence
# ---------------------------------------------------------------------------

def run_chi_square_test(inputFilename, outputDir, col1, col2,
                        chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [col1, col2]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[col1, col2]].dropna()
    if len(df) < 5:
        mb.showwarning(title='Insufficient data',
                       message='At least 5 rows are needed for the Chi-Square test.')
        return filesToOpen

    ct = pd.crosstab(df[col1], df[col2])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        mb.showwarning(title='Insufficient categories',
                       message='Both columns need at least 2 unique values for a Chi-Square test.')
        return filesToOpen

    chi2, p, dof, expected = stats.chi2_contingency(ct)

    min_expected = expected.min()
    if min_expected < 5:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Chi-Square warning',
            'Some expected frequencies are below 5 (min=' + str(round(min_expected, 2)) +
            '). The Chi-Square approximation may be unreliable.', False)

    n = ct.values.sum()
    min_dim = min(ct.shape) - 1
    cramers_v = math.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0

    summary_data = {
        'Statistic': ['Chi-Square', 'p-value', 'Degrees of freedom', "Cramer's V (effect size)",
                       'N (total observations)', 'Significant (alpha=0.05)',
                       'Minimum expected frequency', 'Row variable', 'Column variable'],
        'Value': [round(chi2, 4), round(p, 6), dof, round(cramers_v, 4),
                  n, 'Yes' if p < 0.05 else 'No',
                  round(min_expected, 2), col1, col2]
    }
    summary_df = pd.DataFrame(summary_data)
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'chi2_summary')
    filesToOpen.append(out1)

    residuals = (ct.values - expected) / np.sqrt(expected)
    residuals_df = pd.DataFrame(residuals, index=ct.index, columns=ct.columns)
    residuals_df.index.name = col1
    residuals_df = residuals_df.reset_index()
    out2 = _save_results_csv(residuals_df, inputFilename, '', outputDir, 'chi2_residuals')
    filesToOpen.append(out2)

    obs_exp_rows = []
    for cat in ct.index:
        obs_exp_rows.append({col1: str(cat), 'Observed': int(ct.loc[cat].sum()),
                             'Expected': round(expected[ct.index.get_loc(cat)].sum(), 2)})
    obs_exp_df = pd.DataFrame(obs_exp_rows)
    chart_csv = _save_results_csv(obs_exp_df, inputFilename, '', outputDir, 'chi2_obs_vs_exp')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1], [0, 2]], chart_csv, outputDir, outputFileLabel='chi2',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['bar'],
        chart_title='Chi-Square Test: Observed vs Expected\n' + col1 + ' x ' + col2,
        column_xAxis_label_var=col1, column_yAxis_label_var='Count',
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  1b. Cross-tabulation (contingency table) -- descriptive, no significance test
# ---------------------------------------------------------------------------

def run_crosstab(inputFilename, outputDir, col1, col2,
                 chartPackage='Excel', dataTransformation='No transformation'):
    """Standalone cross-tabulation of two categorical columns: row variable = col1 (A),
    column variable = col2 (B). Unlike run_chi_square_test this runs NO significance test -- it just
    surfaces the A x B grid (e.g., gender x space). Outputs a counts table (with row/column totals), a
    row-percentage table (how B distributes within each A), and a grouped-bar chart of the counts."""
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [col1, col2]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[col1, col2]].dropna()
    if len(df) == 0:
        mb.showwarning(title='Insufficient data',
                       message='No rows remain after dropping blank values in the two selected columns.\n\n'
                                   'Please, select two populated categorical columns and try again.')
        return filesToOpen

    # counts table with row/column totals (the 'Total' margins)
    counts = pd.crosstab(df[col1], df[col2], margins=True, margins_name='Total').reset_index()
    out1 = _save_results_csv(counts, inputFilename, '', outputDir, 'crosstab_counts')
    filesToOpen.append(out1)

    # row-percentage table: each row sums to 100% -- how col2 distributes within each col1 category
    row_pct = (pd.crosstab(df[col1], df[col2], normalize='index') * 100).round(2).reset_index()
    out2 = _save_results_csv(row_pct, inputFilename, '', outputDir, 'crosstab_row_pct')
    filesToOpen.append(out2)

    # grouped-bar chart of the raw counts (no margins): col1 categories on X, one series per col2 category
    chart_df = pd.crosstab(df[col1], df[col2]).reset_index()
    chart_csv = _save_results_csv(chart_df, inputFilename, '', outputDir, 'crosstab_chart')
    filesToOpen.append(chart_csv)

    column_pairs = [[0, c] for c in range(1, chart_df.shape[1])]
    outputFiles = charts_util.run_all(
        column_pairs, chart_csv, outputDir, outputFileLabel='crosstab',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['bar'],
        chart_title='Cross-tabulation: ' + col1 + ' x ' + col2,
        column_xAxis_label_var=col1, column_yAxis_label_var='Count',
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  2. Mann-Whitney U Test
# ---------------------------------------------------------------------------

def run_mann_whitney_test(inputFilename, outputDir, value_col, group_col,
                          chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [value_col, group_col]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[value_col, group_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()

    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Column "' + value_col + '" has no numeric values to test '
                               '(non-numeric and blank rows are skipped).')
        return filesToOpen

    labels = sorted(df[group_col].unique())
    if len(labels) < 2:
        mb.showwarning(title='Group error',
                       message='Column "' + group_col + '" must have at least 2 unique values.')
        return filesToOpen
    if len(labels) > 2:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Mann-Whitney warning',
            'More than 2 groups found. Using the first two alphabetically: ' +
            str(labels[0]) + ' and ' + str(labels[1]) + '.', False)
        labels = labels[:2]
        df = df[df[group_col].isin(labels)]

    group_a = df[df[group_col] == labels[0]][value_col]
    group_b = df[df[group_col] == labels[1]][value_col]

    if len(group_a) < 3 or len(group_b) < 3:
        mb.showwarning(title='Insufficient data',
                       message='Each group needs at least 3 observations.')
        return filesToOpen

    U, p = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')

    n1, n2 = len(group_a), len(group_b)
    cliffs_delta = (2.0 * U) / (n1 * n2) - 1.0
    abs_d = abs(cliffs_delta)
    if abs_d < 0.147:
        effect_interp = 'negligible'
    elif abs_d < 0.33:
        effect_interp = 'small'
    elif abs_d < 0.474:
        effect_interp = 'medium'
    else:
        effect_interp = 'large'

    summary_data = {
        'Statistic': ['U statistic', 'p-value', "Cliff's delta", 'Effect size interpretation',
                       'Significant (alpha=0.05)',
                       'Group A', 'Group A n', 'Group A median', 'Group A IQR (25-75%)',
                       'Group B', 'Group B n', 'Group B median', 'Group B IQR (25-75%)'],
        'Value': [round(U, 4), round(p, 6), round(cliffs_delta, 4), effect_interp,
                  'Yes' if p < 0.05 else 'No',
                  str(labels[0]), n1, round(group_a.median(), 4),
                  str(round(group_a.quantile(0.25), 4)) + ' - ' + str(round(group_a.quantile(0.75), 4)),
                  str(labels[1]), n2, round(group_b.median(), 4),
                  str(round(group_b.quantile(0.25), 4)) + ' - ' + str(round(group_b.quantile(0.75), 4))]
    }
    summary_df = pd.DataFrame(summary_data)
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'mann_whitney_summary')
    filesToOpen.append(out1)

    chart_data = pd.DataFrame({
        'Group': [str(labels[0]), str(labels[1])],
        'Median': [round(group_a.median(), 4), round(group_b.median(), 4)],
        'Q25': [round(group_a.quantile(0.25), 4), round(group_b.quantile(0.25), 4)],
        'Q75': [round(group_a.quantile(0.75), 4), round(group_b.quantile(0.75), 4)]
    })
    chart_csv = _save_results_csv(chart_data, inputFilename, '', outputDir, 'mann_whitney_medians')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1]], chart_csv, outputDir, outputFileLabel='mann_whitney',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['bar'],
        chart_title='Mann-Whitney U Test\n' + group_col + ': ' + str(labels[0]) + ' vs ' + str(labels[1]) +
                    '\nU=' + str(round(U, 2)) + ', p=' + str(round(p, 4)),
        column_xAxis_label_var='Group', column_yAxis_label_var=value_col,
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  3. Kruskal-Wallis H Test
# ---------------------------------------------------------------------------

def run_kruskal_wallis_test(inputFilename, outputDir, value_col, group_col,
                            chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [value_col, group_col]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[value_col, group_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()

    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Column "' + value_col + '" has no numeric values to test '
                               '(non-numeric and blank rows are skipped).')
        return filesToOpen

    labels = sorted(df[group_col].unique())
    if len(labels) < 2:
        mb.showwarning(title='Group error',
                       message='Column "' + group_col + '" must have at least 2 unique values.')
        return filesToOpen

    groups = [df[df[group_col] == lbl][value_col].dropna().values for lbl in labels]
    for i, g in enumerate(groups):
        if len(g) < 2:
            mb.showwarning(title='Insufficient data',
                           message='Group "' + str(labels[i]) + '" has fewer than 2 observations.')
            return filesToOpen

    H, p = stats.kruskal(*groups)

    k = len(groups)
    n_total = sum(len(g) for g in groups)
    eps_squared = (H - k + 1) / (n_total - k) if n_total > k else 0
    eps_squared = max(0, min(eps_squared, 1))

    summary_rows = [
        ['H statistic', round(H, 4)],
        ['p-value', round(p, 6)],
        ['Epsilon-squared (effect size)', round(eps_squared, 4)],
        ['Number of groups', k],
        ['Total N', n_total],
        ['Significant (alpha=0.05)', 'Yes' if p < 0.05 else 'No']
    ]
    for lbl, g in zip(labels, groups):
        summary_rows.append(['Group: ' + str(lbl) + ' (n)', len(g)])
        summary_rows.append(['Group: ' + str(lbl) + ' (median)', round(np.median(g), 4)])

    summary_df = pd.DataFrame(summary_rows, columns=['Statistic', 'Value'])
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'kruskal_wallis_summary')
    filesToOpen.append(out1)

    if p < 0.05 and k >= 3:
        dunn_results = _dunns_test(groups, [str(lbl) for lbl in labels])
        dunn_df = pd.DataFrame(dunn_results)
        out2 = _save_results_csv(dunn_df, inputFilename, '', outputDir, 'kruskal_wallis_posthoc')
        filesToOpen.append(out2)

    chart_data = pd.DataFrame({
        'Group': [str(lbl) for lbl in labels],
        'Median': [round(np.median(g), 4) for g in groups]
    })
    chart_csv = _save_results_csv(chart_data, inputFilename, '', outputDir, 'kruskal_wallis_medians')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1]], chart_csv, outputDir, outputFileLabel='kruskal_wallis',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['bar'],
        chart_title='Kruskal-Wallis Test\nMedians by ' + group_col +
                    '\nH=' + str(round(H, 2)) + ', p=' + str(round(p, 4)),
        column_xAxis_label_var=group_col, column_yAxis_label_var=value_col,
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  4. Mann-Kendall Trend Test
# ---------------------------------------------------------------------------

def run_mann_kendall_trend_test(inputFilename, outputDir, date_col, value_col,
                                chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [date_col, value_col]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[date_col, value_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()

    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Column "' + value_col + '" has no numeric values to test '
                               '(non-numeric and blank rows are skipped).')
        return filesToOpen

    try:
        df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True)
    except:
        mb.showwarning(title='Date parse error',
                       message='Could not parse dates in column "' + date_col + '".')
        return filesToOpen

    df = df.sort_values(date_col).reset_index(drop=True)

    if len(df) < 8:
        mb.showwarning(title='Insufficient data',
                       message='At least 8 observations are needed for a reliable Mann-Kendall test.')
        return filesToOpen

    if len(df) > 5000:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Performance warning',
            'Large dataset (' + str(len(df)) + ' rows). The Mann-Kendall test may take a moment.', False)

    values = df[value_col].values
    mk = _mann_kendall_test(values)

    summary_data = {
        'Statistic': ["Kendall's tau", 'p-value', "Sen's slope", "Sen's intercept",
                       'Trend direction', 'S statistic', 'Z statistic',
                       'Significant (alpha=0.05)', 'N'],
        'Value': [round(mk['tau'], 4), round(mk['p_value'], 6),
                  round(mk['slope'], 6), round(mk['intercept'], 4),
                  mk['trend'], mk['S'], round(mk['z'], 4),
                  'Yes' if mk['p_value'] < 0.05 else 'No', len(values)]
    }
    summary_df = pd.DataFrame(summary_data)
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'mann_kendall_summary')
    filesToOpen.append(out1)

    trend_line = mk['intercept'] + mk['slope'] * np.arange(len(df))
    chart_df = pd.DataFrame({
        date_col: df[date_col].dt.strftime('%Y-%m-%d'),
        value_col: df[value_col].values,
        'Trend Line': np.round(trend_line, 4)
    })
    chart_csv = _save_results_csv(chart_df, inputFilename, '', outputDir, 'mann_kendall_trend')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1], [0, 2]], chart_csv, outputDir, outputFileLabel='mann_kendall',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['line'],
        chart_title='Mann-Kendall Trend Test\ntau=' + str(round(mk['tau'], 3)) +
                    ', p=' + str(round(mk['p_value'], 4)) + ' (' + mk['trend'] + ')',
        column_xAxis_label_var=date_col, column_yAxis_label_var=value_col,
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  5. Log-Likelihood Ratio (Dunning's G-test) for Corpus Comparison
# ---------------------------------------------------------------------------

def run_log_likelihood_test(inputFilename, outputDir,
                            word_col, freq_col1, freq_col2=None,
                            corpus_col=None,
                            chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    if word_col not in df.columns:
        mb.showwarning(title='Column error',
                       message='Column "' + word_col + '" not found in the input file.')
        return filesToOpen

    # Mode B: pivot by corpus column
    if corpus_col is not None and corpus_col in df.columns:
        if freq_col1 not in df.columns:
            mb.showwarning(title='Column error',
                           message='Frequency column "' + freq_col1 + '" not found.')
            return filesToOpen
        pivot = df.pivot_table(index=word_col, columns=corpus_col,
                               values=freq_col1, aggfunc='sum', fill_value=0)
        corpus_labels = list(pivot.columns)
        if len(corpus_labels) < 2:
            mb.showwarning(title='Corpus error',
                           message='Need at least 2 corpus groups in "' + corpus_col + '".')
            return filesToOpen
        if len(corpus_labels) > 2:
            IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Log-likelihood warning',
                'More than 2 corpora found. Using the first two: ' +
                str(corpus_labels[0]) + ' and ' + str(corpus_labels[1]) + '.', False)
            corpus_labels = corpus_labels[:2]
        words = pivot.index.tolist()
        freq_a = pivot[corpus_labels[0]].values.astype(float)
        freq_b = pivot[corpus_labels[1]].values.astype(float)
        label_a, label_b = str(corpus_labels[0]), str(corpus_labels[1])

    # Mode A: two frequency columns
    elif freq_col2 is not None:
        for col in [freq_col1, freq_col2]:
            if col not in df.columns:
                mb.showwarning(title='Column error',
                               message='Column "' + col + '" not found in the input file.')
                return filesToOpen
        df = df[[word_col, freq_col1, freq_col2]].dropna()
        words = df[word_col].tolist()
        freq_a = df[freq_col1].values.astype(float)
        freq_b = df[freq_col2].values.astype(float)
        label_a, label_b = freq_col1, freq_col2
    else:
        mb.showwarning(title='Parameter error',
                       message='Provide either two frequency columns (freq_col1 and freq_col2) '
                       'or a corpus identifier column (corpus_col).')
        return filesToOpen

    total_a = freq_a.sum()
    total_b = freq_b.sum()

    if total_a == 0 or total_b == 0:
        mb.showwarning(title='Empty corpus',
                       message='One of the corpora has zero total frequency.')
        return filesToOpen

    results = []
    for i in range(len(words)):
        a = freq_a[i]
        b = freq_b[i]
        e1 = total_a * (a + b) / (total_a + total_b)
        e2 = total_b * (a + b) / (total_a + total_b)

        g2 = 0.0
        if a > 0 and e1 > 0:
            g2 += a * math.log(a / e1)
        if b > 0 and e2 > 0:
            g2 += b * math.log(b / e2)
        g2 *= 2

        p_val = stats.chi2.sf(g2, df=1) if g2 > 0 else 1.0

        norm_a = a / total_a if total_a > 0 else 0
        norm_b = b / total_b if total_b > 0 else 0
        log_ratio = math.log2((norm_a + 1e-10) / (norm_b + 1e-10))
        pct_diff = 100.0 * (norm_a - norm_b) / (norm_b + 1e-10)

        bic = g2 - math.log(total_a + total_b) if g2 > 0 else 0

        overrep = label_a if log_ratio > 0 else label_b

        results.append({
            'Word': words[i],
            'Freq ' + label_a: int(a),
            'Freq ' + label_b: int(b),
            'G2 (log-likelihood)': round(g2, 4),
            'p-value': round(p_val, 6),
            'Log Ratio': round(log_ratio, 4),
            'Pct Diff': round(pct_diff, 2),
            'BIC': round(bic, 4),
            'Overrepresented in': overrep
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('G2 (log-likelihood)', ascending=False)
    out1 = _save_results_csv(results_df, inputFilename, '', outputDir, 'log_likelihood')
    filesToOpen.append(out1)

    top_over = results_df[results_df['Log Ratio'] > 0].nlargest(20, 'G2 (log-likelihood)')
    top_under = results_df[results_df['Log Ratio'] < 0].nlargest(20, 'G2 (log-likelihood)')
    chart_df = pd.concat([top_over, top_under]).sort_values('Log Ratio', ascending=False)
    chart_df = chart_df[['Word', 'Log Ratio']].reset_index(drop=True)

    if len(chart_df) > 0:
        chart_csv = _save_results_csv(chart_df, inputFilename, '', outputDir, 'log_likelihood_top_words')
        filesToOpen.append(chart_csv)

        outputFiles = charts_util.run_all(
            [[0, 1]], chart_csv, outputDir, outputFileLabel='log_likelihood',
            chartPackage=chartPackage, dataTransformation=dataTransformation,
            chart_type_list=['bar'],
            chart_title='Log-Likelihood Ratio (G2)\nCorpus Comparison: ' + label_a + ' vs ' + label_b,
            column_xAxis_label_var='Word', column_yAxis_label_var='Log Ratio',
            hover_info_column_list=[])
        _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  6. Correlation Test (Spearman / Kendall)
# ---------------------------------------------------------------------------

def run_correlation_test(inputFilename, outputDir, col_x, col_y,
                         method='spearman',
                         chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [col_x, col_y]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[col_x, col_y]].copy()
    for col in [col_x, col_y]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Columns "' + col_x + '" / "' + col_y + '" have no numeric values to test '
                               '(non-numeric and blank rows are skipped).')
        return filesToOpen

    if len(df) < 5:
        mb.showwarning(title='Insufficient data',
                       message='At least 5 observations are needed for a correlation test.')
        return filesToOpen

    if df[col_x].std() == 0 or df[col_y].std() == 0:
        mb.showwarning(title='Constant column',
                       message='One of the columns has zero variance. Correlation is undefined.')
        return filesToOpen

    method_lower = method.lower()
    if method_lower == 'kendall':
        coef, p = stats.kendalltau(df[col_x], df[col_y])
        method_label = 'Kendall'
    else:
        coef, p = stats.spearmanr(df[col_x], df[col_y])
        method_label = 'Spearman'

    abs_coef = abs(coef)
    if abs_coef < 0.1:
        interp = 'negligible'
    elif abs_coef < 0.3:
        interp = 'weak'
    elif abs_coef < 0.5:
        interp = 'moderate'
    elif abs_coef < 0.7:
        interp = 'strong'
    else:
        interp = 'very strong'

    n = len(df)
    ci_lower, ci_upper = '', ''
    if method_lower == 'spearman' and n > 3:
        z = np.arctanh(coef)
        se = 1.0 / math.sqrt(n - 3)
        ci_lower = round(np.tanh(z - 1.96 * se), 4)
        ci_upper = round(np.tanh(z + 1.96 * se), 4)

    summary_data = {
        'Statistic': ['Method', 'Coefficient', 'p-value',
                       '95% CI lower', '95% CI upper',
                       'Interpretation', 'Significant (alpha=0.05)', 'N'],
        'Value': [method_label, round(coef, 4), round(p, 6),
                  ci_lower, ci_upper,
                  interp, 'Yes' if p < 0.05 else 'No', n]
    }
    summary_df = pd.DataFrame(summary_data)
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'correlation_summary')
    filesToOpen.append(out1)

    slope, intercept = np.polyfit(df[col_x], df[col_y], 1)
    df_chart = df.copy()
    df_chart['Regression Line'] = np.round(intercept + slope * df[col_x], 4)
    df_chart = df_chart.sort_values(col_x).reset_index(drop=True)
    chart_csv = _save_results_csv(df_chart, inputFilename, '', outputDir, 'correlation_scatter')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1], [0, 2]], chart_csv, outputDir, outputFileLabel='correlation',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['line'],
        chart_title=method_label + ' Correlation\nr=' + str(round(coef, 3)) +
                    ', p=' + str(round(p, 4)),
        column_xAxis_label_var=col_x, column_yAxis_label_var=col_y,
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  7. Inter-Annotator Agreement (Cohen's / Fleiss' kappa)
# ---------------------------------------------------------------------------

def _cohens_kappa(labels_a, labels_b):
    categories = sorted(set(labels_a) | set(labels_b), key=lambda v: str(v))
    cat_index = {c: i for i, c in enumerate(categories)}
    k = len(categories)
    n = len(labels_a)
    cm = np.zeros((k, k), dtype=float)
    for a, b in zip(labels_a, labels_b):
        cm[cat_index[a], cat_index[b]] += 1
    po = np.trace(cm) / n if n > 0 else 0.0
    row_marg = cm.sum(axis=1) / n
    col_marg = cm.sum(axis=0) / n
    pe = float(np.sum(row_marg * col_marg))
    kappa = (po - pe) / (1 - pe) if (1 - pe) != 0 else 0.0
    return kappa, po, pe, categories, cm


def _fleiss_kappa(rating_matrix):
    # rating_matrix: N items x K categories; cell = number of raters assigning item i to category j
    N, k = rating_matrix.shape
    n_raters = rating_matrix[0].sum()
    p_j = rating_matrix.sum(axis=0) / (N * n_raters)
    P_i = (np.sum(rating_matrix ** 2, axis=1) - n_raters) / (n_raters * (n_raters - 1))
    P_bar = float(np.mean(P_i))
    Pe_bar = float(np.sum(p_j ** 2))
    kappa = (P_bar - Pe_bar) / (1 - Pe_bar) if (1 - Pe_bar) != 0 else 0.0
    return kappa, P_bar, Pe_bar, p_j


def _kappa_interpretation(kappa):
    # Landis & Koch (1977) benchmarks
    if kappa < 0:
        return 'poor (worse than chance)'
    elif kappa <= 0.20:
        return 'slight'
    elif kappa <= 0.40:
        return 'fair'
    elif kappa <= 0.60:
        return 'moderate'
    elif kappa <= 0.80:
        return 'substantial'
    else:
        return 'almost perfect'


def run_kappa_test(inputFilename, outputDir, rater_cols,
                   chartPackage='Excel', dataTransformation='No transformation'):
    """Inter-annotator agreement across 2+ annotator/tool columns.

    Each column in rater_cols holds one annotator's (or tool's) labels for the same items
    (rows). Exactly 2 columns -> Cohen's kappa (+ confusion matrix); 3+ columns -> Fleiss' kappa.
    Typical use: compare Stanza vs spaCy POS/NER tags to measure how well the tools agree."""
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    if not isinstance(rater_cols, (list, tuple)):
        rater_cols = [rater_cols]

    # drop empties and de-duplicate while preserving order (a column picked twice is one rater)
    seen = set()
    unique_cols = []
    for c in rater_cols:
        if c in (None, '') or c in seen:
            continue
        seen.add(c)
        unique_cols.append(c)
    rater_cols = unique_cols

    if len(rater_cols) < 2:
        mb.showwarning(title='Insufficient annotators',
                       message='Inter-annotator agreement requires at least 2 distinct annotator/tool columns.\n\n'
                               'Please, select one column per annotator and try again.')
        return filesToOpen

    for col in rater_cols:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + str(col) + '" not found in the input file.')
            return filesToOpen

    df = df[rater_cols].dropna().copy()
    # treat every label as a trimmed string so numeric and text tags compare consistently
    for col in rater_cols:
        df[col] = df[col].astype(str).str.strip()

    if len(df) < 2:
        mb.showwarning(title='Insufficient data',
                       message='At least 2 items (rows) rated by all annotators are needed.')
        return filesToOpen

    n_raters = len(rater_cols)
    po_obs = pe_chance = 0.0

    if n_raters == 2:
        method_label = "Cohen's kappa"
        labels_a = df[rater_cols[0]].tolist()
        labels_b = df[rater_cols[1]].tolist()
        kappa, po_obs, pe_chance, categories, cm = _cohens_kappa(labels_a, labels_b)
        interp = _kappa_interpretation(kappa)

        summary_df = pd.DataFrame({
            'Statistic': ['Method', 'Kappa', 'Interpretation',
                          'Observed agreement (Po)', 'Expected agreement (Pe)',
                          'N items', 'N categories', 'Annotator 1', 'Annotator 2'],
            'Value': [method_label, round(kappa, 4), interp,
                      round(po_obs, 4), round(pe_chance, 4),
                      len(df), len(categories), rater_cols[0], rater_cols[1]]
        })
        out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'kappa_summary')
        filesToOpen.append(out1)

        # confusion matrix: rows = annotator 1 labels, cols = annotator 2 labels
        cm_df = pd.DataFrame(cm.astype(int), index=categories, columns=categories)
        cm_df.index.name = rater_cols[0] + ' \\ ' + rater_cols[1]
        cm_df = cm_df.reset_index()
        out2 = _save_results_csv(cm_df, inputFilename, '', outputDir, 'kappa_confusion_matrix')
        filesToOpen.append(out2)

    else:
        method_label = "Fleiss' kappa"
        categories = sorted(set().union(*[set(df[c]) for c in rater_cols]), key=lambda v: str(v))
        cat_index = {c: i for i, c in enumerate(categories)}
        N = len(df)
        k = len(categories)
        rating_matrix = np.zeros((N, k), dtype=float)
        for row_i, (_, row) in enumerate(df.iterrows()):
            for col in rater_cols:
                rating_matrix[row_i, cat_index[row[col]]] += 1

        kappa, po_obs, pe_chance, p_j = _fleiss_kappa(rating_matrix)
        interp = _kappa_interpretation(kappa)

        summary_df = pd.DataFrame({
            'Statistic': ['Method', 'Kappa', 'Interpretation',
                          'Mean observed agreement (P-bar)', 'Expected agreement (Pe-bar)',
                          'N items', 'N annotators', 'N categories', 'Annotators'],
            'Value': [method_label, round(kappa, 4), interp,
                      round(po_obs, 4), round(pe_chance, 4),
                      N, n_raters, k, ', '.join(rater_cols)]
        })
        out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'kappa_summary')
        filesToOpen.append(out1)

        # category distribution across all annotations
        dist_df = pd.DataFrame({
            'Category': [str(c) for c in categories],
            'Proportion': [round(float(p), 4) for p in p_j]
        })
        out2 = _save_results_csv(dist_df, inputFilename, '', outputDir, 'kappa_category_distribution')
        filesToOpen.append(out2)

    # chart: observed vs chance agreement (kappa corrects the gap between the two)
    chart_df = pd.DataFrame({
        'Agreement type': ['Observed', 'Expected (chance)'],
        'Proportion': [round(po_obs, 4), round(pe_chance, 4)]
    })
    chart_csv = _save_results_csv(chart_df, inputFilename, '', outputDir, 'kappa_agreement')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1]], chart_csv, outputDir, outputFileLabel='kappa',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['bar'],
        chart_title=method_label + ': kappa=' + str(round(kappa, 3)) + ' (' + interp + ')' +
                    '\nObserved vs chance agreement',
        column_xAxis_label_var='Agreement type', column_yAxis_label_var='Proportion',
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  8. Change-Point Detection (Pettitt's test)
# ---------------------------------------------------------------------------

def _pettitt_test(x):
    # Pettitt's non-parametric test for a single change point (shift in the median).
    # Rank-based O(n) formulation: U_t = 2*cumsum(rank)[:t] - t*(n+1).
    x = np.asarray(x, dtype=float)
    n = len(x)
    ranks = stats.rankdata(x)
    cum = np.cumsum(ranks)
    t_idx = np.arange(1, n)                      # t = 1 .. n-1
    U = 2.0 * cum[:n - 1] - t_idx * (n + 1)
    abs_U = np.abs(U)
    K = float(np.max(abs_U))
    t = int(np.argmax(abs_U)) + 1                # first index of the SECOND segment (0-based)
    p_value = 2.0 * math.exp((-6.0 * K * K) / (n ** 3 + n ** 2))
    p_value = min(p_value, 1.0)
    return {'K': K, 'change_index': t, 'p_value': p_value}


def run_change_point_test(inputFilename, outputDir, date_col, value_col,
                          chartPackage='Excel', dataTransformation='No transformation'):
    """Detect a single abrupt shift in a time-ordered numeric series (e.g. topic prevalence,
    sentiment) using Pettitt's test. Reports where the shift occurs and the mean before/after."""
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [date_col, value_col]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[date_col, value_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()

    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Column "' + value_col + '" has no numeric values to test '
                               '(non-numeric and blank rows are skipped).')
        return filesToOpen

    try:
        df[date_col] = pd.to_datetime(df[date_col], infer_datetime_format=True)
        df = df.sort_values(date_col).reset_index(drop=True)
        x_is_date = True
    except:
        # fall back to input order when the column is not parseable as a date
        df = df.reset_index(drop=True)
        x_is_date = False

    if len(df) < 10:
        mb.showwarning(title='Insufficient data',
                       message='At least 10 observations are needed for change-point detection.')
        return filesToOpen

    values = df[value_col].values
    result = _pettitt_test(values)
    t = result['change_index']

    mean_before = float(np.mean(values[:t]))
    mean_after = float(np.mean(values[t:]))
    if x_is_date:
        cp_label = str(df[date_col].iloc[t].strftime('%Y-%m-%d'))
    else:
        cp_label = 'row ' + str(t)

    summary_df = pd.DataFrame({
        'Statistic': ['Change point (location)', 'Change-point index (row)', 'K statistic', 'p-value',
                      'Significant (alpha=0.05)', 'Mean before', 'Mean after', 'Shift (after - before)',
                      'N'],
        'Value': [cp_label, t, round(result['K'], 4), round(result['p_value'], 6),
                  'Yes' if result['p_value'] < 0.05 else 'No',
                  round(mean_before, 4), round(mean_after, 4),
                  round(mean_after - mean_before, 4), len(values)]
    })
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'change_point_summary')
    filesToOpen.append(out1)

    # step line of the segment means makes the shift visible against the raw series
    seg_mean = np.where(np.arange(len(values)) < t, mean_before, mean_after)
    if x_is_date:
        x_axis = df[date_col].dt.strftime('%Y-%m-%d')
    else:
        x_axis = df.index.astype(str)
    chart_df = pd.DataFrame({
        date_col: x_axis,
        value_col: values,
        'Segment mean': np.round(seg_mean, 4)
    })
    chart_csv = _save_results_csv(chart_df, inputFilename, '', outputDir, 'change_point_series')
    filesToOpen.append(chart_csv)

    sig = 'significant' if result['p_value'] < 0.05 else 'not significant'
    outputFiles = charts_util.run_all(
        [[0, 1], [0, 2]], chart_csv, outputDir, outputFileLabel='change_point',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['line'],
        chart_title='Change-Point Detection (Pettitt)\nchange at ' + cp_label +
                    ', p=' + str(round(result['p_value'], 4)) + ' (' + sig + ')',
        column_xAxis_label_var=date_col, column_yAxis_label_var=value_col,
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  9. Permutation Test (two-group difference in means)
# ---------------------------------------------------------------------------

def run_permutation_test(inputFilename, outputDir, value_col, group_col,
                         n_permutations=10000,
                         chartPackage='Excel', dataTransformation='No transformation'):
    """Distribution-free test of whether the difference in means between two groups is more
    extreme than expected by chance, by repeatedly shuffling the group labels. A robust,
    assumption-light complement to Mann-Whitney for small or non-normal samples."""
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen

    for col in [value_col, group_col]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + col + '" not found in the input file.')
            return filesToOpen

    df = df[[value_col, group_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()

    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Column "' + value_col + '" has no numeric values to test '
                               '(non-numeric and blank rows are skipped).')
        return filesToOpen

    labels = sorted(df[group_col].unique())
    if len(labels) < 2:
        mb.showwarning(title='Group error',
                       message='Column "' + group_col + '" must have at least 2 unique values.')
        return filesToOpen
    if len(labels) > 2:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Permutation test warning',
            'More than 2 groups found. Using the first two alphabetically: ' +
            str(labels[0]) + ' and ' + str(labels[1]) + '.', False)
        labels = labels[:2]
        df = df[df[group_col].isin(labels)]

    a = df[df[group_col] == labels[0]][value_col].values.astype(float)
    b = df[df[group_col] == labels[1]][value_col].values.astype(float)

    if len(a) < 3 or len(b) < 3:
        mb.showwarning(title='Insufficient data',
                       message='Each group needs at least 3 observations.')
        return filesToOpen

    mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
    observed_diff = mean_a - mean_b
    obs_abs = abs(observed_diff)

    # seeded generator -> reproducible p-values across runs
    rng = np.random.default_rng(42)
    pooled = np.concatenate([a, b])
    n1 = len(a)
    perm_diffs = np.empty(n_permutations)
    for i in range(n_permutations):
        rng.shuffle(pooled)
        perm_diffs[i] = pooled[:n1].mean() - pooled[n1:].mean()

    # +1 in numerator and denominator -> unbiased permutation p-value (never exactly 0)
    p_value = (np.sum(np.abs(perm_diffs) >= obs_abs) + 1) / (n_permutations + 1)

    pooled_sd = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) /
                        (len(a) + len(b) - 2)) if (len(a) + len(b) - 2) > 0 else 0.0
    cohens_d = observed_diff / pooled_sd if pooled_sd > 0 else 0.0

    summary_df = pd.DataFrame({
        'Statistic': ['Observed difference in means', 'p-value (two-sided)', "Cohen's d (effect size)",
                      'Permutations', 'Significant (alpha=0.05)',
                      'Group A', 'Group A n', 'Group A mean',
                      'Group B', 'Group B n', 'Group B mean'],
        'Value': [round(observed_diff, 4), round(float(p_value), 6), round(cohens_d, 4),
                  n_permutations, 'Yes' if p_value < 0.05 else 'No',
                  str(labels[0]), len(a), round(mean_a, 4),
                  str(labels[1]), len(b), round(mean_b, 4)]
    })
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'permutation_summary')
    filesToOpen.append(out1)

    # full permutation distribution (lets the user histogram the null distribution if wanted)
    dist_df = pd.DataFrame({'Permuted difference in means': np.round(perm_diffs, 6)})
    out2 = _save_results_csv(dist_df, inputFilename, '', outputDir, 'permutation_distribution')
    filesToOpen.append(out2)

    chart_df = pd.DataFrame({
        'Group': [str(labels[0]), str(labels[1])],
        'Mean': [round(mean_a, 4), round(mean_b, 4)]
    })
    chart_csv = _save_results_csv(chart_df, inputFilename, '', outputDir, 'permutation_means')
    filesToOpen.append(chart_csv)

    outputFiles = charts_util.run_all(
        [[0, 1]], chart_csv, outputDir, outputFileLabel='permutation',
        chartPackage=chartPackage, dataTransformation=dataTransformation,
        chart_type_list=['bar'],
        chart_title='Permutation Test\n' + group_col + ': ' + str(labels[0]) + ' vs ' + str(labels[1]) +
                    '\nobserved diff=' + str(round(observed_diff, 3)) + ', p=' + str(round(float(p_value), 4)),
        column_xAxis_label_var='Group', column_yAxis_label_var=value_col,
        hover_info_column_list=[])
    _append_chart_files(filesToOpen, outputFiles)

    return filesToOpen


# ---------------------------------------------------------------------------
#  9. Adjusted Rand Index / NMI -- agreement between two clusterings / labelings
# ---------------------------------------------------------------------------
def run_adjusted_rand_test(inputFilename, outputDir, labels_col1, labels_col2,
                           chartPackage='Excel', dataTransformation='No transformation'):
    """Agreement between TWO clusterings/labelings of the same items (rows). The Adjusted
    Rand Index (ARI) corrects the Rand index for chance: 1 = identical partitions, 0 = chance
    agreement, < 0 = worse than chance. It is permutation-invariant (the cluster NAMES don't
    matter), so unlike kappa it is the right measure for CLUSTER labels -- e.g. two topic-model
    runs, or a clustering vs a gold partition. Normalized Mutual Information (NMI, 0..1) is
    reported alongside."""
    filesToOpen = []
    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen
    for col in [labels_col1, labels_col2]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + str(col) + '" not found in the input file.')
            return filesToOpen
    df = df[[labels_col1, labels_col2]].dropna().copy()
    df[labels_col1] = df[labels_col1].astype(str).str.strip()
    df[labels_col2] = df[labels_col2].astype(str).str.strip()
    if len(df) < 2:
        mb.showwarning(title='Insufficient data',
                       message='At least 2 items (rows) labeled in BOTH columns are needed.')
        return filesToOpen

    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
    a = df[labels_col1].tolist()
    b = df[labels_col2].tolist()
    ari = float(adjusted_rand_score(a, b))
    nmi = float(normalized_mutual_info_score(a, b))
    if ari > 0.90:
        interp = 'near-identical partitions'
    elif ari > 0.65:
        interp = 'strong agreement'
    elif ari > 0.40:
        interp = 'moderate agreement'
    elif ari > 0.15:
        interp = 'weak agreement'
    elif ari > -0.05:
        interp = 'chance-level agreement'
    else:
        interp = 'worse than chance (systematic disagreement)'

    summary_df = pd.DataFrame({
        'Statistic': ['Adjusted Rand Index (ARI)', 'Interpretation',
                      'Normalized Mutual Information (NMI)', 'N items',
                      'Clusters in "' + str(labels_col1) + '"',
                      'Clusters in "' + str(labels_col2) + '"'],
        'Value': [round(ari, 4), interp, round(nmi, 4), len(df),
                  int(df[labels_col1].nunique()), int(df[labels_col2].nunique())]
    })
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'adjusted_rand_index')
    filesToOpen.append(out1)

    # contingency of the two labelings -- shows how the clusters map onto each other
    ct = pd.crosstab(df[labels_col1], df[labels_col2])
    out2 = _save_results_csv(ct.reset_index(), inputFilename, '', outputDir, 'adjusted_rand_contingency')
    filesToOpen.append(out2)
    return filesToOpen


# ---------------------------------------------------------------------------
# 10. Bayes factor (two groups) -- Bayesian complement to a p-value
# ---------------------------------------------------------------------------
def _jzs_bf10_twosample(t, n1, n2, r=0.707):
    """JZS (Rouder et al. 2009) Bayes factor BF10 for an INDEPENDENT two-sample t test with a
    Cauchy prior of scale r on the standardized effect size. BF10 > 1 favours a difference
    (H1); < 1 favours no difference (H0). Implemented with numerical integration (scipy) so
    no extra dependency is needed."""
    from scipy.integrate import quad
    df = n1 + n2 - 2
    n_eff = n1 * n2 / (n1 + n2)

    def _integrand(g):
        return ((1.0 + n_eff * g * r * r) ** (-0.5)
                * (1.0 + t * t / ((1.0 + n_eff * g * r * r) * df)) ** (-(df + 1) / 2.0)
                * (2.0 * np.pi) ** (-0.5) * g ** (-1.5) * np.exp(-1.0 / (2.0 * g)))

    integ = quad(_integrand, 0, np.inf)[0]
    return (1.0 + t * t / df) ** ((df + 1) / 2.0) * integ


def run_bayes_factor_test(inputFilename, outputDir, value_col, group_col,
                          chartPackage='Excel', dataTransformation='No transformation'):
    """Bayes factor for the difference in means between TWO groups -- the Bayesian complement
    to a p-value. BF10 is how many times more likely the data are under 'the groups differ'
    than under 'no difference': BF10 > 3 = moderate, > 10 = strong evidence FOR a difference;
    BF10 < 1/3 = evidence for NO difference (a p-value can never argue FOR the null; this can).
    Cohen's d effect size is reported too."""
    filesToOpen = []
    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen
    for col in [value_col, group_col]:
        if col not in df.columns:
            mb.showwarning(title='Column error',
                           message='Column "' + str(col) + '" not found in the input file.')
            return filesToOpen
    df = df[[value_col, group_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df[group_col] = df[group_col].astype(str)
    df = df.dropna()
    if df.empty:
        mb.showwarning(title='No numeric data',
                       message='Column "' + value_col + '" has no numeric values to test.')
        return filesToOpen
    labels = sorted(df[group_col].unique())
    if len(labels) < 2:
        mb.showwarning(title='Group error',
                       message='Column "' + group_col + '" must have at least 2 unique values.')
        return filesToOpen
    if len(labels) > 2:
        IO_user_interface_util.timed_alert(GUI_util.window, 4000, 'Bayes factor warning',
            'More than 2 groups found. Using the first two alphabetically: ' +
            str(labels[0]) + ' and ' + str(labels[1]) + '.', False)
        labels = labels[:2]
        df = df[df[group_col].isin(labels)]

    a = df[df[group_col] == labels[0]][value_col].values.astype(float)
    b = df[df[group_col] == labels[1]][value_col].values.astype(float)
    if len(a) < 2 or len(b) < 2:
        mb.showwarning(title='Insufficient data', message='Each group needs at least 2 observations.')
        return filesToOpen

    from scipy import stats as _st
    t_student = float(_st.ttest_ind(a, b, equal_var=True)[0])       # pooled t drives the JZS BF
    p_welch = float(_st.ttest_ind(a, b, equal_var=False)[1])        # Welch p, for reference
    try:
        bf10 = float(_jzs_bf10_twosample(t_student, len(a), len(b)))
    except Exception as _bfe:
        print('Bayes factor integration failed:', str(_bfe))
        bf10 = float('nan')
    bf01 = (1.0 / bf10) if (bf10 == bf10 and bf10 > 0) else float('nan')

    def _bf_interp(bf):
        if bf != bf:
            return 'not available'
        if bf > 100:
            return 'extreme evidence for a difference'
        if bf > 30:
            return 'very strong evidence for a difference'
        if bf > 10:
            return 'strong evidence for a difference'
        if bf > 3:
            return 'moderate evidence for a difference'
        if bf > 1:
            return 'anecdotal evidence for a difference'
        if bf > 1 / 3.0:
            return 'anecdotal evidence for NO difference'
        if bf > 1 / 10.0:
            return 'moderate evidence for NO difference'
        if bf > 1 / 30.0:
            return 'strong evidence for NO difference'
        return 'very strong evidence for NO difference'

    mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
    pooled_sd = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) /
                        (len(a) + len(b) - 2)) if (len(a) + len(b) - 2) > 0 else 0.0
    cohens_d = (mean_a - mean_b) / pooled_sd if pooled_sd > 0 else 0.0

    summary_df = pd.DataFrame({
        'Statistic': ['Bayes factor BF10 (difference vs none)', 'Interpretation',
                      'Bayes factor BF01 (none vs difference)', "Cohen's d (effect size)",
                      't statistic (pooled)', 'p-value (Welch, for reference)',
                      'Group A', 'Group A n', 'Group A mean',
                      'Group B', 'Group B n', 'Group B mean'],
        'Value': [round(bf10, 4) if bf10 == bf10 else 'n/a', _bf_interp(bf10),
                  round(bf01, 4) if bf01 == bf01 else 'n/a', round(cohens_d, 4),
                  round(t_student, 4), round(p_welch, 6),
                  str(labels[0]), len(a), round(mean_a, 4),
                  str(labels[1]), len(b), round(mean_b, 4)]
    })
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'bayes_factor')
    filesToOpen.append(out1)
    return filesToOpen


# ---------------------------------------------------------------------------
# 11. Silhouette -- how cohesive / well-separated a clustering is
# ---------------------------------------------------------------------------
def run_silhouette_test(inputFilename, outputDir, label_col, feature_cols=None,
                        chartPackage='Excel', dataTransformation='No transformation'):
    """How well-separated a clustering is. Given a cluster-label column plus numeric feature
    columns, the silhouette score (-1..1) measures, per item, how close it is to its own
    cluster vs the nearest other cluster. Overall ~1 = tight, well-separated clusters; ~0 =
    overlapping; < 0 = points likely mis-assigned. Per-cluster means are reported so weak
    clusters stand out. Features default to ALL numeric columns except the label (and obvious
    ID columns)."""
    filesToOpen = []
    df = _validate_csv_input(inputFilename)
    if df is None:
        return filesToOpen
    if label_col not in df.columns:
        mb.showwarning(title='Column error',
                       message='Cluster-label column "' + str(label_col) + '" not found.')
        return filesToOpen

    if feature_cols:
        feats = [c for c in feature_cols if c in df.columns and c != label_col]
    else:
        feats = []
        for c in df.columns:
            if c == label_col or str(c).strip().lower() in _SKIP_COLS:
                continue
            if pd.to_numeric(df[c], errors='coerce').notna().mean() >= 0.5:   # majority numeric
                feats.append(c)
    if not feats:
        mb.showwarning(title='No feature columns',
                       message='Silhouette needs at least one NUMERIC feature column besides the cluster '
                               'labels.\n\nSelect the Group column as the cluster labels; all numeric columns '
                               'are used as features.')
        return filesToOpen

    keep = df[[label_col] + feats].copy()
    for c in feats:
        keep[c] = pd.to_numeric(keep[c], errors='coerce')
    keep = keep.dropna()
    if len(keep) < 3:
        mb.showwarning(title='Insufficient data',
                       message='Silhouette needs 3+ rows with a label and complete numeric features.')
        return filesToOpen

    labels = keep[label_col].astype(str).values
    Xv = keep[feats].values.astype(float)
    n_clusters = len(set(labels))
    if n_clusters < 2 or n_clusters >= len(labels):
        mb.showwarning(title='Cluster error',
                       message='Silhouette needs at least 2 clusters and fewer clusters than items. Found ' +
                               str(n_clusters) + ' clusters in ' + str(len(labels)) + ' items.')
        return filesToOpen

    from sklearn.metrics import silhouette_score, silhouette_samples
    overall = float(silhouette_score(Xv, labels))
    samp = silhouette_samples(Xv, labels)
    if overall > 0.70:
        interp = 'strong, well-separated clusters'
    elif overall > 0.50:
        interp = 'reasonable structure'
    elif overall > 0.25:
        interp = 'weak structure (clusters overlap)'
    elif overall > 0:
        interp = 'very weak / artificial structure'
    else:
        interp = 'no substantial structure (points likely mis-assigned)'

    summary_df = pd.DataFrame({
        'Statistic': ['Overall silhouette score', 'Interpretation', 'N clusters', 'N items', 'N features'],
        'Value': [round(overall, 4), interp, n_clusters, len(labels), len(feats)]
    })
    out1 = _save_results_csv(summary_df, inputFilename, '', outputDir, 'silhouette_summary')
    filesToOpen.append(out1)

    per = pd.DataFrame({'Cluster': labels, '_s': samp}).groupby('Cluster', as_index=False).agg(
        Mean_silhouette=('_s', 'mean'), N=('_s', 'size')).sort_values('Mean_silhouette', ascending=False)
    per['Mean_silhouette'] = per['Mean_silhouette'].round(4)
    out2 = _save_results_csv(per, inputFilename, '', outputDir, 'silhouette_by_cluster')
    filesToOpen.append(out2)

    try:
        outputFiles = charts_util.run_all(
            [[0, 1]], out2, outputDir, outputFileLabel='silhouette',
            chartPackage=chartPackage, dataTransformation=dataTransformation,
            chart_type_list=['bar'],
            chart_title='Silhouette by cluster (overall=' + str(round(overall, 3)) + ')',
            column_xAxis_label_var='Cluster', column_yAxis_label_var='Mean silhouette',
            hover_info_column_list=[])
        _append_chart_files(filesToOpen, outputFiles)
    except Exception as _ce:
        print('Silhouette chart skipped:', str(_ce))
    return filesToOpen


# ---------------------------------------------------------------------------
#  Auto-detect: examine a CSV and run appropriate statistical tests
# ---------------------------------------------------------------------------

_DATE_HINTS = {'date', 'year', 'month', 'time', 'day', 'period', 'week', 'quarter'}
_SKIP_COLS = {'document id', 'document', 'sentence id', 'sentence', 'word id',
              'word', 'record id', 'filename', 'interpretation'}


def _is_date_column(series):
    if series.dtype == 'datetime64[ns]':
        return True
    name_lower = series.name.lower().strip()
    if any(hint in name_lower for hint in _DATE_HINTS):
        sample = series.dropna().head(20)
        try:
            pd.to_datetime(sample, infer_datetime_format=True)
            return True
        except:
            return False
    return False


def _get_numeric_cols(df):
    skip = _SKIP_COLS
    numeric = []
    for col in df.columns:
        if col.lower().strip() in skip:
            continue
        if pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() > 1:
            numeric.append(col)
    return numeric


def _get_categorical_group_col(df):
    for col in df.columns:
        name = col.lower().strip()
        if name in _SKIP_COLS:
            continue
        if df[col].dtype == 'object' and 2 <= df[col].nunique() <= 50:
            return col
    return None


def run_automatic_tests(inputFilename, outputDir,
                        chartPackage='Excel', dataTransformation='No transformation'):
    filesToOpen = []

    df = _validate_csv_input(inputFilename)
    if df is None or len(df) < 5:
        return filesToOpen

    numeric_cols = _get_numeric_cols(df)
    date_col = None
    for col in df.columns:
        if _is_date_column(df[col]):
            date_col = col
            break

    # --- Mann-Kendall trend test: date column + numeric columns ---
    if date_col and len(numeric_cols) >= 1:
        for val_col in numeric_cols[:3]:
            try:
                results = run_mann_kendall_trend_test(
                    inputFilename, outputDir, date_col, val_col,
                    chartPackage, dataTransformation)
                filesToOpen.extend(results)
            except:
                pass

    # --- Spearman correlation: pairs of numeric columns ---
    if len(numeric_cols) >= 2:
        pairs = list(combinations(numeric_cols, 2))
        if len(pairs) > 10:
            pairs = pairs[:10]
        for col_x, col_y in pairs:
            try:
                results = run_correlation_test(
                    inputFilename, outputDir, col_x, col_y,
                    method='spearman', chartPackage=chartPackage,
                    dataTransformation=dataTransformation)
                filesToOpen.extend(results)
            except:
                pass

    # --- Chi-square: categorical group col + frequency/count column ---
    group_col = _get_categorical_group_col(df)
    if group_col:
        freq_cols = [c for c in numeric_cols
                     if any(k in c.lower() for k in ('freq', 'count', 'total'))]
        if freq_cols:
            for fc in freq_cols[:2]:
                other_cat = None
                for col in df.columns:
                    if col == group_col or col.lower().strip() in _SKIP_COLS:
                        continue
                    if df[col].dtype == 'object' and 2 <= df[col].nunique() <= 50:
                        other_cat = col
                        break
                if other_cat:
                    try:
                        results = run_chi_square_test(
                            inputFilename, outputDir, group_col, other_cat,
                            chartPackage, dataTransformation)
                        filesToOpen.extend(results)
                    except:
                        pass

    return filesToOpen
