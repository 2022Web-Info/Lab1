import csv

if __name__ == '__main__':
    user_id_dict = {}
    movie_id_dict = {}
    data_L: list[list] = []
    file_name = "../../data/Movie_score.csv"
    result_file_name = "../../data/New_Movie_score.csv"
    with open(file_name, encoding="utf8", mode="r") as f:
        file_reader = csv.reader(f)
        for line in file_reader:
            print(line)
            break
        user_id = 0
        movie_id = 0
        for line in file_reader:
            data_L.append(line)
            if line[0] not in user_id_dict.keys():
                user_id_dict[line[0]] = user_id
                user_id += 1
            if line[1] not in movie_id_dict.keys():
                movie_id_dict[line[1]] = movie_id
                movie_id += 1
        for data in data_L:
            data[0] = user_id_dict[data[0]]
            data[1] = movie_id_dict[data[1]]

    with open(result_file_name, encoding="utf8", mode="w", newline="") as f:
        f_writer = csv.writer(f)
        tag = ['user_id', 'movie_id', 'movie_score', 'time', 'tag']
        f_writer.writerow(tag)
        for data in data_L:
            f_writer.writerow(data)
    print(user_id)
    print(movie_id)

