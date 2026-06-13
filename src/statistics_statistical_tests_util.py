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

    df = df[[value_col, group_col]].dropna()

    if not pd.api.types.is_numeric_dtype(df[value_col]):
        mb.showwarning(title='Column type error',
                       message='Column "' + value_col + '" must be numeric.')
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

    df = df[[value_col, group_col]].dropna()

    if not pd.api.types.is_numeric_dtype(df[value_col]):
        mb.showwarning(title='Column type error',
                       message='Column "' + value_col + '" must be numeric.')
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

    df = df[[date_col, value_col]].dropna()

    if not pd.api.types.is_numeric_dtype(df[value_col]):
        mb.showwarning(title='Column type error',
                       message='Column "' + value_col + '" must be numeric.')
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

    df = df[[col_x, col_y]].dropna()

    for col in [col_x, col_y]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            mb.showwarning(title='Column type error',
                           message='Column "' + col + '" must be numeric.')
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
