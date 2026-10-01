0.题目是要构造一个 data labeling task scheduler。总共有 t 个 task，m 个 model，h 个 human labeler。要求返回一个 scheduling（也就是一个 list of (task, model, human) tuples），满足以下条件：

每个 human labeler 参与的 task 总数量不小于 k。
每个 (task, model) pair 在 schedule 的任意阶段是 evenly distributed 的，也就是说 max_count(task, model) - min_count(task, model) <= 1。
同理，每个 (task, human) pair 在 schedule 的任意阶段也是 evenly distributed 的。
每个 human 对每个 task 最多标注一次。

可能还有一些不那么重要的 constraint 记不太清了，题目本身并不复杂，也没有对 complexity 的要求。


1. coding: social network. 3轮。基本的follow/unfollow。有snapshot，check在某个snapshot是否follow。推荐top k个user，通过已follow的user count来排序。
design: design a payment system. 地里面筋有

# https://www.1point3acres.com/bbs/thread-1166798-1-1.html


2. 
要设计sora的video generation part。client会发一个请求，request video generation，然后需要设计整个scheduling 和worker 的flow。有一个限定条件是一个worker只能生产一个video，然后需要call external GPU pool来工作， 然后这个pool size是波动的，所以worker可能会被随时terminate。感觉如何处理failure scenario是关键。


最近几年第一次面 system design，中间磕巴了几次，然后worker那里说的不是特别好，找不到会不会挂。

# https://www.1point3acres.com/bbs/thread-1166689-1-1.html



3. 投它家纯属试一试，结果居然给了面试。本篇禁止转载去其他平台。昨天发的另一家的今天就在小red刷到了。转载的会把我的坏运气一起转给你哦。

coding: social network, follow(int a, int b), unfollow(int a, int b), int snap(){}, bool is_following(int a, int b, int snapId).
给我的prompt是2 player game，准备了两天的monster gaming结果居然是leetcode style code。而且我捣鼓了半天做不出来，硬写的有bug。


SD： payment system。hold payment, batch process funds, charge payment。
知道它家肯定进不了，纯当mock。面试官很好，问了些关于openai的问题。觉得这公司真是得打鸡血才能进。

# https://www.1point3acres.com/bbs/thread-1166564-1-1.html


4.热乎的 还不知道结果 感觉答的还行吧


设计是象棋


coding似乎是新题 overlapping key range
class Shard:
        id: str
        start: int
        end: int
       
class Shards:
        def __init__(self, limit: int):
                # Provided

                pass

        def add_shard(self, shard: Shard):
                # Provided
                pass

        def remove_shard(self, shard_id: str):
                # Provided
                pass

        def rebalance(self):
                # TODO

在有最多重合限制的情况下，多的要删掉，漏的要补充
"""
limit = 1
('A', 0, 100)
('B', 80, 180)
->
('A', 0, 100)
('B', 101, 180)
"""
至于为什么这个时候要动后面的，是因为要减少数据移动的量。我是没太明白，就说拿我就移动靠后的区间好了


勉强做出来跑完几个测试，没有优化的时间

# https://www.1point3acres.com/bbs/thread-1166300-1-1.html



5. 
店面：感染题 + puzzle board

昂赛：count machine tree + payment system。另外就是常规的xfn，behavior，presentation


效率很快，第二天就收到拒信了。每一轮虽然发挥的都不是很完美，但也不差，比较平均吧。感觉他们家bar很高，表现得要很strong才行。


求米求米，准备下一家面试～

# https://www.1point3acres.com/bbs/thread-1166070-1-1.html


6.
第一轮是变形金刚。

第二轮是给了400多行pytorch代码的文件，要求完成 3 parts + 1 个 bonus part，问了很多时空复杂的问题。比如 matrix A @ matrix B 的时空复杂度是多少，说实话，我之前没想过。

# https://www.1point3acres.com/bbs/thread-1165833-1-1.html


7.
面的最新的商业化部门
经典题 GPU Credits I & II
随缘了, 说实话对他家的前景有疑惑, 现在确实很火热,
但是感觉有点子泡沫在里面;
结尾的时候聊了下他们目前商业化的进度, 感觉很急, 一切都很急

# https://www.1point3acres.com/bbs/thread-1165824-1-1.html


8.
第一轮: hack2hire-GPU Credits II 微调版，不同点在于，在当前 credit 不够 subtract 的时候，getBalance 返回 None. 不用考虑时间复杂度什么的。
总之会做 hack2hire 的版本，5分钟之内就能改成面试时的版本。


第二轮: design a payment system, 模拟线下消费刷卡的场景（而非电商场景），分为 hold 和 实际扣款 两部分功能，咱们的 payment service 需要把请求给到下游的 
credit card provider 来扣款，实际扣款是半夜统一时刻按 batch 扣的。


OpenAI bar很高，我这等菜鸡，大概率是过不了的。不过第二轮的面试官长老帅了，沟通和反馈也很积极，面试体验不错。


# https://www.1point3acres.com/bbs/thread-1165749-1-1.html


9.
题目是 IP address 这道题：https://www.1point3acres.com/interview/post/7100049


准备不够充分，之前没看过题。虽然看到很多人说这家面试不用在意算法，要赶快把 code 弄 work，但还是低估了对速度的要求。
LZ在工作中写码很快，做lc也不在话下，过去面试都是offer收割机，就彻底轻敌了。



一开始熟悉运行环境花了点时间，使用的语言并不是面试官熟悉的语言，所以沟通也要花时间。中间口头解释对 corner case 的考虑，写一些注释等等，回想全都是不必要的。
感觉面试官完全不 care engineering excellence，应该把时间和精力放在快速写代码和 debugging 上，其余都是次要的。


面试官很严格，一上来就说 coding 要 05 分开始。虽然这个 call 提前两分钟开始，02 分时我自我介绍完了，但他还是说不能提早开始。结果 05 分的时候他打不开系统，
弄了两三分钟才成功创建连接，发给我能看到界面，但是题目又刷不出来，于是分享屏幕，又刷新了几次题目才出来，快 15 分才开始写码。
到了 55 分他就 call hard stop 了。他说本应该 50 分结束，补时 5 分钟够了。题目是一问一问放出来的，前一问彻底写完，代码和测试都跑通，才放出下一问。
如果提前知道全部问题，整体设计也会顺一些。我刚写完第三问的代码和测试就到时间了，还没来得及调试。


最后 Q&A，我问他这题一共几问，他说一共 5 问，后两问是什么不能告诉我。地里版本是 4 问，但最后一问有两个分支，我猜其实是一样的。我又问做出多少算通过，
他说要5问全写出来，跑通，with good test coverage。还问了问他们日常工作中的情况，然后面试结束。


其实没什么新的信息，只是用血的教训说明面试他家一定要好好准备，抓紧时间写代码 debug。希望对后来人有帮助。


# https://www.1point3acres.com/bbs/thread-1165663-1-1.html



10.
Coding GPU + SD chess.com

Coding面试官迟到5分钟，卡点做出来pass all 6 test cases
SD聊的不错，面试官最后还说hr will contact you soon

# https://www.1point3acres.com/bbs/thread-1165609-1-1.html



11.
SD : Design remote IDE
Coding : GPU credits


都是面经题，没啥好说的。


Coding 大意了， 之前练过， 面的时候有bug ， debug 了20 分钟死活没找到。

SD 确实没准备到， 临场看题破题。


教训就是 还是要多练， 需要跑test 的coding 和 原来只要写不用execute 的还是有很大差别的， 特别的oai 这种代码特别长的。 出问题debug 真就纯看天。
# https://www.1point3acres.com/bbs/thread-1165242-1-1.html


12. 
店面：
coding: 实现一个简单的SQL 可以query 一个DB by name, by age, filter by id etc.
system design: 设计一个github action的系统，需要支持很多个用户，很多scalability challenges


onsite:
coding: 实现一个in memory kv store。如果系统断线了需要用log file 恢复。
system design: 设计一个storage system for video publishing, similar to youtube.
tech deep dive: GPU infra k8s相关问题。
manager: 没有什么特别的，问的问题都很标准的behavior

# https://www.1point3acres.com/bbs/thread-1165234-1-1.html


13.
Coding
60min - GPU


SD
Design payment sys, 不需要考虑security，重点问了怎么处理reconciliation


# https://www.1point3acres.com/bbs/thread-1165198-1-1.html


14.
线上相棋

ip继承器

# https://www.1point3acres.com/bbs/thread-1164961-1-1.html

15.
刚面完，挂了，造福群里兄弟姐妹，尽可能地说我知道的了。这些，强烈建议全部搞明白再去面。
Coding
传染病的题目
第一问：给定一个矩阵，里面都是植物，里面有X和“.”， X就是感染了的，”.”就是没感染的；感染的X每天都能影响它身边的8个邻居，从不感染变成感染；问多少天可以达到平衡态；简单的BFS，有个newly_infected去记录每天有哪些新被感染的，当这个数组为空的时候，就退出BFS了；
第二问：里面多了一个东西叫做”I”, 这个就是免疫的，它们不会感染，还是问多少天后可以达到平衡态。所以，还是BFS，在BFS中，往queue里面添加东西的时候，要额外加个条件，就是邻居的原始值要不是I才可以加入；
第三问：这些被感染的plant，在感染D天之后，会好，然后开始免疫；这里我是用一个hashMap来做的，key就是天数，value就是set of (i, j)，来表示在那一天可以好转并且免疫的坐标；然后在里面捣鼓就行；这一轮我挂了，我有几个test case一直跑不过；
第四问：网上大牛说的，好像是说如果这个矩阵很大，怎么办？
第五问：有这一问，不过并不知道是什么，我在网上也没搜到。

应该是最少要答上前三问才算过，一定要快。
chat message
toy language
GPU credits
Kv store
Message tree
Design sql
IP cidr (leetcode)
https://www.1point3acres.com/bbs/thread-1160199-1-1.html
https://www.1point3acres.com/bbs/thread-1157855-1-1.html

Memory allocator (leetcode)，要logN, 如果是pythond的话，sortedcontainers中的sortedDict可以搞定，去看下，它为什么是logN就行
宝可梦 — 这个我找不到原题，但是好像就是implement
https://www.1point3acres.com/bbs/thread-1156671-1-1.html
https://www.1point3acres.com/bbs/thread-1155434-1-1.html

其中，2-7这些题，在hack2hire这个网站中都有，得花钱，30一个月吧，买一下，值得，别瞎折腾到处去找题了。30刀，买不了吃亏，买不了上当。你要是当我是软广，那就ignore好了。
# https://www.1point3acres.com/bbs/thread-1164914-1-1.html


16.
SD 问的是设计Slack
面完LZ觉得答得还可以，基本是按Hello Interview的思路答的，不知道挂在哪里，面试官是个大牛，自己公司被收购来的OAI
先讲的DM后讲的channel

用Redis Pub/Sub这块我也花了一些时间解释明白，感觉好像不是面试官经常见到的答案？细细画了一些图讲了flow才解释明白

large channel那一块讨论了好一会，我给的是large channel用pull model，DM和small channel用push model，面试官问能不能都unify成pull model，
这样后端比较consistent，我感觉不太行，就说不行，因为client需要刷新才能收到信息，用户体验不好，现在细想，client甚至notification都收不到呀
Multi-device这块也讨论了好一会，hello interview上加一个session table这个解法他觉得inbox会bloat up，我confirm了一下message收到一次就可以了，
就说收到一次inbox里这个user的所有的session都删掉就好了。另外multi-device这个我没在design里主动cover，他问我multi-device怎么办才加上，或许应该一步到位？
当时也是忘记了，其实准备是都准备到了的
还有一个挂点是没怎么讲scale，好像cache都没加，sharding最后我提了一嘴，之前在large channel那一块讨论花了太多时间，剩5分钟他说good，让我问问题。
现在想其实一开始design应该就把scale这块cover掉，因为其实也很简单，加个cache，怎么sharding说一下，基本就可以handle scalability


楼主面design的经验不多，好久没面试，这轮第二次面design，大家可以讨论，挺想知道哪里没做好。另外楼主面的EM role，估计是staff的bar，
感觉挺难，现在想想scalability自己都没主动提确实不应该

# https://www.1point3acres.com/bbs/thread-1164140-1-1.html


17.
toy language，刷过几乎一样的题目所以做的时候问题不大

有一个toy language grammar， 包含primitives，generics tuples

要实现一个Node class，表示primitive和tuples

primitive是：char, int, float

generices 是 一个类似代称一样的暂时用来称呼变量类型的，like T1，T2

tuple是指一个tuple，里面可能有primitive, generices 或者tuple

然后function tostring

实现完了Node clas后要实现一个infer_return，基本就是input里面有比如T1， T2，然后要输出T1 T2 分别代表什么type。如果发现匹配不上有冲突的话，报错

sd是一个crossword puzzle，这题我卡的比较久，真的很难。让设计一个东西来解crossword pazzle，输入是一个board和一个dictionary。我实在想不出来了只好暴力解

# https://www.1point3acres.com/bbs/thread-1163593-1-1.html


18.
tldr 鸡皮有 + 罗宾汗


年前recuriter发邮件，想着准备准备试试水毕竟毕业之后这么多年好久没认真准备面试了。 基本上地里openai的题都刷过了。
可能因为太紧张面试的时候脑子完全不在线。 最后testcase没过几个，感觉上班ai用多了之后写码速度直线下降。 
SD感觉今年确实多了好多新题，还是建议系统学一下，面试官问的挺深的。 再接再厉吧也希望跟多的朋友们找工顺利！

# https://www.1point3acres.com/bbs/thread-1163019-1-1.html


19.
Coding:

传染病；
toy language;
Memory allocator (这个真的要logn的时间复杂度吗？segment tree那种？）
kv store;
Transformer, 变形金刚bug题？我看到好多人在说这个，可是找不到资料，有大佬能分享下吗？
GPU credit;
Design SQL;
IP iteration, CIDR;
encode and decode strings
SD:
Slack;
Webhook
CI/CD
Slack;
Payment system;
Crossword puzzle;
Calendar like apple;
Place of interest
IDE
YouTube;


# https://www.1point3acres.com/bbs/thread-1162896-1-1.html



20.
recruiter call
technical screening: 1 coding (传染病那个)
onsite: 1 refactoring exercise + 1 coding (玩具语言) + 1 SD (payment)


# https://www.1point3acres.com/bbs/thread-1162681-1-1.html


21.
内存分配+设计油管

内存这题必须logn时间


# https://www.1point3acres.com/bbs/thread-1162405-1-1.html


22.
payment system

KV store

# https://www.1point3acres.com/bbs/thread-1162221-1-1.html



23.
prompt是data structure + algorithm


memory allocator:

allocator(size=1000)
malloc(size) -> pointer
free(pointer) -> bool


memory allocator原题，先提议linked list solution，o(n) time complexity。面试官不是满意，要求brainstorm better solution。之前没准备过，
当场brainstorm，最后给个o(logn) time complexity的solution，
思路是用sort list of free block （sort by free size）+ linked list。sorted list查找free block，linkedlist做book keeping。


brainstorm花了一些时间，然后自己写test花了一些时间（我写了很多test，其实好像完全没必要），最后面试官给了几个他们的test，all pass，刚好卡着还剩5分钟结束。不知道算不算做完- -

# https://www.1point3acres.com/bbs/thread-1162026-1-1.html



24.
VO面了一轮coding 这轮coding发现地里的信息很少，LZ在这里po一下。类似栗抠 饵拔揪 问多少天后感染结束


前两问其实就是此道粒筘，但是一共五问。开放爱面试只讲快不讲efficient，所以LZ强烈推荐大家代码怎么简单怎么来，不要被LC思维局限了


第三问是被感染后D天会免疫从此不再被感染，多少天后所有人都被感染或者都免疫


需要你跑对提供的所有test cases


开放爱面试官LZ感觉都蛮有善，HR很快但从不回消息。希望更多国人能进军OAI

# https://www.1point3acres.com/bbs/thread-1161561-1-1.html



25.
coding
machine message tree


SD
crossword puzzle 
https://www.1point3acres.com/bbs/thread-1156374-1-1.html
 题目没说board大小，面试官说可以想象成中等尺寸：50*50. 有100个word slot要填，字典是1m，只要找出任意一个组合就可以。
 这题目真的难啊。证明完单机不行，就开始设计多机版本。我讲了一个利用stochastic optimization的方法，面试全程就是给面试官讲明白E2E 的流程，
也没其他deep dive。面试官最后来了一句：第一次见这个方法，要回去验证一下。我觉得完了，挂了。所以问了面试官具体怎么做。最正确的答案是 distributed dfs， 
但他没见人答过，也不指望大家答这个。 大部人都是用 stimulation 法，分任务，死胡同的时候再分情况。

# https://www.1point3acres.com/bbs/thread-1161149-1-1.html




26.
coding：toy language，练过了40分钟写完。
sd：设计一个sandbox cloud ide，类似colab。focus在怎么管理虚拟机，stream log 之类的。整体来说比较简单。
technical deepdive：需要做个ppt，讲一讲做的项目。感觉对面小哥觉得我用的项目深度不够。
BQ with manager：why openai，what's your view on AGI，然后一些经典negative questions。'
XFN: 跟pm聊聊和pm一起工作的经历，怎么pitch idea blablabla。

# https://www.1point3acres.com/bbs/thread-1160767-1-1.html



27.
coding是玩具语言那题，一共2问

第一问是node和function toString

第二问是infer function的返回类型

test case都是提前写好的

两问都是一遍test case全过，中间被提示了在函数中最好直接用assert而不是raise exception

结束时候老哥说我worked to the end of the problem

结果挂了。。说我coding的pacing不够

想问一下这题过了的朋友们，后面还有更多的follow up吗？还是需要自己加更多的test case？

# https://www.1point3acres.com/bbs/thread-1160582-1-1.html


28.
很久没系统准备面试，假期前recruiter骚扰想着试一试，这次都看地里面的高频题结果那些个又臭又长的coding都没碰到，整了个leetcode的题lol。。。

coding：ip / cidr iterator

Q1 - 升序iterate 一个 ip address

Q2 - 降序iterate 一个 ip address

Q3 - iterate 一个cidr

这题非常简单，但是我好久没做bit 操作了cidr的时候写test case写错了给自己绕进去了，浪费了好多时间

system design： design online chess.com game



# https://www.1point3acres.com/bbs/thread-1160199-1-1.html



29.
type system for a custom Toy Language. This system must handle primitive types, generics, nested tuples, and function signatures. You will implement the core data structures and a Type Inference engine that substitutes generics with concrete types.

Type Definitions
    Primitives: Lowercase strings like int, float, str, bool
    Generics: Uppercase letters followed by numbers, e.g., T1, T2
    Tuples: Comma-separated types inside brackets, which can be nested. Example: [int, [T1, str]].
    Functions: Defined by a list of parameter types and a single return type. Syntax: [param1, param2] -> returnType.

Part 1: Implement to_str in Node and Function.

Node Class: Represents a type node. It can be a leaf (primitive/generic) or a tuple (list of child nodes).

class Node:
    def  __init__(self, node_type):

        If node_type is a string: It is a primitive or generic.

        If node_type is a list: It is a tuple containing other Node objects.

    def to_str(self):

        Primitives/Generics: Return the string name (e.g., "int").

        Tuples: Return bracketed, comma-separated types (e.g., "[int,T1]").

class Function:
    def    __init__(self, parameters, output_type):
        Represents a function signature.
        parameters: A List[Node] objects.

        output_type: A single Node object.

    def to_str(self):

        Format: (param1,param2,...) -> returnType.

        Example: (int,T1) -> [T1,str]

Part 2: Implement a function get_return_type(parameters, function) that determines the concrete return type of a function based on provided arguments.

def get_return_type(parameters: List[Node], function: Function) -> Node:
    pass

Requirements:
    Generic Resolution: Build a mapping (substitution table) by comparing the Function's expected parameters to the actual parameters provided.

    Substitution: Recursively replace all generics in the function's output_type with the concrete types found during resolution.

    Error Handling:
        Argument Count Mismatch: Raise an error if the number of arguments doesn't match.
        Type Mismatch: Raise an error if a concrete type (e.g., int) is expected but a different type (e.g., str) is provided.
        Generic Conflict: Raise an error if the same generic (e.g., T1) is bound to two different concrete types in the same call.

Test Examples
Example 1: Basic Substitution

    Function: [T1, T2, int, T1] -> [T1, T2]
    Arguments: [int, str, int, int]
    Logic: T1 maps to int, T2 maps to str.
    Result: [int, str]

Example 2: Nested Tuples & Complex Generics

    Function: [[T1, float], T2, T3] -> [T3, T1]
    Arguments: [[str, float], [int, str], int]
    Logic: * T1 is extracted from the first tuple as str.
        T2 maps to the tuple [int, str].
        T3 maps to int.

    Result: [int, str]

Example 3: Conflict Error
    Function: [T1, T1] -> T1
    Arguments: [int, str]
    Error: T1 cannot be both int and str.


# https://www.1point3acres.com/bbs/thread-1158706-1-1.html




30.
SD： 设计slack

coding： 玩具语言 node 和function那道题， 地里面经提到过
# https://www.1point3acres.com/bbs/thread-1158623-1-1.html


31.
social network题目




大概意思是 要实现一个social network 的class 可以生成snapshot 然后用户相互关注. 然后问用户在某一个snapshot 里是不是 关注了彼此

第一问是 实现 类似于

social_network = SocialNetwork()

social_network.add_user("A")

social_network.add_user("B")

social_network.follow("A", "B")

snapshot = social_network.create_snapshot()

assert snapshot.is_follow("A", "B")

第二问是返回follower 和followee 的名单

第三问是给某个用户推荐关注对象。做法是从这个用户已经关注的人出发，查看这些人各自关注了谁，在这些候选人中，统计哪些人被该用户的关注者关注得次数最多，最后选出关注次数最多的前 k 个作为推荐结果

# https://www.1point3acres.com/bbs/thread-1158487-1-1.html



32.
昨天刚刚店面

SD - 地里老题目了，design slack
focused on large channel fan-out challenge; how notifications (notification on unread messages, notification on message push when users are offline) work; 
how db can scale up.
-> 自我感觉聊得还不错，所有的deepdive让面试官都很满意的样子。

Coding - 同样老题目，design kv store, focus on serialization and deserialization。然后还有一个follow up，what if each file has 1kb limit, 
and the kv store serialization needs multiple files to save.

-> 第一问写完了，test，debug了一会，根本没有时间写follow up。OAI家的coding确实好tough。

# https://www.1point3acres.com/bbs/thread-1152021-1-1.html



33.
HM chat
- Why OpenAI?

- What are the risks to AGI?

- How would you decide if a newer model could be released or not?

- How have you come to your current place in your career?

- 其他常规behavioral




Project deepdive
- 自己挑了一个既有深度，又有广度，还有 practical tradeoff 的项目。经过好几家其他公司的捶打，感觉这一轮是最稳的。
当然也只有这一轮是自己可以主导 discussion，也不意外。




Coding - GPU credits
- 有一个 test case 没有通过，很遗憾，最后都没有把这一个 bug 改出来，时间太紧了，不知道是不是挂在这里。




Design
- 这是一个新题，非常难搞，面试官是一个在 AWS EC2 干了快十年的老哥，直接进入他的专属领域，全程几乎被他带着走。不过自己觉得也是有来有回，
对他的各种 guidance 还是能够非常快地抓住。

- 最后这一轮估计还是不够，自我评估就是 design 和 coding 不够好。

- 题目：Design a system to provide remote devbox in the cloud on demand

# https://www.1point3acres.com/bbs/thread-1158080-1-1.html



34.
KV store.

实现一个Key value store，数据按固定大小分片保存到ㄧ個或多个文件中，支持shutdown保存和restore恢复。有提供 encode, decode functions

# https://www.1point3acres.com/bbs/thread-1158071-1-1.html



35.
设计一个企业级 GPT，允许员工就内部文档提问——本质上就是 RAG问题。面试官更关注机器学习方面的内容——如何训练模型，
你会为不同的组件（Retriever, Evaluator, Generator）选择什么样的模型架构，损失函数、优化器、训练机制、训练数据准备、评估策略等等。
基本上你必須讀熟RAG這領域ㄧ些重點papers, 並且非常熟悉traditional Search, Retrieval.
# https://www.1point3acres.com/bbs/thread-1158070-1-1.html



36.
Forward (正向迭代) 要求实现一个 IPV4Iterator 类。 给定一个起始 IP 字符串（比如 "192.168.0.1"），需要让这个迭代器从该起点开始，逐个返回 (yield) 后续所有的 IP 地址，直到达到 IPv4 的上限 255.255.255.255 为止。

代码接口要求： 需要实现标准的 Python 迭代器协议 (Iterator Protocol)，即 __init__, __iter__, 和 __next__。

Part 2: Reverse (反向迭代) 给定一个终点 IP（比如 "192.168.0.255"），实现一个倒序迭代器。要求从这个 IP 开始，反向遍历 (decrement) 直至 0.0.0.0。

Part 3: CIDR (网段解析)：这次的输入是一个 CIDR 格式的字符串（比如 "192.168.1.0/24"）。 你需要解析该字符串，利用位运算 (Bitwise Operation) 算出该网段的 Start IP 和 End IP，然后遍历并返回该网段内包含的所有 IP 地址。

    CIDR 格式说明：IP地址/数字（例如 192.168.1.0/24）。

        斜杠前：基准 IP。

        斜杠后 (/n)：网络前缀长度。意思是该 IP 的 32 位二进制中，前 n 位固定，剩下的 32-n 位（主机位）是可变的。

核心考点是如何根据掩码位（Mask，即 /24）快速计算出网络区间的范围。

Part 4: Optimization 后续问：如何优化时间复杂度和空间复杂度



# https://www.1point3acres.com/bbs/thread-1157855-1-1.html



37.
KV + CICD



38.
第一题宝可梦对战

写起来不难。要练的话可以思考一下怎么implement一个宝可梦对战的简易python版本。 小tips就是熟悉一下python的fstring，打log会很方便。
会问到比如技能威力不一样咋办，技能属性克制怎么搞之类的。

设计题
一个github action，主要会focus在怎么schedule，worker怎么setup，vfs怎么mount，怎么做snapshot failover，怎么stream log。

# https://www.1point3acres.com/bbs/thread-1157378-1-1.html


39.
第一轮system design：

Design a multi tenant CI/CD system which schedules and executes user defined workflows in response to git pushes. The system receives information about pushes via API calls from an internal service which contain the repository id and the current state of the repository (commit hash). Workflows are a sequence of jobs which are defined within a single YAML file in a static location for each repository. Users should be able to view the output and status of jobs as they are running.


第二轮coding具体题目忘了，但是不是那种典型的algorithm，而是更偏向practical coding。感觉答得都不错，不明白挂在哪。看来openai bar高是真的。

# https://www.1point3acres.com/bbs/thread-1157300-1-1.html



40.

东欧面试官。。准备了各种店面的题。。。。结果来了个refactor code的题。Refactor 的是一个chatbot.

大概就是各种slack message 有不同的action指令， 大概就是message 的prefix的不同的来判断要执行的action type，然后invoke后会有不同bot来处理这些message根据message的指令. 读这个题读了一会,最后磕磕绊绊的写了，但是把原来的代码不小心删了，没机会运行，那兄弟给我说没关系他懂了我的意思。唉整体面得确实不好。。。。


然后因为我python写的算法题比较多，最后后面还换成了java，因为更贴近production 的环境，浪费了不少时间。。。

本来想休假后再好好面试，猎头reach out看着机会不错试了试，好几年没面试了， 估计这轮是没了。





































































