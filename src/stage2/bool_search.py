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
            while table1[1][i]['index'] is not None and table1[1][i]['value'] < table2[0][j]:
                i = table1[1][i]['index']
            else:
                i += 1
        else:
            while table2[1][j]['index'] is not None and table2[1][j]['value'] < table1[0][i]:
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


def getPriority(operator: str):
    if operator == ")" or operator == "(":
        return 1
    elif operator == 'OR':
        return 2
    elif operator == 'AND':
        return 3
    elif operator == 'NOT':
        return 4


def calculate(element_stack: list, id_all):
    calculate_stack = []
    for i in range(0, len(element_stack)):
        if element_stack[i] != "NOT" and element_stack[i] != "AND" and element_stack[i] != "OR":
            calculate_stack.append(element_stack[i])
        elif element_stack[i] == "AND":
            elem2 = calculate_stack.pop()
            elem1 = calculate_stack.pop()
            calculate_stack.append(AndOperator(elem1, elem2))
        elif element_stack[i] == "OR":
            elem2 = calculate_stack.pop()
            elem1 = calculate_stack.pop()
            calculate_stack.append(OrOperator(elem1, elem2))
        else:
            elem1 = calculate_stack.pop()
            calculate_stack.append(NotOperator(id_all, elem1))
    return calculate_stack.pop()


def bool_operator(sentence: str, data, id_all):
    cstack = []
    operator_stack = []
    element_stack = []
    while sentence != "":
        cstack.append(("AND", sentence.find("AND")))
        cstack.append(("OR", sentence.find("OR")))
        cstack.append(("NOT", sentence.find("NOT")))
        cstack.append(("(", sentence.find("(")))
        cstack.append((")", sentence.find(")")))
        index = min_index(cstack)
        if cstack[index][1] == -1:
            if sentence in data.keys():
                element_stack.append(data[sentence])
            else:
                element_stack.append(())
            break
        else:
            if cstack[index][0] == "(" or len(operator_stack) == 0:
                operator_stack.append(cstack[index][0])
                if cstack[index][0] == "AND" or cstack[index][0] == "OR":
                    if sentence[0:cstack[index][1]] in data.keys():
                        element_stack.append(data[sentence[0:cstack[index][1]]])
                    else:
                        element_stack.append(())
                sentence = sentence[cstack[index][1] + len(cstack[index][0]):]
            elif getPriority(operator_stack[len(operator_stack) - 1]) > getPriority(cstack[index][0]):
                if cstack[index][0] == ")":
                    if sentence[0:cstack[index][1]] in data.keys():
                        element_stack.append(data[sentence[0:cstack[index][1]]])
                    else:
                        element_stack.append(())
                    while len(operator_stack) != 0 and operator_stack[len(operator_stack) - 1] != "(":
                        element_stack.append(operator_stack.pop())
                    operator_stack.pop()
                    sentence = sentence[cstack[index][1] + len(cstack[index][0]):]
                else:
                    if cstack[index][0] == "AND" or cstack[index][0] == "OR":
                        if sentence[0:cstack[index][1]] in data.keys():
                            element_stack.append(data[sentence[0:cstack[index][1]]])
                        else:
                            element_stack.append(())
                    while len(operator_stack) != 0 and getPriority(
                            operator_stack[len(operator_stack) - 1]) > getPriority(
                        cstack[index][0]):
                        element_stack.append(operator_stack.pop())
                    operator_stack.append(cstack[index][0])
                    sentence = sentence[cstack[index][1] + len(cstack[index][0]):]
            else:
                if cstack[index][0] == "AND" or cstack[index][0] == "OR":
                    if sentence[0:cstack[index][1]] in data.keys():
                        element_stack.append(data[sentence[0:cstack[index][1]]])
                    else:
                        element_stack.append(())
                operator_stack.append(cstack[index][0])
                sentence = sentence[cstack[index][1] + len(cstack[index][0]):]
        cstack = []
    while len(operator_stack) != 0:
        element_stack.append(operator_stack.pop())
    print(element_stack)
    return calculate(element_stack, id_all)


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
    result = bool_operator(sentence, data, id_all)
    if result == ():
        print("无相关结果")
    else:
        print(bool_operator(sentence, data, id_all)[0])
