import IO_csv_util
import pandas as pd
import numpy as np
import CoNLL_verb_analysis_util
import charts_Excel_util
pd.options.mode.chained_assignment = None
# def merge_voice(data, group_col, series, outputDir, inputFilename, topic_name = ""):
# 	col_to_plot = []
# 	for i in len(data):
# 		series_title = data[i][series][1]
# 		headers = group_col.append(series_title)
# 		verb_file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', headers, 'Verb Voice','list')
# 		data[i].groupby(group_col).apply(list).to_csv(verb_file_name)
# 		data[i] = pd.read_csv(verb_file_name)
# 		col_to_plot.append(series_title)
# 		if(len(data)!=1):
# 			plot_data = data[0]
# 			for i in 1:len(data):
# 			pd.merge(plot_data, data[i], on=group_col, how='outer')
#   		else:
# 		plot_data = data[0]
#   		file_name = IO_files_util.generate_output_file_name(inputFilename, '', outputDir, '.csv', headers, topic_name,'frequency_merged')	
# 	plot_data.to_csv(file_name,headers)
# 	return plot_data

# select_col should be one colmun name
# group_col should be a list of a singe column names eg sentence id, document id
def compute_csv_column_frquencies1(inputFilename, group_col, select_col, outputDir, filesToOpen, graph = True, complete_sid = False):
    cols = group_col + select_col
    try:
        data,header = IO_csv_util.get_csv_data(inputFilename, True)
    except:
        # an error message about unable to read the file
        print("Error: cannot read the file")
        return
    data = CoNLL_verb_analysis_util.verb_voice_data_preparation(data)
    data,stats,pas,aux,act = CoNLL_verb_analysis_util.voice_output(data, group_col)
    data = pd.DataFrame(data,columns=header+["Verb Voice"])
    try:
        print(data[select_col])
        print(data[group_col])
    except:
        # an error message about wrong csv file without the necessary columns
        print("Please select the correct csv file")
        return
    name = outputDir + "temp_frequencies.csv"
    data.to_csv(name)
    if(complete_sid):
        complete_sentence_index(name)
    data = data.groupby(cols).size().to_frame("count")
    data.to_csv(name)
    data = pd.read_csv(name)
    data = data.pivot(index = group_col, columns = select_col, values = "count")
    data = data.fillna(0)
    print(data)
    data.to_csv(name)
    print(name)
    if(graph):
        #TODO: need filename generation and chartTitle generation
        data = pd.read_csv(name,header=0)
        cols_to_be_plotted = []
        for i in range(1,len(data.columns)):
            cols_to_be_plotted.append([0,i])
        chartTitle = "test_multi_line"
        Excel_outputFilename = charts_Excel_util.run_all(cols_to_be_plotted,name,outputDir,
                                        "frequency_multi-line_chart", chart_type_list=["line"], 
                                        chart_title=chartTitle, column_xAxis_label_var="Sentence ID")
        if Excel_outputFilename != "":
            filesToOpen.append(Excel_outputFilename)
    return

# remove comments before variable begin with d_id to enable complete document id function
# need to have a document id column and sentence id column
# would complete the file (make document id and sentence id continuous) and padding zero values for the added rows
def complete_sentence_index(file_path):
    data = pd.read_csv(file_path)
    try:
        print(data["Sentence ID"])
    except:
        print("Only enable complete sentence index when there is a Sentence ID column in the csv file")
        return
    if(len(data) == 1):
        return data
    data2 = pd.DataFrame(columns = data.columns.values.tolist())
    # d_id = 1
    s_id = 1
    for i in range(len(data)):
        s_id_max = data.iloc[i]["Sentence ID"]
        # d_id_max = data.iloc[i]["Document ID"]
        # reset the sentence id when switch the document
        # deafut d_id increse by 1 to detect and other not included document
        # if(d_id != d_id_max):
        #     d_id += 1
        #     s_id = 1
        # padding document id when it's not continuous
        # while(d_id < d_id_max):
        #     temp = pd.DataFrame({"Document ID":[d_id],"Sentence ID":[1]})
        #     data2 =pd.concat([data2,temp])
        #     d_id += 1
        #     s_id = 2
        # padding sentence id when it's not continuous
        while(s_id < s_id_max):
            temp = pd.DataFrame({"Sentence ID":[s_id]})
            data2 =pd.concat([data2,temp])
            s_id += 1
        data2 =pd.concat([data2,data.iloc[[i]].copy(deep=True)])
        s_id += 1
        # fill the added sentence id with 0 values
    data2 = data2.fillna(0)
    data2.to_csv(file_path, index = False)
    return

def compute_csv_column_frquencies(inputFilename, group_col, select_col, method_name, outputDir, graph = True, complete_sentece = False):
    if(complete_sentece and ("Sentence ID" in group_col)):
        # should be an error message
        print("Should include Sentence ID in the group_col")
    cols = group_col + select_col
    data,header = IO_csv_util.get_csv_data(inputFilename, True)
    data = CoNLL_verb_analysis_util.verb_voice_data_preparation(data)
    data,stats,pas,aux,act = CoNLL_verb_analysis_util.voice_output(data, group_col)
    data = pd.DataFrame(data,columns=header+["Verb Voice"])
    #data = pd.DataFrame(data,columns=header)
    cols_to_be_plotted = np.unique(data[select_col].values.tolist())
    data = data.groupby(cols).size().to_frame("count")
    # TODO: need to rewrite the file naming part
    # need to reread it to convert to dataframe
    data.to_csv("C:/Users/Tony Chen/Desktop/NLP_working/Test Output/test_out1.csv")
    data = pd.read_csv("C:/Users/Tony Chen/Desktop/NLP_working/Test Output/test_out1.csv")
    data = data.pivot(index = group_col, columns = select_col, values = "count")
    data = data.fillna(0)
    data.to_csv("C:/Users/Tony Chen/Desktop/NLP_working/Test Output/test_out2.csv")
    if(graph):
        #TODO: need filename generation and chartTitle generation
        xlsxFilename = "test_out2.csv"
        chartTitle = "test_multi_line"
        Excel_outputFilename = charts_Excel_util.run_all(cols_to_be_plotted,xlsxFilename,outputDir,
                                       method_name, chart_type_list=["line"], 
                                       chart_title=chartTitle, column_xAxis_label_var=["Sentence ID"])
    return

#===============================================DEBUG USE=====================================================
def main():
    compute_csv_column_frquencies1("C:/Users/Tony Chen/Desktop/NLP_working/Test Input/conll_chn.csv",["Sentence ID"],
    ["Verb Voice"], "C:/Users/Tony Chen/Desktop/NLP_working/Test Output/",[],True,True)
    # complete_sentence_index("C:/Users/Tony Chen/Desktop/NLP_working/Test Output/test_in.csv")
if __name__ == "__main__":
    main()