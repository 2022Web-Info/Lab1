import pandas as pd


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

    movie_data = pd.read_csv("../data/movie_words.csv", dtype={'id': int, 'words': str})
    data = movie_data
    words_all_movie = set()
    movie = dict()
    for i in range(len(data)):
        words_a_movie = eval(data['words'][i])
        movie[data['id'][i]] = words_a_movie
        words_all_movie = words_all_movie.union(words_a_movie)

    return words_all_book, book, words_all_movie, movie


def gen_invert_table():
    invert_index = []
    words_all_book, book, words_all_movie, movie = read_csv()
    for b in words_all_book:
        temp = []
        for j in book.keys():
            field = book[j]
            if b in field:
                temp.append(j)
        invert_index.append({'word': b, 'id_list': sorted(temp)})
    pd.DataFrame(invert_index, columns=['word', 'id_list']).to_csv("../data/book_invert.csv", index=False)

    invert_index = []
    for b in words_all_movie:
        temp = []
        for j in movie.keys():
            field = movie[j]
            if b in field:
                temp.append(j)
        invert_index.append({'word': b, 'id_list': sorted(temp)})
    pd.DataFrame(invert_index, columns=['word', 'id_list']).to_csv("../data/movie_invert.csv", index=False)
    # print(invert_index)


gen_invert_table()
