from utils import *
import synonyms
import csv
import pandas as pd


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


# 对输入的语句进行分词处理并得到每个词相应的近义词
# 这里只选取了第一个最相近的近义词进行处理
def GetMovieSynonymWords() -> list[tuple]:
    sentence = input("请输入查询的语句\n")
    useless_keywords = {'导演', '编剧', '主演', '类型', '制片国家/地区', '又名', 'IMDb', '语言'}
    util = utils()
    words = util.split(sentence)
    # 将停用词去除
    words = words - useless_keywords
    synonym_words = []
    for word in words:
        if synonyms.nearby(word) != ([], []):
            synonym_words.append((word, synonyms.nearby(word)[0][1]))
        else:
            synonym_words.append((word, word))
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
    result = sorted(id_dict.items(), key=lambda x: x[1], reverse=True)
    movie_info = pd.read_csv("../stage1/data/movie.csv")
    for i, (id, _) in enumerate(result):
        if i >= 4:
            break
        print("=" * 20 + f"查询结果 {i + 1} " + "=" * 20)
        print(f"ID:\n\t{id}")
        movie_dict = movie_info.loc[movie_info['id'] == id]
        movie_content = movie_dict.iloc[0]['剧情简介']
        movie_name = movie_dict.iloc[0]['电影名']
        print(f"电影名: \n\t{movie_name}")
        print(f"内容简介: \n{movie_content}")


# 将近义词的 IdList 进行合并
# words: 分好的词集合
# 这里返回的输入的语句是分词之后的 id_list
# 返回字典：key: word, value: id
def Generate_Word_List(words: list[tuple]) -> dict:
    file_name = "data/movie_invert.csv"
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
        for i in range(0, len(synonym_word), 2):
            if synonym_word[i] in dic.keys() and synonym_word[i + 1] in dic.keys():
                query_WordId_dic[synonym_word[i]] = Or_MergeIndexTable(dic[synonym_word[i]], dic[synonym_word[i + 1]])
            elif synonym_word[i] in dic.keys():
                query_WordId_dic[synonym_word[i]] = dic[synonym_word[i]]
            elif synonym_word[i + 1] in dic.keys():
                query_WordId_dic[synonym_word[i]] = dic[synonym_word[i + 1]]
            else:
                query_WordId_dic[synonym_word[i]] = []
    return query_WordId_dic


if __name__ == '__main__':
    Natural_language_process()
