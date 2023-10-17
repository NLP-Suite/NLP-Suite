
# given a comma-separated string in input, the function returns two variables:
#   a string with properly separated values
#   a list of properly separated values
#  https://stackoverflow.com/questions/4298415/omit-last-element-in-comma-separated-list
# x = "first, second, third,"
# y = [ele for ele in x.split(',') if ele]
# y
# ['first', ' second', ' third']

def process_comma_separated_list(keywords, case_sensitive=True):
    if not case_sensitive:
        keywords = keywords.lower()
    if isinstance(keywords,str):
        # keywords_list = [ele for ele in keywords.split(',') if ele]
        keywords_list=keywords.split(',')
    else:
        keywords_list = keywords
    # create a temporary string list that will be used to remove extra leading and trailing blanks and extra ,
    str_temp = ((', '.join(str(ele) for ele in keywords_list)).lstrip()).rstrip()

    # take out any extra blanks left and right
    if str_temp[-1] == ',':
        str_temp = str_temp[:-1]
    str_temp = str_temp.rstrip()
    # split for , and create a list []
    keywords_list = str_temp.split(',')

    str_cleaned = ''
    for w in keywords_list:
        w = w.lstrip()
        w = w.rstrip()
        str_cleaned = str_cleaned + ',' + w
    if str_cleaned[0] == ',':
        str_cleaned = str_cleaned[1:]
    if str_cleaned[-1] == ',':
        str_cleaned = str_cleaned[:-1]
    # create a cleaned list by split the string
    str_cleaned_list=str_cleaned.split(',')
    return str_cleaned, str_cleaned_list
