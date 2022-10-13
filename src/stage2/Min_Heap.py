from typing import Callable


# word 类
class Word(object):
    # word: 输入的字词
    # WordLen: 字词对应的倒排表长度
    def __init__(self, word: str, WordLen: int, id_list: list[str]):
        self.word = word
        self.WordLen = WordLen
        self.id_list = id_list


# 优先队列的 cmp 比较函数，确定先后顺序
def cmp(word1: Word, word2: Word):
    return word1.WordLen < word2.WordLen


class Min_heap(object):
    # 初始化，填入数据以及存储当前堆的长度
    # 此堆是从 1 开始
    def __init__(self, data: list[Word], cmp: Callable[[Word, Word], bool]) -> None:
        self.data = data
        self.lenth = len(data) - 1
        self.cmp = cmp

    # 返回该结点的父亲结点

    def parent(self, i: int) -> int:
        return i // 2

    # 返回左右孩子对应下标

    def left_child(self, i: int) -> int:
        return 2 * i

    def right_child(self, i: int) -> int:
        return 2 * i + 1

    # 维护最小堆的性质
    # p 为待整理元素下标
    # q 为列表的最后一个元素下标
    # 每次整理完之后递归往下看下面的元素是否符合最小堆的定义

    def MIN_HEAPIFY(self, p: int) -> None:
        left = self.left_child(p)
        right = self.right_child(p)
        least = p
        if left <= self.lenth and self.cmp(self.data[left], self.data[least]):
            least = left
        if right <= self.lenth and self.cmp(self.data[right], self.data[least]):
            least = right
        if self.cmp(self.data[least], self.data[p]):
            temp = self.data[least]
            self.data[least] = self.data[p]
            self.data[p] = temp

    # 得到堆顶的值
    def HEAP_MINIMUM(self):
        return self.data[1]

    # pop (弹出堆顶)
    # 首先将最后一个元素放置在堆顶
    # 之后删除最后的元素
    def HEAP_EXTRACT_MIN(self) -> None:
        if self.lenth > 1:
            self.data[1] = self.data[self.lenth]
            del self.data[self.lenth]
            self.lenth = self.lenth - 1
            self.MIN_HEAPIFY(1)
        else:
            del self.data[self.lenth]
            self.lenth = self.lenth - 1

    # 将最小堆中某值减小

    def HEAP_DECREASE_KEY(self, i: int, key: float) -> None:
        virtial_node = Word(self.data[i].word, key, self.data[i].id_list)
        if self.cmp(virtial_node, self.data[i]):
            self.data[i].WordLen = key
            # 将其与他父亲比较，若小于，则将两者替换，在递归向上进行比较
            while i > 1 and self.cmp(self.data[i], self.data[self.parent(i)]):
                temp = self.data[i]
                self.data[i] = self.data[self.parent(i)]
                self.data[self.parent(i)] = temp
                i = self.parent(i)

    # 插入某值进入最小堆

    def HEAP_INSERT(self, key: Word) -> None:
        self.lenth += 1
        node = key
        word_len = key.WordLen
        node.WordLen = 2 ** 31 - 1
        self.data.append(node)
        self.HEAP_DECREASE_KEY(self.lenth, word_len)

if __name__ == '__main__':
    pass
