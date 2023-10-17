
# given a comma-separated string in input, the function returns two variables:
#   a string with cleaned separated values (i.e., no extra blanks) and a list [] of elements from the cleaned string

def process_comma_separated_string_list(keywords, case_sensitive=True):
    if not case_sensitive:
        keywords = keywords.lower()
    if isinstance(keywords,str):
        keywords_list=keywords.split(',')
    else:
        keywords_list = keywords
    temp_keywords_list=[]
    keywords_str=''
    for index, ele in enumerate(keywords_list):
        ele=ele.strip()
        if ele != '':
            temp_keywords_list.append(ele)
            if keywords_str=='':
                keywords_str = ele
            else:
                keywords_str = keywords_str + ',' + ele
    keywords_list=temp_keywords_list

    return keywords_str, keywords_list
