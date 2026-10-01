-1.
# coding Q2: file dedup. 没有刁钻的followup，基本是讨论怎么规模化

# design Q1： inference system

# culture：你有没有做过什么利他不利己的事情？大家会说ai很risky，那为什么还要去做？你怎么看？

# behavior：比较standard。most challenging project，most impactful project etc
# https://www.1point3acres.com/bbs/thread-1165014-1-1.html

0. 时间线

去年11月海投，12月 recruiter A reached out，直接安排了电面。同时也收到了OA，但是没做。
今年1月中旬电面，三天后通知VO。一周前VO，还没有update，应该是挂了。我问recruiter A要update，她让我问recruiter B，但B不回邮件，我觉得是没戏了。

technical都是原题，很多帖子也都提到了。题号在ModernLoop上都能看到。

Coding
Phone Coding Q6

[面试经验] 人类学店面新题
跟这个帖子一样。 https://www.1point3acres.com/bbs/thread-1111070-1-1.html

# 我用的是 longest match 。

# # vocab = {"app": 1, "apple": 2, "UNK": -1}
# # tokenize("apple", vocab) -> [2]
# # tokenize("bbb", vocab) -> [-1, -1, -1]

# def tokenize(text: str, vocab: dict) -> list:
#     tokens = []
#     i = 0

#     while i < len(text):
#         matched = False

#         for j in range(len(text), i, -1):
#             s = text[i:j]
#             if s in vocab and s != "UNK":
#                 tokens.append(vocab)
#                 i = j
#                 matched = True
#                 break

#         if not matched:
#             tokens.append(vocab["UNK"])
#             i += 1

#     return tokens

# Optimize 1

# # vocab = {"app": 1, "apple": 2, "UNK": -1}
# # tokenize("appleappleappleappleapple", vocab) -> [2, 2, 2, 2,2]

# def tokenize(text: str, vocab: dict) -> list:
#     tokens = []
#     i = 0

#     # Precompute max word length for optimization
#     max_len = max((len(w) for w in vocab if w != "UNK"), default=0)

#     while i < len(text):
#         matched = False

#         # Only check up to max word length instead of entire remaining text
#         for j in range(min(i + max_len, len(text)), i, -1):
#             s = text[i:j]
#             if s in vocab and s != "UNK":
#                 tokens.append(vocab)
#                 i = j
#                 matched = True
#                 break

#         if not matched:
#             tokens.append(vocab["UNK"])
#             i += 1

#     return tokens

# Optimize 2

# # vocab = {"app": 1, "apple": 2, "UNK": -1}
# # tokenize("appbbbapp", vocab) -> [1, -1, 1]

# def tokenize(text: str, vocab: dict) -> list:
#     tokens = []
#     i = 0

#     # Precompute max word length for optimization
#     max_len = max((len(w) for w in vocab if w != "UNK"), default=0)

#     while i < len(text):
#         matched = False

#         # Only check up to max word length instead of entire remaining text
#         for j in range(min(i + max_len, len(text)), i, -1):
#             s = text[i:j]
#             if s in vocab and s != "UNK":
#                 tokens.append(vocab)
#                 i = j
#                 matched = True
#                 break

#         if not matched:
#             tokens.append(vocab["UNK"])
#             i += 1

#     # Remove consecutive -1s
#     result = []
#     i = 0
#     while i < len(tokens):
#         result.append(tokens[i])

#         # If current token is -1, skip all following -1s
#         if tokens[i] == -1:
#             while i + 1 < len(tokens) and tokens[i + 1] == -1:
#                 i += 1

#         i += 1

#     return result

# VO Coding Q1

# Web Crawler

# Single threading

# from urllib.parse import urlparse
# from collections import deque

# class Solution:
#     def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
#         hostname = urlparse(startUrl).hostname

#         visited = {startUrl}
#         queue = deque([startUrl])

#         while queue:
#             cur_url = queue.popleft()
#             urls = htmlParser.getUrls(cur_url)
#             for url in urls:
#                 if url in visited:
#                     continue
#                
#                 if urlparse(url).hostname == hostname:
#                     queue.append(url)
#                     visited.add(url)

#         return list(visited)

# Multi threading

# from concurrent.futures import ThreadPoolExecutor, as_completed
# from urllib.parse import urlparse

# class Solution:
#     def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:
#         hostname = urlparse(startUrl).hostname

#         visited = {startUrl}
#         queue = deque([startUrl])

#         with ThreadPoolExecutor() as executor:
#             futures = {executor.submit(htmlParser.getUrls, startUrl)}
#             while futures:

#                 for future in as_completed(futures):
#                     futures.discard(future)
#                     urls = future.result()
#                     for url in urls:
#                         if url in visited:
#                             continue
#                         
#                         if urlparse(url).hostname == hostname:
#                             futures.add(executor.submit(htmlParser.getUrls, url))
#                             visited.add(url)

#         return list(visited)

这是在LC里能跑的代码，面试也是类似的setup。
单线程是bfs。多线程用的是future+threadpool，好处是跟单线程的代码很相似，好改。
记得用 urllib for hostname, urldefrag, etc.
面试的时候不会直接告诉你需要defrag。你要先跑一下code，然后告诉你unique urls count不对，需要你debug。把urls print出来就应该能看到了。


SD Q1
Inference API System Design 
https://www.1point3acres.com/interview/problems/post/7100015
基本包括了所有的问题。
问到了很多实现细节，准备的时候最好考虑一下actual implementation。
GPU和CPU的运行原理不太一样。比如GPU是memory bound，大部分时间花在load model into memory，所以处理10 strings和处理100 strings时间差不多。简单了解一下会有帮助。


BQ
HM主要问了过去的project，比较标准的BQ。突出自己的role，如何solve conflict/pushback，诸如此类。问得也比较详细。还问了project里一共多少人，花了多长时间，impact倒是没怎么问。感觉还是得找大一点的project。


Culture
基本都跟AI Safety相关。

问题：
Anthropic很重视AI Safety。你怎么看？你有没有critique？
你有没有遇到过这种情况？一开始你觉得一个人的观点是错的，但是后来发现却是对的，然后你有了很大的改变。（我当时真是语塞了，面试官就先换了一个题，最后又问了一遍这个题。）
各大公司都在发布大模型，Anthropic也得发，这样会不会有安全隐患？你怎么看？
The Long-Term Benefit Trust can stop Anthropic. 如果真stop了，你怎么看?

我觉得得准备一些critique，并且需要亲自测试一下。

比如我提到了 Claude's new constitution' ，我觉得写得很好，面试官就追问你有没有验证呢？我说我没有全部验证，但我在Opus上发现ta不是只在follow，也会纠正错误的指令。
面试官还会追问。比如我提到了Elon Musk，面试官会追问你觉得他关心AI Safety吗？
从和面试官的对话中感觉Anthropic认为AI Safety远大于financial，为了safety可以放弃financial。

我参考了这些
Dario Amodei Website
Claude's new constitution'
The Long-Term Benefit Trust
Testing our safety defenses with a new bug bounty program
Core Views on AI Safety: When, Why, What, and How
Anthropic's Responsible Scaling Policy'

我是把 articles/transcripts 放到gemini里summarize一下，没时间细读了。

Copy Youtube Transcript
我用的这个chrome extension。

# https://www.1point3acres.com/bbs/thread-1164836-1-1.html



1. coding Q1 
店面老题：web crawler ，也可以参考刷题网伊尔丝儿.
先单线程，followup多线程，只考虑一个hostname下的页面
比伊尔丝儿多的内容是需要考虑fragment，就是url里#…这一块的内容要去掉，不需要考虑url normalization。
两个遇到的坑：
一个是 URL 要先把fragment去掉再去重，这个我虽然知道，但讲的时候顺序没说清楚，让他一直追问 sanitize 发生在哪一步；
另一个就是并发那块，我thread pool + task sync都很熟，刷题也做过类似的，但面试时我脑子一抽先说了几种 primitive 的方式，面试官的表情当场… 后面虽然补救到 threadpool，但他明显已经觉得方向不太对了
面的时候也expand了一些sd的相关问题但没有聊很多，估计是踩坑后就被默默否了

# https://www.hack2hire.com/companies/anthropic/coding-questions/692f5158cd79766b0b310122/practice?questionId=692f515ecd79766b0b310123
# https://www.1point3acres.com/bbs/thread-1157666-1-1.html

2. coding Q2 
電面：给定一个文件夹目录，找出其中所有的重复文件。

整个面试过程都在一个共享的 Google Colab 上进行，我们用平台上的文件来测试代码的正确性。在实现了一个基本的解决方案（即对每个文件的完整内容进行哈希）后，
面试官开始了一系列追问。他首先询问我实现的时间复杂度，我解释说这与所有文件大小的总和成正比。

为了改进效率，我提出了一种多阶段的方法，先使用“廉价”的哈希函数。具体来说，首先从元数据检查文件大小，然后对大小相同的文件哈希其前1024个字节，
最后才在万不得已时进行完整的哈希。面试官随后问这种新方法在最坏情况下的时间复杂度，我回答说，如果所有文件的大小和初始内容都完全相同，那么时间复杂度仍然取决于文件的总大小。
这引出了关于哈希函数的更深层次讨论。我当时苦苦思索，试图找到一个既廉价又哈希碰撞率低的哈希函数。面试后我才意识到，没有哪个哈希函数是完美的，你总能找到反例。
接着，话题转向了系统设计，面试官问我如何判断一个程序是CPU密集型还是I/O密集型。我解释说会用性能分析结果来判断：如果CPU大部分时间处于空闲状态，
程序就是I/O密集型；如果CPU持续繁忙，则是CPU密集型。
之后，面试官提出了一个更复杂的挑战：设计一个持续监控重复文件的系统。这个问题有些模糊，
所以我先与他确认了需求：系统需要在添加重复文件时通知文件所有者，并且要能处理文件的删除。我概述了一个解决方案，
即使用数据库来维护两个映射：一个是从文件哈希到文件的映射（用于重复检测和通知），另一个是从文件到其哈希的映射（用于处理删除）。
我还提到了对于海量文件，可以使用类似 MapReduce 的机制来扩展，并解释了 Map 和 Reduce 操作分别会做什么，以高效地处理数据。

# https://www.1point3acres.com/bbs/thread-1144078-1-1.html


3. coding Q3 [check page for image, check #87.]

# Problem: Converting stack samples to a trace

Sampling profilers are a performance analysis tool for finding the slow parts of your code by periodically sampling the entire call stack.

In our problem the samples will be a list of `Sample`s of a float timestamp and a list of function names, **in order by timestamp**, like this.

* Sample stacks contain every function that is currently executing
* The stacks are in order from outermost function (like "main") to the innermost currently executing function
* An unlimited amount of execution/change can happen between samples. We don't have all the function calls that happened, just some samples we want to visualize.

example:
s2 = [
        Sample(0.0, ['a','b','a','c']),# a -> b -> a -> c
        Sample(1.0, ['a','a','b','c']),
    ]
    # (s, a) (s, b) (s, a), (s, c)
    # (e, c) (e, a), (e, b), (s, a), (s, b), (s, c)
.. where "s" is start and "e" is end.
# https://www.1point3acres.com/bbs/thread-1089271-1-1.html


这里补充一下过的经验
这道题本身不难，只是需要处理input之后对于每一个Sample用stack存放并且对比决定输出。
有一个Followup，只考虑连续出现N次的function
我自己过的情况是题和Followup全写完并且能各跑过1-2个test case
就网上搜集的信息，这一轮和Codesignal不一样，有人CodeSignal过了直接昂赛，有人Codesignal后面接了一个有面试官的店面，有人直接是这一轮店面之后昂赛。遇到哪种都不用惊讶。
# https://www.1point3acres.com/bbs/thread-1112538-1-1.html

4. System design 1
就是 inference api

求问
SD Q4？
Coding Q1 是 多线程爬虫？
# https://www.1point3acres.com/bbs/thread-1163059-2-1.html

5. 面的网络爬虫

给的api，实现爬虫。BFS秒了。给了俩限制条件，很简单的那种，两行代码。  
follow up多线程。问了一些多线程和多processor区别
# https://www.1point3acres.com/bbs/thread-1162619-1-1.html

6. 
去年年底面的General EM岗位，就把地里当时能找到的面经翻了一喂了给了GPT老师给分类整理了一下，
结果EM没有design，是design review和组里做的东西非常相，怀疑就是随便找一个平时的design doc改了改拿出来面试。
EM 面试 Execution and Leadership, Technical Presentation, People, Design Review, Culture Fit 
感觉面的都不错已经是最大准备了，特别是culture 例子都是非常personal related，对方不断点头，不知道哪轮挂了。
# https://www.1point3acres.com/bbs/thread-1162478-1-1.html

7. This interview will be a coding and design exercise involving writing code in Python. 
We recommend Google Colab, but you're welcome to use whatever environment you feel most comfortable with.'  
We will ask you to share your screen in Google Meet. People often run into browser permission issues, so we 
recommend preparing before the interview by starting a google meet with yourself and sharing the screen as a test. 
You should be comfortable with Python's standard library; feel free to use StackOverflow and Google during the interview. '
While it is LLM-related, we don't specifically test your LLM knowledge here. We'll give you all 
the context you need in the interview.

# https://www.1point3acres.com/bbs/thread-1162037-1-1.html

8. 
处理猫的图片。用的pillow
最后才跑通test，中间有个小bug是面试官提示才看出来，没有准备的很好
两天后接到电话fail
# https://www.1point3acres.com/bbs/thread-1161686-1-1.html


9.
HR面完之后直接约了SD电面，邮件里没写具体题号，但是candidate portal里写了：

For the System Design interview Q1, we will evaluate how you would design scalable, secure, and reliable systems 
to solve a complex problem. We recommend reading about best practices for scalable infrastructure design.

我在论坛里搜了一下大家说这是Q4的prompt，是interface api。我现在有点困惑(Q1 vs. Q4)，各位有知道具体可能是哪道题吗？谢谢大家！

# https://www.1point3acres.com/bbs/thread-1161165-1-1.html

10.
海投拿到一个电面。ModernLoop上写的是 Coding Q6 。我看有人说是 tokenize ，有没有面过的兄弟姐妹确认一下？
# https://www.1point3acres.com/bbs/thread-1111070-1-1.html

# https://www.1point3acres.com/bbs/thread-1160525-1-1.html


11. 
还是老题， 店面网虫题

Follow up: what if we have multiple servers, how to optimize your code?
不需要implement， 讲思路就行。

我就说用Redis 当central queue storage with 1 host server access the queue and assign slave servers to batch process.



补充内容 (2026-01-29 14:59 +08:00):
统一回一下，都是网上的IDE，有写好的test case。
Phone screen是12/17， VO 01/19
挂在VO了，bar很迷，不过都还是老题。

# https://www.1point3acres.com/bbs/thread-1160362-1-1.html


12.
经典的tell me a time：

failed project。如何依然从里面找到impact
conflict during cross-functional collaboration，以及如何resolve

# https://www.1point3acres.com/bbs/thread-1159248-1-1.html




13.
面试流程整体其实还挺顺的。
店面网虫题，

VO：第一轮稳健驱虫
第二轮：提示词乐园，

接着项目深挖，整体聊得还算谈笑风生。

HM 是个白女，面相有点 Karen，当下心里“咯噔”一下，隐约觉得不妙，但还是硬着头皮面完，体感还行。
Culture round 主要是安全相关的问题，我自己感觉回答得也 OK。

# https://www.1point3acres.com/bbs/thread-1158823-1-1.html


14. 
有两轮。第一轮是准备ppt present目前的work。我用了两周前自己的一个conference talk。第二轮是coding，
题目是地里的find duplicate files。feedback是coding不够strong。加面了一轮地里的image processing（blur，flip etc operations）。
两天后说挂了。

# https://www.1point3acres.com/bbs/thread-1158568-1-1.html



15. 
Q1，面的是土象出力。
那看起来趴宠是退出历史舞台了。

最近刚面了q3 还是stack trace

请问提示词是concurrency吗？
对的zszs

# https://www.1point3acres.com/bbs/thread-1158153-1-1.html





16. 
Vo 總共五輪：
- Coding: 史大翠絲，follow up 是 consecutive n，最後一列的 end 不用 print， 自己要寫 testcase verify。


- Coding: Mode / Median ，面了才發現這題考查的不是正確性，而是端出了一個 workable solution 後，能不能“持續 iterate” 讓你的 solution 變得更有效率，花更少時間。有 10 nodes, send / recv / barrier 三個 function ，read data 花 10 bytes/sec 然後 send / recv 都各花 1 byte / sec。我感覺 find median 根本考不到，所以重點準備 find mode 就好。我端出 3 個 solutions ，最後竟然是 naive 的 solution (calc local counter on each node, and aggregate to node 0 ) 跑得最快，但顯然 naive solution 不是最佳解，所以面的有點不算好。


- HM: 正常的 Behavior question / Project go through / roles in each project (not deep dive)


- Culture：重點要相信 AGI ，並相信 Safety 很重要，更重要的是要結合自身經歷（工作上、非工作上）argue or fight for AI Safety。Any conflict with collaborators on 哲學問題（非技術問題），然後怎麼 resolve。

Performance: 跟這篇一模一樣：https://www.1point3acres.com/bbs/thread-1157758-1-1.html


注意 followup 是問 one input activation (e.g. mk) + one output activation (e.g. mn) + model weight (kn) 能不能放進 VRAM
Second Follow Up 問 Pipeline Parallelism (2 GPU) / Tensor Parallelism，end to end 多久，memory usage on each, pipeline 或 tensor 的 tradeoff 是什麼

# https://www.1point3acres.com/bbs/thread-1157758-1-1.html




17.
截图是从别人帖子里拿的，面的是这道题。

要求share screen。不能用ai，但是可以google。

有m个图片，有n个pipeline。每个Pipeline有k个操作。要求生产mxn张图片，把每个Pipeline都应用一遍。

用了pillow lib解决了。

会问点follow up的问题，如何scale，用什么方法scale，以及为什么要用这个方法。

写代码的时候最好写成容易被parallel的方式。比如刚开始我在一个方法里，read image, apply pipeline。但是parallel的话，就没必要每次都read image了

不过现在很多公司coding过不过不在根据你做出来没有，比较玄学

# https://www.1point3acres.com/bbs/thread-1157730-1-1.html



18.
Q6 prompt里有“We're interested in seeing you interact in a real work environment, so your interviews may be more open-ended than a standard technical problems, and you should feel empowered to engage with your interviewer and ask questions. This won’t require any specialized knowledge or prep beyond general familiarity with reading and writing code“

搜了下好像是token那道题. 有人在地里发过 https://www.1point3acres.com/bbs/thread-1111070-1-1.html

# https://www.1point3acres.com/bbs/thread-1156951-1-1.html


19.
力扣 邀餓三溜

follow up

如果想要加快速度 該如何處理

如果不想同時發太多request 該如何處理
# https://www.1point3acres.com/bbs/thread-1156842-1-1.html

20.
收到了recruiter coding schedule。 email里的prompt的是 This will be a pure programming problem solving interview which
 doesn't benefit from memorizing standard algorithms or data structures. You can choose to work in your preferred programming language.'
 ' 按照地理的说法是Q3 (stack) 但是portal的coding interview 是Q1 （爬虫）。请问应该相信哪个呢？'
 # https://www.1point3acres.com/bbs/thread-1156674-1-1.html


21
Anthropic recruiter phone screening 问题
我当时问了很多cultural fit的问题，比如为什么ai safety重要之类的，最好要准备一下。
求加米！

感谢回复，我和你的看来不太一样，就是recruiter问了一下我的简历和背景，然后说了一下团队的状况和接下来的面试流程。最后的时候问了一下要不要sponsor以及有没有timeline需要注意的
recruiter在和你约时间的时候会给你发好几个文档，有个文档是关于safeguard的，请一定要仔细阅读。然后recruiter大概率会问你读了没，有什么感想

# https://www.1point3acres.com/bbs/thread-1156340-1-1.html



22.
吐篇矗立，用pillow 挨批爱
# https://www.1point3acres.com/bbs/thread-1155853-1-1.html



23.
电面提示词是concurrency, 但可能webcrawler太多人面过了所以他们现在换题了，目前地里看到过concurrency有碰到LRU cache也有碰到file dedup的所以都需要准备
题目和 https://www.1point3acres.com/bbs/thread-1150952-1-1.html
 一样的，有4个folder, 分别是small images, big images, out, transformations, 
 他们会提供这些path以及里面所有文件的完整path所以基本不用自己做多少os path处理

task是要先找个python library来处理6种transformation (grayscale, flip horizontally, flip vertically, scale, blur, rotate) 
前三个是没有parameter的后三个有。
第一个考点是根据这些快速查docs的能力，这里面scikit image和python pillow都是比较好用的library，
面试的时候要展现你搜索这些library确认能处理这6种transformations. 
建议事先熟悉一下其中一个接下来就是先用small images做测试并且save output图片到out folder里。每一个json file要apply到每一个图片上并且save，
他们会提供util function来帮你形成output file path。
每一个transformation json file里面会有一个到多个transformation, 如果有多个transformation的话都要sequentially apply到图片上。
如果结果是对的话就要做大图片了，他们有个target时间，我用了processpoolexecutor因为我觉得这个虽然也有IO但图像处理会需要cpu不少 
而且每个process不需要shared memory。我做到这里的时候时间已经不够了所以碰到了个bug没有在规定时间内de出来，不知道结果会不会满足target时间需求，
也不清楚后面的follow up会是啥，盲猜大概率会是python thread和process的比较。


# https://www.1point3acres.com/bbs/thread-1154439-1-1.html



24.
我recruiter的email写的是：This interview focuses on systems design and doesn't need specialized '
ML knowledge or research skills. This will be a system design question to evaluate how you would design scalable, secure, and reliable systems to solve a complex problem. We recommend reading about best practices for scalable infrastructure design.
# https://www.1point3acres.com/bbs/thread-1153826-1-1.html


25.
prompt 是 spark 需要怎么准备
# https://www.1point3acres.com/bbs/thread-1153585-1-1.html


26.
求问人类学最近的design Q2
地里之前搜到的结果是prompt playground 不知最近是否换题？感谢大家

提示词：For the Systems Design interview, you'll work through the design of a product. Some areas you may cover are UX '
and user flows, system design, data design, and scaling. The key is to demonstrate your ability to understand user needs 
and clarify requirements, think about potential issues, and manage product and technical trade-offs.


# https://www.1point3acres.com/bbs/thread-1152783-1-1.html


27
收到Screen是Q2, prompt是“We'll provide you with a template containing the interview problem”。'
搜了下最近Q2换了新题是LRU （https://www.1point3acres.com/bbs/thread-1148690-1-1.html），正好是“给你一个已经implement好的in memory cache，
要求在基础功能以上继续扩展”，符合给一个template。请问这个prompt是否是对应新的LRU? 谢谢大家。

# https://www.1point3acres.com/bbs/thread-1152730-1-1.html


28.
人类学 HR 面
你为什么想在 Anthropic 工作？
是什么让你开始寻找新的（工作）机会？
如果最终拿到多个 offer，你的决策框架/评估标准是什么？
你最强的技术能力是什么？
你面试时会使用哪种编程语言？


我的是System Design Q1: we will evaluate how you would design scalable, secure, and reliable systems to solve a complex problem.

# https://www.1point3acres.com/bbs/thread-1152296-1-1.html



29. design Q3
For the System Metrics Design interview Q3, we will evaluate how you would scale, monitor and optimize an existing system in production. 
The focus will be on aspects of a ML driven system outside the model architecture itself.

# https://www.1point3acres.com/bbs/thread-1152058-1-1.html



30.
考的还是file dedup那题
用的完全是code signal environment 我手动建立的file
我是java选手 需要熟悉一下files / stream / hash 相关的class 才能比较顺利的写出来
中间我还在不断的查java doc , 屏幕共享了所以面试官也能看到我怎么查的


# https://www.1point3acres.com/bbs/thread-1151849-1-1.html



31. 
如题 portal里唯一的prompt：

For this interview, you should be familiar with handling concurrency, using primitives/libraries of your choice.


我面了这道题。看到关键字，我以为是考web crawler，工作比较忙所以只重点准备了web crawler。
结果面试官甩给我一道文件去重，所以千万不要只准备这一道题，其他的也要准备一下，都是血泪教训。

# https://www.1point3acres.com/bbs/thread-1151625-1-1.html



32. 
Recruiter面：简单聊了下为什么选择ant，然后交代了面试的流程

电面：Coding Q3 / 斯塔克 特雷斯。地里提到过很多次。follow up是 trace 去噪，我的做法是简单记录一下时间戳，只有「当前function call的开始时间 ～ 当前的时间」 超过N，才加入答案中。代码量不算小；需要通过两个简单的测试样例。面试官很nice，最后正好写完 、测试完。


VO - 代码Q2：不是地里说的新题（缓存）而是老题， 文件 地丢普。没啥好说的就是分两层去重：1）文件大小；2）全文哈希。需要自己创建测试文件。Follow up很猛，面试官很sharp：IO/memory bound？/ 如果所有文件都是同样的内容、且都是大文件怎么办 / 怎么做分布式 / 怎么选择哈希函数 等等。（基本上是个快问快答）

VO - SD Q1：经典硬弗伦斯 阿普哎。基本就是那几个component弄一弄就好了，注意回答重点是batch input。面试官正好就是做data pipeline的所以非常关注系统细节。会提问题比如：系统几乎满载的时候，有几个GPU有workload？以及这个情况下batch queue的长度？

VO - HM：HM感觉人还是不错的，但是整个过程算是不太有兴趣，估计是因为lz不算strong candidate。lz虽然专业对口 ，但没有太多利用llm。
HM会让lz描述当前工作的整个系统架构、需要给出每个环节的具体数字、QPS、etcetc

VO - Cultural：这是lz完全崩掉的一环…… 虽然在面试前已经看了ant的很多博客、CEO采访视频、论文等等，但lz却没有准备足够的【从自身出发】的例子，
导致回答的时候手忙脚乱。甚至有好几问（比如：说说几个你在工作中坚持自己立场的例子）直接愣住了。。。这轮肯定是negative的。

VO后两周整收到拒信。LZ不禁想起地里常说的：behavioral/cultural面试看似不起眼，但只要好好准备到位了，那是事半功倍啊～


# https://www.1point3acres.com/bbs/thread-1151263-1-1.html



33. 
地理没见到的t p s

是swe的题 我面的position是swe，growth
这个题就是给你一些json file 然后又给你一些图片
每个json file都包含了几个关于图片的operation 比如scale这种
我们需要做的是把这些operation apply到每一张图片 然后再把这些图片存到一个指定的directory
处理图片的package说是自己选 我当时是google直接查的 interviewer说除了ai generated的answer都可以查


# https://www.1point3acres.com/bbs/thread-1150952-1-1.html



34.
电面 + Onsite

技术面所有题目都能在地里找到，题库很小，而且有提示。
Culture - 基本就一个话题，AI safety为啥特别重要。 面试官应该至少是个D2，或者VP。
BQ - 围绕past experience各种问，主要是tech leadership，mentorship，带团队，也涉及一些management（我当过EM又转回IC）。

两周后收到email挂了，没有feedback。

# https://www.1point3acres.com/bbs/thread-1150100-1-1.html


35.
这波运气也是够差，楼主被面到了coding的新题
题目描述：给你一个已经implement好的in memory cache，要求在基础功能以上继续扩展
第一问其实不是严格意义上的扩展，而是让你找bug。只要快速理解到这个cache的基础功能，就能很快找到问题在generate cache key那一步。楼主用的python，
这里有个坑就是怎么读args然后转成可以被hash的key，建议看看kwargs
第二问是支持durable cache，要求在cache挂掉的情况下可以重启并且还必须保证不丢数据，
基本思路还是存到disk然后cache挂掉重启的时候从disk文件恢复所有数据。楼主面的时候没搞过这个，所以答得磕磕绊绊。


# https://www.1point3acres.com/bbs/thread-1148690-1-1.html


36.
一开始被interviewer鸽了，好在HR紧急安排了新的一场。考的题目是Q2。具体的问题如下：
题目就是deduplicate files。然后需要手动创建文件。就用os.walk + hash就能混过去了。
几下就写完，面试官开始问很多follow up。包括I/O bound or CPU bound, multi nodes怎么弄，还有hash 算法怎么选。


你们是要真的删除这些文件，还是只需要识别出重复的文件？
识别重复的就行，重复的放在一起

# https://www.1point3acres.com/bbs/thread-1148602-1-1.html


37.
目测挂了。research engineer
coding：Q4， 面经题distributed worker find mode，但followup find median没来得及写，只说了想法。
RL Fundamentals: 没在面经里看到过，所以贡献一下
debug GRPO code. 首先是一个nan error，发现给的code在multinomial sampling之前没做softmax，
直接用了logits，另外算normalized advantage的时候stddev没有加epsilon。fix之后就开始了一系列知识盲区的拷问，
例如：如果ratio = model_logprob - old_logprob 还能不能train出来，为什么要clip ratio,  什么时候ratio会被clip，
clip了会有什么影响，etc etc，然后还问了在这个code里ratio 是不是理论上是1，为什么，print出来发现不是1，debug。。。估计这一轮要挂



Coding +design:
implement一个data batcher, 可以sample weighted data from a given data registry 
（给了data registry and sampling API). 第二问是sampling API can take an offset argument, 
要求data batcher可以produce a ckpt / load from a ckpt. 
第三问是假设batch_size 不能被sum of weights 整除，要怎么sample
# https://www.1point3acres.com/bbs/thread-1148586-1-1.html



38.
前段时间面的现在来回馈地里
店面 duplicate files 地里dp基本上是 昂赛的coding，没准备，碰到的时候慌了一下

昂赛
coding：web crawler，老题了，后续async case的时候没跑通，自己写的async html parser不认识0x89 codec。最后没时间改了。虽然面试官说不用担心总体是对的，
但估计这个挂了， 
建议大家能用threadpool就用threadpool吧，别自己写async parser



culture：怎么处理feedback that emotionally hard to accept，起了冲突最后发现自己是错的，感觉可以照着Stripe的那些principal准备（毕竟老总表妹从Stripe带来的culture）

design：inference API，问的很细，scaling，monitoring，gpu utilization，given traffic估算多少GPU

project：做了个ppt 25分钟present，和面试官谈笑风生，感觉这轮面的好，还给了我一些接下来的tips

hm：BQ，问past project，感觉像是例行公事，上来就说这轮虽说约了55分钟但是只会用30分钟

总体感觉除了coding因为codec没跑出来别的面的都还行。

最后和Recruiter聊了聊感觉是挂在Coding和hm



面试官只问怎么提高I/O效率，那就是multi thread 或者async咯，我面的时候比较较真就说python没有true multi thread所以想秀一手async，没想到有个网页没法decode…

补充内容 (2025-10-01 23:43 +08:00):
AI safety 就是看他们各种blog吧，我说的时候都是reference blog，有的带着批判的去说，比如Dario那👟4东大相关的言论，面试小哥也同意，HR最后也没说这轮有问题，我猜culture这轮就是不能一直吹。

# https://www.1point3acres.com/bbs/thread-1148141-1-1.html



39.
在职跳槽，就投了2家，OpenAI和Anthropic，准备了差不多1个月，最后还是没能过，感觉遗憾不过也算尝试了一下吧，明年还感兴趣的话再去试一次
Round 1: Recruiter call after referral (heard back after 1 week)
Round 2: Phone screen, 网冲

Onsite:
Round 1： 斯达克锤斯
Round 2：因弗伦斯诶皮哎
Round 3： 发要斯蒂度普
Round 4: 文化
Round 5: 嗨满
感觉总共6轮面试4轮面的很不错，SD和HM感觉一般，所以也还可以接受，这些公司应该6/6自我感觉很好才行，下次努力


# https://www.1point3acres.com/bbs/thread-1148045-1-1.html


40.
中厂2YOE海投
Phone: tokenizer,几个follow up忘了,之前有一篇面经说的比较全了
prompt:

For the coding interview, we will be doing coding in a live runtime environment in Python (v3.10). We will be using CodeSignal by default for your interview; to ensure a smooth start, we recommend you take a quick look at CodeSignal’s preparation resources. 
We're interested in seeing you interact in a real work environment, so your interviews may be more open-ended than a standard technical problems, and you should feel empowered to engage with your interviewer and ask questions. 
This won’t require any specialized knowledge or prep beyond general familiarity with reading and writing Python code. Note that use of AI tools during this interview is not permitted, however Google, Stack Overflow, etc. is allowed. We may ask you to share your screen in Google Meet. People often run into browser permission issues, so we recommend preparing before the interview by starting a google meet with yourself and sharing the screen as a test.

onsite:

Coding: 之前有人说Q2改了了,看来截止2025.9还是dedup,follow up就是 cpu bound vs io bound, how to implement in distributed system
SD: 没有题号, prompt engineering playground, 基本就是design chatgpt,假设每一次和chatgpt对话他都不知道之前的context,多问了一个share conversation的功能
Culture: AI Safety, 坚持原则不做你认为错的事, conflict
HM: Project DeepDive, 最困难的技术挑战,然后问了不少collaboration相关的BQ吧,准备几个和product collaborate的故事
Phone的时候亚裔last name面试官有点心不在焉, Oniste前三轮体验都很好面试官很engaged, HM似乎有点uninterested. HM是中间隔了一天面的,听说这种分两天的前几轮面的不好最后一轮直接不给面了,看来前几轮还行😅



补充内容 (2025-10-01 01:31 +08:00):
design的一些具体问题

有哪些core entities,之间的关系,怎么index
特别长的prompt(10mb+)怎么处理
如果用户开了很多窗口,每个都是特别长的prompt,client本地性能不好如何提升ux


# https://www.1point3acres.com/bbs/thread-1147872-1-1.html



41.
55 分钟 design interview. 职位是infra all sde。
Design below api.

batchstring(list<string> input)

{
return list<string> output.
}


大概就是design llm api 需要combine api request 发给backend gpu， 一个gpu 只能process 一个batch at same time。
自我觉得啥都考虑到了，从service 内部实现到不同level的routing，load balancing， racecondition。面试官面的时候都说好， 完了给我拒了，不知道挂在哪了


# https://www.1point3acres.com/bbs/thread-1147020-1-1.html


42.
Behavior：
一个完全别的部门，聊一些完全和工作没有关系的事情
为什么喜欢anthropic，我说了因为安全，trust，然后他问我你怎么知道的，你自己详细对比过吗。我说没有，我是听markting+自己的使用体验，但是没有详细对比
我自己的core value是什么，我怎么在每天工作中实现自己的value
强调anthropic的value是什么，这个value可能会让financial有牺牲，问我怎么看

# https://www.1point3acres.com/bbs/thread-1146336-1-1.html


43.
7月面的，考的爬虫那道题，follow up是多线程，Beautiful Soup不是真正意义上多线程，需要aiohttp改进下。之前其实跑过了，但是面试时候忘写了个await关键字就挂了。。。from typing import Self
# import requests
# import asyncio
# import time
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse

# '''
# def getLinksFrom(link: str) -> list[str]:
#   try:
#     resp = requests.get(link, timeout=5)
#     resp.raise_for_status()
#   except requests.RequestException as e:
#     print(f"Error fetching {link}:{e}")
#     return []

#   soup = BeautifulSoup(resp.text, "html.parser")
#   links = []
#   for a in soup.find_all("a", href=True):
#     abs_url = urljoin(link, a["href"])
#     links.append(abs_url)
#   return links

# class Solution:
#   def __init__(self, max_concurrency=10):
#     self.visited = set()
#     self.semaphore = asyncio.Semaphore(max_concurrency)
#     self.start_hostname = None

#   def sanitize(self, url):
#     idx = url.find('#')
#     if idx > 0:
#       url = url[:idx]
#     return url

#   def get_hostname(self, url):
#     return urlparse(url).hostname

#   async def dfs(self, url):
#     url = self.sanitize(url)
#     if url in self.visited or self.get_hostname(url) != self.start_hostname:
#       return
#     self.visited.add(url)
#     async with self.semaphore:

#       next_urls = await asyncio.to_thread(getLinksFrom, url)
#     await asyncio.gather(*(self.dfs(u) for u in next_urls))

#   async def crawl(self, start_url):
#     self.start_hostname = self.get_hostname(start_url)
#     await self.dfs(start_url)
#     return list(self.visited)

# async def main():
#   start = time.time()
#   solution = Solution(max_concurrency = 10)
#   start_url = "https://andyljones.com"
#   result = await solution.crawl(start_url)

#   print("Time taken:", time.time() - start)

#   print(f"\nCrawled {len(result)} URLs: \n")
#   for url in sorted(result):
#     print(url)

# if __name__ == "__main__":
#   asyncio.run(main())
# '''

# import asyncio
# import aiohttp
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse

# class AsyncCrawler:
#     def __init__(self, max_concurrency=10):
#         self.visited = set()
#         self.semaphore = asyncio.Semaphore(max_concurrency)
#         self.start_hostname = None
#         self.session = None

#     def get_hostname(self, url):
#         return urlparse(url).hostname

#     def sanitize(self, url):
#         idx = url.find('#')
#         if idx > 0:
#             url = url[:idx]
#         return url

#     async def get_links_from(self, url):
#         try:
#             async with self.semaphore:
#                 async with self.session.get(url, timeout=10) as resp:
#                     print(url)
#                     if resp.status != 200:
#                         return []
#                     text = await resp.text()
#                     soup = BeautifulSoup(text, "html.parser")
#                     return [urljoin(url, a["href"])
#                            for a in soup.find_all("a", href=True)]
#         except Exception as e:
#             print("Error fetching {url}: {e}")
#             return[]

#     async def crawl(self, start_url):
#         self.start_hostname = self.get_hostname(start_url)
#         self.session = aiohttp.ClientSession()
#         await self.dfs(start_url)
#         await self.session.close()
#         return list(self.visited)

#     async def dfs(self, url):
#         url = self.sanitize(url)
#         if url in self.visited or self.get_hostname(url) != self.start_hostname:
#             return
#         self.visited.add(url)
#         links = await self.get_links_from(url)
#         # Crawl links concurrently
#         await asyncio.gather(*(self.dfs(link) for link in links))

# def main():
#     start_url = "https://andyljones.com"
#     crawler = AsyncCrawler()
#     result = asyncio.run(crawler.crawl(start_url))
#     print(f"\nCrawled {len(result)} URLs:\n")
#     for url in sorted(result):
#         print(url)

# if __name__ == "__main__":
#     main()


# https://www.1point3acres.com/bbs/thread-1146090-1-1.html



44.
约了第一次recruiter面试 以为常规面试呢 结果recruiter面试晚了7分钟 5分钟时我发邮件问还说没人。进来没有任何解释迟到 直接开始用ai take note, 为啥选这个公司  
我回复想做ai infra. 然后问发给我的材料有看吗 我说没看。recruiter直接说那这样下次再约一次面试吧 我说好。结束大概就说了5分钟不到。
然后第二次约 第二次面 这次对迟到有心理预期 这次迟到8分钟多 也是没有任何解释 直接开面。这次看了材料我回答为啥人类学公司说了一堆ai saftey东西  
然后他说这次应该可以面下一轮了 感觉说是过了 他给我介绍了一堆下面面试的结构多久 几面之类的 说我应该准时到。我没忍住 说这些面试也是晚5分钟开始吗 
当时脸绿 又聊了几句 第二个工作日收到一封拒信 说是不是potential mutual fit.  

# https://www.1point3acres.com/bbs/thread-1145736-1-1.html



45. [check page]
最终是不是挂在SD这一轮不知道，也可能是culture fit给挂了，也可能both挂了，不过我大概的design是这样
大概考察了怎么update model的control plane内容，本不是inference system的一部分但是基本讨论了一下。
dive deep了一下cache的部分，我说cache prompt的时候，用vectorDB，他简单问了similarity check是怎么做的，以及用key-value DB行不行，
肯定是行的只是加个partition range。
我没答好，也被dive deep最多的竟然是在rate limiter里面，他问我如果流量突发过大，如何给用户429，我一开始觉得是要考察rate limiter具体的方法，
就说我们可以用token bucket一类的，
后来发现他是想讨论如何动态来调整rate limit，比如现在call rate正常，但是如果突然GPU cluster里面有一半down 掉了，如何动态让rate limit收紧。
我说的是，如果GPU cluster里面有一半down 掉了，那应该先backpress在aggregator那个地方，降低poller rate，用户首先体会到long latency，
然后我们需要monitor aggregator的SQS/kafka MQ的queue size，根据unread size来动态调整rate。
有点也被trick了，他问我所有event是不是都在一个queue里面我说是，我没反应过来，他也没说话，事后想想肯定不是，一个tier的user应该在一个queue 
（paid user和unpaid user的queue区分开，这样rate limit是不一样的）

# https://www.1point3acres.com/bbs/thread-1145567-1-1.html



46.
上来不聊简历直接问对anthropic有什么看法，了解
然后是对于anthropic公开的documents/博客/访问，有什么看法，反对意见，我内心问号脸。。
反反复复几个问题都是why anthropic，what to ask
问有没有什么其他公司在面，说这些公司里面为什么选择anthropic
讲了一下面试流程，听起来面试挺难的
最后会找3个reference，manager/更senior的同事etc


# https://www.1point3acres.com/bbs/thread-1145234-1-1.html



47.
本人在职跳槽，recruiter六月份通过LinkedIn直接联系的，面的是Infrastructure.

Phone (Coding，国人小姐姐)
前10分钟聊了下过往经历
Coding是Web Crawler，提供了getURLs的function
Follow-up: 优化 (多线程)
用的是Replit，不是很好用，代码写完没提示任何编译问题，点了下run，出现各种import error，修了快5分钟
代码需要run，test结果只要是小于100就是正确的
面完过了两天，recruiter通知pass，准备安排VO

VO
Day 1 - Coding (白人小哥)
Coding Q3，考的是那个Stack Trace的题目，提前准备过，做起来很顺
Follow 1：N consecutive trace消噪
Follow 2：因为最开始是prefix做的比较，这里问了postfix怎么处理
这次是在CodeSignal里面写，需要run，看来他们家放弃用replit面试了？
最后白人小哥说perfect solution，这轮应该没啥问题

Day 1 - System Design (ABC小哥)
Design Q1，考的是那个Inference API的题目，提前准备过，答的也很顺
我用的Meta面试的excalidraw来画的图
Dive deep重点问了如何优化GPU的usage，以及如何处理request暴增，需要scale more GPU时，GPU启动慢如何解决
整个流程不太像面其他公司的SD那种按照套路一步一步走，他们只会focus在他们想dive deep的地方，别的部分一笔带过也没啥问题
比如: BOE计算时候小哥说你可以跳过，全程也没问过任何关于failover / what if xxx failed之类的问题
最后ABC小哥说很满意，设计的很solid，这轮应该也没啥问题

Day 2 - Behavior (白人大叔)
就是简单的问问过去经历，常规的BQ问题，大叔态度很nice，氛围很轻松

Day 2 - Culture (天竺小哥，没口音)
少许的BQ问题
很多的AI Safety讨论
人生理想 (你的人生中有没有什么事情改变了你 之类的)
所有问题不一定非要工作相关，生活上的也可以
总体来说比较玄乎

面试结束过了一周多，recruiter通知挂了，没feedback提供。因为Anthropic是这次跳槽面的最后一家公司，
手里已经有几个还不错的offer了，所以心态上比较放松，自我感觉面的还是很扎实的 (至少两轮tech应该没啥问题，每道题跟GPT小伙伴准备了四五个小时)，
所以我猜应该是挂在culture上？不过整体面试体验还不错，大家都很友好，友好到让我觉得自己“又行了”哈哈。不过根据结果来看，也和地里其它帖子说的差不多，他家bar确实是迷。


问楼主是如何解决需要scale up more GPU的时候，GPU启动慢的问题的。
我说的是 最开始GPU不要利用到100% 一方面越高利用率效率越低，另一方面可以保证万一需要scale up GPU，在新GPU启动过程中，原有GPU有足够buffer抗一阵子，
之后新GPU启动后在更新request调配，面试官说这个方法可以



Interface应该是:
我用的Java
Q1 - List<Event> convertSamplesToEvents(List<Sample> samples)
Q2 - List<Event> convertSamplesToDebouncedEvents(List<Sample> samples, int N)
Q3 - List<Event> convertSamplesToEventsWithSuffix(List<Sample> samples)
具体的interface可以自己随便改的，能做出来就行，我就给array变成List了

Prefix你应该好理解，就是每次你不是得先看到 start再找对应得end么，这其实就是从前往后找，就叫prefix，所以反过来从end找start就是postfix。

Prefix vs Postfix 在这个题里的区别
Prefix 做法
每次采样得到一个调用栈 A → B → C → D。
如果你用 prefix（从栈顶/最外层开始比较），那么两次采样只要前半段一样，就会被当作“重复”。
问题是：在长调用链里，上层函数往往变化不大，真正频繁切换的恰恰是栈底的函数。
所以 prefix 比较可能会过度合并，把本来不同的执行路径当成一样，从而丢失了细粒度信息。

Postfix 做法
Postfix 从 栈底（leaf function）往上比，重点关注最深层的调用序列。
这样可以更准确地区分不同的热点函数。
比如：
main → handler → parse → foo
main → handler → parse → bar
如果用 prefix，它们的前 3 层都一样，会被当作同一个路径。
但用 postfix，从 leaf 开始比，foo vs bar 能清晰区分。

总结
Prefix：容易“糊”在一起，分辨率差（适合做高层归并）。
Postfix：能更精准捕捉到 leaf 层函数的差异（热点分析更有价值）。
在 profiling 场景下，我们通常更关心底层函数的性能瓶颈，所以 postfix 消噪优于 prefix。


# https://www.1point3acres.com/bbs/thread-1145186-1-1.html



48.
電面：给定一个文件夹目录，找出其中所有的重复文件。

整个面试过程都在一个共享的 Google Colab 上进行，我们用平台上的文件来测试代码的正确性。在实现了一个基本的解决方案（即对每个文件的完整内容进行哈希）后，面试官开始了一系列追问。他首先询问我实现的时间复杂度，我解释说这与所有文件大小的总和成正比。

为了改进效率，我提出了一种多阶段的方法，先使用“廉价”的哈希函数。具体来说，首先从元数据检查文件大小，然后对大小相同的文件哈希其前1024个字节，最后才在万不得已时进行完整的哈希。面试官随后问这种新方法在最坏情况下的时间复杂度，我回答说，如果所有文件的大小和初始内容都完全相同，那么时间复杂度仍然取决于文件的总大小。
这引出了关于哈希函数的更深层次讨论。我当时苦苦思索，试图找到一个既廉价又哈希碰撞率低的哈希函数。面试后我才意识到，没有哪个哈希函数是完美的，你总能找到反例。接着，话题转向了系统设计，面试官问我如何判断一个程序是CPU密集型还是I/O密集型。我解释说会用性能分析结果来判断：如果CPU大部分时间处于空闲状态，程序就是I/O密集型；如果CPU持续繁忙，则是CPU密集型。
之后，面试官提出了一个更复杂的挑战：设计一个持续监控重复文件的系统。这个问题有些模糊，所以我先与他确认了需求：系统需要在添加重复文件时通知文件所有者，并且要能处理文件的删除。我概述了一个解决方案，即使用数据库来维护两个映射：一个是从文件哈希到文件的映射（用于重复检测和通知），另一个是从文件到其哈希的映射（用于处理删除）。我还提到了对于海量文件，可以使用类似 MapReduce 的机制来扩展，并解释了 Map 和 Reduce 操作分别会做什么，以高效地处理数据。

如果有人最近要面试 欢迎要面的朋友私信
# https://www.1point3acres.com/bbs/thread-1144078-1-1.html


49.
HR Screening- 沒什麼特別，問了問背景跟Why A家
電面：地裡stack那題，follow up找超過連續出現N次的


VO coding: 去重，面的時候他們剛剛換成全部CodeSignal面試，不跟Replit合作了，面試官花了點時間熟悉CodeSignal
VO HM: 標準BQ，會從一個notable project深挖
VO Culture: 面試官是Head of AI Safety，面的我心驚膽戰，問了對AI Safety有什麼看法，A家哪方面可以做得更好... 等，還有一些標準BQ
VO System design: Q1 問了新題，就是地裡前幾天才出現的題 Deploy LLM model to GPU clusters：1000 workers各自有10Gbps的network bandwidth (in + out)，要如何有效率的load 500GB的model到每一個workers. 一開始給了tree解法，面試官提示了一下idle workers，改成了chunked model + 流水線(1進1出)，最後問了問怎麼manage workers


面VO前就要了reference，面完後兩週收拒信，說了"After consideration, we have decided not to move forward with an offer at this time"，
大概是模板，有一年冷凍期。面試官人都很好，感覺公司氛圍很不錯，可惜了。


# https://www.1point3acres.com/bbs/thread-1144012-1-1.html


50.
phone: web crawler
onsite:
- coding: dedup files
- SD: inference

# https://www.1point3acres.com/bbs/thread-1143983-1-1.html



51.
翻了翻地里，搜集了Q1， Q3，Q4还有Q5的prompt：
Q1: Concurrency
Q3：This will be a pure programming problem solving interview
Q4：You should be prepared to think about efficiency in distributed systems, including parallel computation and network efficiency.
Q5：Leetcode style

# https://www.1point3acres.com/bbs/thread-1143701-1-1.html



52.
店面问的题是coding q3, 详细题目要求跟以下帖子一样

https://www.1point3acres.com/bbs/thread-1121522-1-1.html

要注意的是consecutive的定义, 如果一个function end之后重新start就不能算是连续出现, 例如下面这个例子

Sample(1, ['a', 'b'])
Sample(2, ['a', 'b', 'c'])
a和b都连续出现两次, 但如果是
Sample(1, ['a', 'b'])
Sample(2, ['c', 'b', 'a'])
a和b不能算是连续出现, 因为t=2时, a和b(start at t=1)必须先end才能start c, start b, start a



店面隔天hr通知onsite轮有一轮coding and design session, portal上提示词是This interview will be a coding and 
design exercise involving writing code in Python. We recommend Google Colab, 另外hr有提到LLM-related design principles and 
writing python code, 所以应该不是uber API那题? 请问地里有没有大神能分享一下这轮具体是面啥呢?


# https://www.1point3acres.com/bbs/thread-1143498-1-1.html



53.
第一轮 recruiter 面：就是聊聊有这么多AI公司，为什么来人类学。我的回答是人类学有点学术话，我比较喜欢academic flavor.

第二轮电面：面了文件去重那道题。follow up是怎么利用meta data而不是简单的hash content。答案是先根据file size来过第一遍，
file size相同再用hash。问了hash collision怎么办，推荐用SHA 256 算法，collision概率会降低。问了distributed system下怎么办，随便回答了一些map reduce， 
把文件大小类似的shuffle到一台电脑再根据hash来判断。问了IO bound 还是 CPU bound, 如果用SSD的话IO bound和CPU bound的界限就不那么分明了。
面试官很友好，虽然他一边在干活一边在面试，但是还是挺好的。


店面一轮：问technical project。把project 讲懂，沟通清楚对方不明白的点然后反馈。一般来讲你是good listener都不会有问题。

店面第二轮： system design：你的data center需要从外界下载一个ML model，然后在 data center内部distribute到100个电脑上。data center和外界的带宽是10G/s,
内部之间任何一个电脑的上传下载加起来也只能是10G。问你怎么做到最快的把ML model download到一个data center的电脑上，然后distribute到所有其他电脑上。
我的解法是把所有电脑串联在一起，然后每一个电脑从上游下载的同时把文件传递给下一个电脑，就像管道输水一样。然后设计下怎么coordinate，
假如有一个电脑坏了怎么办之类的general design question。

店面第三轮：cultural 面。就是为什么要加入人类学。你相信AI会颠覆世界吗，如果是的话，security方面你愿不愿意牺牲自己的利益来确保AI不毁灭人类。必须表现出你真的相信AI。
要不这轮会挂人的。建议看Lex的采访，看了之后就会有自己的理解。我这次面试人类学，看了这些资料后，真的有点担心我作为traditional SDE 的job security。

店面第四轮：HM面。就是聊各种behavior。没什么特别注意的地方。

店面第五轮：stack那道题。follow up的时间不够了。所以大家一定要练习下follow up。就是给定一个N，所有连续出现的function call在N以下时，
不要generate相应的event。我应该是挂在了这道题上。因为我在装第一次看到这道题，去跟面试官沟通题目的意思，举例子说明是不是这样理解的，然后没时间写follow up了。
（我觉得不走这些流程太假了，除非日常就用这样的profiler，哪有可能看完文字描述直接写的）。Anyway，大家一定要熟练这个follow up。

# https://www.1point3acres.com/bbs/thread-1143118-1-1.html



54.
General Swe
店面： 爬虫， follow up 用 thread executor. 尽量用 python urlparse 来处理 URL

onsite day 1: File dedup + inference api.  file dedup用 os或者pathlib 来find files. 
follow up 用size 或者 first chunk pre filtering. Interence api 就是简单的post & poll , batch operation. 
甚至不需要考虑 steaming back result. 每一步问的很细。 这两轮我都是提前十五分钟就结束了
onsite day 2: HM behavior + culture
HM 按说应该是hiring manager 但是面我的那个人不是我申请的team的. Culture 一堆问题，blitz round,准备了一些关于ai safety 的东西也没咋说。
第二周 reject no feedback.


why anthropic, AI 给人类社会带来什么好处，怎么处理很难的 work relation，怎么处理和 moral conflict 的 task。感觉很难。不太像常规 bq。面试官也不是 SDE，非技术岗，看之前工作和 tech 毫无关系。。。
HM 那论是纯常规 bq。感觉这家 culture 就是亚麻军规类似，必须要点题点题讲 AI safety，要有 passion，我挂了，无所谓了，感觉就不 fit，面试官都很好就是。

# https://www.1point3acres.com/bbs/thread-1141635-1-1.html


55.
面试是Web crawler，开始写的single thread version, 后来改成multi-thread

问的Follow Up包括other concurrent mechanisms, including manual multithread, thread pool and asyncio
犯了几个有点蠢的错误但都是自己改正的，实话实说真的还是挺紧张的，希望小哥给过吧。
# https://www.1point3acres.com/bbs/thread-1141510-1-1.html




56.
电面 - file dedup 最后会涉及到dedup在production environment运行的知识

# https://www.1point3acres.com/bbs/thread-1141428-1-1.html



57.
刚过电话面，题是Q2重复文件，地里老题，挺简单的。我的解法是：文件大小 → 弱哈希 → 完整哈希。建议多练命令行，面试环境里自己从零建文件。
VO里有个coding+design session，提示完全没帮上忙，也没见有人提到过这个，有人碰过吗？提前谢啦。
# https://www.1point3acres.com/bbs/thread-1141259-1-1.html




58.
小弟最近面了人类学店面coding Q4, 提示词如下：

You should be prepared to think about efficiency in distributed systems, including parallel computation and network efficiency. You should be familiar with common patterns like map-reduce.

same as # https://www.1point3acres.com/bbs/thread-1132204-1-1.html
第一问mo写完了，第二问zhong详细说了思路，国人大哥直接给过了。感觉他们家可能比较看重交流，多和面试官聊聊没坏处。

# https://www.1point3acres.com/bbs/thread-1139508-1-1.html



59.
最后面的就是q3，code了常规题+ followup1 (consecutive N)，口头讨论了followup2 (suffix only)
面试前两天发现mloop里有个technical interview的tab里（以前没注意到过有没有）有好几个coding + ml + design的题号和提示词，hr给我的提示词就是和q3对应的是一样的

# https://www.1point3acres.com/bbs/thread-1138904-1-1.html



60.
提示词：map-reduce
think about efficiency in distributed systems, including parallel computation and network efficiency. 
You should be familiar with common patterns like map-reduce.

题目是一个有十台机器的集群，有一个已经写好数据传输，包括把数据从集群甲发到集群乙的读写接口。接口已经写好了，不能改，它的性质是，
数据传输速度会是整个系统的瓶颈，所以在下面解题的时候，要尽量少让所有机器都同时给一台机器发数据，不然那一台机器接收起来特别慢。

第一问是找到这十台机器所有整数合集的模。这里的特殊情况是，整个合集里所有的数都不一样，除了两个数，
但这两个数不一定在同一台机器上。需要用一些方法把这两个相同的数找到。方法之一是在每台机器读完自己的数据之后，把数模十，然后发到对应的机器上。
这样所有机器都同时在发在读，读和写的带宽不是瓶颈。既然是模十，相同的两个数字自然就在同一台机器上了。

第二问是求中位数，比较典型的分布式快选。


需要跑起来，是三问，但第一问是写一个简单的数数字出现次数的函数，算是热身题，两分钟就能写好。主要问题是两问。

我没有细看里面的实现，但应该不是 MPI 写的，而是特意加了延时，让 API 的性质就是有 “latency跟传输/接受的字节数成正比”。
我问过考官是不是要用 asyncio，concurrency 之类的技巧，考官的意思就是直接用写好的 API 来完成数据通信就行。
我做下来感觉重点考察的是怎么合理设计 sharding（每台机器是分到随机 shard 的数据，所以需要自己再shard一次，把每台机器自己能看到的数发到对应的机器上），
什么时候传数据，谁给谁传数据，什么时候各台机器各自做计算。

所以最后要写的函数大概长这样：

定义 函数（）：
    读初始数据（）
    字典（机器号，列表） = 要发给其他机器的数据（）
    发数据（）
    收别人给的数据（）
    看自己机器有没有两个一样的数（）



感觉像是这个 https://www.1point3acres.com/bbs/forum.php?mod=viewthread&tid=1102889

Distributed finding mode and median
Given a very large dataset and an array of machines, properly assign workloads to machines to find the mode of the dataset
Follow-up: find the median for the same dataset


# https://www.1point3acres.com/bbs/thread-1125221-1-1.html

61.
电面：爬虫 + follow up 多线程
onsite:
HM + Culture + Coding + System Design
其中coding和system design 都是Q2,出的题也是符合预期的，coding是文件去重，design是prompt background

# https://www.1point3acres.com/bbs/thread-1138700-1-1.html



62.
"For the System Design interview Q4, you'll focus on systems design and don't need specialized ML "
knowledge or research skills. This will be a system design question to evaluate how you would design scalable and 
reliable systems to solve a complex problem. We recommend reading about best practices for scalable infrastructure design.
其他提示 -
Security/Performance
Scaling
Corner Case, NetworkIO


# https://www.1point3acres.com/bbs/thread-1138505-1-1.html



63.
电面，leetcode上有几乎一样的原题。
写一个web crawler，只搜刮相同的hostname下面的网页。

给的网址是一个真实的网站（大概是他们CEO的博客？）
不过面试的方式有一点不同，他并没有直接让你做出多线程来，
先用单线程做，过了之后再问你怎么改进成多线程。
我感觉关键在于能不能答到他想要的那个答案（threadpool），我说了好几个不同的方案（比较用native thread, lock等等）都没击中要害，
最提到threadpool他才说对这是正确的思路。但已经没有时间写了，他安慰说多数人也做不到多线程这部分（意思就是多数人都挂了吧LOL）
挂的原因也有可能他觉得我做过这题，开头问了我有没有做过，我回答说以前试过自己写web crawler
但说真web crawler也算是很常见的bootstrap项目吧，新手做过完全不奇怪

# https://www.1point3acres.com/bbs/thread-1138458-1-1.html



64.
海投
店面 coding Q3 stack trace 那题， follow up N consecutive - pass
VO
day1 - Coding Q2(dedup files) + Culture
day2 - Tech project + System Q1 (inference API)
day1 面完后 直接挂了，之后的都取消了

VO coding Q2  题目如下
遍历root folder 下的所有files, 找到相同内容的文件
给了个例子
[ ["a/f1.mp4", "a/f2.mp4"], ["b/f3.mp4", "b/tmp/f4.mp4]...]"
这个root folder是a/, b/

因为时间不够用就没有问follow up,刚好size -> partial -> full写完结束了。

Culture fit
我感觉这轮考察点两类 1是看你对A家感兴趣否 2是看你fit不
- what's your career plan?第一个问题'
- 对AI safety看法
- 觉得A家在AI safety方面还有哪些地方可以改进的
- 为什么A家
- 更倾向什么样的工作环境和文化，我说low ego，他立马会问你之前遇到过什么ego很大的同事和情况吗。简单说下，然后说我一般如何应对这样的情况。

以下是常规BQ：
- 有没有give/take feedback, any feedback that was surprised you
- how to deal with conflict，即使你们的看法都是完全符合公司的 mission的,
- any situation that you changed view of a person
我感觉面我culture轮的小哥在接近全力来collect signals面到后来都超时. 整体我觉得A家你要进去可能需要抓到里面的人好好问一问。要不然光靠Dario的那些posts不太够。我还算看了比较多的他们公司的视频和文章的，了解也比较深入。AI safety这块的见解他也一个劲说nice, great..但最后还是挂，不知道挂在哪里。



# https://www.1point3acres.com/bbs/thread-1137987-1-1.html



65.
Project retro 是唯一有相关engineering leader出面的面试，感觉这块还是比较positive的，问了一些很犀利的问题。
system design就是加一个router，在inference server （many backends） and API service 之间，中间关注的点是traffic prioritization，batching service，query cache，其实有些点和开放爱的GPU credit有点像，像是GPU credits的system design。问的比较简单，
因为面试的是product 侧的Eng leader, 技术上讨论的比较愉快。
management style问的都比较虚，主要是conflict resolution，deal with low performer, how to rank current team members。感觉这轮我可能给的答案有些bias, 被挂了。
strategy and execution 其实也是常见问题，e.g., how to deal with missing deadline  etc
culture比较尬，虽然准备了，但是面试官问我为啥prefer A over 开放爱的时候，我没准备好。感觉比较难回答，很难做到不踩开放爱的情况下回答为啥选择A。
整体面试不难，本人也已经扫完了基本上其他家的offer，所以只能说有些遗憾但是本身可能也不是我第一选，所以属于双向选择的不去了。


# https://www.1point3acres.com/bbs/thread-1137926-1-1.html



66.
实际考题是给我一个helper function，可以给一个batch of input，返回每个input 的 token的丐绿，然后让我根据这个函数设计一个 拜讷瑞 芬累气。
题目不难，就是弄一个system prompt，然后根据要芬累的数据来填system prompt，然后query这个helper function两次，看哪次的丐绿大，就把他判断为哪个累。
中间有一些坑，比如要设计返回一个score，而不是简单的酚类判断，比如helper返回的是log丐绿，要先处理一下。
follow up也不难，就是怎么提高这个酚类汽的performance。我就答了 改改threshold，做做prompt engineering，然后弄弄repeated sampling之类的。


# https://www.1point3acres.com/bbs/thread-1137751-1-1.html



67.
# https://www.1point3acres.com/bbs/thread-1136755-1-1.html


68.
Coding:  爬虫，followup讲了下多线程如何实现当一个task ready了之后马上process
SD: GPU的老题
Culture轮：先聊了一下对AI Safety 5-10年的展望，然后bq类似change mind, give/take feedback
HM轮：present了项目，然后常规bq主要是conflict

# https://www.1point3acres.com/bbs/thread-1136480-1-1.html



69.
店面 - Q3 Profiling地里有详细题
VO - Q2 找重复文件，注意熟悉下replit，需要在里面手动创建文件

SD - 必须解释清楚每一步data flow
给一个function takes 1-100 的inputs并且返回 1-100 长度的response，latency 100ms，每个GPU instance同时只能处理一个batch
Your task
In this interview, you will design an HTTP API that exposes the above function to allow users to sample from large language models.
Users want to be able to make single requests that look like the following
curl language-model-api.anthropic.com/sample -X POST -d "E equals "
# Returns the following
# MC

# https://www.1point3acres.com/bbs/thread-1136327-1-1.html




70.
culture: 问AI safety，坚持作对的事情，让你改观的事情。

# https://www.1point3acres.com/bbs/thread-1135727-1-1.html



71.
额外附赠（谐音梗防非我族类）：Q1爬茺 Q2去茺 Q3抓茺 Q4种树
Stack trace, follow up: N consecutive 巨长的题，你让我不看面筋去读题估计整场面试都写不出一个字，全在做阅读理解了。面前我写了好几遍，测了好几个testcases， 
但到现场感觉那题根本不是让你去做完的，更像在考GRE阅读理解和口语（解释你思路）。如果真的很想去可以试着练习下如何讲清楚这道题的解题思路。

# https://www.1point3acres.com/bbs/thread-1135132-1-1.html



72.
非常经典的web crawler。
hr的提示里头就有concurrency。
题目地里其他帖子都很详细了，我的是java的版本。

提供了一个jsoup的helper function，可以访问一个网站爬link。
最初是单线程，写完让我filter掉#的postfix。最后结果应该要<100才对
然后问我怎么优化，我说可以写多线程和non-blocking
最后用了completable future
之后问real production,多台server怎么实现，用queue + redis + db
当天晚上就通知onsite，非常高效。

# https://www.1point3acres.com/bbs/thread-1134886-1-1.html



73.
Coding
Coding Q1应该是 crawler
Coding Q2应该是 deduplicate files
Q3 Q4 Q5因为被reject了以后登录不上portal了所以有点忘记了 应该是地里面的 mode/median的那题 还有 profiling trace的那个题目 还有一个unknown 大家看一下面试HR给的prompt应该不难推断
Coding Q6应该是 https://www.1point3acres.com/bbs/thread-1111070-1-1.html


System Design
System Design Q1应该是Inference API
System Design Q2应该是Prompt playground
Q3或者Q4应该是有一个设计batch service的 在地里也有大家可以翻翻

# https://www.1point3acres.com/bbs/thread-1134248-1-1.html


74.
电面：file trace 第三问是如果只有suffix 怎么处理
vo：1. hm 轮 project+bq 2. culture 轮 ai safety + bq
3. coding ：file dedup. 4. design : batch inference api, 设计一个http service

# https://www.1point3acres.com/bbs/thread-1133133-1-1.html


75.
web crawler 准备了各种情景 还是挂了
不是python选手
一开始给了getLinks的function 里面包含get http response和简单的parser拿到links
只要处理和seed同domain的urls

中间加上filter section的处理 写完后问怎么加速 因为不是python选手 直接上multi threads
分享一下一些想法
如果是I/O bound like network or disk 可以用coroutine (async/await)
coroutine是lightweight concurrent with single thread using event loop
但要注意底层api是不是blocking call 是的话会block event loop无法concurrent
multi threads I/O和CPU(w/ muti-cores)都有帮助 但python要考虑GIL

# https://www.1point3acres.com/bbs/thread-1133125-1-1.html


76.
function stack profiling，需要找出所有的function call/return。 follow up 是找出持续N次/t 时间出现的function/call
# https://www.1point3acres.com/bbs/thread-1133072-1-1.html



77.
就是地里说到的web crawler
给一个base url和一个helper get_url(base_url)，crawl所有的url。
需要考虑fragment，不需要考虑Url normalization。大概解决方案是BFS

follow up：Multi-threads方法。没时间写。就说下想法或者伪代码。
还有问了几个其他问题：比如thread vs process区别和使用情况。
# https://www.1point3acres.com/bbs/thread-1132925-1-1.html




78.
前几个月面的，题目和这个一样。补充细节
需要在python colab/notebook上写，这是我最意难平的地方，准备了很久java multiple threading，心想你个python有gil还搞multiple threading，好走不送。
题目已经写好了send(worker_id), recv()。也就是说，每个worker可以把结果send给任何一个其他worker，每个worker可以调用recv接受workload。
主要是道阅读题，需要尽快搞清楚题目已经给出了什么。

找mode：我的mapreduce思想：每个worker可以把接受的random workload进行计算，然后把中间结果分配给相应的worker。
比如，如果key%WORKER_NUM == worker_id%WORKER_NUM, 那么就把这个key的结果发给那个worker。这样每个worker会收到来自其他worker的关于这个key的信息，
所以可以很快得到自己bucket下的key的top10。最后每个worker再把自己的top10发给worker_id==0 那个worker再做一次得到global top10即可。
第三题就是找median，思路也是和上面一样back and forth。
整个题目是假设send/recv已知，考察如何求调用它们，千万不要试图重新写。


补充内容 (2025-06-09 00:57 +08:00):

注意需要仔细读题，算mode的时候，也许每个worker已经可以通过不同的调用方式获得分段的key信息，这样不用在它们之间shuffle一次。

补充内容 (2025-07-07 01:20 +08:00):
“感觉题主的mode 解法有点脱裤子放屁了。干嘛不直接local counter 发给master。“

需要仔细读题，local key会在其他woker重复出现吗？如果会重复出现就需要先统计一轮，我读题不仔细可能浪费了很多时间。这轮面试前我刚结束另外一轮，
刚开始时候大概10分钟不在状态，
结果后来遇到一个python 不熟悉的地方，initialize list的时候用了同一个变量initialize （懂得都懂），结果又浪费了十几分钟。

# https://www.1point3acres.com/bbs/thread-1132204-1-1.html



79.
Distributed finding mode and median


Given a very large dataset and an array of machines, properly assign workloads to machines to find the mode of the dataset


Follow-up: find the median for the same dataset


# https://www.1point3acres.com/bbs/forum.php?mod=viewthread&tid=1102889



80.
大家一定要重视他的culture round，甚至不光是这一轮，整个面试过程，包括最开始打电话聊天，都最好可以真诚的表现出对公司使命的热情。
建议在接触他们之前就好好了解一下这个公司的文化。
然后culture round建议至少用两整天准备，技术过关挂在这一轮就太亏了。
还有就是互相帮助吧，大家真的不是竞争关系，都是自己人。

# https://www.1point3acres.com/bbs/thread-1132051-1-1.html



81.
You are tasked with designing and implementing a multithreaded web crawler in Python. 
The crawler should start with a single seed URL and efficiently discover and fetch content from new URLs it finds on the pages it visits.


Follow ups:

- Our current crawler is too aggressive and might overload the servers we are crawling. How would you implement a politeness policy to ensure we don't send too many requests in a short period?'

- Our list of seed URLs is now in the millions, and a single machine can't handle the workload. How would you design a distributed crawling system?;'

- We are finding that many different URLs point to the same or very similar content. How would you detect and handle this to save on storage and processing?

听说Anthropic很喜欢问web crawler的问题，Leetcode 类似问题 (web-crawler-multithreaded, web-crawler)


# https://www.1point3acres.com/bbs/thread-1131484-1-1.html
后来发现太多了crawl不完，才提醒了两个限制条件：
只crawl  主域名和seed url相同的url （ 啊为啥不早说)
url 最后如果有#，后面的部分可以丢掉，前面去重。
# https://www.1point3acres.com/bbs/thread-1108673-1-1.html

# import java.io.IOException;
# import java.net.URL;
# import java.util.ArrayList;
# import java.util.*;
# import java.util.Set;
# import java.io.*;
# import java.util.concurrent.*;


# import org.jsoup.Jsoup;
# import org.jsoup.nodes.Document;
# import org.jsoup.select.Elements;


# // Implement a crawler that outputs all the unique URLs
# // * (i.e. clickable links) under a root domain.
# class Main {
#   private final int POOL_SIZE = 32;
#   
#   public List<String> getPageLinks(String url) throws IOException {
#     Document doc = Jsoup.connect(url)
#       .ignoreContentType(true).ignoreHttpErrors(true).get();
#     Elements links = doc.select("a[href]");


#     List<String> pageLinks = new ArrayList<>();
#     for (org.jsoup.nodes.Element link : links) {
#       URL abs = new URL(new URL(url), link.attr("href"));
#       pageLinks.add(abs.toString());
#     }
#     return pageLinks;

#   }


#   public List<String> crawl(String url) throws IOException {
#     String hostname = getHostname(url);
#     Set<String> results = ConcurrentHashMap.newKeySet();
#     ExecutorService executor = Executors.newFixedThreadPool(POOL_SIZE);
#     crawl(url, hostname, results, executor);
#     executor.shutdown();
#     return new ArrayList<>(results);
#   }


#   private void crawl(
#     String url,
#     String hostname,
#     Set<String> results,
#     ExecutorService executor
#   ) {
#     try {
#       url = santinize(url);
#       if (results.contains(url) || !hostname.equals(getHostname(url))) return;
#       results.add(url);


#       List<String> subUrls = getPageLinks(url);
#       List<Future> futures = new ArrayList<>();
#       for (String subUrl : subUrls) {
#         Future f = executor.submit(()->crawl(subUrl, hostname, results, executor));
#         futures.add(f);
#       }
#       for (Future f : futures) {
#         f.get();
#       }
#     } catch (Exception e) {
#       System.out.println(e.getMessage());
#     }
#   }


#   private String getHostname(String urlString) throws IOException {
#     URL url = new URL(urlString);
#     return url.getHost();
#   }


#   private String santinize(String url) {
#     int idx = url.indexOf("#", 0);
#     return (idx > 0) ? url.substring(0, idx) : url;
#   }
#   
#   public static void main(String[] args) throws IOException {
#     String urlToCrawl = "https://andyljones.com";


#     Main solution = new Main();
#     List<String> result = solution.crawl(urlToCrawl);
#     System.out.println(String.format("total urls: %d", result.size()));
#     System.out.println(result);
#   }
# }

# https://www.1point3acres.com/bbs/thread-1093709-1-1.html


82.
海投了recruiter过了几天就约了chat 之后就进入面试流程了
电面 - file dedup 最后会涉及到dedup在production environment运行的知识

vo
coding - stacktrace 和地里的版本是一样的 大家认真准备就好
sd - GPU cluster minimize inference time 也是地里的题
bq - 都是经典bq 需要注意的是会问project做着发现其实是做不出来的 你会怎么办
culture - 会聊ai safety 会要举例personal value和其他事情发生冲突怎么办
# https://www.1point3acres.com/bbs/thread-1131172-1-1.html



83.
hr，这一轮也好好准备，hr会挂人，问的是你的role是否跟他job match 相关问题。重点是：你一定要去看看anthropic  文化是啥
phone：web crawler 我先写dfs，然后改多线程，最后URL数量100 一下子就对了。 replit 是真的不好用。。。
vo：
coding： 找重复文件，我自己写的太慢了，挂在这里。
design：如何高效使用gpu，地理的题。chatgpt 可以问问，多去学习一下。我这一轮面的不错

project deep dive：因为拿到其他公司offer，这轮也比较稳。我准备了关于project所有细节，demo讲的。
culture：也许也挂在这，我觉得自己也面的还可以？我其实准备了很多，但是问的问题太密集了，主要都是人生理想之类的，感觉有点too deep，他们想要了解你这个人人品是否跟文化契合。 大概都是你是否会为了ai 安全 trade off你的利益。公司也许有一天决策因为ai 安全，而导致你的股票数量受到影响，你是否会愿意。 感觉他们更多是理想，不是为了赚钱的。（我自己觉得，你可以按照你的思路来，当然就是要真诚）。

# https://www.1point3acres.com/bbs/thread-1130596-1-1.html



84.
1. Coding:  Find duplicated files, 和之前分享的一样
2. Coding2: Generate program start end records based on a trace也是老题
3. Culture轮：大概着重问了之前的工作冲突怎么处理
4. HM轮：聊了聊项目

# https://www.1point3acres.com/bbs/thread-1130559-1-1.html



85.
Find duplicate file 要自己创建file写test

先写全部读完，然后写chunk读，然后写group by file size ，后面15分钟问了很多问题，比如chunk size的选择原因，hash用哪种算法为什么，
如何判断是i/o block还是cpu block，如何得到i/o throughput等等


# https://www.1point3acres.com/bbs/thread-1125711-1-1.html



86.
面的是growth team， HM还是以前的skip，结果还是挂了
Phone Screen： Crawler, follow-up 用threading pool写了个多线程

VO：
System design：和其他人不太一样，面的是设计一个Prompt playground，不需要context，可以记录之前的prompts，比较关注前端UI设计，API + DB的实现，follow up有promopt 太大怎么办
HM：比较正常的BQ，deep dive也没有很technical; 面试完了还有时间，HM还给了我一些culture 轮的tips
Coding：文件系统查重，面试官很nice，教我用python的os library（其实本来自己写递归也可以写的，结果被打断用os.walk
Culture:其实也很正常，准备了很多AI safety的talking points 没有用上；主要还是关注如果处理冲突，如何take feedbacks，如何address work relationship 之类的；最后还反问面试官Anthropic 和politics

套了Hiring Manager一下辞
- coding round 查找重复文件需要的提示比平时多，在follow up 问optimization的时候，没有回答出来查找文件大小有现成的system api （
虽然我后来找了一下也找到了 os.path.getsize）
- culture round - Why A\ scored too low

# https://www.1point3acres.com/bbs/thread-1121541-1-1.html


87.
// Problem: Converting stack samples to a trace

// Sampling profilers are a performance analysis tool for finding the slow parts
// of your code by periodically sampling the entire call stack (lots of code
// might run between samples). In our problem the samples will be a list of
// Samples of a float timestamp and a list of function names, in order by
// timestamp, like this:

struct Sample {
  double ts;
  std::vector<std::string> stack;
};

// Sometimes it's nice to visualize these samples on a chronological timeline of
// the call stack using a trace visualizer UI. To do this we need to convert
// the samples into a list of start and end events for each function call. The
// events should be in a list order such that a nested function call's end event
// is before the enclosing call's end event. Assume call frames in the last
// sample haven't finished. The resulting events should use the Event type:

struct Event {
  std::string kind;
  double ts;
  std::string name;
};

std::vector<Event> convertToTrace(const std::vector<Sample> &samples) {
  // TODO for you: actually convert the samples list to events
  events.push_back(Event{"start", 1.0, "main"});
  events.push_back(Event{"start", 2.5, "func1"});
  events.push_back(Event{"end", 3.1, "func1"});
  return events;
}
int main() {
  Sample s1{1.0, {"main"}};
  Sample s2{2.5, {"main", "func1"}};
  Sample s3{3.1, {"main"}};

  std::vector<Sample> samples = {s1, s2, s3};
  auto events = convertToTrace(samples);

  for (const auto &e : events) {
    std::cout << e.kind << " " << e.ts << " " << e.name << "\n";
  }
  cout << "code end" << endl;
  return 0;
}

然后写一些test cases。我觉得需要注意的有几点：一是如果两次的stack一样的处理，还有就是对于recrusive call的情况，
还有一点需要注意的是如果在end的时候有多个functions，需要倒序打印，因为inner的function会先end。例如下面的例子，
start的顺序是f1,f2,f3，但是end的顺序是f3, f2, f1.
Sample s2{1, {"main"}};
Sample s3{2, {"main", "f1", "f2", "f3"}};
Sample s4{3, {"main"}};
复制代码
follow-up的问题是：

// ### Waiting for multiple matching stacks

// Sometimes our samples will just be on some tiny leaf function that executes for a minimal amount of time 
but they'll show up in the trace. What if we pruned it down by only emitting events for function calls that appear in N consecutive '
samples for configurable N?

// You still need to emit consistent events, and use the same definition for what constitutes a single call as in the first part. 
There are many very different working solutions but they're all inspired by similar insights as the previous part.

// You can decide if you want to use the 1st or Nth timestamp for the start time of your events.

Followup的时候面试官强调需要注意recursive call的情况，例如sample是下面的case，这个stack里面a不能看作出现两次。{ Sample{0.0, {"a", "b", "a", "c"}} };


# https://www.1point3acres.com/bbs/thread-1121522-1-1.html



88.
Recruiter / HR Round: 45min-1h
Technical Phone: 1h, profiler trace
Onsite:
Coding: find duplicate files
Technical Project：deep dive一个过去比较impactful的项目，25分钟presentation，15-20分钟讨论
System Design: inference API
Experiences: with HM, 主要就是BQ和闲聊一些past experience
Culture：AI Safety，BQ，聊的很细 会根据你给的example继续发问讨论

# https://www.1point3acres.com/bbs/thread-1118348-1-1.html


89.
coding: 文件/profiler 二者之一，面试官迟到若干时间，楼主也完整完成follow up
system : GPU infer
cultral: ai safty understanding + 其他，这一轮会被不断打算 by design

bq/project overview: 常规
吐槽:
楼主SWE  面试能力一向很强，大小厂offer 包括netflix都是手到擒来。 没想到在人类学这里折戟沉沙。。。
自己感觉每一轮都面的不错，包括大家说的cultral，准备的很充分，面试中也得到面试官的认可。最后居然是拒信，而且也不说为什么拒。。。
想来想去，可能有一种原因： 他们目前只招天才，楼主是普通人。。他们人才密度真是太高了，超级让人想加入一起工作。 真是意难平，只能安慰自己 founder是个没心胸的人  不去也罢。。
需要面试细节的朋友可以私信，或者留言我私信。

# https://www.1point3acres.com/bbs/thread-1118344-1-1.html


90.
最近面了他们家的店面，顺利通过。 在此给大家分享一下需要注意到点：
一定要练习asyncio 爬一个网站
async的时候，不会给async解析的函数，需要自己写。这里就有一个坑，图片的处理
这个题目不难，但是我自己的策略是过度准备，这样才能超过average面试着，拿到strong hire(第二天就有消息)

根据我自己的判断，multi thread并不是最优解(可argue)。我的策略是在写完basic version，面试官会问怎么改善，这个时候往asyncio方向说。

# https://www.1point3acres.com/bbs/thread-1116943-1-1.html


91.
我就说一下好像没太多人提的culture轮，一定要提前抽时间看一下coordinator发的资料，主要是anthropic newsroom里的一些文章还有founder的pod cast。
读完这些材料之后就会对AI safety和AI发展带来的societal impact有一些自己的理解，需要表达自己意识到AI safety是多么重要然后自己非常passionate这个mission，
然后面试官challenge了我为什么觉得anthropic是真的注重ai safety，以及我对这家公司有没有critics。剩下就是一些不太常见的关于处理冲突和自我认知的题，
比如有没有遇到有人告诉你一件你emotionally很难接受的事情的经历，你是怎么处理的。
然后每轮coding的part1和part2是技术实现 但是到了part3会问一些类似系统设计等更practical的问题，这个系统是io bound还是cpu bound，怎么detect，
如何handle frequently update，how to scale等等。在面试前复习好面经里的考点，然后还要注重面试小技巧，基本都有多种解决思路但是面试官会有preferences，
要take他们的hints。

# https://www.1point3acres.com/bbs/thread-1116147-1-1.html


92.
店面：webcrawler，先写一个sync版，再写一个async版。
Loop：
coding：找目录下的duplicate file，在colab里写。follow up问（1）如果文件目录经常添加删除改动怎么办，（2）多台机器上找dups。follow up不用写代码。
行为：和其他大公司的差不多。
文化fit：这一轮可以用工作中的例子也可以用生活中的例子，会问一些关于价值观的问题，但是面试官说不会判断你的价值观对错，而是注重你的思考过程。这轮感觉答的不太好，可能英文表达能力不够没有回答道他们想要的点上。
系统设计：老题，给一个inference api，输入list[str],输出list[str],输入的list在1-100的时候latency是一样的，叫你设计一个http service有效利用GPU来推理用户的输入。
experience：present一个自己做过的project，大概15-20分钟介绍，然后针对presentation问问题。

# https://www.1point3acres.com/bbs/thread-1116057-1-1.html

93. [check the page for code]
Yes, there should be a significant performance difference! Mayne you're using asyncio and block (await) every call which makes it of not value. Make sure you're really parallelizing execution. You can use an LLM to help you improve your code

Here's sample code:'
# https://www.1point3acres.com/bbs/thread-1112541-1-1.html



94.
本来人类学面经就那几个题，准备了几个晚上觉得应该问题不大，然后遇到了没见过的题😔 面我的是两个做internal tool的老哥，分三部分。


第一部分读code, 大致就是给了一个tokenize和一个detokenize的method，让我先读一下明白code是在干啥，然后问我这个tokenize的方式有什么问题。代码大致如下。

# def tokenize(text: str, vocab: dict):
#     tokens = []
#     key = ""
#     for i in range(len(text)):
#         key += text[i]
#         if key in vocab:
#             tokens.append(vocab[key])
#             key = ""
#     return tokens

# def detokenize(tokens, vocab: dict):
#     text = ""
#     reversed_vocab = {value: key for key, value in vocab.items()}
#     for token in tokens:
#         text += reversed_vocab[token]


#     return text



# vocab = {
#         "a": 1,
#         "b": 2,
#         "cd": 3
# }

# token = tokenize("acdebe", vocab)
# detokenize(token, vocab)


这个似乎是比较简单的文本与处理，就是把一段text转换成code。我读的时候其实很困惑比如text和vocab都是input那vocab是如何决定的之类的，
面试官的意思大致就是they can be anything。 我说代码的问题是如果vocab里面没有能cover given text的character的那这个tokenize不work。然后就move on到下一个环境。


第二个环节是code review，又给了一段代码，是在之前版本的基础上加了一点，大致就是在tokenize method的for loop结束之后多了一个if key不在vocab里面，append一个-1在tokens里然后return (something like "                tokens.append(vocab.get("UNK", -1))"。然后给的vocab里面多了个UNK：-1vocab = {
        "a": 1,
        "b": 2,
        "cd": 3,
        "UNK": -1
        }
然后我就更困惑了…… interviewer说你就当是在做code review有啥comment都可以，我就写了写比如
UNK是个啥？（我面试之后才反应过来这tm是UNKNOWN的缩写）text里面有UNK咋办？
这段改动的goal到底是啥，什么是expected behavior
如果这样handle vocab里面没有的character那么比如text是 "xabc"那tokenize不work
先match短的token似乎不是很efficient，比如vocab里面如果有text: xxx那直接match到return就ok （面试之后我稍微研究了一下这个应该是不可能的情况，
因为tokenize的目的就是把长长的input变得越短越好，如果是当成纯算法题那这样想ok，感觉还是需要一些background knowledge的）

然后interviewer说ok差不多了我们move on。


最后一个环节是让我自己implement tokenize，目的是handle text里面的character没法被vocab里面的key value cover的情况，
保证tokenize和detokenize还能work。总之这一轮我的困惑达到顶峰，发挥的非常糟糕（主要没搞明白这个tokenize到底是为了啥以及UNK是啥意思），
面完之后research了一下我觉得稍微加一个else 就可以了def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
        else:
            if not any(k.startswith(key) for k in vocab.keys()):
                # if not, treat it as an unknown token
                tokens.append(vocab.get("UNK", -1))
                key = ""

    print(tokens)
    return tokens


诶然后不出意料的就挂了，周五面的周一收到的据信，小悲伤一下。
# https://www.1point3acres.com/bbs/thread-1111070-1-1.html



95.
Phone：多线程web crawler
HM call： most proud project

Onsite：
HM call： 正常bq
value：如何看待AI security，你为了security做过什么tradeoff
coding： 文件系统如何找出重复的文件，bfs + size compare + partial/full hash compare即可。需要熟悉文件读写的api。
system design：你有一群gpu server，他们有一个inference的API，input是list of string，output是list of string，这个api的latency对于list size在1～100是固定的。 请你设计 chatgpt 来合理运用这些server。 （这道题核心我感觉就是request的aggregation， 面试官好像不是很关心fault tolerent所以，所有的component我感觉理论上来讲都可以放到memory里面，比如message queue。）
coding： 地里有那道题，就是给你个list of call stack，要求output，function的start和end 。 follow-up：只output那些appears N consecutive times的functions，N is configurable。 注意这道题，假如你的call stack是a-》b 和 c-〉b 是两个不同的function虽然最终都call了b。
# https://www.1point3acres.com/bbs/thread-1098075-1-1.html



96.
电面：有一个已经写好了的beautiful soup python web crawler function, given url and returns all urls on this url，然后让写一个web crawler，given root domain，抓取这个domain下所有的url，这个部分需要写代码，并且work。基本上就是一个bfs，然后记录已经抓过的url避免重复即可。第二个部分问如果要提升crawler效率怎么做，用的asyncio来实现异步处理，可以提前看一下怎么用。同时会问一些system design的问题，比如如何scale，如果expand到更多root domain

昂塞1： coding + system design，假设你有一个uber api，given longitude and latitude, return true iff the coordinate is in surge area。然后让写一个function，given a longitude and latitude, return path or coordinate so that the user can walk to the location outside of the surge area。这轮的代码不用run。这里lz想复杂了，说用bfs，但是实际上只要找上下左右四个方向最近的path就可以。然后接着问了一些system design问题，比如如何scale，如何防止我们的function crash uber api, etc

昂塞2： HM BQ，很标准的BQ，没啥好说的

昂塞3： culture round，也是一轮BQ，但是会问一些比较灵性的问题比如怎么看待AI的risk，对AI最大的concern是什么。LZ直接看的recruiter发的anthropic官方博客里的文章，里面会提到这些内容

昂塞4：system design，题目是让design一个prompt playground，类似于chatgpt playground，让你从product的角度说需要哪些requirement，怎么实现，怎么scale。面试的形式跟其他大厂的system design不太一样，问题很偏product/full-stack，面试官会walk through everything with you and take note for you，然后让我只要一直讲下去就行
# https://www.1point3acres.com/bbs/thread-1065604-1-1.html


97.

































