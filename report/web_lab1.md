# web lab1

## stage-2

读取每部电影或书籍简介的分词结果，统计出所有的词项

```python
def read_csv():
    book_data = pd.read_csv("../data/book_words.csv", dtype={'id': int, 'words': str})
    # print(book_data.head())
    data = book_data
    words_all_book = set()
    book = dict()
    for i in range(len(data)):
        words_a_book = eval(data['words'][i])
        book[data['id'][i]] = words_a_book
        words_all_book = words_all_book.union(words_a_book)
```



遍历每个词项，统计出现该词项的文档集合，按照文档编号升序排列，生成倒排表。对于长度超过一定阈值的倒排表生成单层定长的跳表指针序列。

```python
def gen_invert_table():
    invert_index = []
    words_all_book, book, words_all_movie, movie = read_csv()
    for b in words_all_book:
        temp = []
        skip_table = []
        for j in book.keys():
            field = book[j]
            if b in field:
                temp.append(j)

        temp_sorted = sorted(temp)
        len1 = len(temp_sorted)
        if len1 == 1 or len1 == 2:
            for i in range(len1):
                skip_table.append({'index': None, 'value': None})
        else:
            for i in range(len1):
                if i % 2 == 0 and i < len1 - 2:
                    skip_table.append({'index': i + 2, 'value': temp_sorted[i + 2]})
                else:
                    skip_table.append({'index': None, 'value': None})

        invert_index.append({'word': b, 'id_list': temp_sorted, 'skip_table': skip_table})
    pd.DataFrame(invert_index, columns=['word', 'id_list', 'skip_table']).to_csv("../data/book_invert.csv", index=False)
```
