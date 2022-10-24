import csv


# 生成对应的 id 列表的倒排表和跳表指针
def generate_table(data: list):
    skip_table = []
    len1 = len(data)
    if len1 == 1 or len1 == 2:
        for i in range(len1):
            skip_table.append({'index': None, 'value': None})
    else:
        for i in range(len1):  # 0 1 2 3 4
            if i % 2 == 0 and i < len1 - 2:
                skip_table.append({'index': i + 2, 'value': data[i + 2]})
            else:
                skip_table.append({'index': None, 'value': None})
    return data, skip_table


# table 为这种结构, 元组内第一个元素为 id 列表, 第二个元素为该 id 对应的跳表指针
# index, value 是下标和下标对应的 id 值
# ([1007433],[{'index': None, 'value': None}])
def AndOperator(table1, table2):
    if table1 == () or table2 == ():
        return ()
    result = []
    i = j = 0
    while i < len(table1[0]) and j < len(table2[0]):
        if table1[0][i] == table2[0][j]:
            result.append(table1[0][i])
            i += 1
            j += 1
        elif table1[0][i] < table2[0][j]:
            while table1[1][i]['index'] is not None and table1[1][i]['value'] <= table2[0][j]:
                i = table1[1][i]['index']
            else:
                i += 1
        else:
            while table2[1][j]['index'] is not None and table2[1][j]['value'] <= table1[0][i]:
                j = table2[1][j]['index']
            else:
                j += 1
    return generate_table(result)


def OrOperator(table1, table2):
    if table1 == ():
        return table2
    elif table2 == ():
        return ()
    result = set(table1[0]) | set(table2[0])
    result = sorted(list(result))
    return generate_table(result)


def NotOperator(id_all, table):
    if table == ():
        return generate_table(id_all)
    result = set(id_all) - set(table[0])
    result = sorted(list(result))
    return generate_table(result)


def min_index(L: list[tuple]):
    index = 0
    for i in range(1, len(L)):
        if L[index][1] == -1:
            index = i
        elif L[i][1] < L[index][1] and L[i][1] != -1:
            index = i
    return index


def Operator(sentence: str, data:dict, id_all:list):
    L = []
    L.append(("AND", sentence.find("AND")))
    L.append(("OR", sentence.find("OR")))
    L.append(("NOT", sentence.find("NOT")))
    index = min_index(L)
    if L[index][1] == -1:
        if sentence not in data.keys():
            return ()
        else:
            return data[sentence]
    else:
        if L[index][0] == "AND":
            return AndOperator(data[sentence[0:L[index][1]]], Operator(sentence[L[index][1] + 3:], data, id_all))
        elif L[index][0] == "OR":
            return OrOperator(data[sentence[0:L[index][1]]], Operator(sentence[L[index][1] + 2:], data, id_all))
        else:
            return NotOperator(id_all, Operator(sentence[L[index][1] + 3:], data, id_all))


def get_data(file_name: str):
    data_dic = {}
    with open(file_name, mode="r", encoding="utf8") as f:
        f_reader = csv.reader(f)
        next(f_reader)
        for row_line in f_reader:
            data_dic[row_line[0]] = (eval(row_line[1]), eval(row_line[2]))
    return data_dic


if __name__ == '__main__':
    filename_book = "../../data/book_invert_v2.csv"
    filename_movie = "../../data/movie_invert_v2.csv"
    id_all = []
    data = {}
    choice = int(input("输入查询的内容\t\t1 表示查询书籍 2表示查询电影\n"))
    if choice == 1:
        data = get_data(filename_book)
        with open(file="../../data/Book_id.txt", encoding="utf8", mode="r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                id_all.append(eval(row[0]))
    elif choice == 2:
        data = get_data(filename_movie)
        with open(file="../../data/Movie_id.txt", encoding="utf8", mode="r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                id_all.append(eval(row[0]))
    else:
        print("输入错误")
    sentence = input("输入查询语句\n")
    result = Operator(sentence, data, id_all)
    if result == ():
        print("无相关结果")
    else:
        print(Operator(sentence, data, id_all)[0])
