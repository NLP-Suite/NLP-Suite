#from asyncio.windows_events import NULL
from datetime import datetime as dt
import os

# get all files in the directory and filter them for given filetypes
# get their metadata by calling get_file_metadata
def get_all_file_metadata(path,filetypes):
    file_list = os.listdir(path)
    all_meta = []
    for i in file_list:
        for j in filetypes:
            if i.endswith(j):
                all_meta.append(get_file_metadata(path, i))
    return all_meta

# get file metadata   more data available but time makes more sense
# can be added later if necessary
def get_file_metadata(path, filename):
    data = os.stat(os.path.join(path, filename))
    metadata = [filename,-1,-1,-1]
    metadata[1] = dt.fromtimestamp(int(data.st_atime)) #time last access
    metadata[2] = dt.fromtimestamp(int(data.st_mtime)) #time last modified
    metadata[3] = dt.fromtimestamp(int(data.st_ctime)) #time created

    return metadata

#return the file within the given date range
def limit_by_file_date(path, filetypes, date_lower, date_upper, which_date=2):
    # for which date default if date modified
    # 1 stands for date last access
    # 2 stands for date last modified
    # 3 stands for date created
    get_file_metadata = get_all_file_metadata(path, filetypes)
    file_list = []
    for i in get_file_metadata:
        if i[2] >= date_lower and i[2] <= date_upper:
            file_list.append(i)
    return file_list

# =======================================================================================================================
# debug use
# =======================================================================================================================
# def main():
#     path = "C:/Users/Tony Chen/Desktop/NLP_working/NLP-Suite/src"
#     data_type = [".py"]
    
#     a = get_all_file_metadata(path, data_type)
#     print(a)
# if __name__ == "__main__":
#     main()