from Min_Heap import *
from utils import *
import synonyms
import csv


# 将目标的 id 在全局的 list 中删除
def Not_MergeIndexTable(word: list[str], IdAll: list[str]) -> list[str]:
    set1 = set(word)
    set2 = set(IdAll)
    return list(set2 - set1)


# 索引表的与操作
# 将两个与操作的字符对应的索引表筛选，并新生成一个索引项，其文档序号为两者的与
def And_MergeIndexTable(Word1: list[str], Word2: list[str]) -> list[str]:
    set1 = set(Word1)
    set2 = set(Word2)
    return list(set1 & set2)


# 将两个相似词的 id 列表合并
# 使用 set 的并集操作进行合并
def Or_MergeIndexTable(Word1: list[str], Word2: list[str]) -> list[str]:
    set1 = set(Word1)
    set2 = set(Word2)
    return list(set1 | set2)


# 将与操作的字符项全部加入优先队列中
# 逐渐将字符进行 pop
def And_operator(word_list: list[Word], query_dict: dict[list]):
    # 初始化数据列表
    data: list[Word] = [Word("start", 2 * 31, [])]
    min_heap = Min_heap(data, cmp)
    for word in word_list:
        min_heap.HEAP_INSERT(word)
    while min_heap.lenth > 1:
        # pop 出长度最小的两个 bool 项
        # 将词的下标进行存储
        word_min = min_heap.HEAP_MINIMUM()
        min_heap.HEAP_EXTRACT_MIN()
        word_least_min = min_heap.HEAP_MINIMUM()
        min_heap.HEAP_EXTRACT_MIN()
        # 与操作将两个词的索引进行 and 操作
        new_idlist = And_MergeIndexTable(word_min.id_list, word_least_min.id_list)
        # 将两个词组成一个新词，并将其加入最小堆中
        # 长度为两个之和, 名字字符自己设定, 看索引表对应的情况
        new_word = Word("New_name" + word_min.word + word_least_min.word,
                        word_min.WordLen + word_least_min.WordLen,
                        new_idlist)
        query_dict["New_name" + word_min.word + word_least_min.word] = new_idlist
        min_heap.HEAP_INSERT(new_word)
    return query_dict[min_heap.HEAP_MINIMUM().word]


# 对输入的语句进行分词处理并得到每个词相应的近义词
# 这里只选取了第一个最相近的近义词进行处理
def GetMovieSynonymWords() -> list[tuple]:
    sentence = input("请输入查询的语句")
    useful_keywords = {'导演', '编剧', '主演', '类型', '制片国家/地区', '又名', 'IMDb', '语言'}
    util = utils()
    words = util.split(sentence)
    # 将停用词去除
    words = words - useful_keywords
    print(words)
    synonym_words = []
    for word in words:
        if synonyms.nearby(word) != ([], []):
            synonym_words.append((word, synonyms.nearby(word)[0][1]))
        else:
            synonym_words.append((word, word))
    print(synonym_words)
    return synonym_words


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


# bool 查询函数
# 返回满足条件的结果
def Bool_language_process():
    synonym_words = GetMovieSynonymWords()
    query_dict = Generate_Word_List(synonym_words)
    # 存储全部的 id
    id_all = []
    # 读取相应的 id 文件
    file_name = "../../data/Movie_id.txt"
    with open(file_name, encoding="utf8", mode="r") as f:
        for row in f.readlines():
            id_all.append(row.split('\n')[0])
    data = []
    for key in query_dict:
        data.append(Word(key, len(query_dict[key]), query_dict[key]))
    result = And_operator(data, query_dict)
    print(result)


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


if __name__ == '__main__':
    function = input("输入进行的查询操作\n输入 bool 为布尔查询\t 输入 natural 为自然语言查询\n")
    if function == "natural":
        Natural_language_process()
    elif function == "bool":
        Bool_language_process()
    else:
        print("输入错误")
    Bool_language_process()
