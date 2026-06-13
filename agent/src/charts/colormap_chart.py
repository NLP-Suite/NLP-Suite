import json
import logging

import charts_util
from util import collect

logger = logging.getLogger(__name__)


def run_colormap(
    inputFilename,
    outputDir,
    csv_file_categorical_field_list,
    max_rows_var,
    color_1_style_var,
    color_2_style_var,
    normalize_var,
    inputFileData,
):
    """Render colormap charts from categorical csv fields."""
    filesToOpen = []
    all_fields = []
    intermediate_fields = []
    csv_file_categorical_field_list = json.loads(csv_file_categorical_field_list)
    logger.info(csv_file_categorical_field_list)
    for i in range(len(csv_file_categorical_field_list)):
        if i > 0 and i < len(csv_file_categorical_field_list) - 1:
            intermediate_fields.append(csv_file_categorical_field_list[i][0].split("|")[0])
        all_fields.append(csv_file_categorical_field_list[i][0].split("|")[0])

    # mb.showwarning(title='Search values',
    #                         ' different search fields: "' + all_fields_str + '".' + \
    #                         '\n\nThe first selected field "' + csv_file_categorical_field_list[0][0].split('|')[0] + '" will be used as the GroupBy field.' + \
    #                         '\n\nThe last field "' + csv_file_categorical_field_list[len(csv_file_categorical_field_list)-1][0].split('|')[0] + '" will be used as the field whose values will be displayed.' + \
    #                         '\n\nAll other intermediate fields "' + intermediate_fields_str + '" will be used as the conditional WHERE CLAUSE.')

    # if csv_field_categorical_var == '':
    #     mb.showwarning("Warning",
    #                     "The colormap/heatmap algorithm requires a value for 'csv file field.'\n\nPlease, select a value and try again.")
    params = [max_rows_var, color_1_style_var, color_2_style_var, normalize_var]
    outputFiles = charts_util.colormap(
        inputFilename,
        outputDir,
        csv_file_categorical_field_list,
        params,
        inputFileData=inputFileData,
    )

    if outputFiles is not None:
        collect(filesToOpen, outputFiles)

    return outputFiles


def main():
    inputFileData = """Obs,Name,Gender,Fixed,Color,Heritage,Age,Weight,Size
    1,Max,Male,Yes,Dark brown,Designer/deliberate mix,7,70,Large
    2,Isla,Female,Yes,Black,Single breed,8,13,Small
    3,Tyson,Male,No,Black,Mixed breed/unknown,0.33,24,Large
    4,Lexi,Female,Yes,Light brown, Designer,6,24,Small
    5,,Male,Yes,Light brown,Mixed breed/unknown,6,45,Large
    6,Lola,Female,Yes,Black,Mixed breed/unknown,14,85,Large
    7,Lady,Female,Yes,Black,Single breed,11,22,Small
    8,Leo,Male,Yes,Reddish,Single breed,15,14,Small"""

    outputDir = "/Users/aidenamaya/nlp-suite/output"
    inputFilename = "sample.csv"

    #                                     #GROUPBY,     WHERE,         SELECT
    #                                 # GROUPBY format: [field|Val1, Val2...], Vals optional
    #                                 # WHERE format: [field|Val1, Val2...], Vals not optional
    #                                 # SELECT format: [field|]

    csv_file_categorical_field_list = '[["Age|"],["Weight|"]]'
    max_rows_var = 5
    color_1_style_var = "135,207,236"
    color_2_style_var = "0,0,255"
    normalize_var = "log"

    # Run the colormap visualization
    try:
        output_files = run_colormap(
            inputFilename,
            outputDir,
            csv_file_categorical_field_list,
            max_rows_var,
            color_1_style_var,
            color_2_style_var,
            normalize_var,
            inputFileData=inputFileData,
        )
        logger.info("Output files generated: %s", output_files)
    except Exception as e:
        logger.info("An error occurred during testing: %s", e)


if __name__ == "__main__":
    main()
