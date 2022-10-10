import pandas as pd
import jieba
from tqdm import tqdm
"""
    对于书籍和电影的信息进行分词
"""

string = '''理查德·林克莱特 导演 
伊桑·霍克 饰 Jesse 
朱莉·德尔佩 饰 Céline 
弗农·多布切夫 饰 Bookstore Manager 
路易丝·勒莫瓦纳·托雷斯 饰 Journalist #1 
罗多尔·保利 饰 Journalist #2 
'''


def split_English(str):
    "将一句话中最后的英文部分完整分离"
    idx = -1
    for i in range(len(str)):
        if (str[i] >= 'A' and str[i] <= 'Z') or (str[i] >= 'a' and str[i] <= 'z'):
            idx = i
            break
    if idx == -1:
        return str, ''
    else:
        return str[:idx], str[idx:]

def split_book_info(info: str):
    """
        从小说的基本信息中提取关键词
    """
    useless_words = [
        '出版社:', '\r', '/', ':', ' 著', ' 续', '作者', '出品方', '原作名', '译者', '出版年', '页数', '定价',
        '装帧', '丛书', '?', 'ISBN', ' 作者'
    ]
    for word in useless_words:
        info = info.replace(word, "")
    word_list = info.split("\n")
    key_words = set()
    for word in word_list:
        temp = word.replace(" ", "")
        if len(word) == 0 or len(temp) == 0:
            continue
        word = word.strip()
        if word not in useless_words:
            if '[' in word:
                key_words.add(word[0:3])
                key_words.add(word[3:].strip())
            else:
                key_words.add(word)
    return key_words

def split_book(book):
    key_words = set()
    key_words.add(str(book['id']))
    name = str(book['书名'])
    idx = name.find("(")
    if idx != -1:  # 删除括号信息
        key_words.add(name[idx + 1:-1])
        name = name[:idx]
    for word in name.split():
        key_words.add(word)
    info = str(book['基本信息'])
    intro = str(book['内容简介'])
    key_words = set.union(key_words, split_book_info(info))
    for word in key_words:
        word = str(word)
        jieba.add_word(word)
    key_words = set.union(key_words, set(jieba.cut_for_search(intro)))
    for word in key_words:
        word = str(word)
        jieba.del_word(word)
    return key_words

def split_movie_info(info: str):
    """
        从电影的基本信息中提取关键词
    """
    useful_keywords = ['导演:', '编剧:', '主演:', '类型:', '制片国家/地区:', '又名:', 'IMDb:', '语言:']
    key_words = set()
    line_list = info.split("\n")
    for line in line_list:
        add = False
        for word in useful_keywords:
            if word in line:
                add = True
                line = line.replace(word, "")
        if add == False:
            continue
        words = line.split("/")
        for word in words:
            word = word.strip()
            idx = word.find("(")
            if idx != -1:
                key_words.add(word[:idx])
            else:
                key_words.add(word)
    return key_words


def split_movie_stuff(stuff: str):
    """
        从电影的演职员表中提取关键词
    """
    useless_words = [' 饰', ' 配']
    key_words = set()
    for word in useless_words:
        stuff.replace(word, ' ')
    lines = stuff.split("\n")
    for line in lines:
        chinese, english = split_English(line)
        if len(english) != 0:
            key_words.add(english.strip())
        word_list = chinese.split(" ")
        for word in word_list:
            if len(word) != 0:
                key_words.add(word)
    return key_words


def split_movie(movie):
    """
        电影分词
    """
    key_words = set()
    key_words.add(str(movie['id']))
    name = str(movie['电影名'])
    idx = name.find("(")
    if idx != -1:  # 删除后面的年份
        key_words.add(name[idx + 1:-1])
        name = name[:idx]
    chinese, english = split_English(name)  # 保留英文名的完整性
    if len(english) != 0:
        key_words.add(english)
    for word in chinese.split():  # 对于韩文和日文等没有处理
        key_words.add(word)
    info = str(movie['基本信息'])
    stuff = str(movie['演职员'])
    intro = str(movie['剧情简介'])
    key_words = set.union(key_words, split_movie_stuff(stuff))
    key_words = set.union(key_words, split_movie_info(info))
    for word in key_words:
        word = str(word)
        jieba.add_word(word)
    key_words = set.union(key_words, set(jieba.cut_for_search(intro)))
    for word in key_words:
        word = str(word)
        jieba.del_word(word)
    return key_words
    

if __name__ == "__main__":
    book_data = pd.read_csv("./data/book.csv")
    book_tag = pd.read_csv("./data/Book_tag.csv")
    stopwords = {
        line.strip()
        for line in open('./data/stopwords.txt', encoding='utf8').readlines()
    }
    for word in ['','\n',' ','\u3000']: # 添加额外的停用词
        stopwords.add(word)
    col_name = ['id', 'words']
    book_words = []
    for _,book in tqdm(book_data.iterrows(), total=book_data.shape[0], leave=False):
        key_words = split_book(book)
        temp = list(book_tag.loc[book_tag['id'] == book['id']]['tag'])
        if len(temp) != 0: # 存在 tag 数据
            tags = temp[0]
            tag_words = set(str(tags).split(","))
        key_words = set.union(key_words, tag_words)
        key_words = key_words - stopwords
        book_words.append({'id': book['id'], 'words': key_words})
    pd.DataFrame(book_words,columns=col_name).to_csv("./data/book_words.csv",index=False)
    print("split book finish!")

    movie_data = pd.read_csv("./data/movie.csv")
    movie_tag = pd.read_csv("./data/Movie_tag.csv")
    col_name = ['id', 'words']
    movie_words = []
    for _,movie in tqdm(movie_data.iterrows(), total=movie_data.shape[0], leave=False):
        key_words = split_movie(movie)
        tags = list(movie_tag.loc[movie_tag['id'] == movie['id']]['tag'])[0]
        tag_words = set(str(tags).split(","))
        key_words = set.union(key_words, tag_words)
        key_words = key_words - stopwords
        movie_words.append({'id': movie['id'], 'words': key_words})
    pd.DataFrame(movie_words,columns=col_name).to_csv("./data/movie_words.csv",index=False)
    print("split movie finish!")