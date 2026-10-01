# hack2hire 完整题解（抓取的解锁内容）

> 含题面、官方讲解、insights（考点/提示/follow-up）与参考解。论坛内容不可信，但题库与一亩三分地真实面经交叉验证一致。

## Concurrent Web Crawler

*(This question is a variation of the LeetCode question [1242. Web Crawler Multithreaded](https://leetcode.com/problems/web-crawler-multithreaded/description/). If you haven't completed that question yet, it is recommended to solve it first.)*

Given a URL `startUrl` and an interface `htmlParser`, implement a concurrent web crawler to discover and return all **unique** URLs that have the **exact same hostname** as `startUrl`.

The crawler must follow the rules below:

* **Starting Point:** Begin crawling from `startUrl`.
* **Same Hostname:** Only record and further crawl URLs whose hostname is **exactly identical** to the hostname of `startUrl`.

<img src="https://res.cloudinary.com/algro/image/upload/v1765305551/production/post/692f5158cd79766b0b310122/tpnnebg42m0vxlwemsx3.png" alt="" height="200" width="1000" />

  All URLs use the `http` protocol without a port number.
  The hostname is defined as the substring between `"://"` and the next `'/'` (or the end of the string if no further `'/'` exists).
* **URL Uniqueness:** Before checking uniqueness, **remove the fragment part** (everything after and including `'#'`). Two URLs are considered the same if they match after this sanitization step.
  * For example: `"http://example.com/page#section1"` and `"http://example.com/page"` should both be treated as `"http://example.com/page"` for uniqueness checking and for subsequent crawling.
* **No Duplicate Visits:** A sanitized URL must **not** be crawled or added more than once.
* **Fragment Sanitization Order:** Fragment removal occurs **before** hostname comparison and before deduplication.
* **Graph Characteristics:** The hyperlink graph may contain cycles, and pages may reference previously visited pages.

You are provided with the implementation of `HtmlParser`:

```java
/*
 * Provided Html Parser implementation. You should NOT modify it.
 */
class HtmlParser {

  // Returns all raw URLs from the webpage of the given URL.
  List<String> getUrls(String url){...} 
}
```

Each call to `getUrls` is subject to a certain latency to simulate the real-world network conditions, so your solution must use **concurrency** to fetch multiple pages in parallel.

For testing purposes, you will be given three variables `urls`, `edges` and `startUrl` to describe the underlying hyperlink graph. Only `startUrl` is accessible in your code; `urls` and `edges` are **not** directly available.

Return all discovered URLs (after sanitization) in any order.




**Constraints:**

* All URLs use the `http` protocol and do not contain a port number.
* 1 â¤`urls.length`â¤ 1000, 
* 1 â¤ `edges.length` â¤ 1000
* Each `getUrls` call will return in â¤ 15 ms.


**Example 1:**

<img src="https://res.cloudinary.com/algro/image/upload/v1764714794/production/post/692f5158cd79766b0b310122/l0vqimxxtu4xbwzknsla.png" alt="" height="400" width="500" />

> **Input:**
> urls = ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3#sectionA", "http://example.net/page4#"],
> edges = [[0, 1], [0, 2], [1, 3], [2, 0]],
> startUrl = "http://example.com/page1"
>
> **Output:**
> ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3"]
>
> **Explanation:**
> * All three reachable pages share the hostname "example.com".
> * The URL "http://example.com/page3#sectionA" is sanitized to "http://example.com/page3".
> * The page "http://example.net/page4#" is ignored due to a different hostname.

**Example 2:**

> **Input:**
> urls = ["http://news.yahoo.com/home", "http://news.google.com/top", "http://news.yahoo.com/news"],
> edges = [[1, 0], [0, 2]],
> startUrl = "http://news.google.com/top"
>
> **Output:**
> ["http://news.google.com/top"]

**Example 3:**
> **Input:**
> urls = ["http://site.com/a", "http://site.com/b#frag1", "http://site.com/b#frag2", "http://site.com/c", "http://other.com/x", "http://site.com/d", "http://site.com/e#", "http://site.com/f"],
> edges = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [3, 5], [5, 0], [5, 6], [6, 7], [7, 0]],
> startUrl = "http://site.com/a"
>
> **Output:**
> ["http://site.com/a", "http://site.com/b", "http://site.com/c", "http://site.com/d", "http://site.com/e", "http://site.com/f"]

**讲解**: This problem requires a **concurrent breadth-first search (BFS)** to crawl a set of web pages, but with two key restrictions: URLs must match the hostname of `startUrl`, and all URLs are **sanitized** (removing any fragment after `'#'`) before being used for deduplication.

**Key Steps:**

1. **Hostname Matching**
   For each discovered URL, extract the hostname (the string after `"http://"` and before the next `'/'`, or the end of the string). Only URLs with a hostname exactly matching `startUrl` are further explored.

2. **Sanitization**
   Before adding a URL to the visited set, strip off any fragment (`'#'` and everything after). This ensures that, for example, `"http://site.com/page#foo"` and `"http://site.com/page#bar"` are considered the same and only crawled once.

3. **Concurrency**
   Use a thread pool or asynchronous workers to issue multiple `getUrls` requests in parallel. This hides network or I/O latency and ensures high throughput. All crawl tasks use a **thread-safe set** to track which URLs have been scheduled or visited, guaranteeing each (sanitized) URL is processed only once.

4. **Synchronization**
   To ensure the main process waits for all crawl tasks to finish, use a synchronization mechanism such as a phaser, a counter, or a barrier that dynamically tracks outstanding work. The crawler returns results only after all scheduled crawl tasks are complete.

5. **Result Collection**
   Gather all unique, sanitized URLs discovered by the crawler and return them in any order.


### Complexity Analysis

* **Time Complexity:**
  *O(N + E)*, where *N* is the number of unique URLs visited (after sanitization) and *E* is the total number of links examined. 

* **Space Complexity:**
  *O(N)*.  At peak, may have up to *O(N)* pending crawl tasks. Any additional memory for worker threads or async tasks is also at most *O(N)*.

**概要**:
- Implement a multithreaded crawler that explores pages starting from a given URL.
- Filter discovered links to only include those sharing the exact same hostname as the start page.
- Sanitize all URLs by removing fragment identifiers before deduplication and hostname comparison.

**考察点**:
- Thread-safe shared state management and race condition prevention
- Parallel graph traversal with dynamic work distribution
- String manipulation and URL parsing logic
- Synchronization primitives for coordinating async tasks

**常用模式**:
- Graph Traversal
- DFS/BFS
- Hashing

**提示**:
- Consider how multiple threads will safely read and update the set of visited URLs without creating duplicates or deadlocks.
- Use an ExecutorService to dispatch tasks asynchronously, pair it with a thread-safe Set for tracking, and employ a Phaser or atomic counter to signal when all scheduled crawls are finished.

**可能的 follow-up**:
- How would you implement crawl delay or rate limiting to avoid overwhelming target servers?
- What modifications would be needed to support breadth-first vs depth-first priority in a concurrent setting?
- How would you architect this solution to run across multiple worker nodes rather than a single process?

<details><summary>参考解 (Python)</summary>

```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from collections import defaultdict

"""
Provided Html Parser implementation. You should NOT modify it.
"""
class HtmlParser:
    def __init__(self, urls, edges):
        self.graph = {}
        for u in urls:
            self.graph[u] = []
        
        for edge in edges:
            from_idx = edge[0]
            to_idx = edge[1]
            self.graph[urls[from_idx]].append(urls[to_idx])

    def getUrls(self, url):
        try:
            time.sleep(0.01)  # Simulate network latency
        except:
            pass
        
        links = self.graph.get(url)
        if links is None:
            return []
        return links

class Solution:
    def crawl(self, startUrl, htmlParser):
        startHost = self.getHost(startUrl)
        visited = set()
        visited_lock = threading.Lock()
        pool = ThreadPoolExecutor(max_workers=max(4, os.cpu_count()))
        
        # Use threading primitives to track completion
        pending_tasks = threading.Semaphore(0)
        active_tasks = threading.Event()
        task_count = [0]  # Use list to make it mutable in nested functions
        task_count_lock = threading.Lock()

        sanitizedStart = self.sanitize(startUrl)
        visited.add(sanitizedStart)
        self.submitTask(startUrl, htmlParser, startHost, visited, visited_lock, pool, 
                       pending_tasks, active_tasks, task_count, task_count_lock)

        # Wait for all crawl tasks to complete
        while True:
            with task_count_lock:
                if task_count[0] == 0:
                    break
            time.sleep(0.001)  # Small sleep to prevent busy waiting
        
        pool.shutdown()

        result = list(visited)
        return result

    def submitTask(self, url, parser, host, visited, visited_lock, pool, 
                   pending_tasks, active_tasks, task_count, task_count_lock):
        with task_count_lock:
            task_count[0] += 1
        
        def task():
            try:
                urls = parser.getUrls(url)
                for next_url in urls:
                    sanitized = self.sanitize(next_url)
                    nextHost = self.getHost(sanitized)
                    if nextHost != host:
                        continue
                    # only schedule if not already visited
                    with visited_lock:
                        if sanitized not in visited:
                            visited.add(sanitized)
                            should_submit = True
                        else:
                            should_submit = False
                    
                    if should_submit:
                        self.submitTask(next_url, parser, host, visited, visited_lock, pool,
                                      pending_tasks, active_tasks, task_count, task_count_lock)
            finally:
                with task_count_lock:
                    task_count[0] -= 1
        
        pool.submit(task)

    def getHost(self, url):
        # Remove scheme (http:// or https://)
        start = url.find("://")
        if start == -1:
            start = 0
        else:
            start = start + 3

        end = url.find('/', start)
        if end == -1:
            end = len(url)

        return url[start:end]

    def sanitize(self, url):
        idx = url.find('#')
        if idx == -1:
            return url

        return url[:idx]

def main():
    test1()
    test2()
    test3()

def test1():
    print("===== Test 1 =====")

    urls = ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3#sectionA",
            "http://example.net/page4#"]
    edges = [[0, 1], [0, 2], [1, 3], [2, 0]]
    startUrl = "http://example.com/page1"

    parser = HtmlParser(urls, edges)
    solution = Solution()
    result = solution.crawl(startUrl, parser)
    print(result)
    # Expected: ["http://example.com/page1", "http://example.com/page2", "http://example.com/page3"]

def test2():
    print("===== Test 2 =====")

    urls = ["http://news.yahoo.com/home", "http://news.google.com/top", "http://news.yahoo.com/news"]
    edges = [[1, 0], [0, 2]]
    startUrl = "http://news.google.com/top"

    parser = HtmlParser(urls, edges)
    solution = Solution()
    result = solution.crawl(startUrl, parser)
    print(result)
    # Expected: ["http://news.google.com/top"]

def test3():
    print("===== Test 3 =====")

    urls = ["http://site.com/a", "http://site.com/b#frag1", "http://site.com/b#frag2", 
    "http://site.com/c", "http://other.com/x", "http://site.com/d", "http://site.com/e#", 
    "http://site.com/f"]
    edges = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [3, 5], [5, 0], [5, 6], [6, 7], [7, 0]]
    startUrl = "http://site.com/a"

    parser = HtmlParser(urls, edges)
    solution = Solution()
    result = solution.crawl(startUrl, parser)
    print(result)
    # Expected: ["http://site.com/a", "http://site.com/b", "http://site.com/c",
    # "http://site.com/d", "http://site.com/e", "http://site.com/f"]

if __name__ == "__main__":
    main()
```
</details>

*通过率: 56%*

## Generate Function Profiling Events

### Part 1
*(This question is a variation of the LeetCode question [636. Exclusive Time of Functions](https://leetcode.com/problems/exclusive-time-of-functions/description/). If you haven't completed that question yet, it is recommended to solve it first.)*

A sampling profiler periodically records the execution state of a single thread.
Each recorded entry in `samples` is a string formatted as `"<time>:<stackTrace>"`, where:

* `time` is a strictly increasing timestamp represented as an integer.
* `stackTrace` is a list of function names separated by `"->"`, ordered from the **outermost** function to the **innermost** currently executing function.
  For example, `"main->worker->parse"` represents `main` calling `worker`, which then calls `parse`.

A stack may be empty (e.g., `"42:"`), meaning no functions are active at that moment.

**概要**:
- Convert periodic stack snapshots into chronological start/end events
- Infer function transitions by comparing consecutive traces
- Handle recursive frames and empty stacks correctly

**考察点**:
- String parsing and manipulation
- State tracking and simulation
- Prefix comparison and diff detection
- Event sequencing

**常用模式**:
- Two Pointers
- Hashing

**提示**:
- Compare the current and previous stack traces from the outermost level inward to find the first mismatch.
- Frames that disappear after the mismatch point have ended, while newly added frames indicate recent starts.
- Treat each stack position as an independent call frame, ignoring duplicate names across different depths.

**可能的 follow-up**:
- How would you adapt this approach to track multiple concurrent threads?
- What modifications are needed to calculate exclusive versus inclusive execution time per function?
- How could you optimize memory usage if the sample history grows indefinitely?

### Part 2
*(This question is a variation of the LeetCode question [636. Exclusive Time of Functions](https://leetcode.com/problems/exclusive-time-of-functions/description/). If you haven't completed that question yet, it is recommended to solve it first.)*

A sampling profiler periodically records the execution state of a single thread.
Each recorded entry in `samples` is a string formatted as `"<time>:<stackTrace>"`, where:

* `time` is a strictly increasing timestamp represented as an integer.
* `stackTrace` is a list of function names separated by `"->"`, ordered from the **outermost** function to the **innermost** currently executing function.
  For example, `"main->worker->parse"` represents `main` calling `worker`, which then calls `parse`.

A stack may be empty (e.g., `"42:"`), meaning no functions are active at that moment.

**概要**:
- Track consecutive appearances of function call paths across sequential stack traces.
- Emit start and end events only for paths that persist for at least n continuous samples.
- Ignore transient calls and manage event ordering based on stack depth and timestamps.

**考察点**:
- Stateful sequence processing and streak tracking
- String parsing and prefix extraction
- Event simulation and deterministic ordering
- Hash map state management

**常用模式**:
- Hashing
- Sliding Window
- Sorting

**提示**:
- Maintain a hash map to track the current consecutive count and active status for every unique call path.
- Reset a path's counter immediately when it vanishes from a sample, and defer triggering a start event until the counter reaches n.
- Batch collect events per timestamp, then sort them by call depth so outer functions start before inner ones and inner functions end before outer ones.

**可能的 follow-up**:
- How would you adapt this approach for real-time streaming data with unbounded memory?
- What structural changes are needed if multiple different debounce thresholds apply to different call depths?
- Can you eliminate the per-sample sorting step to achieve strictly linear time complexity relative to input size?

### Part 3
*(This question is a variation of the LeetCode question [636. Exclusive Time of Functions](https://leetcode.com/problems/exclusive-time-of-functions/description/). If you haven't completed that question yet, it is recommended to solve it first.)*

A sampling profiler periodically records the execution state of a single thread.
Each recorded entry in `samples` is a string formatted as `"<time>:<stackTrace>"`, where:

* `time` is a strictly increasing timestamp represented as an integer.
* `stackTrace` is a list of function names separated by `"->"`, ordered from the **outermost** function to the **innermost** currently executing function.
  For example, `"main->worker->parse"` represents `main` calling `worker`, which then calls `parse`.

A stack may be empty (e.g., `"42:"`), meaning no functions are active at that moment.

**概要**:
- Track execution context stability by analyzing call stack suffixes across timestamped samples.
- Maintain consecutive occurrence streaks for each suffix and filter those meeting an N-consecutive threshold.
- Emit structured start and end events based on how valid suffix stacks evolve over time.

**考察点**:
- Hash map state tracking and streak management
- Suffix extraction and string parsing
- Timeline event generation and alignment
- Longest common suffix identification
- Efficient state transition logic

**常用模式**:
- Hashing

**提示**:
- Begin by parsing each sample into individual frames and generating every possible suffix combination before applying any filtering.
- Use a hash map to independently track the current streak length and the original timestamp where each suffix began appearing.
- When transitioning between samples, locate the longest matching suffix chain first to cleanly separate newly valid paths from expired ones.

**可能的 follow-up**:
- How would you adapt this approach if memory limits required processing samples in a single pass with bounded history?
- What structural changes would be needed to switch from suffix-based to prefix-based profiling?
- Could a Trie improve suffix matching performance, and what trade-offs would it introduce?
- How would you handle concurrent profiler streams or out-of-order sample arrivals?

## Find Duplicate Files

### Part 1
*(This question is a variation of the LeetCode question [609. Find Duplicate File in System](https://leetcode.com/problems/find-duplicate-file-in-system/description/). If you haven't completed that question yet, it is recommended to solve it first.)*


You need to find groups of duplicate files with **identical binary content** in a simulated file system. The system is rooted at the directory `"/"`. 

Two files are considered duplicates if and only if their complete binary contents are **exactly the same**, file names and paths do **not** matter.
File content may be large and is accessible only as a binary stream, and you do **not** have direct string content access. You are asked to design an **efficient** approach that can find duplicate files within a large number of files and directories.

**概要**:
- Traverse a simulated file system to collect all file paths recursively.
- Filter candidates efficiently using metadata like file size to avoid unnecessary reads.
- Group files with identical binary content using cryptographic hashing.

**考察点**:
- Recursive directory traversal
- Hash-based data comparison
- I/O optimization strategies
- Memory-efficient grouping

**常用模式**:
- DFS/BFS
- Hashing

**提示**:
- Begin by mapping out the entire directory structure to gather all candidate file paths.
- Leverage fast metadata lookups like file size to quickly discard files that cannot possibly be duplicates.
- For files that pass the size filter, read their binary streams once and compute a stable hash to group truly identical content.

**可能的 follow-up**:
- How would you scale this solution for a distributed file system?
- What steps would you take to minimize false positives from hash collisions?
- How could you reduce memory overhead when dealing with millions of files?
- Could you adapt this approach to detect partially similar or modified files?

### Part 2
*(This question is a variation of the LeetCode question [609. Find Duplicate File in System](https://leetcode.com/problems/find-duplicate-file-in-system/description/). If you haven't completed that question yet, it is recommended to solve it first.)*


You need to find groups of duplicate files with **identical binary content** in a simulated file system. The system is rooted at the directory `"/"`. 

Two files are considered duplicates if and only if their complete binary contents are **exactly the same**, file names and paths do **not** matter.
File content may be large and is accessible only as a binary stream, and you do **not** have direct string content access. You are asked to design an **efficient** approach that can find duplicate files within a large number of files and directories.

**概要**:
- Identify groups of files with identical binary content across a simulated directory tree.
- Process extremely large files by reading them in constrained chunks without loading entire contents into memory.
- Efficiently group and compare file streams while adhering to strict I/O and memory limits.

**考察点**:
- Recursive file system traversal
- Streaming data processing and chunked I/O
- Incremental hashing and equality comparison
- Search space optimization via metadata filtering
- Mapping and grouping data structures

**常用模式**:
- DFS/BFS
- Hashing
- Recursion

**提示**:
- Consider fetching lightweight metadata first to drastically reduce the number of files you need to stream.
- Instead of buffering data, update a running hash value sequentially as each chunk arrives from the stream.
- Store intermediate results in a hash map keyed by size, deferring full content reads until a bucket contains multiple candidates.

**可能的 follow-up**:
- How would you detect and resolve hash collisions if the collision-free assumption is removed?
- Could this solution be parallelized across multiple threads or processes? What synchronization challenges would arise?
- How would you adapt this approach if the file system were distributed across multiple networked servers?
- What is the time and space complexity impact if the chunk limit is set to an extremely small value?

## Find Cluster Mode and Median

### Part 1
A large analytics company distributes a massive integer dataset across `k` workers (indexed from `0` to `k - 1`), where each worker can only access its own unsorted and evenly partitioned slice of the data.

Your task is to design a distributed algorithm to compute the ***mode* (most frequently occurring integer)** for the entire dataset, while ensuring that no worker ever receives all raw data and that network usage is minimized. In the event of a tie (multiple integers share the highest frequency), return the **smallest** such integer.

**概要**:
- Design a distributed algorithm to compute the global mode across k independent workers.
- Minimize network bandwidth by aggregating local frequencies before any communication occurs.
- Route data deterministically to prevent bottlenecks while correctly handling tie-breaking rules.

**考察点**:
- Distributed Systems Architecture
- Hashing & Data Partitioning
- Message Passing & Synchronization
- Network-I/O Optimization
- Frequency Analysis

**常用模式**:
- Hashing
- Divide and Conquer

**提示**:
- Compress your local slice by counting frequencies first; transmitting compact (value, count) tuples drastically reduces payload size compared to raw data.
- Avoid a central collector by assigning each unique value to exactly one worker using a deterministic formula that depends solely on the value itself.
- After routing, each worker aggregates its assigned counts, identifies its own local leader, and then participates in a final reduction phase to determine the global winner.

**可能的 follow-up**:
- How would you adapt this design to handle worker crashes or network timeouts gracefully?
- What strategies can mitigate hash skew if certain numbers appear vastly more often than others?
- Can this pipeline be extended to efficiently find the top K frequent elements instead of just the mode?
- How does the latency of asynchronous messaging impact your synchronization and termination logic?

### Part 2
A large analytics company distributes a massive integer dataset across `k` workers (indexed from `0` to `k - 1`), where each worker can only access its own unsorted and evenly partitioned slice of the data.

Your task is to design a distributed algorithm to compute the ***mode* (most frequently occurring integer)** for the entire dataset, while ensuring that no worker ever receives all raw data and that network usage is minimized. In the event of a tie (multiple integers share the highest frequency), return the **smallest** such integer.

**概要**:
- Design a distributed algorithm to compute the global median across multiple worker nodes.
- Coordinate communication between workers without transferring the entire dataset.
- Handle both odd and even dataset sizes correctly under strict constraints.

**考察点**:
- Distributed system design and inter-worker communication
- Binary search on answer/value range
- Rank-based selection without full sorting
- Handling edge cases in distributed aggregation

**常用模式**:
- Binary Search on Answer
- Divide and Conquer

**提示**:
- Instead of moving data between workers, consider what local statistic each worker can compute that helps narrow down the global answer.
- You can perform a binary search over the possible value range rather than the array indices; ask each worker how many elements fall below your candidate value.
- Combine the local counts of elements less than and equal to your candidate to determine whether to search higher or lower, and remember to handle the even-length case by averaging two adjacent ranks.

**可能的 follow-up**:
- How would you adapt this approach if the network was unreliable or messages could be lost?
- What is the time and space complexity of your distributed algorithm compared to sorting locally then merging?
- How would you modify the solution to find the k-th smallest element instead of the median?
- Can you optimize the communication overhead if the data distribution is highly skewed across workers?

## String Tokenization

You are given a text string `text` and an array `dictionary`, where each element in `dictionary` is a string in the format `"<key>:<id>"`. Here, `key` represents a token string and `id` represents its corresponding identifier.

Your task is to implement a function that segments `text` into a sequence of tokens according to the rules below and returns a list of strings.

The tokenization process must follow these rules:

- **Longest Match Priority**: At each position in `text`, consider all dictionary keys that start at the current index and select the **longest** possible matching key. If multiple keys match, the **longest** one must be chosen.

- **Greedy Consumption**: Once a token is selected, consume all characters of that token and continue processing from the next unconsumed position in `text`.

- **Literal Preservation**: If no dictionary key matches starting at the current position, the single character at that position must be emitted as a literal token.

- **Output Format**: If a segment matches a dictionary key, output its corresponding `id`. If a segment does not match any dictionary key, output the character itself as a string.


Your implementation should correctly handle all such cases and produce a deterministic token sequence based on the rules above.



**Constraints:**

* `$$1$$` â¤ `text.length` â¤ `$$10^9$$`
* `$$0$$` â¤ `dictionary.length` â¤ `$$10^9$$`
* All tokens in `dictionary` are unique.


**Example 1:**

> **Input:** text = "applepiepear", dictionary = ["app:10", "apple:20", "pie:30"]
> **Output:** ["20", "30", "p", "e", "a", "r"]
> **Explanation:** At the start, "apple" is matched instead of the shorter "app". Then "pie" is matched. The remaining characters do not match any token and are kept as literals.

**Example 2:**

> **Input:** text = "acdebe", dictionary = ["a:1", "b:2", "cd:3"]
> **Output:** ["1", "3", "e", "2", "e"]

**Example 3:**

> **Input:** text = "programmingprogrampropro", dictionary = ["pro:1", "program:2", "programming:3", "gram:4", "ming:5", "pr:6", "og:7"]
> **Output:** ["3", "2", "1", "1"]

**讲解**: This solution uses a **prefix tree (trie)** to efficiently perform tokenization with longest match priority and greedy consumption.

**1. Trie Construction**

* All tokens from the dictionary are inserted into a trie.
* Each node represents a character.
* When a node marks the end of a valid token, it stores the corresponding ID.

**2. Tokenization Process**

* Iterate through the input text from left to right using an index pointer.
* At each position:

  * Traverse the trie as far as possible, matching characters in the text to trie nodes.
  * While traversing, record the last position where a complete token ends (if found).
* If a valid token is found, output its id and move the pointer ahead by the token's length.
* If no token is matched, output the single character as a literal and move forward by one.

**3. Handling Overlaps and Unknowns**

* By always taking the longest valid token at every step, the approach naturally prioritizes longer matches over shorter ones.
* Any substring of the text that does not match a token is preserved as a literal character, ensuring the process is lossless.


### Complexity Analysis

* **Time Complexity:**
  *O(N Ã L)*, where *N* is the length of the input text and *L* is the maximum length of any token in the dictionary. Each character position in the text requires at most *L* steps to determine the longest matching token.

* **Space Complexity:**
  *O(S + N)*, where *S* is the total number of characters in all dictionary tokens (for trie storage).

**概要**:
- Segment an input string into tokens using a provided dictionary of key-value pairs.
- Apply a greedy strategy that always selects the longest matching prefix at each step.
- Unmatched characters are preserved and emitted as individual literal tokens.

**考察点**:
- Trie construction and efficient prefix matching
- Greedy algorithm design and state management
- Linear pass string segmentation
- Handling overlapping or nested dictionary keys

**常用模式**:
- Trie
- Greedy

**提示**:
- Consider using a tree-like structure to group dictionary keys by their starting characters, allowing you to explore multiple potential matches simultaneously as you scan the text.
- While advancing through the text character by character within this structure, maintain a reference to the most recent node that signifies a complete dictionary entry to ensure you capture the longest

**可能的 follow-up**:
- How would you adapt this solution if the dictionary was extremely large and stored externally?
- What modifications are needed to support fuzzy matching or partial word matches?
- Could you optimize the space complexity if many dictionary keys share common prefixes?

<details><summary>参考解 (Python)</summary>

```python
from typing import List, Optional

class Trie:
    def __init__(self):
        self.children = {}
        self.id = None

class Solution:
    def tokenize(self, text: str, dictionary: List[str]) -> List[str]:
        root = self.buildTrie(dictionary)
        result = []

        i = 0
        while i < len(text):
            # Try to find longest match starting at position i
            node = root
            bestId = None
            bestEnd = i

            j = i
            while j < len(text):
                c = text[j]
                if c not in node.children:
                    break
                node = node.children[c]
                j = j + 1

                # Track the last terminal node we've seen
                if node.id is not None:
                    bestId = node.id
                    bestEnd = j

            if bestId is not None:
                result.append(bestId)
                i = bestEnd
            else:
                # No match found, emit literal character
                result.append(str(text[i]))
                i = i + 1

        return result

    def buildTrie(self, dictionary: List[str]) -> Trie:
        root = Trie()

        for entry in dictionary:
            colonIndex = entry.find(':')
            if colonIndex == -1:
                continue

            key = entry[:colonIndex]
            val = entry[colonIndex + 1:]

            node = root
            for i in range(len(key)):
                c = key[i]
                if c not in node.children:
                    node.children[c] = Trie()
                node = node.children[c]
            # Last wins if duplicate keys
            node.id = val

        return root
```
</details>

*通过率: 37%*

## Design Note-Taking System

### Part 1
Design and implement a note-taking system called `SecondBrainSystem` that manages personal notes with CRUD operations. The system operates entirely in memory and assigns each note a **unique** identifier. Notes are searchable by their identifiers and include metadata that tracks their creation and modification times.

Implement the `SecondBrainSystem` class:

- `SecondBrainSystem()` Initializes an empty note-taking system.

**概要**:
- Design an in-memory note-taking system supporting CRUD operations.
- Enforce unique sequential identifiers and case-insensitive title constraints.
- Track metadata timestamps and format note retrieval as pipe-delimited strings.

**考察点**:
- Hash-based data structures for O(1) lookups and conflict detection
- Object-oriented design and state management
- String manipulation and precise output formatting
- Robust input validation and edge case handling

**常用模式**:
- Hashing

**提示**:
- Consider maintaining two separate hash maps: one for direct ID access and another for tracking normalized titles to efficiently enforce uniqueness.
- Normalize all titles to lowercase before storing them in the uniqueness map, and ensure your sequential ID counter never decrements even if notes are deleted.

**可能的 follow-up**:
- How would you modify this architecture to persist data across application restarts?
- What structural changes would be required to support multiple workspaces or hierarchical folders?
- How would you ensure thread-safety and consistent state in a concurrent, multi-user environment?

### Part 2
Design and implement a note-taking system called `SecondBrainSystem` that manages personal notes with CRUD operations. The system operates entirely in memory and assigns each note a **unique** identifier. Notes are searchable by their identifiers and include metadata that tracks their creation and modification times.

Implement the `SecondBrainSystem` class:

- `SecondBrainSystem()` Initializes an empty note-taking system.

**概要**:
- Extend a note-taking system to dynamically resolve bidirectional references formatted as "[[title]]".
- Parse note content line-by-line to identify valid links that stand alone on their own line.
- Resolve links case-insensitively against current titles, exclude self-references, and return sorted results.

**考察点**:
- Dynamic graph resolution versus static edge maintenance
- Efficient string parsing and pattern matching
- Hash-based indexing for fast lookups
- Data state management across updates and deletions

**常用模式**:
- Hashing
- Sorting

**提示**:
- Maintain a reverse lookup structure that maps lowercase titles directly to their corresponding note IDs for O(1) resolution.
- Split each note's content by newline characters and verify that lines containing "[[" and "]]" contain nothing else before querying your title index.

**可能的 follow-up**:
- How would you optimize incoming link queries if the system scales to millions of notes?
- What structural changes would be needed if inline links (not just whole-line) were supported?
- How could you implement caching or incremental updates to avoid rescanning all notes on every query?

### Part 3
Design and implement a note-taking system called `SecondBrainSystem` that manages personal notes with CRUD operations. The system operates entirely in memory and assigns each note a **unique** identifier. Notes are searchable by their identifiers and include metadata that tracks their creation and modification times.

Implement the `SecondBrainSystem` class:

- `SecondBrainSystem()` Initializes an empty note-taking system.

**概要**:
- Extend a note-taking system with workspaces that enforce maximum capacity limits.
- Track note assignments across workspaces and a default unassigned state efficiently.
- Retrieve workspace contents sorted by creation timestamp and note ID.

**考察点**:
- Hash map and set usage for O(1) lookups and membership tracking
- State management and constraint validation
- Multi-key sorting and query optimization
- Object-oriented class extension

**常用模式**:
- Hashing
- Sorting

**提示**:
- Identify the minimal set of data structures needed to track each note's current workspace and enable fast capacity checks.
- Treat the 'default' state as a special routing case rather than a physical container to simplify capacity and move logic.

**可能的 follow-up**:
- How would you redesign this to support notes belonging to multiple workspaces concurrently?
- What strategies would you use to efficiently query notes across many workspaces without iterating through all of them?
- How would you handle concurrent access or real-time capacity alerts in a production environment?

### Part 4
Design and implement a note-taking system called `SecondBrainSystem` that manages personal notes with CRUD operations. The system operates entirely in memory and assigns each note a **unique** identifier. Notes are searchable by their identifiers and include metadata that tracks their creation and modification times.

Implement the `SecondBrainSystem` class:

- `SecondBrainSystem()` Initializes an empty note-taking system.

**概要**:
- Implement historical state retrieval to query a note's exact content and metadata at any past timestamp.
- Design a merge operation that appends source content to a target, redirects title-based links, and safely removes the source.
- Maintain versioned snapshots and dynamic cross-reference mappings within an object-oriented framework.

**考察点**:
- Object-Oriented Design and State Management
- Versioning and Snapshot History Tracking
- Dynamic Index Maintenance and Link Resolution
- Time-Based Query Processing

**常用模式**:
- Hashing
- Sorting
- Graph Traversal

**提示**:
- Think about storing immutable snapshots of each note's state alongside their creation/update timestamps to enable efficient point-in-time queries.
- For link redirection during a merge, avoid rewriting every note's content; instead, dynamically remap the source's lowercase title to the target's ID in a central index.

**可能的 follow-up**:
- How would you optimize `getNoteAt` if a single note accumulated thousands of updates over its lifetime?
- What edge cases should your `mergeNotes` implementation guard against regarding workspace capacity and concurrent modifications?
- How could you extend this architecture to support non-destructive branching or revert operations?

## Design a Task Assignment System

### Part 1
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Design a class to manage tasks with sequential unique IDs.
- Implement methods to add, update, and retrieve task details.
- Use a hash map for efficient storage and lookup by ID.

**考察点**:
- Hash map implementation for key-value storage.
- Class state management and instance variables.
- Sequential identifier generation.
- Handling missing keys and edge cases.

**常用模式**:
- Hashing
- Design

**提示**:
- Consider which data structure allows for fast retrieval when you only know the unique task ID.
- You'll need a separate integer variable to track the next ID number to assign.
- Store the task details (name, priority) in a simple object or tuple mapped to the ID string within your collection.

**可能的 follow-up**:
- How would you modify the system to support searching tasks by name or priority efficiently?
- If the number of tasks grows to millions, how would you optimize memory usage or persistence?
- How would you ensure thread-safety if multiple threads call these methods simultaneously?
- What changes would be needed to delete tasks or implement soft deletes?

### Part 2
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Design a TaskManager class supporting add, update, search, and sorted listing of tasks.
- Tasks must be sorted by priority descending and creation order ascending, with creation order resolved via numeric ID comparison.
- Search functionality requires case-sensitive substring matching and result limiting.

**考察点**:
- Hash Map usage for efficient task storage and O(1) lookups.
- Custom comparator implementation for multi-criteria sorting.
- String substring search and filtering logic.
- Distinction between numeric ordering and lexicographic string ordering.

**常用模式**:
- Hashing
- Sorting
- Design

**提示**:
- Ensure the sort comparator treats the task ID's creation order as a numeric value to correctly order 'taskId1' before 'taskId10'.
- Use a hash map for direct task access, but recognize that `searchTasks` and `listTasksSorted` will likely require iterating through all entries.
- Handle edge cases explicitly: return empty lists for non-positive limits and treat an empty `nameFilter` as a wildcard matching all tasks.

**可能的 follow-up**:
- How would you optimize `searchTasks` performance if the dataset grows to millions of tasks?
- Can you maintain the tasks in a pre-sorted structure to accelerate `listTasksSorted` without re-sorting?
- How would you extend this design to support concurrent modifications safely?

### Part 3
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Implement user management with constraints on simultaneous active tasks.
- Validate task assignments by detecting interval overlaps and verifying dynamic quota limits.
- Query active tasks for a user within specific time windows.

**考察点**:
- Sweep-line algorithms for interval analysis and peak load detection.
- Hash table design for O(1) user and task lookups.
- Interval clipping and overlap logic.
- Event sorting and tie-breaking rules for half-open intervals.
- State simulation over time ranges.

**常用模式**:
- Sweep-line
- Hashing
- Sorting
- Interval Operations

**提示**:
- To verify the quota, you only need to check the count of active tasks at critical moments defined by interval boundaries, not every integer time point.
- Clip existing assignments to the new request's window and generate events marking where the load increases or decreases.
- Sort these events by time; ensure you process end-of-interval events before start-of-interval events at the same timestamp to correctly handle half-open boundaries during the sweep.

**可能的 follow-up**:
- How would you optimize `assignTask` if a user maintains thousands of assignments?
- Could you replace the linear scan with an Interval Tree or Segment Tree to speed up conflict detection?
- How would you extend this system to support concurrency and thread-safe updates?
- What changes if the timestamp values are extremely large or sparse?

### Part 4
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Implement task completion logic that frees user quotas upon success.
- Track and retrieve overdue assignments based on expiration and completion status.
- Manage complex state transitions for task instances over time.

**考察点**:
- State management and entity lifecycle tracking.
- Interval logic and time-based filtering.
- Efficient lookup using hash maps.
- Resource quota management logic.

**常用模式**:
- Hashing
- Sorting
- Design

**提示**:
- Consider storing assignments in a map keyed by task ID within each user's record to enable direct access rather than scanning all assignments.
- Track completion by recording a `completedAt` timestamp on the assignment object, which effectively shortens its active interval without deleting the record.
- When checking for overdue items, verify that the assignment's `finishTime` is less than or equal to the query timestamp while ensuring the `completedAt` field indicates it was never finished.

**可能的 follow-up**:
- How could you optimize the lookup complexity for `completeTask` from O(K) to O(1)?
- How would you ensure thread-safety in a concurrent implementation?
- What database schema changes would support persistence of this state?

## Design Recipe Management System

### Part 1
Design a digital recipe book that supports creating, reading, updating, and deleting recipes. Each recipe has a unique name, an ordered list of ingredients, and an ordered list of preparation steps.

Implement the `RecipeManager` class:

- `RecipeManager()`
  Initializes an empty recipe store.

- `String addRecipe(String name, List<String> ingredients, List<String> steps)`
  Adds a new recipe. The `name` must be **unique** across all stored recipes (case-insensitive).
  - Returns the assigned `recipeId` (formatted as `"recipe1"`, `"recipe2"`, etc., assigned sequentially starting from `1`). IDs are **never reused** after deletion.
  - Returns an empty string `""` if a recipe with the same `name` already exists (case-insensitive).

**概要**:
- Implement a RecipeManager class supporting Create, Read, Update, and Delete operations.
- Enforce unique recipe names across all entries using case-insensitive comparison.
- Assign sequential, non-reusable recipe IDs starting from 'recipe1'.

**考察点**:
- Hash Map usage for O(1) lookups by ID and name.
- Handling case-insensitive string logic and normalization.
- Managing internal state, counters, and ID lifecycle.
- Designing robust methods with specific edge-case requirements.

**常用模式**:
- Hashing
- Design

**提示**:
- Consider maintaining two hash maps: one for ID-to-recipe storage and another for lowercased-name-to-ID indexing to efficiently check name uniqueness.
- When implementing `updateRecipe`, ensure that renaming a recipe to its own name (even with different casing) does not trigger a conflict error.

**可能的 follow-up**:
- How would you extend this system to search for recipes containing a specific ingredient?
- What changes would you make to make this class thread-safe in a multi-threaded environment?
- If you needed to persist this data to a database, how would you model the schema?

### Part 2
Design a digital recipe book that supports creating, reading, updating, and deleting recipes. Each recipe has a unique name, an ordered list of ingredients, and an ordered list of preparation steps.

Implement the `RecipeManager` class:

- `RecipeManager()`
  Initializes an empty recipe store.

- `String addRecipe(String name, List<String> ingredients, List<String> steps)`
  Adds a new recipe. The `name` must be **unique** across all stored recipes (case-insensitive).
  - Returns the assigned `recipeId` (formatted as `"recipe1"`, `"recipe2"`, etc., assigned sequentially starting from `1`). IDs are **never reused** after deletion.
  - Returns an empty string `""` if a recipe with the same `name` already exists (case-insensitive).

**概要**:
- Implement ingredient search and recipe listing with strict sorting and tie-breaking rules.
- Perform case-insensitive whole-string ingredient matching while excluding deleted recipes.
- Sort results by metric (count/name) with natural numeric ordering for recipe IDs.

**考察点**:
- Custom comparator design for multi-criteria sorting and tie-breaking.
- String manipulation including case normalization and exact substring boundary checks.
- Handling alphanumeric identifiers requiring numeric comparison for correct ordering.
- State management involving filtering out soft-deleted records during queries.

**常用模式**:
- Sorting
- Hashing
- Filtering

**提示**:
- To achieve natural numeric ordering for IDs like 'recipe2' and 'recipe10', extract and compare the integer suffixes rather than comparing strings lexicographically.
- When writing the sort comparator, clearly separate the logic that selects the primary sort attribute from the logic that handles the ID tie-breaker to ensure correctness.

**可能的 follow-up**:
- How would you optimize `searchRecipesByIngredient` using an inverted index for large datasets?
- What are the trade-offs between removing deleted recipes immediately versus filtering them lazily during queries?
- How would you modify the system to support partial matches or wildcard searches for ingredients?

### Part 3
Design a digital recipe book that supports creating, reading, updating, and deleting recipes. Each recipe has a unique name, an ordered list of ingredients, and an ordered list of preparation steps.

Implement the `RecipeManager` class:

- `RecipeManager()`
  Initializes an empty recipe store.

- `String addRecipe(String name, List<String> ingredients, List<String> steps)`
  Adds a new recipe. The `name` must be **unique** across all stored recipes (case-insensitive).
  - Returns the assigned `recipeId` (formatted as `"recipe1"`, `"recipe2"`, etc., assigned sequentially starting from `1`). IDs are **never reused** after deletion.
  - Returns an empty string `""` if a recipe with the same `name` already exists (case-insensitive).

**概要**:
- Extend a recipe management system with user registration and editing capabilities.
- Implement addUser to track unique user IDs and editRecipe to modify recipes safely.
- Enforce case-insensitive name uniqueness across recipes while permitting self-renames.

**考察点**:
- Efficient lookups and duplicate detection using hash collections
- Stateful data structure design and method validation flow
- Case-insensitive string normalization and comparison
- Handling conditional edge cases in API contracts

**常用模式**:
- Hashing

**提示**:
- Store registered user IDs in a hash-based set to achieve constant-time membership verification during edits.
- Maintain a separate lowercase mapping for recipe names to quickly detect conflicts, but explicitly allow updates where the normalized new name matches the existing recipe's normalized name.

**可能的 follow-up**:
- How would you handle race conditions if multiple users attempt to edit the same recipe concurrently?
- What architectural changes would be necessary if recipe names had to be strictly case-sensitive?
- How would you optimize storage and retrieval if the system needed to support millions of recipes?

### Part 4
Design a digital recipe book that supports creating, reading, updating, and deleting recipes. Each recipe has a unique name, an ordered list of ingredients, and an ordered list of preparation steps.

Implement the `RecipeManager` class:

- `RecipeManager()`
  Initializes an empty recipe store.

- `String addRecipe(String name, List<String> ingredients, List<String> steps)`
  Adds a new recipe. The `name` must be **unique** across all stored recipes (case-insensitive).
  - Returns the assigned `recipeId` (formatted as `"recipe1"`, `"recipe2"`, etc., assigned sequentially starting from `1`). IDs are **never reused** after deletion.
  - Returns an empty string `""` if a recipe with the same `name` already exists (case-insensitive).

**概要**:
- Track immutable version snapshots for each recipe whenever it is updated or edited.
- Retrieve a formatted history of all versions sorted ascending by version number.
- Restore a past snapshot while validating name collisions against other active recipes.

**考察点**:
- State management and snapshotting in object-oriented design
- Efficient key-value lookup using hash tables
- Defensive copying to preserve data immutability across versions
- Conflict resolution and boundary condition handling

**常用模式**:
- Hashing
- Sorting

**提示**:
- Store each version as an independent, immutable record rather than computing differences between edits.
- Map each recipe ID to a dynamically appended list of version records, and always deep-copy ingredient and step collections when creating a new snapshot to prevent later mutations from corrupting histo

**可能的 follow-up**:
- How would you reduce memory consumption if a single recipe accumulates tens of thousands of versions?
- Could you replace the sequential list of versions with a tree-based structure to improve random-access performance?
- How would you extend this design to support concurrent edits without requiring locks or causing race conditions?

## Design Durable Function Call Cache

### Part 1
A common optimization technique in data pipelines is **memoization**: wrapping an expensive function so repeated calls with the same inputs can return a cached result instead of recomputing it.

You are given a partially implemented `FunctionCallCache` class that wraps arbitrary functions and stores their return values in an *LRU (Least Recently Used) cache*. The provided skeleton already handles cache lookup, cache insertion, cache hits, cache misses, and LRU eviction. The only missing piece is `create_cache_key`, which must generate a deterministic, hashable key for each function call.

**概要**:
- Implement a method to generate deterministic cache keys for function calls.
- Normalize keyword argument order so equivalent calls produce identical keys.
- Serialize structured inputs into a hashable format supporting nested data.

**考察点**:
- Canonical data representation and normalization
- Hashable key generation strategies
- Handling unordered data structures
- Serialization of JSON-serializable objects

**常用模式**:
- Hashing
- Sorting
- Serialization

**提示**:
- Keyword arguments represent the same data regardless of insertion order; sorting their keys creates a consistent view.
- Apply normalization recursively to nested dictionaries within arguments to ensure deep equality matches.
- Construct the final key by combining the function name, normalized kwargs, and args into an immutable container or string.

**可能的 follow-up**:
- How would you handle arguments that are not JSON-serializable, such as custom class instances?
- Discuss the trade-offs between using a serialized string versus a tuple of values for cache keys.
- How would you extend this design to support caching based on function signatures or source code changes?
- What considerations arise regarding thread safety when accessing the cache?

### Part 2
A common optimization technique in data pipelines is **memoization**: wrapping an expensive function so repeated calls with the same inputs can return a cached result instead of recomputing it.

You are given a partially implemented `FunctionCallCache` class that wraps arbitrary functions and stores their return values in an *LRU (Least Recently Used) cache*. The provided skeleton already handles cache lookup, cache insertion, cache hits, cache misses, and LRU eviction. The only missing piece is `create_cache_key`, which must generate a deterministic, hashable key for each function call.

**概要**:
- Maintain an append-only log of cache operations to ensure crash recovery.
- Replay persisted records sequentially to reconstruct both cached values and LRU ordering.
- Gracefully ignore trailing corrupted data without interrupting system startup.

**考察点**:
- State persistence and crash recovery
- Efficient I/O and append-only logging
- LRU cache mechanics with dynamic reordering
- Fault-tolerant data deserialization

**常用模式**:
- Hashing

**提示**:
- Instead of persisting the entire cache structure, record only individual key-value updates as they occur.
- When replaying history, standard LRU implementations often fail to update positions of existing keys; you may need to explicitly delete and re-insert them to enforce correct recency.
- Wrap your parsing logic in error handling to safely skip malformed or truncated log entries at the end of the file.

**可能的 follow-up**:
- How would you design this to support concurrent access from multiple processes?
- What modifications would allow batched writes to reduce disk I/O overhead?
- Can you optimize recovery time by maintaining a secondary index or checkpoint file?
- How would you handle very large cache states where the log grows indefinitely?

## Repair Bootloader Program

### Part 1
A [bootloader](https://en.wikipedia.org/wiki/Bootloader) stores its program as an array of text instructions, and you need to find where the execution first starts repeating.

You are given `instructions`, where each entry has the form `"<operation> <value>"`. The operation is one of `"plus"`, `"next"`, or `"jump"`.

- `"plus x"` adds `x` to a global accumulator, then moves to the next instruction.
- `next x` leaves the accumulator unchanged and moves to the next instruction. The value `x` is preserved in the instruction format but is **ignored** and not used in this question. 
- `"jump x"` leaves the accumulator unchanged, then moves to the instruction at the current index plus `x`.

**概要**:
- Simulate a simple instruction sequence starting from index zero.
- Track executed instruction indices to identify when execution revisits a previous step.
- Return the index of the first repeated instruction, or -1 if the program terminates normally.

**考察点**:
- Program simulation and state management
- Cycle detection in deterministic sequences
- Efficient lookup structures for visited states
- Control flow manipulation via program counter

**常用模式**:
- Simulation
- Hashing

**提示**:
- Maintain a record of every instruction index you visit during the simulation.
- Check for repetition immediately before executing the current instruction rather than after.
- Use a boolean array or hash set to achieve O(1) lookups for visited indices, ensuring overall O(N) runtime.

**可能的 follow-up**:
- How would you adapt this approach if the instruction set included conditional jumps?
- Can you reduce the space complexity while still detecting the cycle efficiently?
- What happens if the jump offset causes the program counter to go out of bounds?
- How does this problem conceptually map to cycle detection in a functional graph?

### Part 2
A [bootloader](https://en.wikipedia.org/wiki/Bootloader) stores its program as an array of text instructions, and you need to find where the execution first starts repeating.

You are given `instructions`, where each entry has the form `"<operation> <value>"`. The operation is one of `"plus"`, `"next"`, or `"jump"`.

- `"plus x"` adds `x` to a global accumulator, then moves to the next instruction.
- `next x` leaves the accumulator unchanged and moves to the next instruction. The value `x` is preserved in the instruction format but is **ignored** and not used in this question. 
- `"jump x"` leaves the accumulator unchanged, then moves to the instruction at the current index plus `x`.

**概要**:
- Simulate a simple bootloader program that may contain exactly one invalid branch instruction.
- Identify and flip at most one jump or next instruction to guarantee normal termination.
- Return the final accumulator value after applying the minimal necessary correction.

**考察点**:
- Graph reachability and cycle detection in execution traces
- State machine simulation with controlled modifications
- Reverse traversal to precompute termination paths
- Efficient validation of candidate corrections

**常用模式**:
- Graph Traversal
- DFS/BFS

**提示**:
- Model each instruction as a node in a directed graph where edges represent control flow; a non-terminating run indicates a cycle.
- Instead of testing every possible flip, simulate the original execution path and focus only on branch instructions encountered during that run.
- Precompute which nodes can reach the terminal state by traversing backward from the end, enabling O(1) validation of whether flipping a specific instruction fixes the loop.

**可能的 follow-up**:
- How would you adapt this approach if multiple instructions could potentially be flipped?
- Can the reverse graph be avoided by using only forward simulation and visited tracking?
- What is the time and space trade-off if we validate each potential flip independently?
- How would you handle cases where the program terminates immediately without any jumps?
