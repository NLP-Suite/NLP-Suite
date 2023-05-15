


# given a comma-separated string in input, the function returns a variable with separated values
#  https://stackoverflow.com/questions/4298415/omit-last-element-in-comma-separated-list
# x = "first, second, third,"
# y = [ele for ele in x.split(',') if ele]
# y
# ['first', ' second', ' third']
def split_commaSeparated_string(inputString):
    #remove extra blanks
    inputString = inputString.replace(" ", "")
    separatedString_var=[ele for ele in inputString.split(',') if ele]
    return separatedString_var

def commaSeparated_string_2_list(inputString):
    outputList=[]
    outputList=inputString.split(',')
    return outputList
