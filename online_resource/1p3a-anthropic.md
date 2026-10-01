# Anthropic 面试题库 · 一亩三分地会员版（完整）

> 2026-07 从 `interview/problems/company/anthropic` 抓取。已尽量用解锁工具取正文；取不到的给出原帖 URL 供手动查看。
> 原始 HTML 在 raw/1p3a_html/。


# 一、面试情报 Briefings（会员版正文）

## Loop Structure & Timeline

## Pipeline

A typical Anthropic loop runs:

1. **Recruiter screen** (~30 min). Either a referral handoff or a cold reachout. Why-Anthropic and AI-safety screening start here.
2. **Phone screen — coding** (55 min). One prompt from the Coding Q1–Q6 catalog. Recruiter emails the prompt blurb a few days before; matching the blurb to a Q-number is half the prep.
3. **Onsite loop** — five rounds, usually spread across two consecutive days:
   - Coding (a different Q than the phone)
   - System Design (Q1–Q5)
   - Project Deep-Dive (20–25 min presentation + Q&A)
   - Hiring Manager / Behavioral
   - Culture / AI-Safety
4. **Hiring Committee** review.
5. **Reference check** — Anthropic asks for **two coworker references** (typically one manager, one peer/senior IC). This happens *before* the offer and the package is finalized post-HC.

## Calendar time

A fast path goes recruiter → onsite in ~10 days; the full loop including HC and references commonly closes in 3–5 weeks. Some candidates wait 1–2 weeks for a verdict after onsite with no interim signal.

## Common variants

- **Research Engineer / Scientist & Fellows**: replace the standard coding phone screen with a 4-of-N or 6-of-N self-select menu (Coding & Design, ML Programming, ML Configuration System, RL Fundamentals, Prompting/Engineering with LLMs, ML Take-Home).
- **Performance Engineer**: no phone-coding screen — a 2-hour take-home kernel optimization gates straight into the onsite, which adds a Performance Modeling round.
- **EM / managers**: swap one technical round for a Design Doc Review and one for Execution & Leadership; the Culture and Project Deep-Dive rounds stay.
- **AI Safety Fellow**: CodeSignal OA → 5-hour in-home PyTorch assessment with live review.
- **Senior / Staff via strong referral**: the loop can skip the OA and phone screen entirely — recruiter call → a first-round hiring-manager conversation → onsite. That onsite can run five rounds (1 coding, 2 system design, 1 technical project discussion, 1 culture) spread across three days, and the culture round is sometimes run by a non-engineer.

## Tooling & screen-share

Throughout every technical round you are expected to share your screen. Looking things up in language docs or on the web is explicitly permitted — interviewers want to see how you research, not whether you've memorized standard libraries. AI assistants (Copilot, Claude, ChatGPT) are *not* allowed; they're the line everyone watches for. Stay fluent enough in basic syntax and idioms that you don't burn the round on lookups.

## Pre-round recruiter blurb

A defining feature of the Anthropic loop is that the recruiter emails a short paragraph **before** each technical round describing what the upcoming prompt looks like — without naming the specific question. Two examples of the genre:

> "Q is about familiarity with handling concurrency, ability to evaluate tradeoffs between threads, processes, and async, and IO-bound vs CPU-bound reasoning."

> "Q is a standard algorithmic-style round in Google Colab; the interviewer will ask you to write code that compiles and runs, and to iterate based on test failures."

The blurb is the single most useful prep signal Anthropic gives candidates. Map the blurb to a prompt family before the round (the families and their blurbs are documented in the Coding Q & SD Q Portal briefing), and structure your warm-up around the specific data structures and tradeoffs the blurb foreshadows. Candidates who arrive having drilled the blurb-matched family typically clear the round; candidates who treat the blurb as boilerplate often realize mid-round that they could have prepared more narrowly.

## Verdict signals

- Verdicts are usually delivered by email with little to no feedback ("touch design, cannot provide more details"). The no-feedback rule is a stated policy, not an oversight — do not write back asking for resume or round-level critique. Even all-hire loops can end without an offer if no team match exists.
- Reaching reference check does **not** guarantee an offer — HC can still reject after references come back.

## Two-day VO split

Recent candidates report the five rounds frequently split as **day 1 = coding + system design (both Q1-style), day 2 = three non-technical rounds (HM, Project Deep-Dive, Culture)**. A poor day-1 performance can lead to day 2 being cancelled outright, so the technical bar is largely set in the first 24 hours.

来源帖: [Anthropic VO](https://www.1point3acres.com/bbs/thread-1176508-1-1.html) · [人类学昂赛](https://www.1point3acres.com/bbs/thread-1176924-1-1.html) · [Anthropic Onsite 全套](https://www.1point3acres.com/bbs/thread-1180552-1-1.html)

## The Coding Q1–Q6 Portal (and the SD Q1–Q5 Portal)




## Culture Round & AI-Safety Alignment




## Tooling, Languages & AI Usage Rules




## Leveling, Reference Check & Team Match




## AI Safety Fellow & Research Intern Tracks





# 二、外链帖题解（解锁工具编辑版）

## Design a 1-to-1 Chat System

### Design a 1-to-1 Chat System

Design a chat system that supports **only 1-to-1 messaging** between users. Group chats, channels, and other multi-party features are not included.

Interviewers often ask deep questions about how things work under the hood. Do not just guess. You must explain the "how" behind the "what." If you suggest WebSockets, be ready to explain how connections stay open. If you talk about message order, be ready to explain how time works in distributed systems.

**Disclaimer:** This is a sample solution. To prepare best, try to solve the problem yourself first. System design questions are open-ended, and there are many right answers.

## Phase 1: Define the Goals (~5 minutes)

A 1-to-1 chat system is smaller than WhatsApp or Slack. We need to define exactly what to build so we don't waste time on features we don't need.

### User Features

Describe these as things the user can do:

- **Send messages:** Users can send text to another user.
- **Receive messages:** Users get messages almost instantly if they are online.
- **Conversation history:** Users can see old messages.
- **Read receipts:** The sender knows when the other person has read the message.
- **Offline delivery:** If a user is offline, the message waits until they come back online.
Stick to these 4-5 main features. We do not need group admins or channels.

### Technical Requirements

| Requirement | Target | Reason |
| --- | --- | --- |
| **Scale** | 100M DAU, 1B messages/day | A medium-sized system. |
| **Latency** | < 500ms delivery | Needs to feel instant. |
| **Availability** | 99.9%+ | Users expect chat to always work. |
| **Ordering** | Strict order | "Hello" then "How are you?" must not swap. |
| **Durability** | No data loss | We must never lose a sent message. |

**Key Questions to Ask:**

- "What matters more: availability (always working) or consistency (perfect order)?" — *Answer:* Messages must be in order, even if it takes a tiny bit longer.
- "How long do we keep messages?" — *Answer:* Forever (unless we change it for privacy).
- "Do users have multiple devices?" — *Answer:* Yes, a user might use a phone and a laptop.

### Math & Estimations

Let's do some quick math to see how big our servers need to be:

```python
Users:
- Daily Active Users (DAU): 100 million
- Messages per user per day: 10
- Total messages per day: 1 billion

Traffic Load:
- Average messages per second: 1B / 86,400 ≈ 11,500 QPS
- Peak time (busy hours): ~35,000 QPS

Connections:
- Users online at the same time: 10% of DAU = 10M WebSocket connections

Storage:
- Size of one message: 200 bytes
- Storage per day: 200 GB
- Storage per year: ~73 TB
```

With 35,000 QPS and 10 million open connections, we need a distributed system. One server is not enough. We need many servers working together.

## Phase 2: Database Schema & Entities (~5 minutes)

Before we build APIs, let's decide how to store the data.

### Core Data Structures

```python
User
├── user_id (UUID)
├── username
├── email
├── last_seen_at
└── created_at

Device (To handle phone + laptop)
├── device_id (UUID)
├── user_id
├── device_type (phone, desktop, web)
├── push_token (for notifications)
└── last_active_at

Conversation
├── conversation_id (UUID)
├── participant_1 (user_id)
├── participant_2 (user_id)
├── created_at
└── updated_at (time of last message)
-- Rule: participant_1 is always the smaller ID than participant_2
-- Unique index on (participant_1, participant_2)

Message
├── message_id (UUID)
├── conversation_id
├── sender_id
├── client_message_id (string, unique ID from the phone)
├── content (text)
├── sequence_number (1, 2, 3... per conversation)
└── created_at

MessageStatus (Tracks delivery per device)
├── message_id
├── device_id
├── status (sent, delivered)
└── updated_at
-- Primary key: (message_id, device_id)
```

**Canonical Ordering:** This is a trick to handle 1-to-1 chats. Always store the smaller User ID as `participant_1`. This means "Chat between User A and User B" is the exact same row as "Chat between User B and User A". You can find it with one search.

### Key Decisions

**1. Using Sequence Numbers**

Do not use only timestamps to order messages. Computers have different clocks (clock skew). Instead, use a simple number (1, 2, 3...) for each conversation.

```python
def get_or_create_conversation(user_a, user_b):
    # Sort IDs so we always look up the same pair
    p1, p2 = min(user_a, user_b), max(user_a, user_b)
    return db.upsert(participant_1=p1, participant_2=p2)
```

**2. Tracking Message Status**

We track two different things:

- **Delivered:** This is tracked per **device**. Each phone or laptop says "I got it."
- **Read:** This is tracked per **user**. We save a `last_read_sequence_number`. If the user reads message #50, we know they also read #1 through #49.

## Phase 3: How Client and Server Talk (~5 minutes)

We need **bidirectional** communication (two-way talking). The server must be able to push a message to the client without the client asking for it.

### Why WebSockets?

| Protocol | How it works | Best For |
| --- | --- | --- |
| **HTTP** | Client asks, Server answers | Loading web pages |
| **WebSocket** | Connection stays open | Chat, Games |
| **Server-Sent Events** | Server talks, Client listens | News Tickers |

For chat, both sides talk. WebSockets are the best choice because they keep a single line open.

### JSON Commands

**Client sends to Server:**

```json
// Send a message
{
  "action": "send_message",
  "conversation_id": "conv_123",
  "content": "Hello!",
  "client_message_id": "local_456"  // Unique ID to prevent duplicates
}

// Tell server I read messages
{
  "action": "read_receipt",
  "conversation_id": "conv_123",
  "last_read_sequence": 42
}

// Keep connection alive
{ "action": "ping" }
```

**Server sends to Client:**

```json
// Incoming message
{
  "event": "new_message",
  "message_id": "msg_789",
  "conversation_id": "conv_123",
  "sender_id": "user_456",
  "content": "Hello!",
  "sequence_number": 42,
  "timestamp": "2024-01-15T10:30:00Z"
}

// Confirm message reached the other person
{
  "event": "delivered",
  "message_id": "msg_789",
  "conversation_id": "conv_123",
  "timestamp": "2024-01-15T10:30:01Z"
}

// Other person read your message
{
  "event": "read",
  "conversation_id": "conv_123",
  "reader_id": "user_456",
  "last_read_sequence": 42
}
```

**Note on `client_message_id`:** This is for **Idempotency**. If the internet cuts out while sending, the app might retry sending the same message. The server checks this ID. If it has seen it before, it ignores the duplicate.

### Standard HTTP API (REST)

Some things don't need WebSockets. We can use standard HTTP for them:

```http
// Load list of chats
GET /conversations?cursor=...&limit=20

// Load old messages (scrolling up)
GET /conversations/{id}/messages?before_sequence=12345&limit=50

// Start talking to someone new
POST /conversations
Request: { "recipient_user_id": "..." }
```

## Phase 4: System Architecture (~15-25 minutes)

This is the main part of the interview. We need to draw how the pieces fit together.

### The Components

| Component | Job |
| --- | --- |
| **Load Balancer (L4)** | Spreads incoming connections to different servers. |
| **WebSocket Servers** | Holds the open connection to the user's phone/laptop. |
| **Message Service** | The brain. Handles logic, saves messages, assigns numbers. |
| **PostgreSQL** | Long-term storage for all data. |
| **Redis Cluster** | Fast memory storage. Used for routing messages and temporary queues. |

### Life of a Message (The Flow)

Imagine User A sends a message to User B:

- User A sends the message to their **WebSocket Server**.
- The server passes it to the **Message Service**.
- The service saves the message in **PostgreSQL** and gives it a sequence number.
- The service publishes the message to **Redis Pub/Sub**.
- User B's WebSocket Server receives the notification from Redis.
- User B's server pushes the message to User B's phone.
- User B's phone sends an "ACK" (acknowledgment) saying "I got it."
We use an **in-flight queue**. We put the message in a temporary list. We only remove it once the user confirms they received it. This makes sure messages don't get lost.

### The Routing Problem

We have many WebSocket servers. Server 1 has User A. Server 2 has User B. How does Server 1 send data to Server 2?

**Solution: Pub/Sub (Publish/Subscribe)**

We use Redis Pub/Sub. Every WebSocket server "subscribes" to the users connected to it.

- When User B connects to Server 2, Server 2 subscribes to channel `user:B`.
- To send to User B, we just "publish" the message to channel `user:B`.
- Redis ensures Server 2 gets that data. Server 2 then sends it to the real user.
This is better than keeping a giant list of "Who is on which server" because lists get messy if servers crash.

### Handling Offline Users

If User B is offline:

- The message stays in the database (Inbox).
- It sits in a pending queue.
- When User B comes online, they ask the server: "What is the last message I have?"
- The server sends everything that came after that number.

### Detailed Database SQL

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    last_seen_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Devices table (for multiple logins)
CREATE TABLE devices (
    device_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users,
    device_type VARCHAR(20) NOT NULL,
    push_token VARCHAR(255),
    last_active_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    participant_1 UUID NOT NULL REFERENCES users,
    participant_2 UUID NOT NULL REFERENCES users,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Enforce canonical ordering
    CONSTRAINT participant_order CHECK (participant_1 < participant_2),
    UNIQUE (participant_1, participant_2)
);

-- Messages
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations,
    sender_id UUID NOT NULL REFERENCES users,
    client_message_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    sequence_number BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (conversation_id, sequence_number),
    UNIQUE (conversation_id, sender_id, client_message_id)
);

-- Tracking if a message reached a device
CREATE TABLE message_status (
    message_id UUID NOT NULL REFERENCES messages,
    device_id UUID NOT NULL REFERENCES devices,
    status VARCHAR(20) NOT NULL DEFAULT 'sent',
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (message_id, device_id)
);

-- Read Receipts (The highest number read)
CREATE TABLE read_receipts (
    user_id UUID NOT NULL REFERENCES users,
    conversation_id UUID NOT NULL REFERENCES conversations,
    last_read_sequence BIGINT NOT NULL DEFAULT 0,
    last_read_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, conversation_id)
);
```

### Sharding (Splitting Data)

We have too much data for one database. We need to split it (Shard).

We shard by **`conversation_id`**.

- All messages for Chat 123 go to Database A.
- All messages for Chat 456 go to Database B.
This makes loading chat history very fast because all messages for one chat are in the same place.

## Phase 5: Handling Scale & Challenges (~15-20 minutes)

Now we look at the hard problems.

### Problem 1: Message Ordering

How do we make sure User A and User B see messages in the exact same order?

**Solution: Redis INCR**

We use Redis to generate the sequence numbers (1, 2, 3). Redis is single-threaded and very fast.

```python
def send_message(conversation_id, sender_id, content, client_message_id):
    # 1. Get the next number from Redis
    seq = redis.incr(f"seq:{conversation_id}")

    # 2. Save to DB with that number
    message = db.execute("""
        INSERT INTO messages (conversation_id, sequence_number, ...)
        VALUES ($1, $2, ...)
    """, conversation_id, seq, ...)

    return message
```

This is fast. The downside: If the database insert fails, we might have a gap in numbers (1, 2, 4). The client needs logic to handle gaps or request missing items.

### Problem 2: Read Receipts (Too Many Writes)

If a user scrolls through a chat, they might "read" 100 messages in a second. We do not want to update the database 100 times.

**Solution: Debouncing**
Wait a few seconds before sending the update.

```javascript
// Client-side code
let pendingReadReceipt = null;
let timer = null;

function onMessageViewed(sequenceNumber) {
    pendingReadReceipt = sequenceNumber;
    clearTimeout(timer);
    // Wait 2 seconds before sending to server
    timer = setTimeout(() => {
        sendReadReceipt(pendingReadReceipt);
    }, 2000);
}
```

The server only updates if the new number is higher than the old number.

### Problem 3: Multi-Device Sync

The user has a phone and a laptop. Both need the message.

**Solution: Fan-out**
When sending a message to User B:

- Look up User B's devices in the `devices` table.
- Add the message to the Inbox of **every** device.
- Each device must reply "I got it" independently.
- If the user reads a message on the phone, the phone updates `read_receipts`. When the laptop syncs later, it sees the new "last read" number and updates its UI.

### Trade-offs

**Consistency vs. Availability:**
We choose **Consistency** for a single conversation. It is confusing if messages appear out of order. We accept a small delay to ensure order.

**Latency vs. Durability:**
We choose **Durability**. We must write the message to the hard drive (PostgreSQL) *before* we tell the sender "Sent." This adds milliseconds of latency, but ensures we don't lose data if the server crashes.

## Final Review Checklist

Before finishing, check that you covered these points:

**The Basics**

- [ ] Did you confirm it is 1-to-1 only?
- [ ] Did you list the 4-5 main features?
- [ ] Did you do the math for scale?
**Data & API**

- [ ] Did you explain the database tables?
- [ ] Did you explain why you use sequence numbers (not just time)?
- [ ] Did you choose WebSockets?
**Architecture**

- [ ] Did you draw the diagram?
- [ ] Did you explain Pub/Sub for routing?
- [ ] Did you explain how offline messages work?
**Deep Dives**

- [ ] Did you solve the message ordering problem?
- [ ] Did you solve the "too many read receipts" problem?
- [ ] Did you mention multi-device support?

## Quick Summary Table

| Feature | Solution | Why? |
| --- | --- | --- |
| **Connection** | WebSocket | Real-time, two-way talking. |
| **Routing** | Redis Pub/Sub | Easy to scale, handles server crashes. |
| **Storage** | PostgreSQL (Sharded) | Reliable, safe, good for structured data. |
| **Ordering** | Redis INCR | Fast atomic counters. |
| **Offline** | Inbox + In-flight queue | Ensures messages wait for the user. |
| **Read Status** | High-water mark | Efficient (just store the last number read). |
| **Presence** | Redis Heartbeat | Fast way to check who is online. |

This design is simpler than WhatsApp because there are no groups. However, you must focus deeply on **ordering** and **delivery guarantees**. That is where the difficulty lies.

*原帖: https://www.1point3acres.com/interview/thread/7100098*

---

## Task Management System (Online Assessment)

### Task Management System (Interview Problem)

## Problem Summary

You need to build a task management system. There are **4 levels**. Each level gets harder and adds new features:

- **Level 1**: Build basic functions to add, update, and read tasks.
- **Level 2**: Add features to search and sort tasks.
- **Level 3**: Add users. Assign tasks to users with time limits and quotas.
- **Level 4**: Allow users to finish tasks. Find tasks that were not finished on time.
You must solve the current level to move to the next one.

- **Priority** and **Quota** are always positive numbers (or zero).
- **Timestamp** and **Finish Time** are seconds since the system started.
- Time always moves forward. New operations will always have a higher timestamp.

## Level 1: Basics

### Requirement

Create a system to add new tasks, update them, and view their details.

### Operations

#### `addTask(timestamp, name, priority)` → `String`

- Creates a new task.
- Returns a unique ID like `"task_id_1"`, `"task_id_2"`, etc.
- IDs are created in order (1, 2, 3...).
- You can have multiple tasks with the same name. They will have different IDs.
- Ignore the `timestamp` for the logic in Level 1.

#### `updateTask(timestamp, taskId, name, priority)` → `boolean`

- Changes the name and priority of a specific task.
- Returns `true` if successful.
- Returns `false` if the `taskId` is not found.

#### `getTask(timestamp, taskId)` → `Optional<String>`

- Returns a string with task details in **JSON format**.
- Returns `Optional.empty()` if the task is not found.
- **Format Rules:**

Do not put spaces between keys and values.
- Keep spaces that are inside the name string.
- Order: first `name`, then `priority`.

### Level 1 Examples

| Queries | Explanations |
| --- | --- |
| `addTask(1, "Task 1", 5)` | Returns `"task_id_1"` |
| `addTask(2, "Task 1", 5)` | Returns `"task_id_2"`. Same name allowed. |
| `updateTask(3, "task_id_1", "Updated Task 1", 4)` | Returns `true`. Updates the first task. |
| `getTask(4, "task_id_1")` | Returns `'{"name":"Updated Task 1","priority":4}'`. No extra spaces. |
| `getTask(5, "task_id_3")` | Returns `Optional.empty()`. Task does not exist. |
| `updateTask(6, "task_id_3", "Non-existing Task", 1)` | Returns `false`. Task does not exist. |

### Level 1 Code

```python
from typing import Optional

class Task:
    def __init__(self, task_id: str, name: str, priority: int):
        self.task_id = task_id
        self.name = name
        self.priority = priority

class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_counter += 1
        task_id = f"task_id_{self.task_counter}"
        self.tasks[task_id] = Task(task_id, name, priority)
        return task_id

    def update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool:
        if task_id not in self.tasks:
            return False
        self.tasks[task_id].name = name
        self.tasks[task_id].priority = priority
        return True

    def get_task(self, timestamp: int, task_id: str) -> Optional[str]:
        if task_id not in self.tasks:
            return None
        task = self.tasks[task_id]
        return f'{{"name":"{task.name}","priority":{task.priority}}}'
```

## Level 2: Search & Sort

### Requirement

Add tools to find tasks and list them in a specific order.

### New Operations

#### `searchTasks(timestamp, nameFilter, maxResults)` → `List<String>`

- Finds tasks where the name contains the `nameFilter`.
- Returns a list of task IDs (up to `maxResults`).
- **Sorting Rules:**

First, by **priority** (High to Low).
- If priorities are equal, sort by **creation order** (Low IDs first).
- If `maxResults` is 0 or less, return an empty list.

#### `listTasksSorted(timestamp, limit)` → `List<String>`

- Lists all task IDs up to the `limit`.
- Uses the same sorting rules as search: **priority (High -> Low)**, then **creation order**.

### Level 2 Examples

| Queries | Explanations |
| --- | --- |
| `addTask(1, "Alpha", 10)` | Returns `"task_id_1"` |
| `addTask(2, "Bravo", 15)` | Returns `"task_id_2"` |
| `addTask(3, "Bravo Alpha", 5)` | Returns `"task_id_3"` |
| `listTasksSorted(4, 2)` | Returns `["task_id_2", "task_id_1"]`. Sorts by priority. |
| `searchTasks(5, "Bra", 5)` | Returns `["task_id_2", "task_id_3"]`. Matches "Bravo". |
| `updateTask(6, "task_id_1", "Alpha Updated", 20)` | Returns `true`. Priority is now 20. |
| `searchTasks(7, "Al", 1)` | Returns `["task_id_1"]`. "Alpha Updated" is now highest priority. |

### Level 2 Code

Add these methods to the previous code:

```python
class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0
        self.creation_order: dict[str, int] = {}  # Maps task_id to creation number

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_counter += 1
        task_id = f"task_id_{self.task_counter}"
        self.tasks[task_id] = Task(task_id, name, priority)
        self.creation_order[task_id] = self.task_counter
        return task_id

    # ... Include Level 1 methods here ...

    def search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]:
        if max_results <= 0:
            return []

        matching = [
            task_id for task_id, task in self.tasks.items()
            if name_filter in task.name
        ]

        # Sort: Priority Descending (-), then Creation Order Ascending (+)
        matching.sort(key=lambda tid: (-self.tasks[tid].priority, self.creation_order[tid]))

        return matching[:max_results]

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        if limit <= 0:
            return []

        task_ids = list(self.tasks.keys())
        task_ids.sort(key=lambda tid: (-self.tasks[tid].priority, self.creation_order[tid]))

        return task_ids[:limit]
```

## Level 3: Users & Assignments

### Requirement

Add users to the system. Users have a limit on how many tasks they can do at once (quota). Tasks are assigned for a specific time period.

### New Operations

#### `addUser(timestamp, userId, quota)` → `boolean`

- Adds a user with a specific task limit (`quota`).
- Returns `true` if successful.
- Returns `false` if the user ID already exists.

#### `assignTask(timestamp, taskId, userId, finishTime)` → `boolean`

- Assigns a task to a user from `timestamp` until `finishTime`.
- **Quota Rule:** Each active task uses 1 quota slot.
- Returns `false` if:

Task or User doesn't exist.
- User has reached their quota limit at this moment.
- When `timestamp` reaches `finishTime`, the task expires and the quota slot is freed automatically.
- You can assign the same task multiple times. Each assignment is separate.

#### `getUserTasks(timestamp, userId)` → `List<String>`

- Gets a list of IDs for tasks currently assigned to the user.
- A task is "active" if: `start_time <= timestamp < finish_time`.
- **Sorting:** Sort by `finish_time` (soonest first). Tie-break with assignment time.

### Level 3 Examples

| Queries | Explanations |
| --- | --- |
| `addUser(1, "user1", 2)` | Returns `true`. Quota is 2. |
| `addUser(2, "user1", 3)` | Returns `false`. User exists. |
| `addTask(3, "Task A", 10)` | Returns `"task_id_1"` |
| `addTask(4, "Task B", 5)` | Returns `"task_id_2"` |
| `assignTask(5, "task_id_1", "user1", 15)` | Returns `true`. Assigned until time 15. |
| `getUserTasks(6, "user1")` | Returns `["task_id_1"]` |
| `assignTask(7, "task_id_2", "user1", 20)` | Returns `true`. Assigned until time 20. |
| `getUserTasks(8, "user1")` | Returns `["task_id_1", "task_id_2"]`. |
| `assignTask(9, "task_id_1", "user1", 25)` | Returns `false`. Quota full (2 active tasks). |
| `getUserTasks(16, "user1")` | Returns `["task_id_2"]`. Task 1 expired at 15. |
| `getUserTasks(21, "user1")` | Returns `[]`. Both tasks expired. |

### Level 3 Code

```python
from dataclasses import dataclass

@dataclass
class Assignment:
    task_id: str
    user_id: str
    start_time: int
    finish_time: int
    completed: bool = False

class User:
    def __init__(self, user_id: str, quota: int):
        self.user_id = user_id
        self.quota = quota
        self.assignments: list[Assignment] = []

class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0
        self.creation_order: dict[str, int] = {}
        self.users: dict[str, User] = {}

    # ... Include Level 1 & 2 methods here ...

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, quota)
        return True

    def _get_active_assignment_count(self, user: User, timestamp: int) -> int:
        """Count how many assignments are active right now."""
        return sum(
            1 for a in user.assignments
            if a.start_time <= timestamp < a.finish_time and not a.completed
        )

    def assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool:
        if task_id not in self.tasks or user_id not in self.users:
            return False

        user = self.users[user_id]

        # Check if user has space in their quota
        active_count = self._get_active_assignment_count(user, timestamp)
        if active_count >= user.quota:
            return False

        # Add new assignment
        assignment = Assignment(task_id, user_id, timestamp, finish_time)
        user.assignments.append(assignment)
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        active = [
            a for a in user.assignments
            if a.start_time <= timestamp < a.finish_time and not a.completed
        ]

        # Sort by finish_time, then start_time
        active.sort(key=lambda a: (a.finish_time, a.start_time))

        return [a.task_id for a in active]
```

## Level 4: Completion & History

### Requirement

Allow users to finish tasks. You also need to report which tasks were ignored (expired without being finished).

### New Operations

#### `completeTask(timestamp, taskId, userId)` → `boolean`

- Marks a task as done.
- The task must be active right now.
- Frees up one quota slot immediately.
- **Constraint:** If the user has the same task assigned multiple times, complete the one that started earliest.
- Returns `false` if the task is not assigned to this user at this time.

#### `getOverdueAssignments(timestamp, userId)` → `List<String>`

- Lists tasks that expired in the past without being completed.
- "Overdue" means `finish_time <= timestamp` AND the task was never finished.
- **Sorting:** Sort by `finish_time` (oldest expiry first).
- If a task expired multiple times, list it multiple times.

### Level 4 Examples

| Queries | Explanations |
| --- | --- |
| `assignTask(6, "task_id_1", "user1", 15)` | Assignment active [6, 15). |
| `completeTask(10, "task_id_1", "user1")` | Returns `true`. Task done. Quota freed. |
| `getUserTasks(11, "user1")` | Returns `[]`. No active tasks. |
| `getOverdueAssignments(18, "user1")` | Returns `[]`. Task 1 was finished, so it is not overdue. |
| `assignTask(13, "task_id_3", "user1", 25)` | Assignment active [13, 25). |
| `getOverdueAssignments(30, "user1")` | Returns `["task_id_3"]`. It expired at 25 without completion. |
| `assignTask(35, "task_id_1", "user1", 45)` | Re-assign Task 1. |
| `assignTask(40, "task_id_1", "user1", 55)` | Re-assign Task 1 again. Overlapping. |
| `completeTask(43, "task_id_1", "user1")` | Completes the first one (started at 35). |
| `getUserTasks(44, "user1")` | Returns `["task_id_1"]`. The second one is still active. |

### Level 4 Code

Update the completion and overdue logic:

```python
class TaskManagementSystem:
    # ... Level 1-3 methods ...

    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        if task_id not in self.tasks or user_id not in self.users:
            return False

        user = self.users[user_id]

        # Find active assignments for this task
        active_assignments = [
            a for a in user.assignments
            if a.task_id == task_id
            and a.start_time <= timestamp < a.finish_time
            and not a.completed
        ]

        if not active_assignments:
            return False

        # Complete the earliest one
        active_assignments.sort(key=lambda a: a.start_time)
        active_assignments[0].completed = True
        return True

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        if user_id not in self.users:
            return []

        user = self.users[user_id]

        # Find assignments that expired and were not finished
        overdue = [
            a for a in user.assignments
            if a.finish_time <= timestamp and not a.completed
        ]

        # Sort by finish_time, then start_time
        overdue.sort(key=lambda a: (a.finish_time, a.start_time))

        return [a.task_id for a in overdue]
```

## Full Solution Code

Here is the complete code with all features combined:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class Assignment:
    task_id: str
    user_id: str
    start_time: int
    finish_time: int
    completed: bool = False

class Task:
    def __init__(self, task_id: str, name: str, priority: int):
        self.task_id = task_id
        self.name = name
        self.priority = priority

class User:
    def __init__(self, user_id: str, quota: int):
        self.user_id = user_id
        self.quota = quota
        self.assignments: list[Assignment] = []

class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0
        self.creation_order: dict[str, int] = {}
        self.users: dict[str, User] = {}

    # Level 1
    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_counter += 1
        task_id = f"task_id_{self.task_counter}"
        self.tasks[task_id] = Task(task_id, name, priority)
        self.creation_order[task_id] = self.task_counter
        return task_id

    def update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool:
        if task_id not in self.tasks:
            return False
        self.tasks[task_id].name = name
        self.tasks[task_id].priority = priority
        return True

    def get_task(self, timestamp: int, task_id: str) -> Optional[str]:
        if task_id not in self.tasks:
            return None
        task = self.tasks[task_id]
        return f'{{"name":"{task.name}","priority":{task.priority}}}'

    # Level 2
    def search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]:
        if max_results <= 0:
            return []

        matching = [
            task_id for task_id, task in self.tasks.items()
            if name_filter in task.name
        ]

        matching.sort(key=lambda tid: (-self.tasks[tid].priority, self.creation_order[tid]))
        return matching[:max_results]

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        if limit <= 0:
            return []

        task_ids = list(self.tasks.keys())
        task_ids.sort(key=lambda tid: (-self.tasks[tid].priority, self.creation_order[tid]))
        return task_ids[:limit]

    # Level 3
    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, quota)
        return True

    def _get_active_assignment_count(self, user: User, timestamp: int) -> int:
        return sum(
            1 for a in user.assignments
            if a.start_time <= timestamp < a.finish_time and not a.completed
        )

    def assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool:
        if task_id not in self.tasks or user_id not in self.users:
            return False

        user = self.users[user_id]
        active_count = self._get_active_assignment_count(user, timestamp)
        if active_count >= user.quota:
            return False

        assignment = Assignment(task_id, user_id, timestamp, finish_time)
        user.assignments.append(assignment)
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        active = [
            a for a in user.assignments
            if a.start_time <= timestamp < a.finish_time and not a.completed
        ]

        active.sort(key=lambda a: (a.finish_time, a.start_time))
        return [a.task_id for a in active]

    # Level 4
    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        if task_id not in self.tasks or user_id not in self.users:
            return False

        user = self.users[user_id]
        active_assignments = [
            a for a in user.assignments
            if a.task_id == task_id
            and a.start_time <= timestamp < a.finish_time
            and not a.completed
        ]

        if not active_assignments:
            return False

        active_assignments.sort(key=lambda a: a.start_time)
        active_assignments[0].completed = True
        return True

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        overdue = [
            a for a in user.assignments
            if a.finish_time <= timestamp and not a.completed
        ]

        overdue.sort(key=lambda a: (a.finish_time, a.start_time))
        return [a.task_id for a in overdue]
```

## Big O Analysis

Here is how efficient the solution is:

| Operation | Time Complexity | Space Complexity |
| --- | --- | --- |
| addTask | O(1) | O(1) |
| updateTask | O(1) | O(1) |
| getTask | O(1) | O(1) |
| searchTasks | O(T log T) | O(T) |
| listTasksSorted | O(T log T) | O(T) |
| addUser | O(1) | O(1) |
| assignTask | O(A) | O(1) |
| getUserTasks | O(A log A) | O(A) |
| completeTask | O(A log A) | O(A) |
| getOverdueAssignments | O(A log A) | O(A) |

**Definitions:**

- **T** = Total number of tasks.
- **A** = Number of assignments for a specific user.

*原帖: https://www.1point3acres.com/interview/thread/7100097*

---

## Banking System (Online Assessment)

### System Overview

You need to build a bank system that runs in the computer's memory. There are **4 levels** to this problem. You must finish one level to move to the next.

- **Level 1:** create accounts, add money, and move money between accounts.
- **Level 2:** Rank accounts by how much they spend.
- **Level 3:** Schedule payments and handle cashback rewards.
- **Level 4:** Merge two accounts and look up old balances.
You will keep all data from previous levels as you move forward.

## Level 1: Basic Actions

### Goal

Start with an empty bank. Write code to create accounts, put money in, and send money to others.

### Functions to Write

#### create_account

```python
create_account(self, timestamp: int, account_id: str) -> bool
```

- **Action:** Create a new account with the name `account_id`.
- **Returns `True`:** If the account is new and created successfully.
- **Returns `False`:** If that name is already taken.

#### deposit

```python
deposit(self, timestamp: int, account_id: str, amount: int) -> int | None
```

- **Action:** Add `amount` to the account.
- **Returns:** The new total balance after the deposit.
- **Returns `None`:** If the account does not exist.

#### transfer

```python
transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None
```

- **Action:** Move `amount` from the source account to the target account.
- **Returns:** The new balance of the source account if successful.
- **Returns `None` if:**

Either account does not exist.
- You try to transfer money to yourself (source and target are the same).
- The source account does not have enough money.

## Level 2: Ranking Spenders

### Goal

The bank wants to know who spends the most money. You need to rank accounts based on how much money goes out.

### New Function

#### top_spenders

```python
top_spenders(self, timestamp: int, n: int) -> list[str]
```

- **Action:** Find the top `n` accounts that have sent the most money out.
- **Outgoing Money Includes:**

Money transferred to others.
- Money paid/withdrawn (added in Level 3).
- **Sorting Rules:**

Sort by total outgoing money (Highest to Lowest).
- If two accounts spent the same amount, sort them alphabetically by `account_id` (A to Z).
- **Returns:** A list of strings in this format:
`["id1(spent_amount)", "id2(spent_amount)"]`
- **Note:** If there are fewer than `n` accounts, just return all of them. Do not include Cashback in these totals.

## Level 3: Payments and Cashback

### Goal

Add a feature to pay for things. Every payment gets **2% cashback** refund after 24 hours. You also need to check the status of these payments.

### New Functions

#### pay

```python
pay(self, timestamp: int, account_id: str, amount: int) -> str | None
```

- **Action:** Subtract `amount` from the account.
- **Cashback Rule:** The user earns 2% of the transaction amount. Round this down to the nearest whole number.
- **Timing:** The cashback is added back to the account exactly **24 hours** later.

24 hours = 86,400,000 milliseconds.
- Refund time = `timestamp + 86400000`.
- **Returns:** A unique ID string for this payment (e.g., `"payment1"`).
- **Returns `None` if:**

The account does not exist.
- The account does not have enough money.
- **Note:** This withdrawal counts towards the "outgoing money" used in `top_spenders`.

#### get_payment_status

```python
get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None
```

- **Action:** Check the status of a specific payment.
- **Returns:**

`"IN_PROGRESS"`: If the cashback has not arrived yet.
- `"CASHBACK_RECEIVED"`: If the cashback has been added to the account.
- **Returns `None` if:**

The account or payment ID does not exist.
- The payment ID belongs to a different account.

## Level 4: Merging and History

### Goal

Combine two accounts into one. The new account keeps the money and history of both. You also need to look up balances from the past.

### New Functions

#### merge_accounts

```python
merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool
```

- **Action:** Merge Account 2 *into* Account 1.
- **Result:**

Account 1 gets all of Account 2's money.
- Account 1 inherits Account 2's spending history (for `top_spenders`).
- Any cashback Account 2 was waiting for will now go to Account 1.
- You can look up Account 2's old payment statuses using Account 1's ID.
- Account 2 is **deleted** from the system.
- **Returns `True`:** If the merge works.
- **Returns `False` if:**

You try to merge an account into itself.
- Either account does not exist.

#### get_balance

```python
get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None
```

- **Action:** Find out how much money `account_id` had at a specific time (`time_at`).
- **Returns:** The balance at that exact moment.
- **Returns `None`:** If the account did not exist at that time.
- **Note:** If an account was merged, the main account inherits the history.

## Special Rules & Edge Cases

### Recreating an Account

- If Account B is merged into Account A, Account B is deleted.
- You are allowed to create a **new** Account B later.
- This new Account B starts with $0. It does not have the history of the old Account B (because that history moved to Account A).

### History Checks

- Imagine Account B merged into Account A at time `T`.
- If you ask for Account B's balance **before** time `T`: You get the old balance.
- If you ask for Account B's balance **after** time `T`: You get `None` (unless you created a new Account B).

## System Constraints

- **Timestamps:** Numbers representing milliseconds. They are always unique and always increase.
- **IDs:** Valid text strings.
- **Amounts:** Positive whole numbers.

*原帖: https://www.1point3acres.com/interview/thread/7100004*

---

## Cloud Storage System (Online Assessment)

## Problem Summary

Your goal is to build a simple, in-memory cloud storage system. This system will store files and their details, such as name and size.

**Important:** This system runs entirely in memory (RAM). You do not need to save files to your actual hard drive.

You will build this system in four stages:

- **Stage 1**: Add, copy, and read files.
- **Stage 2**: Search for files using start and end patterns.
- **Stage 3**: Manage users and storage limits.
- **Stage 4**: Compress and restore files.
You must pass all tests in a stage to move to the next one.

## Data Format

**Input**: A list of commands (an array of string arrays).

**Output**: An array of strings containing the result of each command.

**Rules**:

- Each query runs one specific operation.
- File names and directory names will never conflict in the input.

## Part 1: Basic File Management

### Goal

The system needs to handle adding files, copying them, and checking their size.

### Commands

#### ADD_FILE

```python
ADD_FILE <name> <size>
```

- Creates a new file with the given `name`.
- `size` is the memory needed in bytes.
- **Fails** if a file with that name exists.
- Returns `"true"` if successful, otherwise `"false"`.

#### COPY_FILE

```python
COPY_FILE <nameFrom> <nameTo>
```

- Copies the file `nameFrom` to the new path `nameTo`.
- **Fails** if:

The source file does not exist.
- The source is a directory, not a file.
- A file already exists at the destination.
- Returns `"true"` if successful, otherwise `"false"`.

#### GET_FILE_SIZE

```python
GET_FILE\_SIZE <name>
```

- Returns the size of the file as a string.
- Returns an empty string `""` if the file is missing.

### Example Walkthrough

**Input:**

```javascript
[
  ["ADD_FILE", "/dir1/dir2/file.txt", "10"],
  ["COPY_FILE", "/root-existing_file.txt", "/dir1/file.txt"],
  ["COPY_FILE", "/dir1/dir2/file.txt", "/dir1/file.txt"],
  ["ADD_FILE", "/dir1/file.txt", "15"],
  ["COPY_FILE", "/dir1/file.txt", "/dir1/dir2/file.txt"],
  ["GET_FILE_SIZE", "/dir1/file.txt"],
  ["GET_FILE_SIZE", "/not-existing.file"]
]
```

**Result:** `["true", "false", "true", "false", "false", "10", ""]`

## Part 2: Searching for Files

### Goal

Add a feature to search for file names based on how they start (prefix) and end (suffix).

### New Command

#### FIND_FILE

```python
FIND_FILE <prefix> <suffix>
```

- Finds all files that start with `prefix` and end with `suffix`.
- Returns a string list in this format: `"<name1>(<size1>), <name2>(<size2>), ..."`
- **Sorting Rules:**

Sort by file size (largest to smallest).
- If sizes are equal, sort alphabetically by name (A-Z).
- Returns `""` if no files match.

### Example Walkthrough

**Input:**

```javascript
[
  ["ADD_FILE", "/root/dir/another_dir/file.mp3", "10"],
  ["ADD_FILE", "/root/file.mp3", "5"],
  ["ADD_FILE", "/root/music/file.mp3", "7"],
  ["COPY_FILE", "/root/music/file.mp3", "/root/dir/file.mp3"],
  ["FIND_FILE", "/root", ".mp3"],
  ["FIND_FILE", "/root", "file.txt"],
  ["FIND_FILE", "/dir", "file.mp3"]
]
```

**Result:** `["true", "true", "true", "true", "/root/dir/another_dir/file.mp3(10), /root/dir/file.mp3(7), /root/music/file.mp3(7), /root/file.mp3(5)", "", ""]`

## Part 3: Managing Users and Storage Limits

### Goal

Allow multiple users to use the system. Each user has a storage limit (capacity).

### New Commands

#### ADD_USER

```python
ADD_USER <userId> <capacity>
```

- Creates a user with a specific storage limit in bytes.
- **Fails** if the `userId` already exists.
- Returns `"true"` if successful, otherwise `"false"`.

#### ADD_FILE_BY

```python
ADD_FILE_BY <userId> <name> <size>
```

- Works like `ADD_FILE`, but the file belongs to `userId`.
- **Fails** if adding this file exceeds the user's `capacity`.
- Returns the **remaining storage space** for that user if successful.
- Returns `""` if the operation fails.
**Important Notes:**

- Standard `ADD_FILE` calls are owned by "admin" (who has unlimited space).
- `COPY_FILE` keeps the owner of the original file.

#### UPDATE_CAPACITY

```python
UPDATE_CAPACITY <userId> <capacity>
```

- Updates the storage limit for a user.
- If the user's current files are too big for the new limit, the system must delete files.
- **Deletion Logic:** Delete the **largest files first** until the user is under the limit. If files are the same size, delete them alphabetically.
- Returns the **number of files deleted** as a string.
- Returns `""` if the user does not exist.

### Example Walkthrough

**Input:**

```javascript
[
  ["ADD_USER", "user1", "125"],
  ["ADD_USER", "user1", "100"],
  ["ADD_USER", "user2", "100"],
  ["ADD_FILE_BY", "user1", "/dir/file.big", "50"],
  ["ADD_FILE_BY", "user1", "/file.med", "30"],
  ["ADD_FILE_BY", "user2", "/file.med", "40"],
  ["COPY_FILE", "/dir/file.med", "/dir/another/file.med"],
  ["COPY_FILE", "/file.med", "/dir/another/another/file.med"],
  ["ADD_FILE_BY", "user1", "/dir/file.small", "10"],
  ["ADD_FILE", "/dir/admin_file", "200"],
  ["ADD_FILE_BY", "user1", "/dir/file.small", "5"],
  ["ADD_FILE_BY", "user1", "/my_folder/file.huge", "100"],
  ["ADD_FILE_BY", "user3", "/my_folder/file.huge", "100"],
  ["UPDATE_CAPACITY", "user1", "300"],
  ["UPDATE_CAPACITY", "user1", "50"],
  ["UPDATE_CAPACITY", "user2", "1000"]
]
```

**Result:** `["true", "false", "true", "75", "45", "", "true", "false", "5", "true", "", "", "", "0", "2", ""]`

## Part 4: Compressing Files

### Goal

Add the ability to compress files to save space.

### New Commands

#### COMPRESS_FILE

```python
COMPRESS_FILE <userId> <name>
```

- Compresses a file if it belongs to `userId`.
- **Action**:

Rename the file to `<name>.COMPRESSED`.
- Change the file size to exactly **half** of the original.
- **Fails** if the file is already compressed (names ending in `.COMPRESSED` cannot be compressed again).
- Returns the **remaining storage space** for the user.
- Returns `""` if the operation fails.
**Note**: `COPY_FILE` preserves the `.COMPRESSED` suffix.

#### DECOMPRESS_FILE

```python
DECOMPRESS_FILE <userId> <name>
```

- Unzips a file if it belongs to `userId`.
- **Action**: Revert the name by removing `.COMPRESSED`.
- **Fails** if:

The unzipped file makes the user go over their storage limit.
- A file with the original name already exists.
- Returns the **remaining storage space** for the user.
- Returns `""` if the operation fails.

### Example Walkthrough

**Input:**

```javascript
[
  ["ADD_USER", "user1", "1000"],
  ["ADD_USER", "user2", "5000"],
  ["ADD_FILE_BY", "user1", "/dir/file.mp4", "500"],
  ["COMPRESS_FILE", "user2", "/dir/file.mp4"],
  ["COMPRESS_FILE", "user3", "/dir/file.mp4"],
  ["COMPRESS_FILE", "user1", "/folder/non_existing_file"],
  ["COMPRESS_FILE", "user1", "/dir/file.mp4"],
  ["GET_FILE_SIZE", "/dir/file.mp4.COMPRESSED"],
  ["GET_FILE_SIZE", "/dir/file.mp4"],
  ["COPY_FILE", "/dir/file.mp4.COMPRESSED", "/file.mp4.COMPRESSED"],
  ["ADD_FILE_BY", "user1", "/dir/file.mp4", "500"],
  ["DECOMPRESS_FILE", "user1", "/dir/file.mp4.COMPRESSED"],
  ["UPDATE_CAPACITY", "user1", "2000"],
  ["DECOMPRESS_FILE", "user2", "/dir/file.mp4.COMPRESSED"],
  ["DECOMPRESS_FILE", "user3", "/dir/file.mp4.COMPRESSED"],
  ["DECOMPRESS_FILE", "user1", "/dir/file.mp4.COMPRESSED"],
  ["DECOMPRESS_FILE", "user1", "/file.mp4.COMPRESSED"]
]
```

**Result:** `["true", "true", "500", "", "", "", "750", "250", "", "true", "0", "", "0", "", "", "", "750"]`

*原帖: https://www.1point3acres.com/interview/thread/7100005*

---

## Web Crawler

## Problem Statement

You are given:

- A starting web address called `startUrl`.
- A tool called `HtmlParser` that finds all links on a specific web page.
You need to build a web crawler. It must find **all URLs** that you can reach from the `startUrl`.

**Important Rule:** You must only keep URLs that belong to the same **hostname** as the `startUrl`. The order of the list does not matter.

Here is the interface for the `HtmlParser`:

```java
interface HtmlParser {
    // Returns all URLs from a given page URL.
    public List<String> getUrls(String url);
}
```

Your function signature will look like this: `List<String> crawl(String startUrl, HtmlParser htmlParser)`.

### Core Rules

Your crawler must follow these steps:

- **Start** at the `startUrl`.
- **Use** `HtmlParser.getUrls(url)` to get all links from that page.
- **Avoid duplicates**: Do not visit the same URL more than once.
- **Check the Hostname**: Only follow links if the **hostname** matches the `startUrl`.
- Assume all links use `http` and do **not** use port numbers.

### Things to Clarify

- **URL Fragments**: Ask the interviewer about links with `#` (like `http://example.com/page#section1`). Should you treat them as the same page or a new page?
- **URL Normalization**: Ask if you need to clean up or standardise the URLs. Usually, you can assume this is not needed for the basic part.

## Part 2: Multithreading (Important!)

First, solve the problem using a single thread. Once that works, make a **multithreaded or concurrent version** to make it faster.

### Goals

- **Run in Parallel**: Download multiple pages at the same time.
- **Thread Safety**: Make sure your data (like the visited list) doesn't get corrupted when many threads touch it at once.
- **Avoid Duplicates**: Even with multiple threads, never visit a URL twice.
- **Check the Hostname**: Keep following the hostname rule.

### Hint for the Candidate

Use a **Thread Pool** to manage your threads.

- Do **not** make a new thread for every single URL. This will crash the system.
- A thread pool limits how many threads run at once.
- Common setup: Use a fixed size (like 10-20 threads) and a queue for tasks.

## Solution: JavaScript Implementation

Below is a full JavaScript solution. It handles tasks concurrently and cleans up URLs to prevent duplicates.

### ThreadPool Class

```javascript
class ThreadPool {
    constructor(maxConcurrency) {
        this.maxConcurrency = maxConcurrency;
        this.queue = [];
        this.runningTasks = 0;
        this.waitForFinishPromise = null;
        this.waitForFinishResolve = null;
    }

    // Add a task to the queue and start processing
    execute(task) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                task,
                resolve,
                reject
            });
            this._processQueue();
        });
    }

    _processQueue() {
        // Stop if we reached the max number of running tasks
        if (this.runningTasks >= this.maxConcurrency) {
            return;
        }

        // If queue is empty, check if all work is fully done
        if (this.queue.length === 0) {
            if (this.runningTasks === 0) {
                this.waitForFinishResolve && this.waitForFinishResolve();
                this.waitForFinishPromise = null;
                this.waitForFinishResolve = null;
            }
            return;
        }

        // Run the next task from the queue
        const { task, resolve, reject } = this.queue.shift();
        this.runningTasks++;
        Promise.resolve()
            .then(task)
            .then(resolve, reject)
            .finally(() => {
                this.runningTasks--;
                this._processQueue();
            });
    }

    // Returns a promise that finishes when all tasks are done
    waitForFinish() {
        if (this.runningTasks === 0 && this.queue.length === 0) {
            return Promise.resolve();
        }

        if (!this.waitForFinishPromise) {
            this.waitForFinishPromise = new Promise((resolve) => {
                this.waitForFinishResolve = resolve;
            });
        }
        return this.waitForFinishPromise;
    }
}
```

### URL Helper Function

```javascript
function getProcessedUrlObject(url) {
    const newUrl = new URL(url);
    // Remove the hash (#) part so http://example.com/page#1
    // and http://example.com/page#2 are seen as the same URL
    newUrl.hash = "";
    return newUrl;
}
```

### Main Crawler Logic

```javascript
async function crawl(startUrl, htmlParser, maxConcurrency = 10) {
    const processedStartUrlObject = getProcessedUrlObject(startUrl);
    const startHostName = processedStartUrlObject.hostname;

    const result = [processedStartUrlObject.toString()];
    const visited = new Set([processedStartUrlObject.toString()]);
    const pool = new ThreadPool(maxConcurrency);

    const crawlUrl = async (url) => {
        try {
            const nextUrls = await htmlParser.getUrls(url);
            for (const nextUrl of nextUrls) {
                const nextUrlProcessedObject = getProcessedUrlObject(nextUrl);
                const nextUrlProcessedString = nextUrlProcessedObject.toString();

                // Only crawl if hostname matches and we haven't visited it yet
                if (nextUrlProcessedObject.hostname === startHostName
                    && !visited.has(nextUrlProcessedString)) {
                    visited.add(nextUrlProcessedString);
                    result.push(nextUrlProcessedString);
                    // Add to the pool (fire and forget)
                    pool.execute(() => crawlUrl(nextUrl)).catch((err) => {
                        console.error(`Error crawling ${nextUrl}:`, err);
                    });
                }
            }
        } catch (error) {
            console.error(`Error fetching URLs from ${url}:`, error);
        }
    };

    // Start crawling from the first URL
    await pool.execute(() => crawlUrl(startUrl));
    // Wait for everything to finish
    await pool.waitForFinish();

    return result;
}
```

### How to Run the Code

```javascript
// Example with a fake HtmlParser
class HtmlParser {
    constructor(urls) {
        this.urls = urls;
    }

    async getUrls(url) {
        // Fake a network delay
        await new Promise(resolve => setTimeout(resolve, Math.random() * 15));
        return this.urls[url] || [];
    }
}

const urls = {
    "http://news.yahoo.com": [
        "http://news.yahoo.com/news/topics/",
        "http://news.yahoo.com/news"
    ],
    "http://news.yahoo.com/news/topics/": [
        "http://news.yahoo.com/news",
        "http://news.yahoo.com/news/sports"
    ],
    "http://news.yahoo.com/news": [
        "http://news.google.com"
    ],
    "http://news.yahoo.com/news/sports": []
};

const parser = new HtmlParser(urls);
const result = await crawl("http://news.yahoo.com", parser, 2);
console.log("Crawled URLs:", result);
// Output should be yahoo.com URLs only (no google.com)
```

### Why We Built It This Way

- **ThreadPool**: We made a custom queue. This lets us limit how many downloads run at once so we don't overwhelm the system.
- **URL Normalization**: We remove the `#` part of URLs. This ensures we don't treat the same page as two different links.
- **Thread Safety**: We use a `Set` to track visited pages. Because JavaScript is single-threaded (event loop), we don't have race conditions here.
- **Error Handling**: If one link fails, we log the error, but the crawler keeps going.
- **Concurrency Control**: We limit the number of parallel requests to be polite to the server.

## System Design Questions

The interviewer may ask these questions verbally. You usually don't need to code these, but you should know how to explain them.

### 1. Threads vs Processes

**Question:** What is the difference between a thread and a process? Which one is better for a web crawler?

**Answer Strategy:**

- **Threads**: These are "lightweight." They share memory. They are great for tasks that wait a lot (like waiting for a website to load). This is called **I/O-bound**.
- **Processes**: These are "heavy." They have their own separate memory. They are better for tasks that do heavy math (**CPU-bound**).
- **For Crawling**: Use **Threads**. Crawling is mostly waiting for the internet, and threads are more efficient for that.

### 2. Scaling to Many Machines

**Question:** If we have millions of URLs, one computer isn't enough. How do we build a distributed system?

**Answer Strategy:**

- **URL Distribution**: How do we split the work? We can use **Consistent Hashing** on the hostname to decide which machine crawls which website.
- **Coordination**: Machines need to talk to check for duplicates. We can use a shared cache like **Redis**.
- **Load Balancing**: We need to make sure every machine has roughly the same amount of work.
- **Fault Tolerance**: If a machine crashes, another machine needs to pick up its work.

### 3. Being "Polite" (Rate Limiting)

**Question:** If we crawl too fast, we might crash the website. How do we prevent this?

**Answer Strategy:**

- **robots.txt**: Always check this file first. It tells us what we are allowed to crawl.
- **Rate limiting**: Set a limit. For example, "only 1 request per second for `yahoo.com`."
- **Throttling**: If the server starts responding slowly, our crawler should slow down automatically.
- **Distributed Control**: If multiple machines are crawling the same site, they need to coordinate so they don't attack the site together.

### 4. Handling Duplicate Pages

**Question:** Many URLs point to the exact same content. How do we detect this so we don't waste space?

**Answer Strategy:**

- **Fingerprinting**: Create a hash (like **MD5** or **SHA-256**) of the page content. If the hash matches one we already have, it's a duplicate.
- **URL Normalization**: Clean up the URL text (remove tracking IDs, sort parameters) before fetching.
- **Similarity Check**: Use algorithms like **Simhash** or **Jaccard similarity** to find pages that are *mostly* the same, even if a few words changed.

*原帖: https://www.1point3acres.com/interview/thread/7100011*

---

## Culture & Behavioral Interview Questions

## Introduction

Anthropic focuses heavily on whether you fit their culture, care about AI safety, and how you think about ethics. You can answer these questions using stories from your job or your personal life. Interviewers are looking at **how** you think. They are not judging if your values are "right" or "wrong."

## Views on AI Safety and Company Mission

### 1. Why is AI Safety important to you personally?

**Advice for Candidate:**

- They want to hear a **real story**, not just ideas from a textbook.
- A good way to answer: "I used to only care about speed and numbers, but a specific event made me realize safety matters more."
- Explain how this connects to your interest in Anthropic.
- Do not give generic answers. They can tell if you are just saying what they want to hear.
- If you don't have work experience with safety, admit it. Then, show that you understand it through books or self-study.

### 2. Do you believe AI will change the world? If yes, would you give up personal gain to keep humanity safe?

**Advice for Candidate:**

- You **must truly believe** that AI has the power to change everything. This is a screening question.
- Watch Lex Fridman's interviews (especially with Dario Amodei and other AI safety researchers) to really understand this.
- Be ready to talk about risks seriously. Do not brush them off.
- Some candidates say they felt worried about their own job security after studying these topics. This shows the deep level of engagement they are looking for.

### 3. What do you think about AI Safety? How can Anthropic improve?

**Advice for Candidate:**

- Read about Anthropic’s current safety work (like Constitutional AI, red teaming, and interpretability research).
- Give helpful, thoughtful ideas. Do not just complain.
- Show that you have thought hard about specific safety problems.

### 4. What are your main values? How do you use them in your daily work?

**Advice for Candidate:**

- Be specific. Give examples. They want to see your values in action, not just hear a list.
- If your values match Anthropic's values, explain how.
- Talk about times you succeeded and times you struggled to stick to your values.

### 5. Working at Anthropic might pay less than other companies. How do you feel about that?

**Advice for Candidate:**

- They are testing if you care more about the mission than the money.
- Be honest. If money is important to you, explain your feelings carefully.
- Talk about what trade-offs you are willing to make and why.
- Show that you thought about this seriously before applying.

## Handling Feedback and Disagreements

### 6. Tell me about a time you got feedback that hurt your feelings. How did you handle it?

**Advice for Candidate:**

- You can use principles from Stripe (like "growth mindset" or "intellectual honesty") to prepare.
- Be vulnerable. It is okay to admit it was hard emotionally.
- Focus on what you learned and how you improved.
- Do not say you agreed right away. They want to see how you processed the information.

### 7. Describe a time you had a conflict and later realized you were wrong.

**Advice for Candidate:**

- This tests if you are humble and can change your mind.
- Explain why you thought you were right at first (show you weren't just being careless).
- Describe the exact moment you realized you were wrong.
- What did you do to fix it?
- What did you learn about yourself?

### 8. How do you handle arguments when everyone wants the same goal?

**Advice for Candidate:**

- This is about handling disagreements between well-meaning people.
- Show that you can disagree without being rude.
- Explain the tools you use (like data, getting outside opinions, or focusing on shared goals).
- Avoid saying, "I just convinced them I was right." Show that you solved the problem together.

### 9. Have you ever been surprised by feedback you gave or received?

**Advice for Candidate:**

- They are looking for self-awareness. They want to know if you can see your own blind spots.
- The "surprise" part shows you are open to changing how you see yourself.
- Explain how you handled the surprise and what you did with that new knowledge.

### 10. Describe a time you changed your opinion of a person.

**Advice for Candidate:**

- This tests if you can update your beliefs and avoid judging people too strictly.
- Show that you are open-minded and humble.
- What new information changed your view?
- How did this change your working relationship?

## Standing Up for Your Beliefs

### 11. Give examples from work where you stood firm on something you believed in.

**Advice for Candidate:**

- They might ask for more than one example.
- Explain what was at stake and why it mattered.
- Explain how you defended your position.
- What happened in the end? Would you do it again?

### 12. Tell me about a time you refused to do something because you thought it was wrong.

**Advice for Candidate:**

- This covers a core value: integrity is more important than speed.
- Be specific about why you thought it was wrong.
- How did you tell your boss or team?
- What happened next? How did you handle it?
- Do not sound like you are better than everyone else. Show thoughtful reasoning.

## Interest in Anthropic

### 13. Why do you want to join Anthropic?

**Advice for Candidate:**

- Generic answers about "safety" and "trust" will lead to hard follow-up questions.
- Be ready for: "How do you know we are good at safety? Have you compared us to other companies?"
- If you haven't compared them in detail, be honest: "I am basing this on my experience using the tool and what I read, but I haven't done a full comparison."
- Mention specific work or research from Anthropic that you like.

### 14. Why do you choose Anthropic over OpenAI?

**Advice for Candidate:**

- **This is a hard question.** It is hard to answer without insulting OpenAI.
- Focus on what attracts you **TO** Anthropic, not what pushes you away **FROM** OpenAI.
- Example: "Anthropic's research on Constitutional AI matches how I think about safety," rather than "OpenAI doesn't care about safety."
- Admit that both companies do important work, but explain why Anthropic's style fits you better.
- You can talk about different philosophies (like being open vs. being careful) without being mean.

### 15. What do you think about Anthropic's involvement in politics and policy?

**Advice for Candidate:**

- Some interviewers may ask about Anthropic's work with the government.
- Read about their policy positions.
- Be ready to discuss the role AI companies play in creating laws.

## Life Goals and Personal Changes

### 16. What are your goals in life? Has anything changed who you are as a person?

**Advice for Candidate:**

- **This does NOT need to be about work.** Life examples are totally fine.
- They want to know what drives you and how you handle big experiences.
- Show deep thinking, not just a list of achievements.
- Connect this to why you want to work on AI if you can, but don't force it.

## Final Advice

- Prepare points about AI safety, but know they might not use them all. Most questions focus on how you act with people and your values.
- The interviewer will not judge if your values are right or wrong. Instead, they will check:

How deeply you have thought about them.
- If you can stick to them under pressure.
- If you can reflect and grow.
- Watch Lex Fridman interviews with Dario Amodei, Chris Olah, and other AI safety researchers to really understand the topics.
- **Be yourself.** Experienced interviewers can tell if you practiced your answers too much or if you are faking it.

*原帖: https://www.1point3acres.com/interview/thread/7100007*

---

## Employee Management System (Online Assessment)

## Problem Summary

You need to build a simple system to manage employees. This challenge has **4 parts**. Each part gets a little harder than the last:

- **Part 1**: Add new employees and track when they arrive and leave.
- **Part 2**: Calculate total work hours and find the employees who work the most.
- **Part 3**: Handle promotions (pay raises) that start later and calculate pay for specific dates.
- **Part 4**: Add "double pay" periods for everyone.
You must solve the current part before you can move to the next one.

## Part 1: Basic Features

### Goal

Build the core tools to add people to the system and track their office hours.

### Required Actions

#### Create New Employee

- Add a person to the system using their:

Name
- Job Position
- Hourly Salary (pay rate)
- Save this data in the system.

#### Record Check-In/Check-Out

- Log the time when an employee arrives (clocks in).
- Log the time when an employee leaves (clocks out).
- Keep a list of these entry and exit times.

## Part 2: Tracking Time

### Goal

Add features to check how long employees have worked and rank them by their hours.

### New Actions

#### Get Total Work Time

- Find out how much time a specific person has spent in the office.
- Add up the time from all their check-in/check-out sessions.

#### Find Top K Workers

- Find the "Top K" employees who have the most total office time.
- Sort the results so the person with the most time is at the top.

## Part 3: Raises and Pay Checks

### Goal

Add a way to give promotions. However, the promotion does not happen right away. You also need to calculate how much money someone earned between two specific dates.

### New Actions

#### Set Promotion

- Announce a change in job title or a pay raise for an employee.
- **Important:** This change does **not** start immediately.
- The new rate begins the **next time the employee clocks in** after the announcement.
- Any work done after that next clock-in uses the new salary rate.

#### Calculate Pay for a Period

- Calculate the total money an employee earned during a specific time range.
- **Formula:** Time Worked × Hourly Rate.
- You must handle:

Changes in pay rate if a promotion happened during this time.
- Only counting time when the employee was actually clocked in.

## Part 4: Bonus Pay Periods

### Goal

Add special time blocks where every employee earns double their normal pay.

### New Actions

#### Set Double Pay Times

- Pick specific start and end times where all work pays double.
- During these times, the pay rate is **2 × Base Hourly Rate**.

#### Advanced Pay Calculation

- Update the pay calculator from Part 3 to handle these bonus periods.
- If work happens during a double pay period, use the doubled rate.
- You need to handle complex cases like:

When a person's work hours overlap with a double pay period.
- When there are multiple different double pay periods.
- When a person gets a promotion *and* works during a double pay period.

*原帖: https://www.1point3acres.com/interview/thread/7100008*

---

## Inference API System Design

## Problem Requirements

You need to design a high-concurrency **inference API system**. This system must handle many requests happening at the same time. You are given an API endpoint for inference, and you cannot change it. Your job is to build the infrastructure around it. You must specifically focus on the **batch service** that groups requests before sending them to GPU workers.

### Rules and Constraints

- **Cannot change API**: You must work with the existing inference API.
- **Client waits for answer**: Clients send a standard HTTP request and wait for the reply (synchronous). However, inside your system, you can do the work in the background (asynchronous).
- **Fast response**: Even though you process things in the background, the user must get an answer quickly (usually under 500ms to 1s).
- **High traffic**: The system must handle many users at once without slowing down.
- **Limited GPUs**: GPUs are expensive and limited. You must use them efficiently.

### Questions the Interviewer Might Ask

Be ready to answer deeper questions on these topics:

- **Batching**: How do you decide when to send a batch? Do you wait for a full batch or set a time limit?
- **Adding GPUs**: How many GPUs do you need for 10,000 RPS (Requests Per Second)? What if it takes 5 minutes to turn on a new GPU?
- **Rate Limiting**: What happens if half your GPUs break? How do you limit users automatically?
- **Queues**: Do you use one queue or many? How do you make sure paid users go first?
- **Monitoring**: What numbers do you track? How do you know when to add more servers?
- **Latency**: Where does the time go? If it takes 500ms, how much of that is waiting vs. doing work?
- **Load Balancing**: If the system is 75% full, how do you spread the work across GPUs?
- **Caching**: Should you save answers to repeat questions? How do you handle questions that are almost the same?
- **Errors**: What if a GPU crashes while working? Do you try again?
- **Cost**: GPUs cost a lot of money. How do you save money but still keep the system fast?

## Sample Solution

**⚠️ Note**: This is just one example. To prepare well, try to solve the problem yourself first. Use this guide to check your work.

## Step 1: Defining the Scope

Before designing, ask questions to understand exactly what you need to build.

### Questions to Ask

**Basic Features:**

- What kind of work is this? (Text, images, etc.)
- Do we need to run different versions of the model at the same time?
- Do we stream the answer back (word by word) or send it all at once?
- Do we need to save the history of all questions and answers?
**What is Included:**

- Are we building just the batching part, or the whole API system?
- Do we handle updating the models?
- Should we save answers (cache) for repeated questions?
- Do we manage the GPU servers directly?
**Performance Goals:**

- How many requests per second (RPS) do we expect? (e.g., 1,000 or 10,000)
- How fast must the answer be? (e.g., 95% of requests under 1 second)
- How long can a request wait in the queue?
- How big is each request?
**Security:**

- Do users need a password or API key?
- Are there different types of users (free vs. paid)?
- Do we need to save logs for security checks?
- Is the data private?

### What the System Must Do

**Functional Requirements:**

- **Group Requests**: Combine small requests into batches so the GPU works efficiently.
- **User Tiers**: Handle free, paid, and enterprise users differently (give priority to paid users).
- **Auto-Scaling**: Add or remove GPU workers based on how busy the system is.
- **Rate Limiting**: Stop the system from crashing by limiting how many requests users can send.
- **Monitoring**: Track how healthy the system is.
**System Qualities:**

- **Speed**: Answers should take less than 1 second (P95).
- **Growth**: Start with 1,000 RPS but plan for 10,000+ RPS.
- **Reliability**: The system should almost never go down (99.9% uptime).
- **Cost**: Use GPUs fully to save money.

## Step 2: Estimating Scale and Capacity

Doing some quick math helps us decide how many servers we need.

### Basic Assumptions

**Traffic:**

- Goal: 1,000 requests/second at peak times.
- Future: Plan for 10x growth (10,000 RPS).
- Usage: 80% just asking questions (inference), 20% saving data.
- Peak: The busiest time is 3x busier than average.
**GPU Details:**

- Time to process a batch (32 requests): 50ms.
- Batch size: 32 requests.
- GPU Memory: 40GB.
- Model Size: 10GB (leaving 30GB for work).
**Users:**

- 100,000 daily users.
- Each user sends 10 requests per day.
- Users: 70% Free, 25% Paid, 5% Enterprise.

### The Math

**Request Volume:**

```python
Daily requests: 100K users × 10 requests = 1M requests/day
Requests per second (average): 1M / 86,400 seconds = 11.6 RPS
Peak traffic (3x): ~35 RPS
Target to build for: 1,000 RPS (to be safe and ready for growth)
```

**GPU Needs** (See Step 4 for details):

```python
We know:
- Target: 1000 RPS
- Batch size: 32 requests
- Time to process batch: 50ms
- Waiting to form batch: ~20ms
- Moving data: ~5ms

Total time for one batch: 75ms
Batches one GPU can do in 1 second: 1000ms / 75ms = 13.3
Requests one GPU can do in 1 second: 13.3 × 32 = 426

GPUs needed (exact): 1000 / 426 = 2.35
GPUs needed (aiming for 70% usage): 2.35 / 0.7 ≈ 4 GPUs
```

**Storage:**

```python
Request info: 100 bytes each
Result info: 2KB each
Daily storage: 1M × 2KB = 2GB/day
Yearly storage: ~700GB

Conclusion: Standard databases or S3 can easily handle this.
```

**Cost:**

```python
GPU cost (A100):
- $3/hour per GPU
- 4 GPUs × $3 × 24 hours × 30 days = $8,640/month

Other servers (Database, Load Balancer, etc.): ~$150/month

Total: ~$8,800/month (Most of the money goes to GPUs)
```

### Main Lessons

- **GPUs are expensive**: We must use them carefully.
- **Start small**: We only need 4 GPUs to start.
- **Storage is cheap**: Saving data is not a problem.
- **Speed is key**: We have about 75ms for processing, which leaves plenty of time to stay under the 1-second limit.

## Step 3: Designing the API

We need to define how the client talks to our system and how our internal servers talk to each other.

### API Endpoints

**Client-facing REST API:**

```typescript
// Send a question (Client waits for this)
POST /api/v1/inference
Request:
{
  "model": "gpt-4",
  "input": "What is the capital of France?",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 100
  }
}
Response:
{
  "request_id": "req_abc123",
  "output": "The capital of France is Paris.",
  "metadata": {
    "tokens_used": 15,
    "latency_ms": 523,
    "model_version": "gpt-4-2024"
  }
}

// Check status (for background work)
GET /api/v1/inference/{request_id}
Response:
{
  "status": "completed", // queued, processing, completed, failed
  "output": "...",
  "metadata": {...}
}
```

**Internal APIs (Batcher to GPU):**

```typescript
// Send a batch of questions (Internal use only)
POST /internal/batch-inference
Request:
{
  "batch_id": "batch_xyz789",
  "requests": [
    {"request_id": "req_1", "input": "...", "parameters": {...}},
    {"request_id": "req_2", "input": "...", "parameters": {...}},
    // ... up to 32 requests
  ]
}
Response:
{
  "batch_id": "batch_xyz789",
  "results": [
    {"request_id": "req_1", "output": "...", "status": "success"},
    {"request_id": "req_2", "output": "...", "status": "success"}
  ]
}

// Check GPU health
GET /internal/health
Response:
{
  "status": "healthy",
  "gpu_utilization": 0.75,
  "queue_depth": 12,
  "requests_per_second": 450
}
```

**Monitoring APIs:**

```typescript
// Get metrics for auto-scaling
GET /api/v1/metrics
Response:
{
  "gpu_utilization": 0.75,
  "queue_depth": 12,
  "p95_latency_ms": 450,
  "requests_per_second": 850,
  "error_rate": 0.001
}
```

### Security

- Use an API key (e.g., `Authorization: Bearer <key>`).
- Limit usage based on the key and user type (Free vs. Paid).

## Step 4: Database and Data Structure

This section defines how we store data and move it around.

### Data Objects

**Request Queue (Message Queue - Redis/Kafka):**

```python
{
  "request_id": "req_abc123",
  "user_id": "user_456",
  "tier": "paid",           // free, paid, enterprise
  "model": "gpt-4",
  "input": "...",
  "parameters": {...},
  "timestamp": "2024-01-15T10:30:00Z",
  "timeout": "2024-01-15T10:30:05Z"  // 5 second timeout
}
```

**Batch Info (Inside the Batcher):**

```python
{
  "batch_id": "batch_xyz789",
  "requests": ["req_1", "req_2", ..., "req_32"],
  "created_at": "2024-01-15T10:30:00.100Z",
  "sent_to_gpu": "2024-01-15T10:30:00.150Z",
  "gpu_worker_id": "gpu-worker-3"
}
```

**Request Database (PostgreSQL/Redis):**

```sql
-- Main table for history (PostgreSQL)
CREATE TABLE requests (
  request_id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50),
  model VARCHAR(50),
  status VARCHAR(20),  -- queued, processing, completed, failed
  created_at TIMESTAMP,
  completed_at TIMESTAMP,
  latency_ms INTEGER,
  tokens_used INTEGER
);

-- Fast lookup for active requests (Redis)
{
  "req_abc123": {
    "status": "processing",
    "batch_id": "batch_xyz789",
    "client_connection_id": "conn_123"  // To send the answer back
  }
}
```

**GPU List (Redis):**

```python
{
  "gpu-worker-1": {
    "status": "healthy",
    "current_utilization": 0.78,
    "requests_processed": 15234,
    "last_heartbeat": "2024-01-15T10:30:05Z"
  },
  "gpu-worker-2": {...},
  ...
}
```

### Choosing the Database

**Redis (In-Memory):**

- Use this for Queues, Live Tracking, and Rate Limits.
- **Why:** It is extremely fast (<1ms) and handles many requests.
**PostgreSQL (Permanent Storage):**

- Use this for History, User Info, and Logs.
- **Why:** It is reliable (ACID) and good for complex searches.
**Kafka (Queue Alternative):**

- Use this if you absolutely cannot lose a message if a server crashes.
- **Trade-off:** It is slower than Redis (~5-20ms vs ~1ms). For this problem, Redis is better because speed is critical.

### Indexing

```sql
-- Make searching faster
CREATE INDEX idx_requests_user_id ON requests(user_id, created_at DESC);
CREATE INDEX idx_requests_status ON requests(status) WHERE status IN ('queued', 'processing');
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
```

## Step 5: System Overview

The system has 6 main parts. Here is how they fit together.

### Architecture Diagram

```python
┌─────────────┐
│   Clients   │
└──────┬──────┘
       │ (sync HTTP request)
       v
┌─────────────────┐
│  Load Balancer  │
└──────┬──────────┘
       │
       v
┌──────────────────────┐◀──────────┐
│  Rate Limiter/       │           │ Feedback: Tells Gateway if GPUs are full
│  API Gateway         │           │ 
└──────┬───────────────┘           │
       │ (write to queue)          │
       v                           │
┌─────────────────────┐            │
│  Message Queue(s)   │            │
│  (one per tier)     │            │
│  - Free tier queue  │            │
│  - Paid tier queue  │            │
│  - Enterprise queue │            │
└──────┬──────────────┘            │
       │ (poll/consume)            │
       v                           │
┌──────────────────────┐           │
│  Request Batcher     │           │
│  (Batching Service)  │           │
│  - Groups requests   │           │
│  - Manage timeouts   │───────────┘
└──────┬───────────────┘
       │ (batched requests)
       v
┌──────────────────────┐
│   GPU Worker Pool    │
│  - Load balancer     │
│  - Multiple GPU pods │
└──────┬───────────────┘
       │ (batched responses)
       v
┌──────────────────────┐
│  Response Handler    │
│  (maps back to       │
│   original requests) │
└──────┬───────────────┘
       │
       v
    (return to client)
```

### What Each Part Does

**1. Load Balancer**

- Spreads traffic across different API Gateways.
- Handles secure connections (SSL).
**2. Rate Limiter / API Gateway**

- Checks API keys.
- Limits usage based on user tier.
- Sends requests to the correct queue.
- Keeps the connection open so the client gets an answer.
**3. Message Queues (Redis)**

- Separate queues for Free, Paid, and Enterprise users.
- Keeps requests organized.
- Acts as a buffer if the GPUs are busy.
**4. Request Batcher**

- Pulls requests from the queue.
- Groups them into a batch (e.g., wait for 32 requests OR 40ms time limit).
- Sends batches to GPUs.
**5. GPU Worker Pool**

- The actual servers doing the AI work.
- Processes the batch and returns results.
**6. Response Handler**

- Takes the batch result and breaks it back into individual answers.
- Matches answers to the waiting clients.

### How a Request Moves Through the System

- **Client → Load Balancer**: Client sends a request.
- **API Gateway**: Checks if the user is allowed (Paid user). Puts the request in the "Paid Queue" and keeps the connection open.
- **Queue**: The request waits here. (Average wait: ~20ms).
- **Batcher**: Picks up the request, waits a few milliseconds to find other requests, groups them, and sends them to a GPU.
- **GPU**: Processes the whole batch (takes ~50ms).
- **Response**: The system separates the answers and sends yours back to you.
**Total Time: ~91-131ms** (Much faster than the 500ms limit).

## Step 6: Deep Dive into Key Components

In an interview, you can't design everything perfectly. Focus on these 3 critical areas.

### Strategy 1: Grouping Requests (Batching)

This is the most important part. We trade a tiny bit of waiting time for much better efficiency.

**The Problem:** When should we send a batch to the GPU?

**Approaches:**

**Option A: Fixed Batch Size (Efficient)**

- Wait until you have exactly 32 requests.
- **Pros:** GPU works perfectly.
- **Cons:** If traffic is low, the first user waits a long time for 31 other people.
**Option B: Timeout-Based (Fast - Recommended)**

- Wait until you have 32 requests OR until 40ms has passed.
- **Pros:** Fast even during low traffic.
- **Cons:** Sometimes sends small batches (less efficient).
**Option C: Adaptive**

- Change the batch size and timeout automatically based on traffic.
- **Pros:** Best of both worlds.
- **Cons:** Hard to build.
**Discussion Points:**

- Larger batches = Better GPU use, but slower for users.
- Smaller batches = Faster for users, but wastes GPU power.

### Strategy 2: Scaling Up and Down

**The Problem:** Traffic changes all the time. How do we adjust?

**Things to know:**

- **Horizontal Scaling:** Adding more machines.
- **Cold Start:** Turning on a new GPU takes 1-5 minutes. You can't just switch it on instantly.
**Approach:**

- Don't run GPUs at 100%. Aim for 70-80%. This leaves room for sudden spikes while new servers turn on.
- **Scale UP** when:

GPU usage > 80% for 2 minutes.
- Queue has more than 100 items.
- Latency is getting too high.
- **Scale DOWN** when:

GPU usage < 50% for 10 minutes.
- Remove servers slowly so you don't accidentally remove too many.

### Strategy 3: Tracking System Health

**The Problem:** How do you know if the system is broken?

**Metrics to Track:**

- **Utilization:** How hard are the GPUs working?
- **Throughput:** Requests per second.
- **Latency:** How long does a request take? (Track P95 and P99).
- **Queue:** How many requests are waiting?
- **Errors:** How many requests failed?

### Strategy 4: Calculating GPU Needs

**Given:** 1,000 requests/second.

**Factors:**

- **Inference time:** 50ms per batch.
- **Batch size:** 32.
- **Overhead:** It takes time to group requests (~20ms) and move data (~5ms).
**Calculation:**

```python
1. Total time per batch: 50ms (work) + 20ms (wait) + 5ms (move) = 75ms.
2. Batches per GPU per second: 1000ms / 75ms = 13.3 batches.
3. Requests per GPU per second: 13.3 batches × 32 requests = 426 requests.

4. GPUs needed (Raw): 1000 / 426 = 2.35.
5. GPUs needed (Safe limit of 70% usage): 2.35 / 0.7 ≈ 4 GPUs.
```

### Strategy 5: Controlling Traffic Flow

**The Problem:** What if a GPU crashes and the others get overwhelmed?

**Solution: Dynamic Rate Limiting**

You need to limit users based on the *current* health of the system.

- **Green Zone (Queue < 100):** Normal. Accept everyone.
- **Yellow Zone (Queue 100-500):** Warning. Slow down free users.
- **Red Zone (Queue > 500):** Critical. Reject new requests (Error 429).
**Formula:**
If you have 10 GPUs and each can handle 100 RPS, your capacity is 1,000 RPS.
If 5 GPUs break, your capacity drops to 500 RPS. You must immediately lower the rate limit.

### Strategy 6: Caching Answers

**The Problem:** Why calculate the same answer twice?

**Option A: Exact Match (Key-Value Store)**

- If the prompt is exactly the same, return the saved answer.
- **Fast and safe.**
**Option B: Similarity Match (Vector DB)**

- If the prompt is *almost* the same, return a saved answer.
- **Risk:** The answer might be wrong for the new context.
- **Cost:** Calculating similarity takes time. Only use this if saving the inference time is worth the effort.

### Strategy 7: Handling Timeouts and Retries

**The Problem:** A request takes too long. What do we do?

**Timeouts:**

- **Client Timeout:** The user gives up after 5 seconds.
- **Server Timeout:** We stop trying after 4 seconds (to give a clean error before the client gives up).
**Retries:**

- **Client:** Can retry on network errors or Rate Limit errors (429).
- **Server:** If a GPU crashes, try one more time on a different GPU. Do not retry too many times, or you will crash the whole system.

## Step 7: Finding and Fixing Weak Spots

A good engineer anticipates problems.

### Potential Bottlenecks

- **Load Balancer Failure**: If this breaks, the site is down.

*Fix:* Use two load balancers (Active-Passive).
- **GPU Overload**: Traffic spikes higher than expected.

*Fix:* Keep a buffer (70% usage). Use queue depth to predict spikes.
- **Queue Full**: Too many requests fill up memory.

*Fix:* Set a limit (e.g., 1000 max). Reject requests if the queue is full.
- **Database Slow**: Too many connections.

*Fix:* Use a connection pooler (like PgBouncer). Use Redis for fast data.
- **Network Lag**: Moving data takes too long.

*Fix:* Keep servers close together (same zone). Only send necessary data.

### Disaster Recovery

- **Region Outage**: If a whole data center goes down, switch to a backup region.
- **Bad Update**: If a new model version breaks things, roll back to the old one immediately.

## Extra Discussion Points

### Option A: Using a Queue (Recommended)

**Queue sits BEFORE the Batcher.**

- **Why:** If the Batcher crashes, the request is safe in the queue (Redis/Kafka).
- **Benefit:** Keeps Paid and Free users separated easily.

### Option B: Fast but Risky (In-Memory)

**Batching happens inside the API Gateway memory.**

- **Why:** It's faster (no queue hop).
- **Risk:** If the server crashes, you lose the requests.
- **Use Case:** Only if speed is the *only* thing that matters.

### Decision: Saving Requests to Disk vs Memory

- **Kafka (Disk):** Safe. No data loss. Slower.
- **Redis/Memory:** Fast. Some risk of data loss on crash.
- **Verdict:** For this problem, **Redis** is usually best because we need low latency, but **Kafka** is better if these are financial/critical transactions.

### Queue Length

- **Normal:** The queue should be almost empty (0-30 requests).
- **Bad:** If the queue grows > 500, the system is failing.

### GPU Utilization Target

- **Target:** 70-80%.
- **Why not 100%?** If you run at 100%, any tiny spike creates a massive queue instantly. You need "headroom" to absorb bumps in traffic.

## Mistakes to Avoid

- **Unlimited Queues**: Never let a queue grow forever; it will crash the server.
- **One Queue for Everyone**: Free users will block Paid users. Use separate queues.
- **Ignoring Cold Start**: Forgetting that new GPUs take 5 minutes to start.
- **Too Many Retries**: If the system is down, retrying continuously makes it harder to recover.
- **No Backpressure**: You must be able to tell users "Stop" when the system is full.

## How to Pass the Interview

- **Go Deep**: Pick 2-3 areas (like Batching or Rate Limiting) and explain them very well.
- **Be Practical**: Show you know GPUs are expensive and latency matters.
- **Explain Trade-offs**: Always say "I chose X because..." and explain why Y was worse for this case.
- **Use Numbers**: Don't just say "it scales." Say "At 10,000 RPS, we need X servers."

## Practice Questions

- **Estimation**: If you have 10,000 RPS and each request takes 100ms, how many GPUs do you need? (Don't forget to ask about batch size!)
- **Scaling**: How do you handle traffic while waiting 5 minutes for new GPUs to turn on?
- **Monitoring**: Latency just doubled. What is the first thing you check?
- **Rate Limiting**: Design a rule that slows down users when the queue gets too long.
- **Cost**: How do you balance saving money (fewer GPUs) with being fast (more GPUs)?

## Study Materials

- **Load Balancing**: Round-robin vs Least Connections.
- **Queues**: Pub-Sub vs Point-to-Point.
- **Rate Limiting**: Token Bucket algorithm.
- **GPU Metrics**: FLOPs and Memory Bandwidth.

## Final Thoughts

- This is a **practical** interview.
- They want to see if you understand **real systems**, not just theory.
- Always have a reason for your choices.
- Remember: GPUs are expensive! Using them efficiently is a big part of the answer.

*原帖: https://www.1point3acres.com/interview/thread/7100015*

---

## Prompt Playground System Design

## The Design Problem

**Goal:** Design a "playground" tool for Prompt Engineering, similar to the OpenAI Playground or Anthropic Console. This is a **full-stack system design** question. You need to focus on product features, how the UI looks, how the code works, and how it scales.

### What is Prompt Engineering?

**Prompt engineering** means testing and changing input text (prompts) to get the best result from an AI model.

- **Not a Chatbot:** This is not like ChatGPT. There is no conversation history.
- **Independent Runs:** Every time you click "Run," the model starts fresh. It has no memory of the previous run.

### Example User Flow

- **Write:** A user types: "Write a recipe."
- **Refine:** They change it to: "You are a chef. Write a recipe for pasta."
- **Test:** They add examples of good recipes to help the model.
- **Repeat:** They keep changing the prompt until the result is perfect.
- **Save:** They save the best version to use later.

### Follow-up Questions

The interviewer might ask about these harder topics:

- **Scale:** How do we handle 10MB text files?
- **Versions:** How do we track changes if a user saves 1000 times?
- **Cost:** How do we stop users from spending too much money on the LLM API?
- **Search:** How do you search through huge text documents?

## Step 1: Defining the Requirements

First, ask questions to understand exactly what you need to build.

### Questions to Ask

**Features:**

- Can users create, edit, and save prompts?
- Do we need to save the history of changes (version control)?
- Does it support different models (like GPT-4, Claude)?
- Can users share prompts?
**Constraints:**

- **Max Size:** How big can a prompt be? (Answer: 10MB for editing).
- **Users:** How many people at once? (Answer: Thousands).
- **Speed:** Do we need real-time streaming? (Answer: Yes).

### Summary of Needs

**Functional Requirements (What it does):**

- **Editor:** A text box that handles huge text (10MB). Note: 10MB is about 2.5 million tokens, which is too big for most models to actually run, but we must store it.
- **Execution:** Send prompts to an API (like OpenAI) and stream the answer back.
- **History:** Auto-save versions so users can go back to old drafts.
- **Library:** Organize prompts with tags and search.
- **Sharing:** Create links to share prompts with others.
**Non-Functional Requirements (How it performs):**

- **Speed:** No lag when typing in a 10MB file.
- **Reliability:** Do not lose data if the browser crashes.
- **Scalability:** Support thousands of users editing at the same time.

## Step 2: Estimating Scale and Costs

Let's do some math to see how big the system needs to be.

### Assumptions

- **Users:** 1 million total users.
- **Daily Usage:** 10,000 users per day.
- **Prompt Size:** Most are small (1KB), but some are huge (10MB).
- **Read vs Write:** Users read/view prompts much more than they save them (80% read, 20% write).

### Calculations

**Traffic:**

- Reads: ~0.6 requests per second (very low).
- Writes: ~0.12 requests per second (very low).
- **Conclusion:** Traffic is low. We don't need complex database sharding yet.
**Storage:**

- Prompts: 1M users × 10 prompts × 1KB = 10GB.
- Versions: If we save every version, it gets big (300GB).
- **Conclusion:** Storage is cheap. We can use S3 for big files and a database for small ones.
**Costs:**

- **LLM API Cost:** This is the most expensive part.
- If we use high-end models (like Claude 3.5 Sonnet), it could cost $450/day.
- **Strategy:** We must use **Caching** to save money. If a user runs the exact same prompt twice, show the saved result instead of paying the API again.

## Step 3: API Definition

We need clear rules for how the frontend (browser) talks to the backend (server).

### Main API Calls

```typescript
// Managing Prompts
createPrompt(userId: string, content: string, tags: string[]): Promise<Prompt>
updatePrompt(promptId: string, content: string): Promise<PromptVersion>
getPrompt(promptId: string): Promise<Prompt>

// Managing Versions (History)
getVersions(promptId: string): Promise<PromptVersion[]>
revertToVersion(promptId: string, versionNumber: number): Promise<PromptVersion>

// Running the Prompt
// Returns an ID to track the job
executePrompt(promptId: string, model: string, params: ModelParams): Promise<ExecutionId>

// Real-time Updates (WebSocket)
// The server sends these messages to the client:
{
  type: "TOKEN",      // A piece of the answer
  text: "..."
}
{
  type: "DONE",       // Finished
  cost: 0.05          // How much it cost
}
```

## Step 4: Database Schema Design

This is how we organize data in the database.

### The Data Model

We will use **PostgreSQL** because our data is structured and relationships are important.

**1. Prompts Table**

- `id`: Unique ID.
- `user_id`: Who owns it.
- `current_version`: The number of the latest version.
- `content_preview`: The first 500 characters (for fast searching).
- *Note: We do NOT store the full text here.*
**2. PromptVersions Table**

- `prompt_id`: Links to the prompt.
- `version_number`: e.g., Version 1, Version 2.
- `is_snapshot`: **True** if this is a full copy. **False** if it is just a list of changes (diff).
- `content`: The text (or a link to S3 if it is larger than 100KB).
**3. Executions Table**

- `id`: Unique job ID.
- `status`: Queued, Running, Success, or Failed.
- `cost_usd`: How much this run cost.
- `response_text`: The answer from the AI.

### Storage Strategy

- **Snapshots vs. Diffs:** To save space, we don't save the full text every time.

**Snapshot:** Save the full text every 10th version (v1, v10, v20).
- **Diff:** For versions in between (v2-v9), only save the *changes* from the previous version.

## Step 5: Architecture Overview

Here is how the different parts of the system connect.

### Component Diagram

- **Client (Browser):**

Uses **Monaco Editor** (like VS Code) to handle large text files smoothly.
- Uses **IndexedDB** to save drafts on your computer so you don't lose work if internet fails.
- **Load Balancer:**

Sends traffic to the API servers.
- **API Servers (Node.js):**

Handles requests.
- Checks if the user is allowed (Auth).
- Connects to WebSockets.
- **Redis (Cache):**

Stores recent prompts for speed.
- Counts requests to limit usage (Rate Limiting).
- **PostgreSQL (Database):**

Stores user data and small prompts.
- **S3 (File Storage):**

Stores huge prompts (over 100KB).
- **Bull Queue:**

A waiting list for jobs. If many people click "Run" at once, this puts them in line.
- **LLM API:**

External services like OpenAI or Anthropic.

### How Data Moves (The Flow)

**When a User Clicks "Run":**

- Browser sends a WebSocket message: "Run this prompt."
- Server checks: "Is the prompt too long for this model?"
- Server puts the job in the **Bull Queue**.
- A background worker picks up the job and calls the LLM API.
- As the API sends text back, the worker streams it to the Browser via WebSocket.
- When finished, the result is saved to the Database.

## Step 6: Deep Dive into Key Components

In an interview, focus on these hard problems.

### 1. Handling 10MB Prompts

**The Problem:** 10MB of text makes browsers slow. Also, AI models cannot read 10MB (context window limits).

- **Browser Fix:** Use **Monaco Editor** with "virtual scrolling." This only draws the text you can currently see on the screen, not the whole file.
- **Execution Fix:**

Calculate the number of tokens using a tokenizer library.
- **Validate:** If the prompt is 10MB (2.5M tokens) but the model only supports 200K tokens, **block the request**. Show an error: "Prompt too long."
- The 10MB limit is for *storage and editing*, not for running the AI.

### 2. Version Control (Snapshots + Diffs)

**The Problem:** If a user saves 1000 times, storing 10MB 1000 times is too expensive.
**The Solution:**

- **Version 1:** Save full text (Snapshot).
- **Version 2:** Save only the changes (Diff).
- ...
- **Version 10:** Save full text again (Snapshot).
- **Reconstruction:** To read Version 5, the system takes Snapshot 1 and adds the changes from V2, V3, V4, and V5.

### 3. Syncing Multiple Tabs

**The Problem:** A user has the same prompt open in two tabs.
**The Solution:**

- **Same Device:** Use `BroadcastChannel` API. If you type in Tab A, Tab B updates automatically.
- **Conflict:** If Tab A and Tab B try to save different things at the exact same time, use **Optimistic Locking**. The server checks the version number. If they don't match, ask the user which version to keep.

### 4. Search Strategy

**The Problem:** Searching the full text of huge prompts is slow and expensive.
**The Solution:**

- **Fast Search:** Store the first 500 characters in PostgreSQL. This is free and fast.
- **Deep Search:** Use **Elasticsearch** for the full text, but truncate prompts to 100KB to save money. Most important keywords are usually at the start.

## Step 7: Fixing Performance Issues

Identifying where the system might break.

- **Cost of LLM API:**

*Risk:* Users running the same prompt over and over cost us money.
- *Fix:* **Cache responses.** If the prompt + model + settings are identical, return the saved answer from the last run.
- **Latency (Slowness):**

*Risk:* Loading a 10MB prompt from S3 takes time.
- *Fix:* Use a CDN (Content Delivery Network) or cache active prompts in Redis.
- **Rate Limits:**

*Risk:* OpenAI blocks us because we send too many requests.
- *Fix:* Use the **Queue**. If we hit the limit, hold the jobs in the queue and retry them later.

## Additional Design Details

### API Design

We use **Cursor-based Pagination**.

- Instead of saying "Page 1, Page 2," we say "Give me 50 items starting after this specific ID."
- This is faster for databases and works better when data is constantly being added.

### UI Layout

- **Left:** Library/History sidebar.
- **Center:** The big Editor.
- **Right:** Configuration (Temperature, Model selection).
- **Bottom:** The output window (streaming text).

### Security

- **Prompt Injection:** Warn users if a shared prompt looks dangerous.
- **Data Privacy:** Allow users to delete their data fully (GDPR).
- **Access:** Use JWT tokens for login.

## Comparing Different Approaches

**Version Control:**

- *Option A (Save Everything):* Simple code, but storage costs are huge.
- *Option B (Snapshots + Diffs):* Complex code, but saves massive amounts of storage. **We chose B.**
**Streaming:**

- *Option A (WebSockets):* Fast, two-way communication. Harder to scale.
- *Option B (SSE - Server Sent Events):* Easier, but only one-way (Server to Client).
- *Decision:* **WebSockets** are better here because we need to send "Stop Generation" signals and other commands while streaming.

## Interview Advice

**How to use this guide:**

- Do **not** try to memorize every word.
- In a 45-minute interview, pick **2 or 3 deep topics** (like Version Control or Handling Large Files) and explain them well.
**Key Points to Remember:**

- **Not a Chatbot:** Emphasize that each run is standalone.
- **Storage vs. Execution:** 10MB is fine to store, but impossible to run on current models. You must explain this distinction.
- **Trade-offs:** Always say "We could do X or Y. I chose X because..." (e.g., "I chose Diffs to save storage, even though it makes reading slightly slower").

*原帖: https://www.1point3acres.com/interview/thread/7100017*

---

## Recipe Manager (Online Assessment)

## Problem Summary

You need to build a recipe management system that runs in memory. The problem has **4 levels**. Each level adds new features to the previous one:

- **Level 1**: Basic actions (Create, Read, Update, Delete).
- **Level 2**: Search for recipes and sort the results.
- **Level 3**: Add users and check permissions.
- **Level 4**: Save history and restore old versions.
You must finish the current level to move to the next one. You can always use data from earlier levels.

**Time Limit**: 90 minutes

## Level 1: Basic Operations

### Goal

Start with an empty system. You need to write functions to create, find, change, and remove recipes.

### Functions

#### add_recipe

```python
add_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

- Makes a new recipe using an ID, a name, and a list of ingredients.
- Returns `True` if the recipe is created.
- Returns `False` if:

The ID already exists.
- The name already exists (ignore case).
**Rule:** Recipe names must be unique. If "Pasta Carbonara" exists, you cannot add "pasta carbonara" or "PASTA CARBONARA".

#### get_recipe

```python
get_recipe(self, recipe_id: str) -> dict | None
```

- Finds a recipe by its ID.
- Returns a dictionary with `id`, `name`, and `ingredients`.
- Returns `None` if the recipe is missing.

#### update_recipe

```python
update_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

- Changes the name and ingredients of an existing recipe.
- Returns `True` if successful.
- Returns `False` if:

The recipe does not exist.
- The new name is taken by a **different** recipe.
**Rule:** You can keep the same name for the recipe you are editing. You just cannot use a name that belongs to someone else.

#### delete_recipe

```python
delete_recipe(self, recipe_id: str) -> bool
```

- Removes the recipe with the matching ID.
- Returns `True` if deleted.
- Returns `False` if the recipe does not exist.

## Level 2: Finding and Organizing Data

### Goal

Add a way to search for recipes. You must return the results in a specific order.

### New Functions

#### search_recipes

```python
search_recipes(self, query: str) -> list[dict]
```

- Finds recipes where the name contains the `query` text (ignore case).
- Returns a list of recipes sorted by:

**First**: Number of ingredients (Low to High).
- **Second**: Recipe ID (Low to High).
- Returns an empty list if nothing is found.

#### get_all_recipes

```python
get_all_recipes(self) -> list[dict]
```

- Returns every recipe in the system.
- The list must use the same sorting rules as `search_recipes`.

## Level 3: Adding Users

### Goal

Add a user system. Some actions now require a valid user ID to work.

### New Functions

#### add_user

```python
add_user(self, user_id: str, username: str) -> bool
```

- Creates a new user.
- Returns `True` if created.
- Returns `False` if the user ID already exists.

#### edit_recipe

```python
edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

- Updates a recipe, but checks the user first.
- Returns `True` if successful.
- Returns `False` if:

The `user_id` is invalid.
- The `recipe_id` does not exist.
- The new name is taken by another recipe.
**Note:** This function replaces the old update logic. It does the same thing but adds a user check.

## Level 4: History and Rollbacks

### Goal

Stop overwriting data. Instead, save every change as a new "version" of the recipe.

### Changes to Existing Functions

#### edit_recipe (Updated)

```python
edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool
```

- Now, this function **adds a new version** to the history list instead of deleting the old data.
- Versions are numbered (1, 2, 3...).
- The newest version is the "current" one.
- All validation rules from Level 3 still apply.

### New Functions

#### get_recipe_history

```python
get_recipe_history(self, recipe_id: str) -> list[dict] | None
```

- Returns a list of all versions for a recipe.
- The list is ordered from oldest to newest.
- Returns `None` if the recipe is missing.

#### rollback_recipe

```python
rollback_recipe(self, user_id: str, recipe_id: str, version: int) -> bool
```

- Copies an old version and saves it as the **newest** version.
- This does NOT delete any history. It just adds a copy of the old data to the end of the list.
- Returns `True` if successful.
- Returns `False` if:

The user or recipe is invalid.
- The version number does not exist.
- The old name now conflicts with another recipe's current name.
**Example:**

- History: v1("Pasta"), v2("Spaghetti").
- `rollback_recipe` to version 1.
- Result: v1("Pasta"), v2("Spaghetti"), v3("Pasta").

## Critical Rules

### Name Uniqueness

- "PASTA", "Pasta", and "pasta" are the same name.
- Always ignore case when checking for duplicates.
- Store the name exactly as the user typed it.

### Rollback Conflicts

- When restoring an old version, check its name.
- If that old name is now used by a **different** recipe, the rollback must fail.
- A recipe never conflicts with its own history.

### Version Numbers

- Start counting at 1.
- Every edit or rollback adds +1 to the version number.
- Never reset or reuse numbers.

## System Limitations

- IDs are strings.
- Recipe names are never empty.
- Ingredient lists can be empty.
- Code must be fast enough for standard use.

## Code Solution

**⚠️ Disclaimer**: Try to solve this yourself first. This code is for reference to check your work.

**Note**: This code shows the final state (Level 4). It includes the user check and version history logic inside `edit_recipe`.

```python
class RecipeManager:
    def __init__(self):
        self.recipes = {}  # Stores recipe ID -> data and history
        self.users = {}    # Stores user ID -> user data
        self.name_to_id = {}  # lowercase name -> recipe_id (for checking duplicates)

    # ==================== Level 1: Basic Operations ====================

    def add_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool:
        # Check if ID exists
        if recipe_id in self.recipes:
            return False

        # Check if name exists (ignore case)
        if name.lower() in self.name_to_id:
            return False

        # Create recipe with history list
        self.recipes[recipe_id] = {
            'id': recipe_id,
            'history': [{'name': name, 'ingredients': ingredients.copy()}]
        }
        self.name_to_id[name.lower()] = recipe_id
        return True

    def get_recipe(self, recipe_id: str) -> dict | None:
        if recipe_id not in self.recipes:
            return None

        recipe = self.recipes[recipe_id]
        current = recipe['history'][-1]  # Get the newest version
        return {
            'id': recipe_id,
            'name': current['name'],
            'ingredients': current['ingredients'].copy()
        }

    def update_recipe(self, recipe_id: str, name: str, ingredients: list[str]) -> bool:
        if recipe_id not in self.recipes:
            return False

        # Check for name conflict (ignore case), but allow same recipe to keep name
        existing_id = self.name_to_id.get(name.lower())
        if existing_id is not None and existing_id != recipe_id:
            return False

        # Remove the old name from the tracking map
        old_name = self.recipes[recipe_id]['history'][-1]['name']
        del self.name_to_id[old_name.lower()]

        # Update recipe (Overwrites data for Levels 1-3)
        self.recipes[recipe_id]['history'] = [{'name': name, 'ingredients': ingredients.copy()}]
        self.name_to_id[name.lower()] = recipe_id
        return True

    def delete_recipe(self, recipe_id: str) -> bool:
        if recipe_id not in self.recipes:
            return False

        # Remove name from tracking map
        current_name = self.recipes[recipe_id]['history'][-1]['name']
        del self.name_to_id[current_name.lower()]

        # Delete the recipe
        del self.recipes[recipe_id]
        return True

    # ==================== Level 2: Finding and Organizing Data ====================

    def _sort_recipes(self, recipes: list[dict]) -> list[dict]:
        """Sort by ingredient count (low to high), then by ID."""
        def sort_key(r):
            ingredient_count = len(r['ingredients'])
            recipe_id = r['id']
            # Sort numerically if ID is a number, otherwise alphabetically
            if recipe_id.isdigit():
                return (ingredient_count, 0, int(recipe_id), "")
            else:
                return (ingredient_count, 1, 0, recipe_id)
        return sorted(recipes, key=sort_key)

    def search_recipes(self, query: str) -> list[dict]:
        results = []
        query_lower = query.lower()

        for recipe_id, recipe in self.recipes.items():
            current = recipe['history'][-1]
            if query_lower in current['name'].lower():
                results.append({
                    'id': recipe_id,
                    'name': current['name'],
                    'ingredients': current['ingredients'].copy()
                })

        return self._sort_recipes(results)

    def get_all_recipes(self) -> list[dict]:
        results = []
        for recipe_id, recipe in self.recipes.items():
            current = recipe['history'][-1]
            results.append({
                'id': recipe_id,
                'name': current['name'],
                'ingredients': current['ingredients'].copy()
            })
        return self._sort_recipes(results)

    # ==================== Level 3: Adding Users ====================

    def add_user(self, user_id: str, username: str) -> bool:
        if user_id in self.users:
            return False

        self.users[user_id] = {'id': user_id, 'username': username}
        return True

    def edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool:
        # Check user validity
        if user_id not in self.users:
            return False

        # Check if recipe exists
        if recipe_id not in self.recipes:
            return False

        # Check name conflict (ignore case), excluding self
        existing_id = self.name_to_id.get(name.lower())
        if existing_id is not None and existing_id != recipe_id:
            return False

        # Remove old name from tracking map
        old_name = self.recipes[recipe_id]['history'][-1]['name']
        del self.name_to_id[old_name.lower()]

        # Add new version (Level 4 behavior)
        self.recipes[recipe_id]['history'].append({
            'name': name,
            'ingredients': ingredients.copy()
        })
        self.name_to_id[name.lower()] = recipe_id
        return True

    # ==================== Level 4: History and Rollbacks ====================

    def get_recipe_history(self, recipe_id: str) -> list[dict] | None:
        if recipe_id not in self.recipes:
            return None

        history = []
        for i, version in enumerate(self.recipes[recipe_id]['history'], 1):
            history.append({
                'version': i,
                'name': version['name'],
                'ingredients': version['ingredients'].copy()
            })
        return history

    def rollback_recipe(self, user_id: str, recipe_id: str, version: int) -> bool:
        # Check user
        if user_id not in self.users:
            return False

        # Check recipe
        if recipe_id not in self.recipes:
            return False

        history = self.recipes[recipe_id]['history']

        # Check if version exists (starts at 1)
        if version < 1 or version > len(history):
            return False

        # Get data from the old version
        old_version = history[version - 1]

        # Check name conflict: if old name is different, does it exist elsewhere?
        current_name = history[-1]['name']
        if old_version['name'].lower() != current_name.lower():
            existing_id = self.name_to_id.get(old_version['name'].lower())
            if existing_id is not None and existing_id != recipe_id:
                return False

        # Remove current name from tracking map
        del self.name_to_id[current_name.lower()]

        # Add the old version data as a NEW version at the end
        history.append({
            'name': old_version['name'],
            'ingredients': old_version['ingredients'].copy()
        })
        self.name_to_id[old_version['name'].lower()] = recipe_id
        return True
```

*原帖: https://www.1point3acres.com/interview/thread/7100006*

---

## LRU Cache (Python)

## The Problem

You are given a Python code for an in-memory LRU (Least Recently Used) cache. The code works, but there is a mistake in how it creates keys.

The error happens when the cache tries to handle variable arguments (`*args`) and keyword arguments (`**kwargs`).

Your task is to:

- **Read** the current code and see how it works.
- **Find the mistake** in the key creation step.
- **Fix the code** so it handles `*args` and `**kwargs` correctly.

### What You Need to Do

Your solution must:

- **Find the error** — Understand why `*args` and `**kwargs` break the current key maker.
- **Make keys hashable** — Change arguments into a format that can be used as dictionary keys.
- **Handle all arguments** — Work correctly with both `*args` and `**kwargs`.
- **Keep the cache accurate** — Ensure the same inputs always create the exact same key.

### Helpful Tips

- **Python Knowledge**: You need to know:

How `*args` and `**kwargs` work in Python.
- Which data types work as dictionary keys (hashable) and which do not.
- How to change arguments into a hashable format.
- **Hints**:

Remember that keyword arguments can be in any order. For example, `func(a=1, b=2)` is the same as `func(b=2, a=1)`.
- Think about changing unhashable types (like lists or dicts) into hashable types (like tuples or frozensets).
- Check Python's `functools` library for ideas.

## Part 2: Saving Data to Disk

After fixing the bug, you need to update the cache to save data to the disk. The system must:

- **Recover after a crash** — If the program stops or restarts, it should reload the old data.
- **Save data safely** — Do not lose data during normal use or if the program crashes.
- **Keep LRU order** — The saved data must remember which items were used most recently.

### System Requirements

- **Save to disk** — Store cache items in a file.
- **Reload on start** — Read the file and fill the cache when the program begins.
- **Keep data matching** — Make sure the memory cache and the file have the same data.
- **Watch speed** — Find a balance between writing fast and saving safely.

### Things to Discuss

**Discussion Points:**

- **File Format**:

How will you save the data (JSON, pickle, or a custom format)?
- Should you use one file or many files?
- **How to Write**:

Write-through: Save to disk every time (slow but safe).
- Write-back: Save in groups later (fast but risky).
- Append-only log: Add new changes to the end of a log file.
- **How to Recover**:

How do you rebuild the LRU order?
- Do you need extra data like timestamps?
- **Speed vs. Safety**:

Blocking writes vs. non-blocking (async) writes.
- Choosing between speed and data safety.
- The cost of Disk I/O.

## Extra Questions

These questions are for talking only. You do not need to write code. Be ready to explain your thoughts.

### 1. Ways to Remove Old Data

**Question:** Besides LRU, what other rules can we use to remove items from the cache? When is each one useful?

**Discussion Points:**

- **LRU (Least Recently Used)**: Remove the item not used for the longest time.
- **LFU (Least Frequently Used)**: Remove the item used the least amount of times.
- **FIFO (First In First Out)**: Remove the oldest item added.
- **Random**: Remove an item by chance.
- **TTL (Time To Live)**: Remove items after a set time expires.
- **Trade-offs**: Each rule is good for different situations.

### 2. Caching Across Multiple Computers

**Question:** How would you make this cache work on many computers in a distributed system?

**Discussion Points:**

- **Consistency**: How to keep data the same everywhere.

Shared distributed cache (like Redis or Memcached).
- Strategies to delete old data (invalidation).
- Eventual consistency vs strong consistency.
- **Partitioning**: How to split data between computers.

Consistent hashing.
- Splitting by range.
- **Replication**: Copying data so it is safe if one computer fails.
- **Network**: The cost of sending data between computers.

### 3. Handling Multiple Users (Concurrency)

**Question:** How would you make the cache safe if many threads use it at the same time?

**Discussion Points:**

- **Locking**:

Global lock (easy but slow).
- Fine-grained locking (faster but harder to code).
- Read-write locks (good for many reads).
- **Lock-free**: Using atomic operations.
- **Tools**: Mutexes, semaphores, condition variables.
- **Deadlocks**: How to avoid getting stuck.
- **Speed**: How locks affect performance.

### 4. Managing Memory Usage

**Question:** How do you stop the cache from using too much RAM?

**Discussion Points:**

- **Limits**:

Max number of items.
- Max memory usage.
- Size limit per item.
- **Measuring**: How to calculate the size of an object.
- **When to clear**: When to start removing items.
- **Pressure**: Cleaning up before the system runs out of memory (OOM).
- **Trade-offs**: Balancing cache hits vs. using memory.

*原帖: https://www.1point3acres.com/interview/thread/7100002*

---

## Distributed Model Deployment System Design

## The Challenge

You need to design a system to download a **large ML model** (500GB) and send it to **all GPU workers** in a data center. The system must work quickly, handle limited internet speed, and keep working even if computers fail.

### The Rules & Limits

- **Model size**: 500GB (Very large file).
- **Number of workers**: 100 to 1000 computers with GPUs.
- **External bandwidth**: 10 Gbps (Speed to download from the internet/cloud).
- **Internal bandwidth**: 10 Gbps "full-duplex" per worker.

*Note:* "Full-duplex" means a worker can upload at 10 Gbps and download at 10 Gbps at the exact same time.
- **Goal**: Make the total time to deploy the model to EVERY worker as short as possible.
- **Reliability**: The system must not stop if a worker crashes.

### Follow-up Questions to Expect

- **Strategy**: Why is a pipeline better than a tree or doing it one by one? Show the math.
- **Bandwidth**: How do we use 100% of the network speed?
- **Chunking**: Why split the file into small pieces? How big should pieces be?
- **Failures**: What if a worker in the middle of the chain breaks?
- **Scaling**: Does it still work with 10,000 workers?

## Proposed Solution

**⚠️ Note**: This is a sample guide. Try to solve the problem yourself first. Use this to check your work.

## Step 1: Understanding the Requirements

First, we need to ask questions to understand exactly what we are building.

### Questions to Ask

**Features:**

- **Updates:** Do we send only new parts of the file? (Assume yes).
- **Versions:** Do we need to keep old versions?
- **Rollback:** Can we quickly switch back to an old model?
**Scope:**

- **Tasks:** Are we just moving files, or loading them into GPU memory too?
- **Locations:** Is this for one data center or many?
**Performance:**

- **Time Limit:** How fast must it be? (Target: ~8 minutes for 100 workers).
- **Frequency:** How often do we do this? (Daily).
- **Failures:** How often do workers break? (1-5% of the time).

### Summary of Needs

**1. Moving the Data**

- Download 500GB from cloud storage (S3/GCS).
- Send to 100-1000 workers.
- Split files into "chunks" (pieces) to send them faster.
**2. Managing the Process**

- A central "Coordinator" decides the order of workers.
- Track which worker has which chunk.
- Handle new workers joining or leaving.
**3. Handling Errors**

- Check if workers are alive using a "heartbeat".
- If a worker fails, route data around them.
- Retry if a file piece is corrupted.
**4. Data Safety**

- Use "Checksums" (SHA256) to make sure files are not broken.
- Verify the whole file at the end.
**5. Monitoring**

- Show a progress bar for the deployment.
- Track network speed and errors.

## Step 2: Doing the Math

We need to estimate how long different methods will take. This proves why our choice is best.

**Assumptions:**

- **Model:** 500GB.
- **Network:** 10 Gbps.
- **Chunk Size:** 1GB.

### Option 1: Sequential (One by One) - The Bad Way

Every worker downloads the file directly from the internet at the same time. The 10 Gbps internet connection is shared by everyone.

- **Speed per worker:** 10 Gbps / 100 workers = 0.1 Gbps.
- **Time:** 500GB / 0.1 Gbps = **~11 hours**.
**Result:** Too slow. The internet connection is the bottleneck.

### Option 2: Binary Tree - The Okay Way

Worker A downloads it. Worker A sends it to B and C. B sends to D and E, etc.
At every level, the parent splits its upload speed between two children.

- **Root download:** 400 seconds.
- **Each level after:** 800 seconds (because speed is split).
- **Total for 100 workers:** **~100 minutes**.
**Result:** Better, but splitting bandwidth slows it down.

### Option 3: Pipeline (Chain) - The Best Way

Worker 1 gets a small piece (Chunk 1). It immediately sends Chunk 1 to Worker 2, while downloading Chunk 2.
This creates a chain. All workers upload and download constantly.

- **Download Phase:** Time to pull 500GB into the first worker = 400 seconds.
- **Propagation Phase:** Time for the last chunk to hop from Worker 1 to Worker 100.

Time per hop: 0.8 seconds.
- 99 hops: ~80 seconds.
- **Total Time:** 400s + 80s = **~8 minutes**.
**Result:** This is the winner. It is very fast regardless of how many workers you add.

## Step 3: API Design

We define how the parts of the system talk to each other.

### Coordinator API

The central brain of the system.

```typescript
// Start a new deployment
interface DeploymentRequest {
  modelId: string;
  sourceUrl: string;       // Where the file lives (S3)
  targetWorkers: string[]; // List of worker IDs
}

// Check how it is going
createDeployment(request: DeploymentRequest): Promise<DeploymentResponse>
getDeploymentStatus(deploymentId: string): Promise<DeploymentStatus>
```

### Worker API

The computers receiving the model.

```typescript
// Tell Coordinator "I am here"
registerWorker(info: WorkerInfo): Promise<{ registered: boolean }>

// Tell Coordinator "I am still alive" (Heartbeat)
interface HeartbeatRequest {
  workerId: string;
  status: 'idle' | 'downloading' | 'complete' | 'failed';
  chunksReceived: number[]; // Which pieces do I have?
}

sendHeartbeat(request: HeartbeatRequest): Promise<{ continue: boolean }>

// Ask another worker for a file piece
requestChunk(request: ChunkRequest): Promise<ChunkResponse>
```

### Manifest File

This is the "map" of the file. It lists all the pieces (chunks).

```typescript
interface Manifest {
  modelId: string;
  totalSize: number;
  chunkSize: number;
  numChunks: number;
  // List of all pieces and their verification codes
  chunks: ChunkInfo[];
  globalChecksum: string; // Verification for the whole file
}
```

## Step 4: Data Structure Design

How we store information in the database.

**1. Manifest (The Map)**
Shared with all workers so they know what to download.

```go
type Manifest struct {
    ModelID        string
    NumChunks      int
    Chunks         []ChunkInfo
    GlobalChecksum string     // SHA256 hash
}
```

**2. Worker State (The Status)**
Stored in the Coordinator's memory (or Redis/etcd).

```go
type WorkerState struct {
    WorkerID           string
    Status             WorkerStatus
    ChunksReceived     []int      // List of chunk IDs owned
    DownstreamWorker   string     // Who do I send data to?
    UpstreamWorker     string     // Who do I get data from?
}
```

**Storage Choices:**

- **etcd:** Use this for the Coordinator state. It handles failures well.
- **Local Disk:** Workers save the file chunks here.

## Step 5: System Architecture

### The Diagram

Imagine a long line of people passing buckets of water.

- **External Storage (S3):** The water source.
- **Coordinator:** The person shouting directions.
- **Workers (W1, W2, ... W100):** The people passing buckets.
**Flow:**
`S3` --> `W1` --> `W2` --> `W3` ... --> `W100`

### How It Works (The Phases)

**Phase 1: Setup**
The Coordinator chops the file list into 500 pieces (1GB each). It tells the workers: "Get ready. W1 gives to W2, W2 gives to W3..."

**Phase 2: Seeding**
Worker 1 (W1) downloads "Chunk 0" from S3.
As soon as W1 has Chunk 0, it sends it to W2.
At the same time, W1 downloads Chunk 1 from S3.

**Phase 3: The Pipeline**
Everyone is busy.

- W1 is downloading from S3 and sending to W2.
- W2 is receiving from W1 and sending to W3.
- This happens for all 500 chunks.
**Phase 4: Finish**
Workers verify the files using checksums. They tell the Coordinator "Success".

## Step 6: Deep Dive

### 1. The Pipeline Logic

This code shows how workers do two things at once: receive and send.

```python
# Coordinator logic
def create_deployment(model_id, workers):
    # 1. Create file list and checksums
    manifest = generate_manifest(model_id)

    # 2. Arrange workers in a line (Topology)
    # Put workers in the same rack next to each other
    topology = assign_pipeline_topology(workers) 
    # Result: [W1, W2, W3, ..., W100]

    # 3. Tell everyone what to do
    distribute_manifest(workers, manifest)
    start_download(topology[0]) # Start W1

# Worker Logic (Middle Worker)
def middle_worker():
    manifest = receive_manifest()

    # Run two threads at the same time
    
    # Thread 1: Receive Data
    Thread(target=receive_loop).start()
    
    # Thread 2: Send Data
    Thread(target=send_loop).start()

def receive_loop():
    for chunk_id in range(500):
        data = receive_from_upstream(chunk_id)
        if check_hash(data):
            save_to_disk(data)
        else:
            ask_for_retry(chunk_id)

def send_loop():
    for chunk_id in range(500):
        # Wait until I have the chunk
        while not have_chunk_on_disk(chunk_id):
            wait()
        
        data = read_from_disk(chunk_id)
        send_to_downstream(chunk_id, data)
```

### 2. Choosing Chunk Size

How big should the pieces be?

- **Too Small (10MB):** Too much asking/answering overhead. Slow.
- **Too Big (50GB):** The next worker waits too long to start. Pipeline stalls.
- **Just Right (1GB):** Takes about 0.8 seconds to transfer. Good balance.

### 3. Handling Failures

What happens if Worker 3 (W3) crashes?

**Before:** W1 → W2 → **W3** → W4 → W5

- **Detection:** The Coordinator notices W3 stopped sending "heartbeats".
- **Fix:** The Coordinator tells W2 to skip W3 and talk directly to W4.
- **Result:** W1 → W2 → W4 → W5.
- **Recovery:** W4 asks W2 for any pieces it missed.

### 4. Rack Awareness

Data moves faster between computers in the same rack (cabinet).

- **Bad Order:** Rack A -> Rack B -> Rack A -> Rack B. (Lots of jumping).
- **Good Order:** Rack A (all) -> Rack B (all). (Only one jump).
We sort the list of workers by their Rack ID to keep data local.

## Step 7: Fixing Bottlenecks

### 1. External Bandwidth

**Problem:** The download from S3 is only 10 Gbps.
**Solution:** Only the first worker (W1) downloads from S3. Everyone else gets data from W1 via the local network. This saves the internet connection.

### 2. Disk Speed

**Problem:** Writing 500GB quickly can be too fast for hard drives.
**Solution:** Use NVMe SSDs (very fast disks). Write data in parallel streams.

### 3. Coordinator Overload

**Problem:** If 10,000 workers send updates constantly, the Coordinator will crash.
**Solution:**

- Workers only send updates every 10 chunks (batching).
- Use multiple Coordinators (one leader, several backups).

### 4. Corruption

**Problem:** Bits get flipped during transfer. The file is broken.
**Solution:**

- Calculate the SHA256 Hash of every chunk.
- If the hash doesn't match, ask for that chunk again.

## Interview Tips

### What Matters Most

- **Do the Math:** You must compare the Sequential vs. Pipeline times. Prove why Pipeline is best.
- **Identify the Limit:** The 10 Gbps internet link is the main limit (bottleneck).
- **Handle Failures:** A system that crashes when one worker fails is a bad system. Explain how you fix it.
- **Network Topology:** Mention "Rack Awareness." It shows you understand real data centers.

### Common Mistakes

- Forgetting to calculate time.
- Not checking for data corruption (Checksums).
- Making the system too complicated (Keep it simple: a line of workers).
- Ignoring that cross-rack communication is slower.

*原帖: https://www.1point3acres.com/interview/thread/7100001*

---

## Deduplicate Files

## Problem Requirements

You are given a main folder (root directory). Your task is to find all duplicate files inside it. You must return lists of file paths where the files have exactly the same content.

### Example Input and Output

**Folder Structure:**

```python
root/
├── a/
│   ├── f1.mp4
│   └── f2.mp4
└── b/
    ├── f3.mp4
    └── tmp/
        └── f4.mp4
```

**Expected Result:**

```python
[
    ["a/f1.mp4", "a/f2.mp4"],           # Group 1: These files are identical
    ["b/f3.mp4", "b/tmp/f4.mp4"]        # Group 2: These files are identical
]
```

### Rules

- **Look at every file** in the folder and all its sub-folders.
- **Group by content:** Put files with the exact same data into the same group.
- **Duplicates only:** Do not list files that are unique (no duplicates).
- **Check sub-folders:** You must look inside nested directories recursively.

### Simple Solution

Here is a straightforward way to solve this:

- Use `os.walk()` to visit every file in the folder.
- Calculate a full hash (like MD5 or SHA-256) for the **entire content** of each file.
- Group files that have the same hash.
- Return groups that contain more than one file.

### Code Signature

```python
def find_duplicate_files(root_path: str) -> List[List[str]]:
    """
    Find all duplicate files in the directory tree.

    Args:
        root_path: Root directory to search

    Returns:
        List of groups, where each group contains paths to duplicate files
    """
    pass
```

### Important Tips

- You may need to **create test files yourself** during the interview (for example, in Google Colab).
- Think about tricky cases: empty files, shortcuts (symbolic links), or permission errors.
- Consider the time complexity: it depends on the total size of all the files combined.

## Faster Solution

Hashing the entire content of every file is slow if the files are large. We can use a **multi-step process** to avoid reading full files when we don't have to.

### Three-Step Process

- **Step 1 - Check File Size:**

Group files by their size first.
- If two files have different sizes, they cannot be duplicates.
- This is very fast because we only read metadata, not the file content.
- **Step 2 - Check Partial Hash:**

For files that have the same size, read only the first small part (like 1024 bytes).
- Hash this small part.
- If the beginning of the files is different, they are not duplicates.
- **Step 3 - Check Full Hash:**

Only calculate the full hash if the size **and** the partial hash match.
- This ensures the answer is correct but saves a lot of time.

### How Fast is It?

- **Best case:** Most files have unique sizes. We only check metadata. Complexity: O(number of files).
- **Worst case:** All files are the same size and start with the same data. We must hash everything. Complexity: O(total file size).
- **Average case:** Much faster than the simple solution because we filter out most non-duplicates early.

### Code Structure

```python
def find_duplicate_files_optimized(root_path: str) -> List[List[str]]:
    # Step 1: Group by file size
    size_groups = group_by_file_size(root_path)
    # Result: {size1: [file1, file2, ...], size2: [file3, ...], ...}

    # Step 2: For each size group, compute partial hash
    partial_hash_groups = {}
    for files in size_groups.values():
        if len(files) > 1:
            group_by_partial_hash(files, partial_hash_groups)
    # Result: {partial_hash1: [file1, file2, ...], partial_hash2: [file3, ...], ...}
    # Note: Step 3 will handle rare collisions across different sizes

    # Step 3: For each partial hash group, compute full hash
    full_hash_groups = {}
    for files in partial_hash_groups.values():
        if len(files) > 1:
            group_by_full_hash(files, full_hash_groups)
    # Result: {full_hash1: [file1, file2, ...], full_hash2: [file3, ...], ...}

    # Return only groups with duplicates
    return [files for files in full_hash_groups.values() if len(files) > 1]
```

## Follow-up Questions

The interviewer may ask these questions to discuss your design skills. You usually do not need to code the answers, but you should explain your logic.

### 1. Bottlenecks: Disk vs. Processor

**Question:** is this program limited by the disk speed (I/O bound) or the processor speed (CPU bound)?

**Discussion Points:**

**How to find out**:

- **Use profiling tools** to check CPU usage and wait times.
- If the CPU is waiting a lot, it is **I/O bound** (waiting for the disk).
- If the CPU is working 100%, it is **CPU bound** (math is taking too long).
**For this problem**:

- It is usually **I/O bound** because reading files from a disk is slower than calculating hashes.
- **Exception:** If you have a very fast SSD, the disk might be so fast that the CPU becomes the bottleneck.
**How to optimize**:

- **If I/O bound:** Read multiple files at the same time (parallel) or optimize the chunk size.
- **If CPU bound:** Use faster hash algorithms (like xxHash) or use multiple CPU cores.

### 2. Choosing a Hash Algorithm

**Question:** Which hash function would you use (MD5, SHA-256, etc.) and why?

**Discussion Points:**

**Common Options**:

- **MD5:** Fast, but not secure. It is okay for checking duplicates.
- **SHA-256:** Slower, but very secure. The chance of two different files having the same hash is extremely low.
- **xxHash:** Extremely fast. Great for checking files, but not for security.
**Trade-offs**:

- **Speed vs. Accuracy:** Faster hashes (MD5, xxHash) might make mistakes (collisions) slightly more often than slow ones (SHA-256).
- **Security:** You do not need cryptographic security for this task.
**Recommendation**:

- Use **SHA-256** for safety.
- Use **xxHash** if speed is the most important factor.
- **Note on Collisions:** It is theoretically possible for two different files to have the same hash. With SHA-256, this is almost impossible in real life. If you need 100% certainty, compare the files byte-by-byte after the hashes match.

### 3. Scaling to Many Machines

**Question:** How would you solve this if you had millions of files across many computers?

**Discussion Points:**

**MapReduce Method**:

- **Map Phase:** Each computer looks at a list of files. It sends out data like `(hash, file_path)`.
- **Shuffle Phase:** The system groups all files with the same hash together.
- **Reduce Phase:** A computer receives a list of files that share the same hash and confirms if they are duplicates.
**Partitioning**:

- Group files by size first. Send files of the same size to the same machine.
- This keeps the work organized.
**Distributed Storage**:

- Use a database like Redis to store the map: `hash -> [list of file paths]`.
- **Important:** Do not send the actual file content over the network. Only send the hashes.

### 4. Real-Time Monitoring

**Question:** How would you design a system that alerts users immediately when a duplicate is added?

**Discussion Points:**

**System Design**:

- **File Watcher:** Use OS tools (like `inotify` on Linux) to watch for new files.
- **Database**: Keep two tables:

`hash_to_files`: Maps a hash to a list of files.
- `file_to_hash`: Maps a file path to its hash (useful when deleting files).
- **Action**:

**File Added:** Calculate the hash. Check the database. If the hash exists, send an alert.
- **File Deleted:** Look up the file's hash and remove it from the database.
- **Alerts:** Use a queue system (like Kafka) to send notifications to users.

### 5. Picking the Chunk Size

**Question:** How do you decide how big the "partial hash" chunk should be?

**Discussion Points:**

**Factors**:

- **Disk Speed:** Bigger chunks mean fewer read operations.
- **Differentiation:** Bigger chunks are better at finding differences between files.
- **Memory:** Bigger chunks use more RAM.
**Typical Values**:

- **1KB - 4KB:** Good for a quick check.
- **64KB - 1MB:** Better for SSDs where reading data is very fast.
**Testing:**

- The best way to decide is to run tests with different sizes on your specific data and measure the speed.

*原帖: https://www.1point3acres.com/interview/thread/7100000*

---

## Hiring Manager Interview Questions

## Summary

The hiring manager interview at Anthropic looks closely at your past projects, leadership style, and how you work with others. You should expect to talk about your experience in great detail. Focus on technical challenges, how you lead, and how you collaborate with different teams, such as product management.

## Technical Experience & Projects

### 1. Explain a Recent System Architecture

**Advice for Candidates:**

- Be ready to describe the **full system architecture** of your current or recent work.
- **You must use specific numbers**: QPS (Queries Per Second), latency, throughput, data size, and user counts.
- Explain what each part does and how it connects to the others.
- Prove that you know the system very well, not just a little bit.
- Interviewers will ask hard questions about your numbers and technical choices.

### 2. Your Hardest Technical Problem

**Advice for Candidates:**

- Pick a problem that was actually difficult, not just a small bug.
- Explain *why* it was hard (was the scale big? was the logic complex? was the goal unclear?).
- Walk through your steps and how you thought about the problem.
- Talk about the trade-offs you had to consider.
- Explain the final result and what you learned from the experience.
- This is a very common question, so prepare for it well.

### 3. Your Best Project

**Advice for Candidates:**

- Focus on the result for both the technology and the business.
- Explain what made this project special or difficult.
- Be clear about what *you* did versus what the *team* did.
- Show that you have deep technical knowledge and understand the project's impact.

## Working with Others

### 4. Working with Product Managers

**Advice for Candidates:**

- **Prepare several stories** about working with product teams.
- This is very important for the hiring manager round.
- Show that you can work well with people who are not technical.
- Explain how you handle technical limits while trying to reach product goals.
- Examples: Deciding which features to build first, changing the scope of work, or discussing if something is technically possible.

### 5. Resolving Disagreements

**Advice for Candidates:**

- This question is asked very often.
- Use a real story where the stakes were high.
- Show that you can stay calm and professional.
- Explain how you tried to understand the other person's point of view.
- Describe how you fixed the issue and what happened next.
- Do not try to look like a hero. Show humility and teamwork.

## Leading and Teaching

### 6. Mentoring and Technical Leadership

**Advice for Candidates:**

- Talk about times you led projects or teams (officially or unofficially).
- Give specific examples of teaching or mentoring other engineers.
- If you were an engineering manager who went back to being an Individual Contributor (IC), talk about both roles.
- Show how you helped guide technical decisions.
- Discuss how you help your teammates improve.

### 7. Leading a Difficult Project

**Advice for Candidates:**

- Focus on leadership skills like assigning tasks, communicating, and removing roadblocks.
- Talk about both technical problems and people problems.
- Show how you kept the team happy and focused on the goal.
- Explain how you handled things when they went wrong.

## Your Goals and Work Style

### 8. Your Future Career Goals

**Advice for Candidates:**

- They might ask this question **first**.
- Be honest about what you want (Technical/IC track vs. Management track).
- Show that you have a plan for your own growth.
- Connect your goals to what Anthropic does.
- Talk about the kind of impact you want to make.

### 9. Your Ideal Work Culture

**Advice for Candidates:**

- Read about Anthropic's culture before the interview.
- Be honest—fitting in is important to them.
- Talk about how you collaborate, how fast you like to work, and your values.
- Show you know the environment where you do your best work.
- Connect this to Anthropic's mission if it matches your own beliefs.

## Key Advice for Success

- **Use Numbers:** Always have metrics ready (QPS, latency, scale, team size, time taken, results).
- **Collaboration Stories:** Have multiple examples of working with product teams and other partners.
- **Show Leadership:** Even as an IC, talk about how you lead technically or teach others.
- **Be Specific:** Do not give vague answers. Use real examples with details.
- **Go Deep:** Be ready to explain every detail of your projects. The interviewer will ask many questions.
- **Show Growth:** Talk about what you learned from your mistakes and challenges.
- **Balance Skills:** This role needs someone good at coding *and* good at working with people.

*原帖: https://www.1point3acres.com/interview/thread/7100013*

---

## Batch Image Processor

## Introduction

In this coding challenge, you will build a tool to edit many images at once. You are given a folder of images and a list of changes (in JSON format). Your job is to apply these changes to each image and save the results.

This test checks if you can:

- **Research quickly** - You can and should look up documentation.
- Read settings from JSON files.
- Read and write files efficiently.
- Make your code run faster using parallel processing.

### Interview Notes

- **Searching online is allowed.** The interviewer wants to see how you learn new APIs.
- You can use any resource (except AI answers).
- **Recommended Libraries:** **Pillow (PIL)** or **scikit-image**. It helps to know one of these before the interview.
- You will start with small images. Later, you must optimize the code to handle large images within a time limit.

## Files and Folders

You get four directories:

```python
project/
├── small_images/      # Small files to test your code
│   ├── image1.png
│   ├── image2.jpg
│   └── ...
├── large_images/      # Big files to check speed/performance
│   ├── photo1.png
│   ├── photo2.jpg
│   └── ...
├── transformations/   # JSON files that list the changes
│   ├── transform1.json
│   ├── transform2.json
│   └── ...
└── output/            # Where you save the finished images
```

You also get helper tools to list files and create output file names.

## How to Change the Images

Every JSON file in the `transformations/` folder lists changes to make in order. There are **six types** of changes:

### Simple Changes (No Settings)

| Type | Description |
| :--- | :--- |
| `grayscale` | Turn the image black and white |
| `flip_horizontal` | Mirror the image left-to-right |
| `flip_vertical` | Mirror the image top-to-bottom |

### Advanced Changes (With Settings)

| Type | Setting | Description |
| :--- | :--- | :--- |
| `scale` | `factor` (float) | Resize the image (e.g., 0.5 is half size) |
| `blur` | `radius` (int) | Blur the image by this amount |
| `rotate` | `angle` (float) | Rotate the image by degrees |

### Example JSON File

```json
{
  "transformations": [
    { "type": "grayscale" },
    { "type": "scale", "factor": 0.5 },
    { "type": "rotate", "angle": 90 }
  ]
}
```

This list tells the program to:

- Turn the image grayscale.
- Shrink it to 50% size.
- Rotate it 90 degrees.

## What You Need to Do

### Part 1: Make it Work

- **Pick a Library**: Choose a Python library that can do all six changes.

Pillow (PIL)
- scikit-image
- OpenCV
- **Write Functions**: Write code to handle each of the six change types.
- **Process the Images**:

Read every transformation JSON file.
- For each JSON file, go through every source image.
- Apply the changes in order.
- Save the final image to the output folder.
- **Test**: Make sure it works correctly using the `small_images/` folder.

### Part 2: Make it Fast

Once the code works, process the `large_images/` folder. You must finish within a **target time limit**.

Keep in mind:

- Editing images uses the CPU a lot.
- You can process different images at the same time (they don't depend on each other).
- You should use parallel strategies.

## Function Signature

```python
def process_images(
    image_dir: str,
    transformation_dir: str,
    output_dir: str,
    get_output_path: Callable[[str, str], str]
) -> None:
    """
    Process all images with all transformation configurations.

    Args:
        image_dir: Path to directory containing source images
        transformation_dir: Path to directory containing transformation JSON files
        output_dir: Path to directory for saving processed images
        get_output_path: Utility function that generates output path
                        given (image_path, transform_json_path)
    """
    pass
```

## Example Solution

**Note**: This is just one way to solve it. In the interview, use your own style and explain your steps.

### Picking the Right Tool

**Pillow (PIL)** is a great choice because:

- It is easy to use.
- It can do all the required changes built-in.
- It is very popular and well-documented.
**scikit-image** is also good if you like using NumPy.

### Pillow Cheat Sheet

Use these terms when searching the docs:

| Change | Pillow Command |
| :--- | :--- |
| Grayscale | `PIL.ImageOps.grayscale()` |
| Flip horizontal | `PIL.ImageOps.mirror()` |
| Flip vertical | `PIL.ImageOps.flip()` |
| Scale/Resize | `Image.resize(size, resample)` |
| Blur | `PIL.ImageFilter.GaussianBlur(radius)` |
| Rotate | `Image.rotate(angle, expand=True)` |

### Simple Solution Code

```python
from PIL import Image, ImageFilter, ImageOps
import json
import os
from pathlib import Path

def load_transformations(json_path: str) -> list:
    """Load transformation specifications from a JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data.get('transformations', [])

def apply_transformation(image: Image.Image, transform: dict) -> Image.Image:
    """Apply a single transformation to an image."""
    transform_type = transform['type']

    if transform_type == 'grayscale':
        # Convert to grayscale. We convert back to RGB because 
        # some later steps might expect 3 color channels.
        return ImageOps.grayscale(image).convert('RGB')

    elif transform_type == 'flip_horizontal':
        return ImageOps.mirror(image)

    elif transform_type == 'flip_vertical':
        return ImageOps.flip(image)

    elif transform_type == 'scale':
        factor = transform['factor']
        new_size = (int(image.width * factor), int(image.height * factor))
        return image.resize(new_size, Image.Resampling.LANCZOS)

    elif transform_type == 'blur':
        radius = transform['radius']
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    elif transform_type == 'rotate':
        angle = transform['angle']
        return image.rotate(angle, expand=True)

    else:
        raise ValueError(f"Unknown transformation type: {transform_type}")

def apply_all_transformations(image: Image.Image, transformations: list) -> Image.Image:
    """Apply a sequence of transformations to an image."""
    result = image.copy()
    for transform in transformations:
        result = apply_transformation(result, transform)
    return result

def process_images(
    image_dir: str,
    transformation_dir: str,
    output_dir: str,
    get_output_path
) -> None:
    """Process all images with all transformation configurations."""

    # Get all image and transformation files.
    # Note: In a real interview, helper functions might give you these lists.
    image_files = [f for f in Path(image_dir).iterdir()
                   if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    transform_files = list(Path(transformation_dir).glob('*.json'))

    for transform_file in transform_files:
        transformations = load_transformations(str(transform_file))

        for image_file in image_files:
            # Load image
            image = Image.open(str(image_file))

            # Apply transformations
            result = apply_all_transformations(image, transformations)

            # Save to output directory
            output_path = get_output_path(str(image_file), str(transform_file))
            result.save(output_path)

            # Close images to free memory
            image.close()
            result.close()
```

### Fast Solution Code (Parallel)

For big images, use `ProcessPoolExecutor`. Image editing is **CPU-bound** (it does a lot of math). You need multiprocessing to get around Python's GIL restrictions.

**Important**: On Windows, you must put the executor code inside `if __name__ == '__main__':`. This stops the code from starting infinite new processes.

```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageFilter, ImageOps
import json
from pathlib import Path
import os

# Note: This function must be at the module level (not inside another function)
# so Python can send it to other processes (pickling).
def apply_transformation(image: Image.Image, transform: dict) -> Image.Image:
    """Apply a single transformation to an image."""
    transform_type = transform['type']

    if transform_type == 'grayscale':
        return ImageOps.grayscale(image).convert('RGB')
    elif transform_type == 'flip_horizontal':
        return ImageOps.mirror(image)
    elif transform_type == 'flip_vertical':
        return ImageOps.flip(image)
    elif transform_type == 'scale':
        factor = transform['factor']
        new_size = (int(image.width * factor), int(image.height * factor))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    elif transform_type == 'blur':
        radius = transform['radius']
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    elif transform_type == 'rotate':
        angle = transform['angle']
        return image.rotate(angle, expand=True)
    else:
        raise ValueError(f"Unknown transformation type: {transform_type}")

def process_single_image(args: tuple) -> str:
    """Process a single image with a transformation configuration.

    This function runs in a separate process.
    """
    image_path, transform_path, output_path = args

    # Load transformation config
    with open(transform_path, 'r') as f:
        data = json.load(f)
    transformations = data.get('transformations', [])

    # Load and process image
    image = Image.open(image_path)
    result = image.copy()

    for transform in transformations:
        result = apply_transformation(result, transform)

    # Ensure output directory exists and save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path)

    image.close()
    result.close()

    return output_path

def process_images_parallel(
    image_dir: str,
    transformation_dir: str,
    output_dir: str,
    get_output_path,
    max_workers: int = None
) -> None:
    """Process all images in parallel using multiple processes."""

    # Collect all work items
    image_files = [f for f in Path(image_dir).iterdir()
                   if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]
    transform_files = list(Path(transformation_dir).glob('*.json'))

    work_items = []
    for transform_file in transform_files:
        for image_file in image_files:
            output_path = get_output_path(str(image_file), str(transform_file))
            work_items.append((str(image_file), str(transform_file), output_path))

    # Process in parallel using multiple CPU cores
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single_image, work_items))

    print(f"Processed {len(results)} images")
```

## Interview Questions

The interviewer will likely ask how you made the code faster. Be ready to explain the difference between Threading and Multiprocessing.

### Why Multiprocessing?

**Question**: Why did you use `ProcessPoolExecutor` instead of `ThreadPoolExecutor`?

**Key Points to Discuss**:

| Feature | ProcessPoolExecutor | ThreadPoolExecutor |
| :--- | :--- | :--- |
| **Best For** | CPU Tasks (Math, Logic) | I/O Tasks (Waiting for data) |
| **GIL Impact** | Bypasses GIL (Fast) | Stuck by GIL (Slow for CPU) |
| **Memory** | Separate memory per process | Shared memory |
| **Overhead** | High (Slow to start) | Low (Fast to start) |

**Why use it here?**

- Image changes (blur, rotate) require heavy math. This is **CPU-intensive**.
- The Python **GIL (Global Interpreter Lock)** prevents threads from running Python code at the exact same time.
- Processes run in their own memory space. This lets them use all CPU cores at once.
**When is Threading better?**

- Downloading files, waiting for a database, or reading files from a slow drive (**I/O-bound**).
- When tasks spend most of their time waiting.
**The GIL Explained Simply:**

```python
Thread 1: [Work] [Wait] [Work] [Wait]
Thread 2:      [Wait] [Work]  [Wait] [Work]
                    ↑ Only one thread works at a time

Process 1: [Work] [Work] [Work]
Process 2: [Work] [Work] [Work]
                    ↑ Both work at the same time
```

**Advanced Answer:**

- This problem has both I/O (reading files) and CPU (editing images) work.
- If your hard drive is very slow, threading might work.
- However, image editing is usually heavier than reading the file. This makes the CPU the bottleneck, so Multiprocessing is the correct choice.

### Other Questions

**How do you handle huge images that don't fit in RAM?**

- Process the image in small chunks (tiles) instead of loading the whole thing.
**How do you make this code safe for production?**

- Check if the JSON is valid.
- Add error handling so one bad image doesn't crash the whole program.
- Add logging to track progress.
**How do you scale to millions of images?**

- One computer isn't enough. Use a message queue to send work to many different computers.

*原帖: https://www.1point3acres.com/interview/thread/7100010*

---

## Tokenize (Python)

## Part 1: Understanding the Code

You are given two functions: `tokenize` and `detokenize`. Your goal is to:

- **Read the code** and understand what it does.
- **Find the bugs** or logic errors in the tokenization process.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
    return tokens

def detokenize(tokens, vocab: dict):
    text = ""
    reversed_vocab = {value: key for key, value in vocab.items()}
    for token in tokens:
        text += reversed_vocab[token]
    return text
```

**Example:**

```python
vocab = {
    "a": 1,
    "b": 2,
    "cd": 3
}

tokens = tokenize("acdebe", vocab)
result = detokenize(tokens, vocab)
```

### Your Task

- **Explain** how this code works to your interviewer.
- **Identify** the problems with this logic.
- **Explain** when this code will fail.

### Questions to Ask Yourself

- How does the code choose which token to pick?
- What happens if the text has a letter that is NOT in the `vocab`?
- What happens to the `key` variable if it never finds a match?
- Does this code pick the best match, or just the first one it sees?

## Part 2: Reviewing a Proposed Fix

Another engineer tried to fix the code. They added a new rule for "unknown" items. Review their code below.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""

    # NEW: Check if there is leftover text at the end
    if key:
        tokens.append(vocab.get("UNK", -1))

    return tokens

vocab = {
    "a": 1,
    "b": 2,
    "cd": 3,
    "UNK": -1  # NEW: Added UNK (Unknown) token
}
```

**Changes made:**

- Logic added after the loop to check if `key` is empty.
- Added `"UNK": -1` to the dictionary.

### Your Task

Act like a code reviewer. Give feedback, ask questions, and point out concerns.

### Points to Consider

- What is `UNK` used for?
- Does this change actually fix the main problem?
- What happens if the unknown character is in the **middle** of the text, not the end?
- Think about edge cases:

Input text is `"xabc"` (starts with an unknown letter).
- Input text contains the word `"UNK"`.
- Does the logic always find the correct tokens?

## Part 3: Writing a Better Solution

Now, write your own version of the `tokenize` function. It needs to handle characters correctly even if they are not in the vocabulary.

### Requirements

- **Handle unknown characters:** Do not crash if a character is missing from the `vocab`.
- **Stay correct:** Ensure `tokenize` and `detokenize` logic holds up.
- **Use the UNK token:** Replace missing characters with `UNK: -1`.
- **Know the limits:** If the original text actually says "UNK", you won't be able to tell the difference between that and a real unknown character later. This is a known limitation.

### Key Challenges

- When should you stop adding letters to the `key`?
- How do you know if the current string you are building will **never** match a real token?
- Should you check if any word in the `vocab` starts with your current `key`?

### Helpful Context

- **Tokenization:** Breaking text into small chunks (tokens) and giving them numbers (IDs).
- **UNK:** Short for "UNKNOWN". It is a placeholder for data the model hasn't seen before.
- **Greedy Matching:** Taking the first match you find immediately. The original code does this.
- **Prefix Check:** You might need to check if your current string is the start (prefix) of any valid key. If it isn't, you know you won't find a match.

### Example Solution Approach

One way to solve this is to "look ahead." Check if the current `key` could possibly become a match later. If not, treat it as unknown.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
        else:
            # Check: Does any key in vocab start with this string?
            if not any(k.startswith(key) for k in vocab.keys()):
                # No match is possible. Mark as UNK.
                tokens.append(vocab.get("UNK", -1))
                key = ""

    # Handle any leftover text
    if key:
        tokens.append(vocab.get("UNK", -1))

    return tokens
```

This is just one way to do it. Be ready to discuss why this works or if there is a better way.

## Part 4: Follow-Up Questions

Be ready to talk about these topics during the interview:

### 1. Tokenization Strategies

**Question:** What are the different ways to tokenize text? What are the pros and cons?

**Simple Explanation:**

- **Character-level:** Every letter is a token.

*Pro:* Small vocabulary.
- *Con:* Produces very long lists of tokens.
- **Word-level:** Every word is a token.

*Pro:* Easy to understand.
- *Con:* Huge vocabulary; struggles with new words.
- **Subword (BPE, WordPiece):** Breaks words into meaningful chunks (like "ing" or "ed"). This is the standard for modern AI.
- **Byte-level:** Uses raw bytes (UTF-8). No need for `UNK` tokens.

### 2. Algorithm Complexity

**Question:** How fast is your code? Can you make it faster?

**Simple Explanation:**

- **Current speed:** $O(n \times m \times k)$.

$n$ = length of text.
- $m$ = average length of a vocab word.
- $k$ = total number of words in vocab.
- **The Slow Part:** The line `any(k.startswith(key)...)` loops through the whole dictionary every time. This is slow.
- **The Fix:** Use a **Trie** (Prefix Tree). This makes lookups much faster, reducing complexity to $O(n \times m)$.

### 3. Ambiguity and Optimal Tokenization

**Question:** The "greedy" approach (taking the first match) isn't always best. Can you prove it?

**Simple Explanation:**

- Imagine your vocab is `{"ab": 1, "abc": 2, "c": 3}`.
- Your text is `"abc"`.
- **Greedy:** Sees "ab", matches it. Then sees "c", matches it. Result: 2 tokens (`ab`, `c`).
- **Optimal:** Sees "abc", matches it immediately. Result: 1 token (`abc`).
- **Solution:** To find the best path, you would use **Dynamic Programming** or the **Viterbi algorithm**. However, this is slower than the greedy method.

### 4. Handling UNK in Real Systems

**Question:** How do big apps (like ChatGPT or Google Translate) handle unknown words?

**Simple Explanation:**

- **Subwords:** They break the unknown word down. If "microscope" is unknown, they might break it into "micro" and "scope".
- **Character Fallback:** If a word is totally new, they might spell it out letter by letter.
- **Training:** Having too many `UNK` tokens makes the model dumb. Engineers try very hard to avoid them by using better tokenization (like BPE).

*原帖: https://www.1point3acres.com/interview/thread/7100003*

---

## LLM Request Batching API System Design

## The Challenge

Design an HTTP API for a Large Language Model (LLM) service. Users send single requests, but the system must group these requests into batches to run efficiently on GPUs.

### The Problem Requirements

You have a backend function you must use. You cannot change it.

```python
def batchstring(inputs: list[str]) -> list[str]:
    """
    Processes a batch of string inputs and returns string outputs.

    Constraints:
    - Input size: 1-100 strings per batch
    - Output size: 1-100 strings (one per input)
    - Latency: ~100ms per batch (fixed time, does not change with size)
    - Concurrency: Each GPU instance can only process ONE batch at a time
    """
    # Fixed implementation - you cannot modify this
    pass
```

### What We Need to Build

You need to design a system that:

- Takes single requests from users (via HTTP).
- Groups them into batches inside the system.
- Sends these batches to GPUs.
- Matches the answers back to the correct users.
- Keeps the system fast (low Latency).

### Questions the Interviewer Might Ask

Be ready for questions like:

- **Scale:** How many requests per second (RPS)? (e.g., 100 vs 10,000).
- **Speed:** How fast must the response be? (e.g., P95 < 500ms).
- **Users:** Do paid users get priority?
- **Hardware:** How many GPUs do we have?
- **Routing:** How does the server know which user gets which answer?
- **Errors:** What happens if a GPU crashes?

## Sample Solution

**Note**: This is a guide. You should try to solve the problem yourself first.

## Step 1: Clarifying the Requirements

First, ask questions to understand exactly what you need to build.

### Questions to Ask

**Traffic and Speed:**

- "How many requests per second (RPS) do we expect?"

*Why ask:* This tells us if we need a simple setup or a complex distributed system.
- "What is the allowed Latency?" (e.g., 500ms).

*Why ask:* This helps us decide how long we can wait to fill a batch.
**Hardware:**

- "How many GPUs can we start with?"
- "Is the GPU function reliable, or does it crash often?"
**The Problem Details:**

- "Does the 100ms processing time change if the batch is small?" (Answer: No, it is fixed).
- "Do we need to let users cancel requests?" (Answer: No).

### Summary of What We Are Building

**What it does:**

- Takes single string inputs via HTTP POST.
- Users wait for the answer (Synchronous).
- Groups 1-100 requests into a batch.
- Sends batch to the `batchstring()` function.
- Returns the correct answer to the user.
- Handles high traffic (1000+ RPS).
**Performance Goals:**

- **Latency:** P95 < 500ms.
- **Uptime:** 99.9%.
- **Efficiency:** Use GPUs well (aim for 70-80% usage).

## Step 2: Estimating Scale and Resources

We need to do some math to guess how many GPUs we need.

### Assumptions

- **Traffic:** 1000 requests per second (RPS).
- **Batch Size:** We aim for 32 requests per batch.
- **GPU Speed:** 100ms per batch.
- **Timeout:** We wait 50ms max to fill a batch.

### The Math

**How many GPUs do we need?**

- **Throughput per GPU:**

1 batch takes 100ms.
- In 1 second (1000ms), a GPU can run 10 batches.
- Each batch has 32 requests.
- So, 1 GPU handles: 10 batches × 32 requests = 320 requests per second.
- **Total GPUs needed:**

We have 1000 RPS.
- 1000 / 320 = 3.125 GPUs.
- Round up to **4 GPUs**.
- **Add Safety Buffer:**

We don't want to run at 100% capacity. Let's aim for 70%.
- 4 GPUs / 0.7 ≈ 5.7.
- **Final count: 6 GPUs.**
**How long will users wait (Latency)?**

- **Waiting for batch:** 0ms to 50ms. Average is ~15-25ms.
- **Network travel:** ~10ms.
- **GPU time:** 100ms (fixed).
- **Total Average:** 25 + 10 + 100 = **135ms**.
- This is good. It is well under the 500ms limit.

## Step 3: API Design

This defines how users talk to our system and how our internal servers talk to each other.

### User API (Public)

**Request:**

```python
POST /api/inference
Content-Type: application/json

{
  "input": "E equals "
}
```

**Response:**

```json
{
  "output": "E equals mc^2",
  "latency_ms": 145,
  "request_id": "req_abc123"
}
```

### Internal API (Batcher to GPU)

**Request:**

```json
{
  "batch_id": "batch_xyz",
  "inputs": ["E equals ", "Q: What is ", ...],
  "request_ids": ["req_1", "req_2", ...],
  "return_to": "api-instance-1"
}
```

## Step 4: Data Storage

We need to decide how to store data in memory and in the database.

### 1. In-Memory (API Server)

The API server needs to remember who is waiting for an answer.

```python
# Map request IDs to the open user connection
pending_requests = {
  "req_abc123": <HTTP connection object>,
  "req_def456": <HTTP connection object>
}
```

### 2. Redis (Shared Storage)

We use Redis to pass messages between servers.

**Request Queue:**
A list where API servers put new requests.

```python
Key: "batch_queue"
Value: [
  '{"request_id": "req_1", "input": "...", "return_to": "api-1"}',
  ...
]
```

**Response Channels (Pub/Sub):**
Channels to send answers back to the specific API server that asked.

```python
Channel: "responses:api-instance-1"
Channel: "responses:api-instance-2"
```

## Step 5: Basic System Architecture

Here are the main parts of the system.

```python
[User] -> [Load Balancer] -> [API Server 1] -> [Redis Queue] -> [Batcher] -> [GPU]
                                     ^                                        |
                                     |                                        |
                                     L__________[Redis Pub/Sub]_______________|
```

### Component Roles

- **Load Balancer:** Sends user requests to different API servers.
- **API Server:**

Takes the user request.
- Assigns a `request_id`.
- Puts the request in the **Redis Queue**.
- Waits for the answer.
- **Batching Service:**

Takes requests from the **Redis Queue**.
- Groups them into a batch (wait for 32 items or 50ms).
- Sends the batch to a GPU.
- **GPU Worker:**

Runs the `batchstring()` function.
- Returns the result to the Batching Service.
- **Redis Pub/Sub:**

Used to send the answer back from the Batching Service to the API Server.

## Step 6: Deep Dive into Components

In the interview, pick 2 or 3 hard parts to explain in detail.

### 1. The Batching System

This is the most important part. We need to balance **Speed** vs. **Efficiency**.

**Strategy: Size + Timeout**

We send a batch to the GPU when EITHER:

- The batch is full (e.g., 32 requests).
- OR the time limit runs out (e.g., 50ms).
**Why this is good:**

- If traffic is high, batches fill fast (Efficient).
- If traffic is low, we don't make one user wait forever (Fast).
**Code Logic:**

```python
current_batch = []
start_time = now()

while True:
    req = queue.get()
    current_batch.append(req)

    is_full = len(current_batch) >= 32
    is_timeout = (now() - start_time) >= 50ms

    if is_full or is_timeout:
        send_to_gpu(current_batch)
        current_batch = []
        start_time = now()
```

### 2. Matching Responses to Users

This is tricky. The user connects to **API Server 1**, but the **Batching Service** (on a different computer) handles the logic. How does the answer get back to **API Server 1**?

**The Solution: Redis Pub/Sub**

- **API Server 1** generates a request. It adds a tag: `"return_to": "api-1"`.
- It puts the request in the global queue.
- **API Server 1** subscribes to a Redis channel named `"responses:api-1"`.
- The **Batching Service** processes the request via GPU.
- When the result is ready, the Batching Service looks at the `"return_to"` tag.
- It publishes the result to the channel `"responses:api-1"`.
- **API Server 1** sees the message on that channel.
- It finds the waiting user connection in memory and sends the HTTP response.

### 3. Connection Limits (The C10K Problem)

If 10,000 users are waiting for answers at the same time, the server might run out of open connections.

**The Math:**

- 10,000 requests per second.
- Wait time is 0.15 seconds.
- Concurrent connections = 10,000 * 0.15 = **1,500 connections**.
**Is this a problem?**

- Default server limit is often 1,024. This will fail.
- **Fix:** We must increase the OS limit (File Descriptors) to 65,000.
- With multiple API servers (e.g., 3 servers), each handles 500 connections. This is safe.

## Step 7: Fixing Potential Problems

A good design must handle failures.

### Problem 1: GPU Crashes

**Scenario:** A GPU crashes while processing a batch of 32 requests.
**Solution:**

- The Batching Service should detect the error.
- It can retry the batch on a different GPU.
- If it fails again, return a `500 Error` to the users so they know to try again.

### Problem 2: Single Point of Failure

**Scenario:** If the Redis Queue dies, the whole system stops.
**Solution:**

- Use Redis Cluster (multiple Redis nodes).
- If the main node dies, a backup node takes over automatically.

### Problem 3: Low Traffic Inefficiency

**Scenario:** At night, only 1 request comes every second.
**Problem:** The GPU waits 50ms, processes 1 item, then sits idle. This wastes money.
**Solution:**

- Use **Auto-scaling**.
- Detect low traffic and turn off 5 of the 6 GPUs.
- Spin them back up when traffic increases in the morning.

### Monitoring

You need dashboards to watch the system health.

- **Critical Alert:** If Queue size > 1000 (System is backed up).
- **Critical Alert:** If Latency > 500ms (System is too slow).
- **Warning:** If GPU usage > 85% (Need to add more GPUs soon).

*原帖: https://www.1point3acres.com/interview/thread/7100012*

---

## Converting Stack Samples to Trace Events

## Problem Statement

A sampling profiler takes a snapshot of the active call stack at specific times. You get a list of these snapshots (samples), sorted by time. Each sample has:

```cpp
struct Sample {
    double ts;                      // timestamp
    std::vector<std::string> stack; // call stack (outermost → innermost)
};
```

Your job is to turn these samples into a timeline of events. You need to create a list showing when functions started and ended:

```cpp
struct Event {
    std::string kind;   // "start" or "end"
    double ts;          // timestamp
    std::string name;   // function name
};
```

### Example Scenario

**Input samples** (sorted by time):

```python
t=1.0: ["main"]
t=2.5: ["main", "func1"]
t=3.1: ["main"]
```

**Expected output**:

```python
start 1.0 main
start 2.5 func1
end   3.1 func1
```

### Key Rules

- **Sorted Input:** The samples come in the correct time order.
- **Find Changes:** Look at two samples side-by-side to see what is different:

Create **End events** for functions that are no longer there (remove from the bottom up).
- Create **Start events** for new functions (add from the top down).
- **No Auto-Closing:** Do not create "end" events for functions remaining after the very last sample.
- **Handle Recursion:** If the same function name appears at different depths in the stack, treat them as separate frames.

### Function Signature

```java
List<Event> convertSamplesToEvents(List<Sample> samples)
```

### Important Hints

- The stack list goes from the root (like "main") down to the leaf (the function running right now).
- To decide what started or ended, find the longest shared starting part (prefix) of the two consecutive stacks.

## Follow-up Question: Reducing Noise

Sometimes fast functions appear for a very short time and clutter the data. Modify your code to only create start/end events if a function appears in **N samples in a row** (N is a number you can set).

### Defining a Streak

A function is "consecutive" only if the **exact same frame** (same depth and parent functions) appears N times in a row.

**Important:** If a function stops and then starts again later, the counter resets. You cannot add the two separate appearances together.

### Debouncing Example (N = 2)

**Input samples**:

```python
t=1.0: ["main"]
t=2.0: ["main"]
t=3.0: ["main", "foo"]
t=4.0: ["main", "foo"]
```

**Expected output**:

```python
start 2.0 main     # main appeared in 2 samples, so it is confirmed
start 4.0 foo      # foo appeared in 2 samples, so it is confirmed
```

### Edge Case Warning

Look at these samples:

```python
Sample(1, ['a', 'b'])
Sample(2, ['a', 'b', 'c'])
```

Here, `a` and `b` are consecutive because they are in the same position in both lists.

However, in this case:

```python
Sample(1, ['a', 'b'])
Sample(2, ['c', 'b', 'a'])
```

Here, `a` and `b` do **NOT** count as consecutive. At t=2, the stack changed completely. The frames `a` and `b` from t=1 must close before the new stack starts. Even though the names are the same, the call path is different.

### Function Signature

```java
List<Event> convertSamplesToDebouncedEvents(List<Sample> samples, int N)
```

### Important Hints

- You can mark the start time at the 1st sample or the Nth sample (either is fine if you are consistent).
- Focus on tracking the streak correctly. Any interruption resets the count to zero.

## System Design Discussion

These questions are for verbal discussion. You do not need to write code, but you should be ready to explain your logic.

### Comparing from Top vs. Bottom

**Question:** The basic solution compares stacks from the top down (Prefix). How is comparing from the bottom up (Postfix/Suffix) different, and why might it be better for profiling?

**Discussion Points:**

**Prefix Comparison (Top-Down)**:

- Compares starting from the root (e.g., "main").
- If the top layers match, it treats them as the same call chain.
- **Problem:** This is not very detailed. It might group different leaf functions together if the top layers look the same.
- Top-level functions usually change less often, so this method misses small details.
**Postfix Comparison (Bottom-Up)**:

- Compares starting from the leaf (the deepest function).
- It looks for the deepest parts of the stack that are different.
- **Benefit:** This is more accurate for profiling. The leaf function is where the work actually happens, and it changes the most.
**Example**:

```python
Stack A: main → handler → parse → foo
Stack B: main → handler → parse → bar
```

- **Prefix comparison**: The first 3 layers match. It might treat these as the same event.
- **Postfix comparison**: The leaves ("foo" vs "bar") are different. This clearly shows that the activity changed.
**Why This Matters**: In profiling, we want to know exactly which leaf function is running. Postfix comparison helps by:

- Distinguishing between different paths of execution.
- Better identifying "hot spots" (functions using the most resources).
- Reducing noise by focusing on real changes at the bottom of the stack.

*原帖: https://www.1point3acres.com/interview/thread/7100016*

---

## Distributed Mode and Median

## Problem Statement

You are given a large dataset spread across several machines (usually 10 workers). You have a pre-built interface to send and receive data. Each machine holds a part of the dataset locally.

Your task is to build a distributed system to find the **mode** (the most frequent value) of the entire dataset.

**Important Rule:** The speed of sending data is the main limit. You must not send all data to one machine at the same time. This will cause a "bottleneck" and slow everything down.

**Provided Interface:**

```python
# Send data to a specific worker
def send(worker_id, data):
    pass

# Receive data from any worker
def recv():
    pass
```

### System Constraints & Goals

- **Data**: Mostly unique integers. One integer appears twice (the duplicate) but on different machines. All others appear once.
- **Language**: Python.
- **Workers**: 10 machines (set by `WORKER_NUM`).
- **Identity**: Your current worker ID is `worker_id`.
**Your solution must:**

- **Use the given interface** without changing it.
- **Share the load** evenly so no single worker is overwhelmed.
- **Work in parallel** (workers send and receive at the same time).
- **Handle delays** (latency) in sending/receiving.
- **Return the mode** correctly.

### Key Hints

- **Managing Traffic**: Use a "modulo" strategy to decide where to send data. This prevents traffic jams.
- **Clarify Ties**: Ask the interviewer what to return if two numbers have the same count. Should you return the smallest one? The largest? Or all of them?
- **Top 1 is Enough**: Because we organize data by "keys" in Step 2, each worker will know the final total for the specific numbers it owns. Therefore, each worker only needs to send its single best result (Top 1) to the final aggregator, not the Top K.

## Solution Part 1: Finding the Mode

### Step 1: Count Locally

First, each worker counts the numbers it currently holds.

```python
from collections import Counter

def phase1_local_count(local_data):
    """
    Count how many times each number appears in the local list.

    Args:
        local_data: List of integers on this worker

    Returns:
        Counter object: {value: count}
    """
    return Counter(local_data)
```

**Example:**

- Worker 0 has `[1, 2, 3]` → Counts: `{1:1, 2:1, 3:1}`

### Step 2: Grouping by Key (The Shuffle)

This is the most important step. Each worker looks at its keys and decides where to send them using `key % num_workers`.

- If a number is `13` and there are 10 workers, `13 % 10 = 3`. So, data for `13` goes to Worker 3.
- This ensures all counts for the number `13` end up on the same machine.

```python
def phase2_shuffle_counts(local_counter, worker_id, num_workers):
    """
    Send counts to other workers based on modulo (key % workers).
    This ensures all instances of the same key go to the same place.
    """
    # Create empty lists for each target worker
    buckets = [[] for _ in range(num_workers)]

    # Sort keys into buckets based on modulo
    for key, count in local_counter.items():
        target_worker = key % num_workers
        buckets[target_worker].append((key, count))

    # Send buckets to other workers
    for target_id in range(num_workers):
        if target_id != worker_id:
            send(target_id, buckets[target_id])

    # Receive buckets from other workers
    received_data = []
    for _ in range(num_workers - 1):
        data = recv()
        received_data.extend(data)

    # Add the data we kept for ourselves
    received_data.extend(buckets[worker_id])

    return received_data
```

**Why this works:**

- Worker `i` only handles keys where the remainder is `i`.
- Everyone sends and receives at the same time, keeping the network balanced.

### Step 3: Find Local Winners

Now, each worker aggregates the data it received. It finds the "winner" (most frequent value) among the keys it is responsible for.

```python
def phase3_aggregate_local(received_data):
    """
    Combine all counts received and find the local max.

    Returns:
        aggregated: Combined counts
        top_1: The (key, count) with the highest frequency here
    """
    # Combine counts for the same key
    aggregated = Counter()
    for key, count in received_data:
        aggregated[key] += count

    # Find the most frequent value in this specific partition
    if aggregated:
        top_1 = aggregated.most_common(1)[0]
    else:
        top_1 = (None, 0)  # No data received

    return aggregated, top_1
```

**Why Top 1 is enough:**

- Every distinct number lives on exactly one worker.
- The worker holding that number has the *final, correct* count for it.
- The global winner is definitely one of these local winners.

### Step 4: Find the Global Winner

Finally, every worker sends its single best result to Worker 0. Worker 0 picks the winner.

```python
def phase4_global_reduction(local_top_1, worker_id, num_workers):
    """
    Send local top 1 to Worker 0. Worker 0 finds the global mode.
    """
    if worker_id == 0:
        # Start with our own best value
        best_key, best_count = local_top_1

        # Get best values from everyone else
        for _ in range(num_workers - 1):
            remote_key, remote_count = recv()
            
            # Tie-breaking logic: 
            # If counts are equal, pick the smaller key (deterministic).
            if remote_count > best_count or (remote_count == best_count and remote_key is not None and best_key is not None and remote_key < best_key):
                best_key, best_count = remote_key, remote_count

        return best_key
    else:
        # Send our best value to Worker 0
        send(0, local_top_1)
        return None
```

### Full Code: Mode Solution

```python
def find_mode_distributed(local_data, worker_id, num_workers):
    """
    Main function to find the distributed mode.
    """
    # Phase 1: Count what we have locally
    local_counter = phase1_local_count(local_data)

    # Phase 2: Send counts to the correct owners
    received_data = phase2_shuffle_counts(local_counter, worker_id, num_workers)

    # Phase 3: Combine data and find local winner
    aggregated, local_top_1 = phase3_aggregate_local(received_data)

    # Phase 4: Worker 0 decides the global winner
    mode = phase4_global_reduction(local_top_1, worker_id, num_workers)

    return mode
```

**Complexity:**

- **Time:** Fast. Most work is split by `num_workers` (W).
- **Traffic:** The main cost is Step 2. In Step 4, we only send 1 item per worker.
- **Space:** Each worker only stores `unique_keys / W`.

## Follow-up Question: Finding the Median

After finding the mode, you might be asked to find the **median**.

**The Challenge:**
The median is the "middle" value if you sorted all the numbers. Unlike the mode, you cannot just count frequencies independently. You need to know the order of values across all machines.

### Solution Part 2: Median Strategy

We use a strategy called **Distributed Quickselect**. This finds the median without sorting the whole massive dataset.

- **Build a Histogram:** Use the same "Shuffle" logic from the Mode solution so each worker owns a specific range of numbers.
- **Binary Search:** Guess a value (pivot), count how many numbers are smaller than it, and adjust the guess.

### Step 1 & 2: Count and Sort

We reuse the code from the Mode solution to build a distributed map of `{value: count}`. We also calculate the total number of items.

```python
def build_distributed_histogram(local_data, worker_id, num_workers):
    """
    Create a distributed count map.
    Worker 0 also calculates the total count of items.
    """
    # 1. Count locally
    local_counter = Counter(local_data)

    # 2. Shuffle data to correct workers
    received_data = phase2_shuffle_counts(local_counter, worker_id, num_workers)

    # 3. Aggregate
    local_histogram = Counter()
    for key, count in received_data:
        local_histogram[key] += count

    # 4. Calculate total items (Worker 0 coordinates)
    if worker_id == 0:
        total_count = sum(count for count in local_histogram.values())
        for _ in range(num_workers - 1):
            remote_count = recv()
            total_count += remote_count
        
        # Tell everyone the total
        for i in range(1, num_workers):
            send(i, total_count)
        return local_histogram, total_count
    else:
        my_count = sum(count for count in local_histogram.values())
        send(0, my_count)
        total_count = recv()
        return local_histogram, total_count
```

### Step 3: Distributed Search (Quickselect)

We search for the median by narrowing down the range `[min, max]`.

```python
def distributed_quickselect(local_histogram, worker_id, num_workers, target_position):
    """
    Find the value at 'target_position' using binary search.
    """
    if not local_histogram:
        min_val, max_val = float('inf'), float('-inf')
    else:
        min_val, max_val = min(local_histogram.keys()), max(local_histogram.keys())

    # Worker 0 finds global min and max
    if worker_id == 0:
        global_min = min_val
        global_max = max_val
        for _ in range(num_workers - 1):
            remote_min, remote_max = recv()
            global_min = min(global_min, remote_min)
            global_max = max(global_max, remote_max)
        
        # Tell everyone the range
        for i in range(1, num_workers):
            send(i, (global_min, global_max))
    else:
        send(0, (min_val, max_val))
        global_min, global_max = recv()

    # Binary search loop
    low, high = global_min, global_max

    while low < high:
        # Worker 0 picks a pivot (middle value)
        if worker_id == 0:
            pivot = (low + high) // 2
            for i in range(1, num_workers):
                send(i, pivot)
        else:
            pivot = recv()

        # Everyone counts numbers <, =, and > the pivot locally
        count_less = sum(count for val, count in local_histogram.items() if val < pivot)
        count_equal = local_histogram.get(pivot, 0)
        count_greater = sum(count for val, count in local_histogram.items() if val > pivot)

        # Worker 0 collects all counts
        if worker_id == 0:
            total_less = count_less
            total_equal = count_equal
            total_greater = count_greater

            for _ in range(num_workers - 1):
                remote_less, remote_equal, remote_greater = recv()
                total_less += remote_less
                total_equal += remote_equal
                total_greater += remote_greater

            # Decide where to look next
            if target_position < total_less:
                # Median is smaller than pivot
                new_low, new_high = low, pivot - 1
            elif target_position < total_less + total_equal:
                # We found it!
                new_low, new_high = pivot, pivot
            else:
                # Median is larger than pivot
                new_low, new_high = pivot + 1, high

            # Tell everyone the new range
            for i in range(1, num_workers):
                send(i, (new_low, new_high))

            low, high = new_low, new_high
        else:
            # Send our counts to Worker 0
            send(0, (count_less, count_equal, count_greater))
            # Wait for next instruction
            low, high = recv()

    return low
```

### Full Code: Median Solution

```python
def find_median_distributed(local_data, worker_id, num_workers):
    """
    Main function for distributed median.
    """
    # 1. Build the histogram and get total count
    local_histogram, total_count = build_distributed_histogram(
        local_data, worker_id, num_workers
    )

    if total_count == 0:
        return None 

    # 2. Determine which index is the median
    median_position = total_count // 2 

    # 3. Find the value at that index
    median = distributed_quickselect(
        local_histogram, worker_id, num_workers, median_position
    )

    return median
```

### Alternative Method: Sorting

If there are not many *unique* numbers, you can just send all sorted lists to Worker 0.

```python
def find_median_sorted_ranges(local_histogram, worker_id, num_workers, total_count):
    """
    Simple approach: Send all data to Worker 0. 
    Only works if unique_keys is small.
    """
    sorted_local = sorted(local_histogram.items())

    if worker_id == 0:
        all_values = []
        all_values.extend(sorted_local)

        # Collect data from everyone
        for _ in range(num_workers - 1):
            remote_sorted = recv()
            all_values.extend(remote_sorted)

        # Sort combined list and find median
        all_values.sort(key=lambda x: x[0])

        median_position = total_count // 2
        cumulative = 0
        for value, count in all_values:
            cumulative += count
            if cumulative > median_position:
                return value
    else:
        send(0, sorted_local)
        return None
```

**Warning:** This creates a bottleneck at Worker 0. Only use it if you know the number of unique keys is low.

## Discussion Questions

Be ready to discuss these topics with your interviewer.

### 1. Handling Uneven Data (Data Skew)

**Question:** What if millions of items map to Worker 1, but only a few map to Worker 2?
**Answer:** This is a "hotspot."

- **Better Hashing:** Use a stronger hash function (like MurmurHash) instead of simple modulo to randomize the spread better.
- **Split Keys:** If one key (like "Justin Bieber") is super popular, split it into `("Justin Bieber", 1)`, `("Justin Bieber", 2)` so different workers can count parts of it.

### 2. What if a Machine Dies? (Fault Tolerance)

**Question:** How do we handle crashes?
**Answer:**

- **Checkpoints:** Save progress to disk after every step.
- **Replicas:** Send data to 2 workers instead of 1.
- **Retry:** If Worker 5 dies, the coordinator assigns its job to Worker 6 and restarts the step.

### 3. Data Sizes

**Question:** How does the strategy change based on size?

- **Tiny Data:** Don't distribute. Send it all to one machine and sort it there.
- **Huge Data:** Use "approximate" algorithms (like HyperLogLog) to guess the count with 99% accuracy but 0.1% of the memory.
- **Streaming:** Use "sliding windows" (only count the last hour of data).

### 4. Improving Speed (Communication)

**Question:** Can we make the network part faster?
**Answer:**

- **Batching:** Group many small messages into one big packet.
- **Tree Reduction:** Instead of everyone sending to Worker 0, Worker 1 sends to 2, 2 sends to 4... forming a tree. This prevents Worker 0 from getting flooded.
- **Compression:** Zip the data before sending.

### 5. Other Statistics

**Question:** How would you calculate other metrics?

- **Top K:** Keep a list of the top K items locally. Merge these lists at the end.
- **Percentiles (P99):** Same logic as Median (which is P50).
- **Distinct Count:** Use HyperLogLog.

### 6. Real-World Production

**Question:** What else is needed for a real system?
**Answer:**

- **Monitoring:** dashboards to see if a worker is slow.
- **Security:** Encrypting data between workers.
- **Deadlock Prevention:** ensuring workers don't get stuck waiting for each other forever.

### 7. Comparison with MapReduce/Spark

**Question:** Why write this instead of using Spark?
**Answer:**

- **Spark/Hadoop:** Good for general purpose, fault-tolerant, easy to use.
- **Custom Solution:** Better if you need extreme performance for *this specific problem* and want to remove the "overhead" (extra weight) of a big framework.

*原帖: https://www.1point3acres.com/interview/thread/7100009*

---

## In-memory Database (Online Assessment)

## Problem Overview

You need to build a simple in-memory database. This challenge has **4 levels**. You must solve the current level to unlock the next one.

- **Level 1**: Basic tools to add, update, and get data.
- **Level 2**: Search and filter data.
- **Level 3**: Make data expire automatically (TTL).
- **Level 4**: Look up old data from the past.
You will keep all data from previous levels as you move forward.

## Data Format

**Input**: You will get a list of commands (an array of strings).

**Output**: Return an array of strings with the results for every command.

**Note**: Commands are listed in order of time (strictly increasing timestamps).

## Level 1: Core Features

### Goal

The database stores **records**. Here is how they work:

- **Key**: A unique ID string to find the record.
- **Fields**: Variables inside the record. A field is a string name and an integer value.
Every command has a **timestamp** (in milliseconds). Timestamps are always unique and always increase.

### Commands

#### SET

```python
SET <timestamp> <key> <field> <value>
```

- Add a field-value pair to the record.
- If the field exists, update the `value`.
- If the record does not exist, create it.
- Returns `""`.

#### COMPARE_AND_SET

```python
COMPARE_AND_SET <timestamp> <key> <field> <expectedValue> <newValue>
```

- Update the `field` to `newValue` **only if** the current value is `expectedValue`.
- If the value does not match (or the field is missing), do nothing.
- Returns `"true"` if updated, `"false"` if not.

#### COMPARE_AND_DELETE

```python
COMPARE_AND_DELETE <timestamp> <key> <field> <expectedValue>
```

- Delete the `field` **only if** the current value is `expectedValue`.
- If the value does not match, do nothing.
- Returns `"true"` if deleted, `"false"` if not.

#### GET

```python
GET <timestamp> <key> <field>
```

- Get the value of a `field`.
- If the record or field is missing, return `""`.

### Example

**Queries:**

```javascript
[
  ["SET", "0", "A", "B", "4"],
  ["SET", "1", "A", "C", "6"],
  ["COMPARE_AND_SET", "2", "A", "B", "4", "9"],
  ["COMPARE_AND_SET", "3", "A", "C", "4", "9"],
  ["COMPARE_AND_DELETE", "4", "A", "C", "6"],
  ["GET", "5", "A", "C"],
  ["GET", "6", "A", "B"]
]
```

**Walkthrough:**

- **SET**: Add B=4 to record A. -> `""`
- **SET**: Add C=6 to record A. -> `""`
- **COMPARE_AND_SET**: Value of B is 4. Match! Update to 9. -> `"true"`
- **COMPARE_AND_SET**: Value of C is 6. Expected 4. No match. -> `"false"`
- **COMPARE_AND_DELETE**: Value of C is 6. Match! Delete C. -> `"true"`
- **GET**: Field C is gone. -> `""`
- **GET**: Value of B is 9. -> `"9"`
**Output:** `["", "", "true", "false", "true", "", "9"]`

### Test Case

**Input:**

```javascript
[
  ["SET", "160000000", "a", "a", "1"],
  ["SET", "160000001", "a", "A", "2"],
  ["GET", "160000002", "a", "a"],
  ["COMPARE_AND_DELETE", "160000003", "a", "a", "0"],
  ["GET", "160000004", "a", "a"],
  ["COMPARE_AND_DELETE", "160000005", "a", "a", "1"],
  ["GET", "160000006", "a", "a"],
  ["GET", "160000007", "a", "A"],
  ["COMPARE_AND_DELETE", "160000008", "a", "A", "2"],
  ["SET", "160000009", "a", "A", "7"],
  ["SET", "160000010", "a", "A", "9"],
  ["GET", "160000011", "a", "a"],
  ["GET", "160000012", "a", "A"]
]
```

**Expected Output:**

```javascript
["", "", "1", "false", "1", "true", "", "2", "true", "", "", "", "9"]
```

## Level 2: Filtering Data

### Goal

Now you need to search inside records. This level adds commands to list fields.

### New Commands

#### SCAN

```python
SCAN <timestamp> <key>
```

- Returns a single string listing all fields in the record.
- Format: `"<field_1>(<value_1>), <field_2>(<value_2>), ..."`
- Fields must be sorted **lexicographically** (alphabetical order).
- If the record is empty or missing, return `""`.

#### SCAN_BY_PREFIX

```python
SCAN_BY_PREFIX <timestamp> <key> <prefix>
```

- Returns a string listing fields that start with `prefix`.
- Format: Same as SCAN, sorted **lexicographically**.
- If no fields match, return `""`.

### Example

**Queries:**

```javascript
[
  ["SET", "1", "A", "BC", "1"],
  ["SET", "2", "A", "BD", "2"],
  ["SET", "3", "A", "C", "3"],
  ["SCAN_BY_PREFIX", "4", "A", "B"],
  ["SCAN", "5", "A"],
  ["SCAN_BY_PREFIX", "6", "B", "B"]
]
```

**Walkthrough:**

- **SET** three fields: BC=1, BD=2, C=3.
- **SCAN_BY_PREFIX** "B": Finds BC and BD. -> `"BC(1), BD(2)"`
- **SCAN**: Finds all. -> `"BC(1), BD(2), C(3)"`
- **SCAN_BY_PREFIX**: Record B does not exist. -> `""`
**Output:** `["", "", "", "BC(1), BD(2)", "BC(1), BD(2), C(3)", ""]`

## Level 3: Automatic Expiration (TTL)

### Goal

Add **Time-To-Live (TTL)** support. This means data can expire and delete itself automatically.

**How it works:**

- If you set a value at `timestamp` with a `ttl`, the data is alive from `timestamp` up to `timestamp + ttl`.
- At exactly `timestamp + ttl`, the data is dead. You cannot access it anymore.
- If you update the value, you update the TTL too.

### New Command

#### SET_WITH_TTL

```python
SET_WITH_TTL <timestamp> <key> <field> <value> <ttl>
```

- Add or update a field with a timer.
- The field works normally until time `timestamp + ttl`.
- Returns `""`.

### Changes to Old Commands

All previous commands must now check for expiration:

- **GET**: Return `""` if the field has expired.
- **SCAN**: Do not show expired fields.
- **COMPARE**: Cannot update or delete expired fields.

### Example 1

**Queries:**

```javascript
[
  ["SET_WITH_TTL", "1", "A", "BC", "1", "9"],
  ["SET_WITH_TTL", "5", "A", "BC", "2", "10"],
  ["SET", "6", "A", "BD", "3"],
  ["SCAN_BY_PREFIX", "14", "A", "B"],
  ["SCAN_BY_PREFIX", "15", "A", "B"]
]
```

**Walkthrough:**

- **SET_WITH_TTL**: BC=1. Expires at 1+9 = 10.
- **SET_WITH_TTL**: Update BC=2. Expires at 5+10 = 15.
- **SET**: BD=3. No TTL (lives forever).
- **SCAN (Time 14)**: BC expires at 15, so it is still alive. -> `"BC(2), BD(3)"`
- **SCAN (Time 15)**: BC expired exactly at 15. Only BD remains. -> `"BD(3)"`
**Output:** `["", "", "", "BC(2), BD(3)", "BD(3)"]`

### Example 2

**Queries:**

```javascript
[
  ["SET", "1", "A", "B", "1"],
  ["SET_WITH_TTL", "2", "X", "Y", "5", "15"],
  ["GET", "3", "X", "Y"],
  ["SET_WITH_TTL", "4", "A", "D", "2", "10"],
  ["SCAN", "13", "A"],
  ["SCAN", "14", "A"],
  ["SCAN", "16", "X"],
  ["SCAN", "17", "X"],
  ["COMPARE_AND_DELETE", "20", "X", "Y", "5"]
]
```

**Walkthrough:**

- **SET**: B=1 (forever).
- **SET_WITH_TTL**: Y=5 (expires at 17).
- **GET**: Y is alive. -> `"5"`
- **SET_WITH_TTL**: D=2 (expires at 14).
- **SCAN (Time 13)**: B and D are alive. -> `"B(1), D(2)"`
- **SCAN (Time 14)**: D expired at 14. -> `"B(1)"`
- **SCAN (Time 16)**: Y is alive (expires 17). -> `"Y(5)"`
- **SCAN (Time 17)**: Y expired at 17. -> `""`
- **COMPARE_AND_DELETE**: Y is already expired/gone. -> `"false"`
**Output:** `["", "", "5", "", "B(1), D(2)", "B(1)", "Y(5)", "", "false"]`

## Level 4: Historical Data

### Goal

You need to look at the past. This level lets you see what value a field had at a specific time in history.

### New Command

#### GET_WHEN

```python
GET_WHEN <timestamp> <key> <field> <at_timestamp>
```

- Return the value the field had at time `at_timestamp`.
- **Note**: The field might be deleted *now*, but if it existed *then*, you must return it.
- You are guaranteed that `at_timestamp` ≤ current `timestamp`.
- If `at_timestamp` is 0, treat it like a normal GET for the current time.
- If nothing existed at that specific past time, return `""`.

### Example

**Queries:**

```javascript
[
  ["SET_WITH_TTL", "1", "A", "B", "10", "5"],
  ["GET", "2", "A", "B"],
  ["SET", "3", "A", "B", "20"],
  ["GET_WHEN", "10", "A", "B", "2"],
  ["GET_WHEN", "10", "A", "B", "7"],
  ["GET", "10", "A", "B"]
]
```

**Walkthrough:**

- **SET_WITH_TTL**: B=10. Expires at 6.
- **GET**: Time 2. B is alive. -> `"10"`
- **SET**: Update B=20 (forever). This overwrites the old value.
- **GET_WHEN (Time 10, asking about Time 2)**: At Time 2, B was 10. -> `"10"`
- **GET_WHEN (Time 10, asking about Time 7)**:

The first value (10) expired at 6.
- The new value (20) was set at 3.
- So at Time 7, the value was 20. -> `"20"`
- **GET**: Current value is 20. -> `"20"`
**Output:** `["", "10", "", "10", "20", "20"]`

### Important Logic

- **History**: You must save old data. Even if a record is deleted now, you might need to query it later using `GET_WHEN`.
- **Merges**: If records are merged or changed, keep the history of the previous states.
- **TTL**: When checking past data, check if the TTL was valid **at that specific past moment**.

*原帖: https://www.1point3acres.com/interview/thread/7100014*

---


## 未能解锁的外链帖（请自行打开查看）

- [Bootloader](https://www.1point3acres.com/interview/thread/7100492)


# 三、会员题库 Qbank（元数据 + 链接，正文需在站内查看）

| 题目 | 类别 | 频率 | 时长 | 轮次 | 最近考 | 标签 | 链接 |
|---|---|---|---|---|---|---|---|
| Coding Q1 — Concurrent Web Crawler | coding | high | 55 | phone-screen, onsite-coding | 2026-05-03 | concurrency, threading, async, bfs, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-web-crawler) |
| Coding Q2 Lru Cache Durability | coding | high | 55 | phone-screen, onsite-coding | 2026-06-04 | caching, persistence, python, kwargs, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q2-lru-cache-durability) |
| Recruiter Screen Why Anthropic | behavioral | high | 30 | recruiter-screen | 2026-06-12 | recruiter, behavioral, ai-safety, screening | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/recruiter-screen-why-anthropic) |
| Coding Q3 Stack Trace | coding | high | 55 | phone-screen, onsite-coding | 2026-06-17 | two-pointer, string-processing, stack, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q3-stack-trace) |
| Coding Q2 File Deduplication | coding | high | 55 | phone-screen, onsite-coding | 2026-06-23 | filesystem, hashing, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q2-file-deduplication) |
| Coding Q1 Image Processing | coding | high | 55 | phone-screen, onsite-coding | 2026-06-26 | concurrency, multiprocessing, pillow, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-image-processing) |
| Onsite Project Deep Dive | behavioral | high | 55 | onsite-deep-dive | 2026-06-26 | presentation, technical-deep-dive, project-retro | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/onsite-project-deep-dive) |
| Sd Q2 Prompt Playground | system-design | high | 55 | onsite-system-design | 2026-06-26 | product-design, schema-design, sharing, ux, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q2-prompt-playground) |
| Performance Engineer Modeling | other | low | 60 | onsite-research, tech-screen | 2025-12-11 | gpu, a100, matmul, arithmetic-intensity, performance-modelin | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/performance-engineer-modeling) |
| Performance Engineer Take Home | coding | low | 120 | take-home | 2025-12-11 | gpu, kernel, optimization, memory-coalescing, loop-unrolling | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/performance-engineer-take-home) |
| Prompting Engineering With Llms | coding | low | 55 | phone-screen, tech-screen | 2026-01-31 | llm, prompting, colab, evaluation, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/prompting-engineering-with-llms) |
| Ml Take Home Research | other | low | 240 | take-home | 2026-02-13 | take-home, ml-experiment, pandas, numpy, matplotlib, live-re | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/ml-take-home-research) |
| Ml Programming Screen | coding | low | 55 | phone-screen, tech-screen | 2026-02-18 | transformer, attention, einsum, numpy, pytorch, ml-knowledge | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/ml-programming-screen) |
| Rl Fundamentals Grpo Debug | coding | low | 55 | phone-screen, tech-screen, onsite-coding | 2026-03-02 | reinforcement-learning, grpo, pytorch, ml-knowledge, debuggi | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug) |
| Sd Q5 Data Infrastructure | system-design | single | 55 | phone-screen, onsite-system-design | 2026-03-07 | data-engineering, ingestion, etl, access-control, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q5-data-infrastructure) |
| Ml Configuration System | system-design | low | 55 | phone-screen, tech-screen | 2026-04-17 | config-management, ml-infra, design, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/ml-configuration-system) |
| Mech Interp Take Home | other | single | 240 | take-home | 2026-04-19 | take-home, interpretability, double-descent, linear-regressi | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/mech-interp-take-home) |
| Onsite Design Doc Review | system-design | low | 55 | onsite-system-design | 2026-04-28 | design-review, critique, new-round, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/onsite-design-doc-review) |
| Coding Q4 Distributed Mode Median | coding | medium | 55 | phone-screen, onsite-coding | 2026-05-03 | distributed-systems, map-reduce, bandwidth, python, hard | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q4-distributed-mode-median) |
| Oa Worker Management | coding | low | 90 | oa | 2026-05-10 | oa, codesignal, oop, interval, payroll, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-worker-management) |
| Oa In Memory Database | coding | medium | 90 | oa | 2026-05-10 | oa, codesignal, oop, ttl, snapshot, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-in-memory-database) |
| Coding Design Data Batcher | coding | medium | 55 | phone-screen, tech-screen, onsite-coding | 2026-05-14 | sampling, checkpointing, iterator, python, hard | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-design-data-batcher) |
| Oa Fellows Dns Resolver | coding | low | 90 | oa | 2026-05-27 | codesignal, simulation, recursion, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-fellows-dns-resolver) |
| Oa Task Management | coding | low | 90 | oa | 2026-05-27 | codesignal, data-structure, snapshot, ttl, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-task-management) |
| Oa File Systems | coding | low | 90 | oa | 2026-05-28 | oa, codesignal, oop, filesystem, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-file-systems) |
| Oa Bank System | coding | medium | 90 | oa | 2026-06-15 | oa, codesignal, oop, transactions, merge, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-bank-system) |
| Coding Bootloader | coding | low | 55 | phone-screen, onsite-coding | 2026-06-15 | simulation, cycle-detection, parsing, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-bootloader) |
| Oa Recipe Manager | coding | medium | 90 | oa | 2026-06-16 | oa, codesignal, oop, versioning, user-system, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/oa-recipe-manager) |
| Sd Q3 Model Distribution | system-design | medium | 55 | phone-screen, onsite-system-design | 2026-06-17 | distribution, bandwidth, tree-broadcast, bittorrent, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q3-model-distribution) |
| Sd Q4 1To1 Chat System | system-design | medium | 55 | phone-screen, onsite-system-design | 2026-06-17 | chat, websocket, kafka, redis, presence, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q4-1to1-chat-system) |
| Sd Q1 Inference Api | system-design | very-high | 55 | phone-screen, onsite-system-design | 2026-06-21 | llm-inference, batching, kv-cache, gpu, scaling, hard | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q1-inference-api) |
| Onsite Hm Behavioral | behavioral | very-high | 55 | onsite-bq | 2026-06-23 | behavioral, collaboration, leadership, mentorship, impact | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/onsite-hm-behavioral) |
| Coding Q6 Tokenizer | coding | medium | 55 | phone-screen, onsite-coding | 2026-06-26 | string-processing, greedy, trie, python, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q6-tokenizer) |
| Onsite Culture Ai Safety | behavioral | very-high | 55 | onsite-bq | 2026-06-26 | culture, ai-safety, values, critical-thinking | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/onsite-culture-ai-safety) |
| Agents Coding Llm Tool Use | coding | medium | 55 | phone-screen, tech-screen | 2026-06-29 | llm, agents, tool-use, prompt-engineering, colab, medium | [看题](https://www.1point3acres.com/interview/problems/company/anthropic/agents-coding-llm-tool-use) |

# 四、OJ 题库（站内原生题，链接自行查看）

| 题目 | 链接 |
|---|---|
| Fix a Buggy LRU Cache Key Built from args and kwargs | [看题](https://www.1point3acres.com/interview/problems/314ff29a-4b15-5906-b526-b347b7b1bfb2) |
| Optimized Infection Simulation on a 2D Grid | [看题](https://www.1point3acres.com/interview/problems/01599122-965f-57e6-99b0-d43238e938fc) |
| Longest-Match Tokenizer with Unknown Token Merging | [看题](https://www.1point3acres.com/interview/problems/48917c0b-2887-5f92-8547-15fedbc869aa) |
| Multi-Level In-Memory Database with TTL and Time Travel | [看题](https://www.1point3acres.com/interview/problems/a3816a9d-04af-5a4a-8363-20be75018fd2) |
| Stack Trace Suffix Matching | [看题](https://www.1point3acres.com/interview/problems/3f55c628-6ee0-5304-8799-4ae500643827) |
| Find Duplicate Files in a File System | [看题](https://www.1point3acres.com/interview/problems/b8e1c8cd-db6a-557c-ad93-1c39e581475d) |
| Find All Possible Recipes from Given Supplies | [看题](https://www.1point3acres.com/interview/problems/89c84243-c0ab-5947-8e9b-9a29a3f7895c) |
| Find Duplicate Files by Content | [看题](https://www.1point3acres.com/interview/problems/4b32579d-bdcc-5a45-96da-f8c56b1aafe4) |
| Find Duplicate Files by Content | [看题](https://www.1point3acres.com/interview/problems/ab528b5f-7c0a-5745-adfb-22d830ac4807) |
| Fix Bootloader Program by Swapping One Instruction to Avoid Loop | [看题](https://www.1point3acres.com/interview/problems/61e8a96a-9a4c-4360-8605-6dc9dced96a8) |
| DNS Solver Implementation (Round 1) | [看题](https://www.1point3acres.com/interview/problems/a540d34e-f411-435f-a363-e46f29964ad4) |
| Debug / Fix an Extremely Randomized Trees (ExtraTrees) Implementation in NumPy | [看题](https://www.1point3acres.com/interview/problems/84071144-2958-4ae1-aeca-131436139171) |
| Task Management System (CRUD + Priority Ordering + User Quota + History Query) | [看题](https://www.1point3acres.com/interview/problems/284aa27f-5e4a-45d2-b3d9-49d46fd2b2e5) |
| Thread-Safe Linked List Task Queue Transformation | [看题](https://www.1point3acres.com/interview/problems/549736b2-61b8-48ae-aa7f-45dbce76c46b) |
| High-Concurrency Prompt Template Deduplication (Array + Hash Map) | [看题](https://www.1point3acres.com/interview/problems/c70ba245-6dae-4c2d-a468-a77101e44faf) |
| LLM-Oriented String Processing (Technical Phone Screen) | [看题](https://www.1point3acres.com/interview/problems/5ca0d0e0-a2d7-422b-ac91-29e2ff6cbd2a) |
| Implement an LRU Cache | [看题](https://www.1point3acres.com/interview/problems/fef6cb52-1fcf-44cf-8072-e610257ede5e) |
| In-Memory Database with Backup and Restore | [看题](https://www.1point3acres.com/interview/problems/1091f5c2-4b7c-4b13-9db8-7caada56c79f) |
| Basic SQL Exercise + Learning/Skill-Growth Discussion | [看题](https://www.1point3acres.com/interview/problems/a278d355-79f7-44a0-8a10-ce7e6c8e055f) |
| Python Data Analysis on a Provided Dataset (Capacity Management Context) | [看题](https://www.1point3acres.com/interview/problems/d03ad0c8-580a-4af4-8619-328ea8011719) |
| Implement a UI From a Figma Mock in React + TypeScript | [看题](https://www.1point3acres.com/interview/problems/1a1fb907-7914-40b7-aa33-f5825437aa91) |
| Implement an LRU Cache (HashMap + Doubly Linked List) and Debug an Existing Implementation | [看题](https://www.1point3acres.com/interview/problems/4d278295-f27d-4425-9bc3-2be3388a320c) |
| Implement a Weighted Data Batcher with Deterministic Save/Resume (DataRegistry Iterator Interface) | [看题](https://www.1point3acres.com/interview/problems/afa9e386-7de2-4dd2-8747-3810328a9c39) |
| Image Processing Pipeline (Grayscale / Scale / Resize) with Performance Optimization | [看题](https://www.1point3acres.com/interview/problems/6d14e9e2-3f95-453c-aca6-3f04fcbb34f0) |
| Find and Deduplicate Duplicate Files (by size and by content hash) | [看题](https://www.1point3acres.com/interview/problems/8a4bd412-9a23-4420-9802-67e8a38e8448) |
| Single-thread Web Crawler, then Multi-threaded Crawler | [看题](https://www.1point3acres.com/interview/problems/24ef32e6-b554-41ca-977b-307982b4d871) |
| File Deduplication (find duplicate files) | [看题](https://www.1point3acres.com/interview/problems/42afe615-f6b2-494c-807f-37c309841f8b) |
| Web Crawler (single-threaded first, then concurrent) | [看题](https://www.1point3acres.com/interview/problems/3823a702-699e-4bf5-bd78-8ce518c640ad) |
| Debug an LRU Cache Implementation + Persistence After Crash (Follow-ups) | [看题](https://www.1point3acres.com/interview/problems/f8f1f1af-e60a-4322-9122-43d00c8db24f) |
| Implement a Same-Domain Web Crawler with Deduplication (Sync + Async Follow-up) | [看题](https://www.1point3acres.com/interview/problems/40fd31e7-ff92-4cc8-946f-cd43f39a9412) |