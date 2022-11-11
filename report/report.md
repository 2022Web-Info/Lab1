# 实验 1 信息获取与检索分析

方羿 PB19111647	熊鹏 PB19111	张舒恒 PB19030888

## stage1. 爬虫

### 实验要求

> 针对给定的电影、书籍 ID，爬取其豆瓣主页，并解析其基本信息。
>
> a) 对于电影数据，至少爬取其基本信息、剧情简介、演职员表；
>
> b) 对于书籍数据，至少爬取其基本信息、内容简介、作者简介；
>
> c) 爬虫方式不限，网页爬取和 API 爬取两种方式都可，介绍使用的爬虫方式工具；
>
> d) 针对所选取的爬虫方式，发现并分析平台的反爬措施，并介绍采用的应对策略；
>
> e) 针对所选取的爬虫方式，使用不同的内容解析方法，并提交所获取的数据。
>
> f) 该阶段无评测指标要求，在实验报告中说明爬虫（反爬）策略和解析方法即可。



### 实验设计

本实验总共分为爬取数据+解析数据两个阶段，具体如下：

#### 一、爬取数据

##### 页面获取

数据爬取采用的是 python 的 requests 库，通过直接请求对应的 url, 获取 html 的内容。

这里以电影爬取为例，来说明具体实现过程：

``` python
# 获取具体的 movie_id
id = movie_id[k]	
# 根据 movie_id 构造 url
url = "https://movie.douban.com/subject/" + id + "/"
# 通过 request 库获取对应的 html 网页内容
response = requests.get(url,headers=headers)
content = response.content.decode('utf8')
```

##### 反爬策略

对于未登录用户的网页请求，**豆瓣规定同一 ip 地址在一定时间内最多请求100多次**；但对于登录的用户，则没有这一限制。

因此我们采取的反爬策略是：**通过携带 cookie 进行请求，模拟登录过的用户，从而绕过豆瓣的限制。**具体实现：

- 先通过浏览器获得登录后的 cookie
- 在 header 中携带 cookie  数据

``` python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
    "Cookie": '这里是登录后的用户的cookie,因为很长,这里就没直接粘贴上来'
}
```

#### 二、解析数据

在获取了 html 数据后，下一步就是从 html 中获取需要的信息。这里我采用的是**用 xpath 解析 html 文档**，来获取需要的信息。

这里以电影为例，说明具体过程：

``` python
# 用一个字典来存电影信息
movie = {"id":id,"电影名":"","基本信息":"","剧情简介":"","演职员":"","豆瓣评分":""}
# 解析 html 文档
html = etree.HTML(content)
# 获取电影名
title = html.xpath('//*[@id="content"]/h1/span/text()')
for str in title:
    movie["电影名"] += str
# 获取评分信息
rating = html.xpath('//div[@class="rating_self clearfix"]//strong/text()')
if len(rating):
    movie["豆瓣评分"] += html.xpath('//div[@class="rating_self clearfix"]//strong/text()')[0]
else:   # 《建国大业》等电影禁止评分
    movie["豆瓣评分"] = "暂无评分"
# 获取基本信息
info = html.xpath('//*[@id="info"]/span/text() | //*[@id="info"]/span//a/text() | //*[@id="info"]
for str in info:
    if str[0] == '\n':
        movie["基本信息"] += '\n'
    else:
        movie["基本信息"] += str
# 获取完整的简介
intro = html.xpath('//span[@class="all hidden"]/text()')
if len(intro) == 0:
    intro = html.xpath('//span[@property="v:summary"]/text()')
for str in intro:
    str = str.strip("\n").strip(" ").strip("\n")
    movie["剧情简介"] += str + '\n'
# 获取演职员表
stuff = html.xpath('//li[@class="celebrity"]//span/text() | //li[@class="celebrity"]//span//a/tex
for i, str in enumerate(stuff):
    movie["演职员"] += str + " "
    if i % 2 != 0 :
        movie["演职员"] += "\n"
```



### 结果展示

- 具体代码详见 `./src/stage1/catch_book.py` 和 `./src/stage1/catch_movie.py` 
- 电影和书籍的爬取详细结果见：`./data/movie.csv` 和 `./data/book.csv`

- 这里仅展示部分截图

  <center>
      <img style="border-radius: 0.
  3125em;
      box-shadow: 0 2px 4px 0 rgba
  (34,36,38,.12),0 2px 10px 0 
  rgba(34,36,38,.08);
      zoom: 35%;"  
      src="./figs/01.png">
      <br>
      <div style="color:orange; 
  border-bottom: 1px solid 
  #d9d9d9;
      display: inline-block;
      color: #999;
      padding: 2px;">电影爬取结果</div>
  </center>

<center>
    <img style="border-radius: 0.
3125em;
    box-shadow: 0 2px 4px 0 rgba
(34,36,38,.12),0 2px 10px 0 
rgba(34,36,38,.08);
    zoom: 35%;"  
    src="./figs/02.png">
    <br>
    <div style="color:orange; 
border-bottom: 1px solid 
#d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">书籍爬取结果</div>
</center>



## stage 2. 布尔检索

### 实验要求

>基于第一阶段爬取的豆瓣 Movie/Book 信息，实现电影或书籍的搜索引擎。对于给定的查询，能够以精确查询或模糊语义匹配的方法返回最相关的书籍或者电影集。
>
>**1. 对一阶段中爬取的电影和书籍数据进行预处理，将文本表征为关键词集合**
>
>**2. 在经过预处理的数据集上建立倒排索引表**𝑺**，并以合适的方式存储生成的倒排索引文件**
>
>**3. 对于给定的 bool 查询，根据你生成的倒排索引表，返回符合查询规则的电影或/和书籍集合并以合适的方式展现给用户**

### 实验设计

#### 一、分词

分词使用了结巴分词库，同时人工提取了一些如 人名、电影名之类的特殊名词，加入到结巴分词的人工字典中，帮助更好的分词。

这里以电影为例，说明具体的实现：

``` python
movie_data = pd.read_csv("./data/movie.csv")
movie_tag = pd.read_csv("./data/Movie_tag.csv")
col_name = ['id', 'words']
movie_words = []
# 读取每个电影
for _,movie in tqdm(movie_data.iterrows(), total=movie_data.shape[0], leave=False):
    # 对电影的基本信息、演职员表等进行分词
    key_words = split_movie(movie)
    # 读取电影的 tag 
    tags = list(movie_tag.loc[movie_tag['id'] == movie['id']]['tag'])[0]
    tag_words = set(str(tags).split(","))
    key_words = set.union(key_words, tag_words)
    key_words = key_words - stopwords
    # 存每个电影的分词结果
    movie_words.append({'id': movie['id'], 'words': key_words})
# 将分词结果存下来，方便下一位同学使用
pd.DataFrame(movie_words,columns=col_name).to_csv("./data/movie_words.csv",index=False)
with open("./data/word_dict.pkl","wb") as f:
    pickle.dump(word_dict,f)
print("split movie finish!")
```

具体的电影分词函数如下：

``` python
def split_movie(movie):
    key_words = set()
    # 电影ID作为一个词
    key_words.add(str(movie['id']))
    # 电影名的分词
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
    # 电影基本信息、演职员表、剧情简介的分词
    info = str(movie['基本信息'])
    stuff = str(movie['演职员'])
    intro = str(movie['剧情简介'])
    key_words = set.union(key_words, split_movie_stuff(stuff))
    key_words = set.union(key_words, split_movie_info(info))
    for word in key_words:
        word = str(word)
        jieba.add_word(word)
        word_dict.append(word)
    key_words = set.union(key_words, set(jieba.cut_for_search(intro)))
    for word in key_words:
        word = str(word)
        jieba.del_word(word)
    return key_words
```

#### 二、建立倒排表

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

#### 三、布尔查询

#### 四、自然语言查询

### 结果展示

- 具体代码详见 `./src/stage2` 文件夹下：

  ``` bash
  split_words.py	# 分词
  # ToDo 这里要填每个文件是干嘛的
  ```





## stage 3. 推荐

### 实验要求

> 在这次实验中，你们需要自行划分训练集与测试集，在测试集上为用户对书籍或电影的评分进行排序，并用 NDCG 对自己的预测结果进行评分和进一步分析。

### 实验设计

#### 一、MF 模型介绍

1. 本此实验，使用了矩阵分解模型 (MF) 来预测 user 对 item 的评分。

2. **模型说明**

   MF（矩阵分解）是一种 latent factor models ，它根据 user-item 的评分矩阵（高度稀疏化），构建 user 和 item 的向量。

3. **参数说明**

   MF 模型将 user 和 item 映射到一个 f 维的 latent factor 空间，用内积表示 user-item 互动。即：

   item_i 表示为 $q_i \in \mathbb{R}^f$ ，表示 item_i 含有这些 factor 的程度

   user_i 表示为 $p_u \in \mathbb{R}^f$ ,  表示 user_i 喜爱这些 factor 的程度

   $\hat{r}_{ui} = q_i^Tp_u$ , 表示 user 对 item 的评分的预测值

4. **考虑误差**

   考虑评分时不同 user 和 item 的误差，可以将评分拆解为 4 个部分：global average**（$\mu$）**, item bias **（$b_i$）**, user bias**（$b_u$）**, user-item iteraction **（$q_i^Tp_u$)**。

   举个例子，假设所有电影的平均打分是 3.7，《Titanic》很好，它的评分会比同题材平均分高，其 item bias 是 0.5， 而 Joe 是一个严格的人，其打分偏低，user bias 为 -0.3。那么 Joe 对 Titanic 评分为：3.7 + 0.5 - 0.3 + $q_i^Tp_u$ 。

5. **评分预测**

   user 对 item 的评分可以表示为：
   $$
   \hat{r}_{ui}(t) = \mu + b_u(t) +q_i^Tp_u(t)
   $$

6. **优化目标**
   $$
   \min _{p^* , q^* , b^*} \sum_{(u, i) \in \mathrm{K}}\left(r_{u i}-\mu-b_{u}-b_{i}-p_{u}^{T} q_{i}\right)^{2}
   $$

#### 二、数据集处理

本次实验我们选择预测电影的排序，使用助教给的豆瓣电影评分数据集 `Movie_score.csv`

首先我们**将电影和用户进行重新编号处理**，将用户重新编号为 0 - 544，0 - 999，将结果存到 `New_Movie_score.csv` 中

然后，**我们将数据集按时间戳排序，并按照 8：1：1 的比例，分词训练集、验证集和测试集。**

具体实现见 `./src/stage3/GetData.py` 和 `./src/stage3/Dataset.py`

#### 三、MF模型实现

MF 的模型实现如下：

``` python
class MF(nn.Module):

    def __init__(self, user_num, item_num, mean , embedding_size, dropout):
        """
        	user_num: 用户数
        	item_num: 电影数
        	mean: 所有评分的平均分
        	embedding_size: 潜在因子数
        	dropout: 丢弃率
        """
        super(MF, self).__init__()
        self.user_emb = nn.Embedding(user_num, embedding_size) # p_u
        self.item_emb = nn.Embedding(item_num, embedding_size) # q_i
        self.user_bias = nn.Embedding(user_num, 1)	# b_u
        self.item_bias = nn.Embedding(item_num, 1)	# b_i

        self.user_emb.weight.data.uniform_(0, 0.005)
        self.item_emb.weight.data.uniform_(0, 0.005)
        self.user_bias.weight.data.uniform_(-0.01, 0.01)
        self.item_bias.weight.data.uniform_(-0.01, 0.01)

        self.mean = nn.Parameter(torch.FloatTensor([mean]), False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, u_id, i_id):
        U = self.user_emb(u_id)	# p_u
        I = self.item_emb(i_id) # q_i
        b_u = self.user_bias(u_id).squeeze()	# b_u
        b_i = self.item_bias(i_id).squeeze()	# b_i
        return self.dropout((U * I).sum(1) + b_u + b_i + self.mean)
```

#### 四、评估

本次实验使用 ndcg 来评估最后的结果。具体计算步骤如下：

1. 对于测试集中的每个 user, 我们先预测它在测试集中的 item 的评分，将其按照评分排序，得到 predict_rank，用它的真实得分和预测的排序结果算出 DCG

2. 然后，再将该 user 在测试集中的 item 按照评分由高到低排序，得到 gt_rank, 用它的真实评分和真实排序计算出 iDCG

3. 两者相除，即可算出该 item 的 ndcg

   - 例如，对于 user_id = 31 的用户，我们的预测排序是：['126(4)', '299(3)', '3(3)', '981(1)', '676(4)']， DCG = 29.149976941591724
   - 真实排序是：['676(4)', '126(4)', '299(3)', '3(3)', '981(1)']，iDCG = 31.365535017320155
   - 该用户的 ndcg = DCG / iDCG = 0.9293632939943478

4. 最后，对于所有用户的 ndcg 求平均，即是最的 ndcg。

   特别的，对于在测试集中没有 item 的用户，我们直接将其忽略，不计算他的 ndcg。

具体实现如下:

``` python
def metrics(model, evaluate_set:dict):
    """
        evaluate_set 是一个列表,每个元素是一个字典,存了 电影ID->评分
    """
    NDCG = 0
    count = 0
    for user_id, item_dic in enumerate(evaluate_set):
        item_id = list(item_dic.keys())
        user = torch.full((len(item_id),),user_id,dtype=torch.int64).cuda()
        item = torch.tensor(item_id,dtype=torch.int64).cuda()
        prediction = model(user, item).detach().cpu().numpy()[:,np.newaxis]
        temp = np.array(list(item_dic.values()))[:,np.newaxis]
        # rank 是一个列表 [[predict,score],...] 按照 predict 的分数降序
        rank = np.concatenate([prediction,temp],axis=1).tolist()
        rank.sort(reverse=True)
        DCG = 0
        for i,(_,score) in enumerate(rank):
            DCG += (2**score - 1) / math.log2(i+2)  # 因为 i 从 0 开始所以额外加1
        iDCG = 0
        iRank = list(item_dic.values())
        iRank.sort(reverse=True)
        for i, score in enumerate(iRank):
            iDCG += (2**score - 1) / math.log2(i+2)
        if iDCG != 0:
            NDCG_i = DCG / iDCG
            NDCG += NDCG_i
            count += 1
    return NDCG / count
```



### 结果分析

1. 我们训练了 20 个 ecpoch, 取验证集里 ndcg 最高的模型作为最终模型，最后得到的结果如下图所示，测试集的最终的 ndcg = 0.844：

   ![](./figs/result.png)

2. 然后我们根据训练好的模型，将每个 user 的预测排名和实际排名存到 `./src/stage3/Data/rank_result.csv` 中。部分结果如下图所示：

<img src="C:\Users\peterfang\AppData\Roaming\Typora\typora-user-images\image-20221111201459237.png" alt="image-20221111201459237" style="zoom:50%;" />

- 观察以上排序数据，我们发现存在部分排序预测实际不是很好，比如 user_id=18 的，它相当于完全错了，但是按照上述ndcg的算法，它的 ndcg = 0.8540645566659568

- 同时存在像 user_id=16 的数据那样，只有一个 item 的情况，这样不管模型好坏，它 ndcg = 1

- 所以算出来的 ndcg 实际上是虚高的。因此，ndcg 在我们这种场景下，可能不是一个很好的评估模型好坏的指标。

  (当然也可能是我这种 ndcg 的算法有问题。但是实验文档里没有说怎么算。我问了一个助教，助教说可以这么算)

  

## 提交文件说明





## 实验小结

1. 通过本次实验，我们熟悉了爬虫的使用方法。
2. 通过本次实验，我们熟悉了倒排表的构建，并实现了一个简单的布尔检索系统。
3. 通过本次实验，我们熟悉了一些推荐模型。



## 实验建议

1. 建议实验文档里可以把实验要求写的更明确一点, 比如 stage3 的文档可以把 ndcg 怎么算详细规定一下。
2. 感觉stage3可以改成预测用户喜欢的电影 (测试集中电影评分 >= 3的当成是喜欢)，然后对所有非训练集和验证集中的电影进行评分预测，取前10个当成预测的用户喜欢的电影，然后用 recall@10 和 ndcg@10 当成评价指标。这种任务更像推荐任务。

