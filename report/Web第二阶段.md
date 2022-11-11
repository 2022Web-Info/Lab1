## 第二阶段

### 布尔查询 和 自然语言查询

#### 布尔查询

> ​		对于给定的 `bool` 查询 $\text{Q}_\text{bool}$ ，根据生成的倒排索引表 S，返回符合查询规则的电影或书籍集合，并以合适的方式展现给用户，给出电影名称和分类或部分简介。

##### 具体思路

​		输入布尔表达式，首先对其进行处理，使他计算次序符合 `AND`, `OR`, `NOT` 的运算次序，例如 `A OR B AND C` 计算的次序为 `A OR (B AND C)`。

​		假设输入都是合法的

先将输入的布尔表达式转化成后缀布尔表达式，例如 A AND B 转换成 A B AND

**一、中缀布尔表达式转后缀布尔表达式**

设立了两个栈，分别存储 `操作符` 和 `字符`

1. 首先，对于输入的语句，搜索 `AND` ，`OR`，`NOT`，`(`，`)` 所在的位置

   	     2. 如果都不出现在语句中，说明语句处理完毕，跳转到 4
         	     3. 判断搜寻到的操作符是否满足下列情况
               	     1. `(` 或者 `操作符` 栈为空：
                     - 直接将操作符加入对应栈中，并根据操作符类型选择是否将操作符前方临近的字符加入字符栈中
                     - AND，OR 时添加
               	     2. 如果 栈顶 的操作符优先级高于搜寻到的操作符优先级
                     	     1. 如果该操作符是 `)`
                              - 将操作符栈的字符 `pop` 到 字符栈中，直到 `(` 
                     	     2. 否则，将操作符栈 `pop` 到字符栈中，直到不满足上述条件
                     	     3. 其他情况，则直接将操作符压入栈中，并根据操作符类型选择是否将操作符前方临近的字符加入字符栈中。
                     	     4. 布尔查询语句字符处理完毕，将操作符栈中剩余的所有操作符压入字符栈中

**二、计算后缀表达式**

​		新建立了一个栈，存储布尔表达式中间过程和最终的计算结果

`element_stack` 为上面最终得到的字符栈，`calcula_stack` 存储中间过程的计算结果

```python
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
```

**三、布尔查询**

​		我们在第一部分 `布尔表达式中缀转后缀` 已经把每一个词分离出来了，我们进行 `AND`, `OR`, `NOT` 操作时，只需要将这个词对应的倒排表进行 `AND`, `OR`, `NOT` 操作即可。

> ​		起初，我们想先调用近义词库，先把分离出的每个词先找他临近的近义词，先把这些词的倒排表合并，再进行查询语句的布尔运算，但是 `synonyms` 库的效果不尽人意，所以我们在布尔查询里面没有使用近义词库。

​		`AND` 对应倒排表运算，我们采用了跳表指针进行合并。

```python
# ([1007433],[{'index': None, 'value': None}])
# table 为上述结构, 元组内第一个元素为 id 列表, 第二个元素为该 id 对应的跳表指针
# index, value 是下标和下标对应的 id 值
def AndOperator(table1, table2):
    if table1 == () or table2 == ():
        return ()
    result = []
    i = j = 0
    while i < len(table1[0]) and j < len(table2[0]):
        # 两个 list 相等，则合并到新表中
        if table1[0][i] == table2[0][j]:
            result.append(table1[0][i])
            i += 1
            j += 1
        elif table1[0][i] < table2[0][j]:
            # 判定记录是否存在跳表指针以及跳表指针的后续 id 是否小于当前判定的列表 id
            # 满足，则跳转，否则不跳
            while table1[1][i]['index'] is not None and table1[1][i]['value'] < table2[0][j]:
                i = table1[1][i]['index']
            else:
                i += 1
        else:# 同理
            while table2[1][j]['index'] is not None and table2[1][j]['value'] < table1[0][i]:
                j = table2[1][j]['index']
            else:
                j += 1
    return generate_table(result)
```

​		`OR` 运算代表的是倒排表的并集运算，我们这里采用的是直接使用 `set` 集合的或运算进行合并。

​		得到新表后，重新插入跳表指针

```python
def OrOperator(table1, table2):
    if table1 == ():
        return table2
    elif table2 == ():
        return ()
    result = set(table1[0]) | set(table2[0])
    # 排序
    result = sorted(list(result))
    # 重新生成跳表指针
    return generate_table(result)
```

​		`NOT` 运算是将全部 id 减去 对应词的 id 列表，我们这里采用的是直接使用 `set` 集合的补运算进行合并。

​		得到新表后，重新插入跳表指针。

```python
def NotOperator(id_all, table):
    if table == ():
        return generate_table(id_all)
    result = set(id_all) - set(table[0])
    result = sorted(list(result))
    return generate_table(result)

```

##### 结果展示

三位成员的尾号分别为：71，47，88

查询的电影对应为：**摩登时代**、**记忆碎片**、**小鬼当家**

查询结果分别为

<div>
    <table>
        <tr>
            <td>
                <img src="C:\Users\熊鹏\AppData\Roaming\Typora\typora-user-images\image-20221109233707956.png" alt="image-20221109233707956" style="zoom:125%;"/>
            </td>
        </tr>
        <tr>
            <td>
                                <img src="C:\Users\熊鹏\AppData\Roaming\Typora\typora-user-images\image-20221109235446457.png" alt="image-20221109235446457" style="zoom:125%;"/>
            </td>
        </tr>
        <tr>
            <td>
                <img src="C:\Users\熊鹏\AppData\Roaming\Typora\typora-user-images\image-20221110000127028.png" alt="image-20221110000127028" style="zoom:125%;" />
            </td>
        </tr>
    </table>
</div>

#### 自然语言查询

​		先对输入的语句进行分词处理，调用第一部分所写的分词函数，分词之后调用近义词库，将近义词对应的倒排表合并，之后再统计每个分词中对应倒排表 id 出现的次数，将其排序。

**分词，找近义词**

```python
# 对输入的语句进行分词处理并得到每个词相应的近义词
# 这里只选取了第一个最相近的近义词进行处理
def GetMovieSynonymWords() -> list[tuple]:
    sentence = input("请输入查询的语句")
    useless_keywords = {'导演', '编剧', '主演', '类型', '制片国家/地区', '又名', 'IMDb', '语言'}
    util = utils()
    words = util.split(sentence)
    # 将停用词去除
    words = words - useless_keywords
    print(words)
    synonym_words = []
    for word in words:
        if synonyms.nearby(word) != ([], []):
            synonym_words.append((word, synonyms.nearby(word)[0][1]))
        else:
            synonym_words.append((word, word))
    return synonym_words
```

**合并近义词的倒排表**

```python
# 将近义词的 IdList 进行合并
# words: 分好的词集合
# 这里返回的输入的语句是分词之后的 id_list
# 返回字典：key: word, value: id
def Generate_Word_List(words: list[tuple]) -> dict:
    file_name = "../../data/movie_invert.csv"
    # 存储倒排索引表所有的数据
    dic = {}
    # 存储查询语句分词之后的索引数据
    query_WordId_dic = {}
    with open(file_name, encoding="utf8", mode='r') as f:
        csv_reader = csv.reader(f)
        # 从第二行开始读取
        next(csv_reader)
        # 将第二个字符串转为列表
        # 列表中含有的是 id 字段
        for row in csv_reader:
            dic[row[0]] = eval(row[1])
            # print(type(dic[row[0]][0]))
    # print(dic)
    # 将 两个/多个 近义词的 id_list 合并
    for synonym_word in words:
        print(synonym_word)
        for i in range(0, len(synonym_word), 2):
            if synonym_word[i] in dic.keys() and synonym_word[i + 1] in dic.keys():
                print(synonym_word[i], synonym_word[i + 1])
                query_WordId_dic[synonym_word[i]] = Or_MergeIndexTable(dic[synonym_word[i]], dic[synonym_word[i + 1]])
                print(query_WordId_dic)
            elif synonym_word[i] in dic.keys():
                query_WordId_dic[synonym_word[i]] = dic[synonym_word[i]]
            elif synonym_word[i + 1] in dic.keys():
                query_WordId_dic[synonym_word[i]] = dic[synonym_word[i + 1]]
            else:
                query_WordId_dic[synonym_word[i]] = []
    return query_WordId_dic
```

**自然语言处理函数**

```python
# 自然语言处理函数
# 处理已经得到的词对应的 id 列表
# 统计各 id 出现的次数
# 并将其进行排序输出
def Natural_language_process() -> None:
    # 记录查询语句中出现的词 以及对应的 id 列表
    query_dict = {}
    synonym_words = GetMovieSynonymWords()
    query_dict = Generate_Word_List(synonym_words)
    # 记录每一个 id 出现的次数
    id_dict = {}
    # 遍历字典中的每一个词
    for word in query_dict:
        id_list = query_dict[word]
        # 遍历词对应中 id_list 每一个 id
        # 并记录 id 出现的次数
        for id in id_list:
            if id in id_dict.keys():
                id_dict[id] += 1
            else:
                id_dict[id] = 1
    # 输出排序后的结果
    print(sorted(id_dict.items(), key=lambda x: x[1], reverse=True))
```

##### 结果展示

从上到下分别是分词、近义词、词对应的 id 列表和最终查询结果。

第一位是 id ：3541415

![image-20221110001412398](C:\Users\熊鹏\AppData\Roaming\Typora\typora-user-images\image-20221110001412398.png)

![image-20221110001240013](C:\Users\熊鹏\AppData\Roaming\Typora\typora-user-images\image-20221110001240013.png)

结果与预期一致。