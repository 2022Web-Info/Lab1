import pickle
import jieba


class utils():
    def __init__(self) -> None:
        word_dict = []
        self.jieba = jieba
        with open("./data/word_dict.pkl", "rb") as f:
            word_dict = pickle.load(f)
        for word in word_dict:
            self.jieba.add_word(word)
        self.stopwords = {
            line.strip()
            for line in open('./data/stopwords.txt', encoding='utf8').readlines()
        }
        for word in ['', '\n', ' ', '\u3000']:  # 添加额外的停用词
            self.stopwords.add(word)

    def split(self, str) -> set:
        words = set(self.jieba.cut_for_search(str))
        words = words - self.stopwords
        return words

if __name__ == "__main__":
    util = utils()
    print(util.split("诺兰导演的盗梦空间"))