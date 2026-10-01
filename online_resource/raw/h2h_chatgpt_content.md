## 1. ð¤ What is ChatGPT?

ChatGPT is an AI-powered conversational assistant where users type text prompts and receive AI-generated responses in real time. The system maintains multi-turn conversations, streaming each response token by token so the user sees output appearing progressively rather than waiting for a complete answer.

## 2. Requirements

We are designing the backend for a ChatGPT-like conversational AI service where users send text prompts within multi-turn conversations, the system assembles conversation context, dispatches inference to a GPU cluster, and streams generated tokens back in real time via *Server-Sent Events (SSE)*. The core tension is that users expect sub-second responsiveness, but every response requires expensive GPU inference that takes seconds to produce, so the architecture must bridge this gap with streaming delivery, intelligent scheduling, and a lean pre-inference pipeline.

### Clarifying Questions

::::qa-item
:::you[You]
"Should the system persist conversation history durably, so users can resume a conversation across sessions?"
:::
:::interviewer[Interviewer]
"Yes, conversations must be durable. Users expect to return to a thread days later and continue from where they left off."
:::
:::takeaway[Takeaway]
Durable conversation history is part of the core product contract, not an optional extra. The design therefore needs a clear boundary between persisted conversation state and the live streaming path.
:::
::::

::::qa-item
:::you[You]
"What latency targets apply to the streaming response? Specifically the time before the first token appears and the token delivery rate once the stream is running?"
:::
:::interviewer[Interviewer]
"Time-to-first-token at or below 500 milliseconds at p50 and 2 seconds at p95. Once streaming begins, the delivery rate should be 30 to 60 tokens per second per stream."
:::
:::takeaway[Takeaway]
The synchronous path before the first token has a tight latency budget. Context loading, safety checks, and scheduling overhead all have to fit within that budget instead of growing unchecked.
:::
::::

::::qa-item
:::you[You]
"When a conversation grows longer than the model's token limit, what should the system do with the excess history?"
:::
:::interviewer[Interviewer]
"Truncate the oldest turns. Users understand that very long conversations lose early context. We do not need to summarize. Just drop from the beginning."
:::
:::takeaway[Takeaway]
This makes truncation the required behavior when history exceeds the model limit. The system needs a predictable way to assemble recent context without pretending the full conversation always fits.
:::
::::

<!-- ###PREMIUM_CONTENT_DELIMITER### -->

::::qa-item
:::you[You]
"How many simultaneous inference requests should the system be able to serve at peak?"
:::
:::interviewer[Interviewer]
"Around 50,000 concurrent inference requests at peak. GPU compute is the dominant cost, so utilization efficiency matters."
:::
:::takeaway[Takeaway]
At this scale, the core problem is no longer just request handling. The system needs an explicit policy for who gets scarce GPU capacity first when demand exceeds supply.
:::
::::

::::qa-item
:::you[You]
"What should happen if the SSE connection drops before the AI has finished generating the response?"
:::
:::interviewer[Interviewer]
"The partial response should be recoverable. If the user refreshes or reconnects, they should be able to see what was generated before the disconnect."
:::
:::takeaway[Takeaway]
Recovery must include already generated assistant text, not just fully completed prior turns. The persistence contract therefore has to support reconnecting users seeing what the system had already produced before the stream broke.
:::
::::

::::qa-item
:::you[You]
"When the GPU cluster reaches capacity and cannot immediately serve all incoming requests, what is the priority policy, and is it acceptable to reject some requests?"
:::
:::interviewer[Interviewer]
"Paid subscribers must be served within SLO. Free-tier users can be queued or rejected with a clear error. Do not drop paid requests under any normal operating condition."
:::
:::takeaway[Takeaway]
This makes service tier part of the scheduling contract. Under overload, the system must protect paid-user latency even if free-tier traffic waits longer or gets rejected.
:::
::::

### Functional requirements

- Users can send a text message within a conversation and receive an AI-generated response streamed token by token.
- Users can create new conversations, list existing ones, and resume a previous conversation with full history context.
- The system assembles relevant conversation history into a context payload for each inference request, respecting the model's token limit.
- The system enforces safety guardrails on both user input (prompt filtering) and model output (response filtering) before delivery.
- The system applies per-user rate limits and token-budget caps based on subscription tier.

:::collapse[Out of scope (below the line)]{variant="warning"}
- Image, audio, video, or multi-modal input/output
- Plugin, tool-use, or function-calling orchestration
- Model training, fine-tuning, or *reinforcement learning from human feedback (RLHF)* pipeline
- Retrieval-augmented generation (RAG) with external knowledge
- Multi-model marketplace or model-selection UI
- Admin dashboard, analytics, or billing internals
:::

### Non-functional requirements

- *Time-to-first-token (TTFT)* at or below `500 ms` at p50 and `2 s` at p95 under normal load.
- Sustained token throughput of `30` to `60` tokens per second per active stream.
- `99.9%` availability for the chat completion API.
- Support `100M` registered users, `10M` daily active users, and peak `50K` concurrent inference requests.
- Completed conversation turns must survive service restarts. In-flight partial responses can be regenerated on failure.
- GPU compute dominates operational cost. The design must address utilization efficiency and tier-based throttling.

### Back-of-the-envelope estimation

| Metric | Value | Drives |
|---|---|---|
| Registered users | 100M | User and conversation storage sizing |
| Daily active users | ~10M | API gateway and SSE connection pool |
| Peak concurrent inference | ~50K | GPU cluster capacity and admission control |
| Average tokens per response | ~300 | GPU-seconds per request and cost modeling |
| Model context window | ~8K tokens | Context assembly budget and truncation strategy |
| Target TTFT (p50) | â¤ 500 ms | Latency budget for pre-inference pipeline |
| Token throughput per stream | 30â60 tokens/s | SSE delivery rate and GPU decode speed |

The concurrent inference count is the most consequential number. At 50K simultaneous requests hitting a finite GPU cluster, the system cannot naively queue everything. Admission control, continuous batching, and tier-based priority scheduling determine who gets GPU time and who waits or gets rejected. This constraint shapes the entire inference pipeline described in the High-Level Design and every deep dive that follows.

The TTFT target also deserves attention. The `500 ms` p50 budget must cover rate-limit checks, context assembly from stored history, safety pre-screening, and the time for the GPU to produce the first decoded token. Every millisecond spent in the pre-inference pipeline eats into GPU scheduling time. This forces the design to keep the synchronous pre-inference path lean and push heavier work to asynchronous processing where possible.

## 3. Data model design

Completed conversation turns are the durable truth of this system. Once a user message and the corresponding assistant response are saved, they must survive crashes and restarts. Conversation metadata (title, model version, timestamps) must also be durable for listing and resumption. In-flight token streams are ephemeral. If the server crashes mid-generation, the partial response is discarded and the client retries. Rate-limit counters and inference queue state live in Redis and are rebuilt on restart.

::img[Conversation and message data model]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/5a3561a6-da2b-46cc-b822-c492a9c9b81f_20260409.svg"}

The durable boundary is intentionally small. The conversations table owns conversation-level metadata: user ID, title, model identifier, and timestamps including an updated_at column bumped on every new message. The messages table stores the conversation log: each row represents one turn with a role column (user, assistant, or system) that distinguishes them. A token_count column on each message supports context budget tracking, allowing the context assembler to sum tokens from recent history without re-tokenizing stored text. The usage_tracking table aggregates per-user token consumption by time period for rate-limit enforcement and billing. The authoritative rate-limit check runs against Redis for speed, but usage_tracking in PostgreSQL provides a durable fallback and audit trail.

### Access patterns

- **Context assembly**: fetch messages by conversation_id, ordered by created_at, summing token_count until the budget is reached. This is the hot read path and benefits from a composite index on (conversation_id, created_at). Redis caches the assembled context keyed by conversation_id and the hash of the last included message_id, keeping repeat context assembly under the 50 ms TTFT budget for follow-up turns.
- **List conversations**: query by user_id, ordered by updated_at descending, paginated. A standard B-tree index on (user_id, updated_at) serves this efficiently.
- **Append a completed turn**: insert the user message row at request time, then insert the assistant response row after generation completes. The conversation's updated_at is bumped on each insert.
- **Rate-limit check**: read current-period usage for the user from Redis. Fall back to usage_tracking on cache miss.

### Storage tradeoff

PostgreSQL handles all durable state. The scale here (roughly 50K concurrent inference requests, not billions of writes per day) does not require a specialized write-heavy store. Conversation-scoped access patterns map naturally to relational indexes, and the transactional consistency of PostgreSQL keeps turn persistence simple: the assistant response is either fully written or not present at all.

Redis serves the ephemeral hot-path state: rate-limit counters with atomic `INCR` and time-to-live (TTL) based expiration, per-user token budgets for the current billing period, and cached conversation metadata to avoid database round-trips during context assembly. Redis is a helper here, not the source of truth. If Redis is flushed, the system rebuilds counters from PostgreSQL and continues serving.

The alternative would be a wide-column store like DynamoDB for the message log, which would scale writes more aggressively. But the write volume for this system is moderate (each inference request produces one user row and one assistant row), and the relational flexibility for conversation listing and metadata queries makes PostgreSQL the simpler, interview-defensible default.

## 4. API design

The client contract for this system has two sides. The SSE stream is the fast path: tokens arrive in real time as the model generates them. The REST conversation history endpoint is the durable truth: after a stream drops or the client reconnects, history is the only reliable record of what was said. Clients should treat the stream as best-effort and the stored conversation as authoritative.

User messages are sent via REST POST. Generated tokens flow back through an SSE stream on the same HTTP connection. Internally, the API layer communicates with GPU inference workers over gRPC for low-overhead, schema-typed dispatch. These three communication modes are each chosen for a specific reason, not assembled as a general-purpose stack.

### Send a message and stream the response

`POST /v1/chat/completions`

This is the core interface. The client sends a user message with a conversation_id. The server acknowledges the request, opens an SSE stream on the response, and begins delivering generated tokens as they are produced. Each SSE event carries a content delta (the next chunk of text), the role (always assistant for generated output), and eventually a finish reason (stop, length limit, or error) and token usage metadata.

The request includes a conversation_id to resume context and a content field with the user's message. The server handles context assembly, safety checks, and inference dispatch internally. The client never sends raw token arrays or model parameters in this scoped design.

If the client needs to cancel generation mid-stream, it closes the SSE connection. The server detects the closed connection and signals the inference worker to stop decoding, freeing GPU resources for other requests.

### SSE event stream contract

The stream emits four event types: `delta` (a content chunk), `usage` (token counts for the completed turn), `done` (generation finished successfully), and `error` (something went wrong). Delta events arrive continuously at the model's decode rate, typically 30 to 60 per second. The `done` event triggers the server to persist the completed assistant message to PostgreSQL.

The client accumulates deltas locally and renders them progressively. If the stream drops before a `done` event, the client has a partial local copy but no server-side guarantee that it was saved. Recovery happens through the history endpoint described below.

:::collapse[Bad Solution: WebSocket for token streaming]{variant="bad"}
WebSocket provides a full-duplex channel, which is unnecessary here. Token streaming is unidirectional: the server sends tokens to the client. The client's only outbound action (sending a new message) happens via a separate REST POST, not on the same connection. WebSocket adds complexity in connection management, is harder to proxy through CDNs and load balancers, and requires the client to handle bidirectional framing for a fundamentally one-way data flow.
:::

:::collapse[Good Solution: SSE over HTTP/2]{variant="good" open}
SSE is purpose-built for server-to-client streaming. It works natively over HTTP/2 with multiplexing, simplifies reconnect semantics (the browser handles EventSource retries automatically), and matches what the real ChatGPT API uses. Because user messages travel via REST, there is no need for a bidirectional channel. SSE is the simpler, more appropriate transport for this use case.
:::

### Fetch conversation history

`GET /v1/conversations/{conversation_id}/messages?cursor={message_id}&limit=50`

Returns messages for a conversation, paginated by cursor. This endpoint serves two purposes: scrollback for browsing older messages and recovery after a dropped stream. The client provides the last message_id it has seen as the cursor. If the cursor is omitted, the server returns the most recent page.

This is the authoritative recovery path. After any stream failure, the client fetches history to determine what was actually persisted and what needs to be regenerated.

### Supporting endpoints

- **Create a conversation**: `POST /v1/conversations` creates a new conversation and returns a conversation_id.
- **List conversations**: `GET /v1/conversations` returns the current user's conversations sorted by last activity, paginated.
- **Delete a conversation**: `DELETE /v1/conversations/{conversation_id}` removes a conversation and its messages.

> [!TIP]
> In the interview, spend your time on the streaming endpoint, the SSE event contract, and the history recovery path. These three define the system's core contract. Conversation CRUD is standard and can be described in one sentence each.

## 5. High-level design

Users expect to see output within half a second, but every response requires GPU inference that takes seconds to produce. I want to start with the minimal design that delivers streaming tokens correctly, then show where it falls short under real operating pressure.

### Core Architecture

A single Chat Service accepts a POST to `/v1/chat/completions`, fetches the user's recent messages from PostgreSQL to assemble a token-counted context payload, and dispatches that payload to a GPU worker pool over gRPC. As each token is decoded, the worker streams it back to the Chat Service, which forwards it to the client as an SSE delta event. Completed turns are written to PostgreSQL after generation finishes. One service, one database, one GPU worker pool. No inference orchestrator, no safety pre-check, no continuous batching.

::img[ChatGPT minimal: single Chat Service, PostgreSQL, and GPU worker pool]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/29e2d877-0807-41c4-b624-9f450807c09f_20260529.svg"}

This minimal design works as a prototype, but three specific gaps prevent it from scaling under real operating conditions:

- A GPU worker that completes one full sequence before starting the next holds unused capacity between decode steps. Without continuous batching, GPU utilization collapses as concurrent requests grow.
- With no pre-inference safety check, every policy-violating prompt reaches the GPU worker unchanged, consuming expensive compute before the system can reject it.
- Without a dedicated scheduling layer, routing logic for directing requests to available workers, enforcing tier-based priority, or isolating a canary model version must live inside the Chat Service itself.

Those three gaps (batching efficiency, pre-inference gating, and scheduling isolation) are what the inference orchestrator layer is designed to address.

::img[ChatGPT system architecture]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/68f94094-4315-425d-83f9-e8a03dfb0d42_20260409.svg"}

The architecture has five layers, introduced here as they appear in the request flow. The API gateway handles authentication, TLS termination, and request routing. The chat service sits behind the gateway and owns the business logic: rate limiting, context assembly, safety checks, and conversation persistence. The inference orchestrator is an internal scheduling layer that accepts context payloads from the chat service over gRPC and dispatches them to available GPU workers. The GPU worker pool runs vLLM with continuous batching, generating tokens and streaming them back through the orchestrator to the chat service and out to the client via SSE. PostgreSQL stores conversations and messages. Redis handles rate-limit counters, per-user token budgets, and cached conversation metadata for fast context assembly lookups.

### The chat completion flow

::img[Chat completion flow: message to streaming response]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/828574cc-8c42-4d74-9e74-6f0d2fd40543_20260409.svg"}

When a user sends a message, the request passes through the API gateway to the chat service. The chat service performs three checks on the synchronous pre-inference path: a rate-limit check against Redis (does this user have remaining quota?), context assembly (fetch recent messages from PostgreSQL, sum token counts, truncate to fit the model's window), and a safety pre-check on the user's prompt (run the input through a lightweight classifier to catch obvious policy violations). These three checks must stay under 100 ms combined to preserve the TTFT budget, broken down in the next subsection.

If all checks pass, the chat service dispatches the assembled context payload to the inference orchestrator over gRPC. The orchestrator places the request in its scheduling queue and assigns it to a GPU worker when capacity is available. The GPU worker begins decoding tokens using vLLM's continuous batching engine.

As each token is decoded, the worker streams it back through the orchestrator to the chat service. The chat service forwards each token to the client as an SSE delta event. The user sees text appearing progressively. When generation finishes, the chat service sends a `done` event, persists the complete assistant message to PostgreSQL, and closes the SSE connection. The user's message was already persisted at the start of the flow.

If the SSE connection drops mid-generation, the partially streamed tokens are lost from the client's perspective. The server may or may not have persisted partial progress depending on implementation. In either case, the client's recovery path is the same: fetch conversation history via GET to see what was saved, then re-send the message if the assistant response is missing. The Deep Dives section examines this recovery contract in detail.

### TTFT budget breakdown

The time-to-first-token budget breaks down roughly as follows: rate-limit check (1 to 2 ms from Redis), context assembly (10 to 50 ms depending on conversation length and cache hit), safety pre-check (20 to 50 ms for a lightweight classifier), gRPC dispatch and queue wait (variable), and first-token decode on the GPU (200 to 400 ms for a warm model). The pre-inference overhead should stay under 100 ms so that the GPU decode time dominates the TTFT target.

### Admission control and caching

Redis is critical on the hot path. Rate-limit counters use atomic `INCR` with TTL-based sliding windows. Conversation metadata (token counts per message, conversation model version) is cached to avoid hitting PostgreSQL on every context assembly. The cache is rebuildable: if Redis restarts, the chat service falls back to PostgreSQL reads and repopulates the cache on the next request.

Rate limiting happens before any GPU work starts. This is intentional. GPU time is the most expensive resource in the system, and the design should reject over-quota requests before they consume any inference capacity. A request that passes the rate-limit gate but finds the inference queue full receives a 503 with a retry-after header, signaling the client to back off.

The inference orchestrator is the admission control boundary. When the GPU worker pool is saturated, the orchestrator stops accepting new requests and returns a backpressure signal to the chat service. The chat service translates this into the 503 response. Free-tier users hit this boundary first because the orchestrator prioritizes paid-tier requests in its scheduling queue.

This separation matters. The chat service handles all the cheap, fast pre-inference work (rate checks, context assembly, safety). The inference orchestrator handles all the expensive, slow GPU scheduling. Keeping these boundaries clean means the system can scale the API layer independently from the GPU fleet.

> [!TIP]
> A common mistake is treating this system as a simple API proxy: forward the prompt to a model endpoint and return the result. The real design is the orchestration layer between the API and the GPU cluster, where scheduling, batching, streaming, and safety all intersect.

## 6. Deep dives

The High-Level Design traced the request path from user message to streaming response. These deep dives examine where that path faces real engineering pressure: scheduling inference across a finite GPU cluster, assembling the right context within token limits, and recovering when the streaming connection fails mid-response.

### GPU inference scheduling and continuous batching

The GPU cluster is the most expensive and constrained resource in the system. A naive approach processes one inference request per GPU at a time: accept a request, run the full sequence to completion, then accept the next. This wastes the majority of GPU compute because the model spends significant cycles on memory-bound attention operations where the GPU arithmetic units sit idle between token decodes.

Continuous batching, the approach used by vLLM, solves this by allowing new requests to join an in-progress batch at every decode step. When the scheduler has an active batch generating tokens on a GPU, a new request can enter that batch immediately without waiting for the longest sequence to finish. As individual sequences complete and leave the batch, new ones take their place. The GPU stays busy instead of alternating between full utilization and idle wait.

::img[GPU inference scheduling and continuous batching]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/079db5a7-76a0-4b94-8c9e-ccb56ca66013_20260409.svg"}

> [!TIP]
> **How I'd say it in the interview**: "Continuous batching is what turns a per-request GPU monopoly into a shared resource. Without it, one long sequence blocks every other request on that GPU. With it, short completions leave and new ones enter at every decode step."

The key resource constraint is KV-cache memory. Each active sequence in a batch consumes GPU memory proportional to its context length. vLLM's `PagedAttention` allocates KV-cache in fixed-size pages rather than reserving a contiguous block per sequence, avoiding the memory fragmentation that would otherwise waste 60 to 80 percent of GPU memory. When memory pressure rises, the scheduler can preempt lower-priority sequences by evicting their KV-cache pages to CPU memory and resume them later.

The backpressure path is critical. When GPU memory is fully committed, the inference orchestrator stops accepting new requests from the chat service and returns a queue-full signal. The chat service translates this into a 503 with a retry-after header for the client. Paid-tier users get priority placement in the scheduling queue, while free-tier users are the first to be queued or rejected under load. This tiered admission control is how the system manages GPU cost pressure without degrading the experience for paying customers.

### Context window management and token budget assembly

Every inference request must fit within the model's context window, typically around 8K tokens for this design. The context assembler must decide what conversation history to include, what to truncate, and how much room to reserve for the model's generated response.

The token budget has four partitions: the system prompt (a fixed instruction block, usually 200 to 500 tokens), the current user message, reserved generation room (typically 1K to 2K tokens for the model's output), and conversation history filling the remainder. The assembler works backward from the budget. After subtracting the system prompt, user message, and generation reserve, the remaining tokens are allocated to conversation history. Messages are included newest-first until the budget runs out. Older messages beyond the budget are simply dropped.

::img[Context window token budget assembly]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/ecf2f266-9c5a-446f-9e7d-01085eed839a_20260409.svg"}

This newest-first truncation is the simplest strategy and works well for most conversations. The most recent exchanges carry the most relevant context for the model's next response. But for long conversations where earlier messages established critical facts (a user's name, project constraints, or specific instructions), truncation silently drops information the model needs.

The alternative is summarization: compress older turns into a shorter summary that preserves key facts while consuming fewer tokens. Summarization requires a separate inference call (using the same model or a smaller, faster one), which adds latency and GPU cost. For most conversations, the extra inference cost is not justified. A practical middle ground is to summarize only when conversation length exceeds a threshold (around 20 to 30 turns), cache the summary alongside the conversation, and refresh it periodically rather than on every request. This keeps the common case fast while preventing context degradation in extended conversations.

The context assembler caches its output in Redis, keyed by conversation_id and a hash of the last message_id included. If the user sends a follow-up message immediately, the assembler can extend the cached context with the new exchange rather than re-fetching and re-tokenizing the full history. This cache hit path is important for the TTFT budget because context assembly from a cold conversation with dozens of messages can take 30 to 50 ms.

### Streaming delivery contract and failure recovery

The SSE stream is not just a UX convenience. It fundamentally shapes the API contract, the failure recovery model, and the persistence boundary of the system. In a synchronous API, the server either returns a complete response or an error. With streaming, the server commits to a long-lived connection and begins delivering partial results before it knows the full cost or outcome of the response.

The event schema defines what the client can trust. Delta events carry content fragments. A `done` event signals that generation completed and the full response has been persisted to PostgreSQL. An `error` event signals a failure: model timeout, safety violation detected in output, or infrastructure error. If the client receives a `done` event, it knows the response is durable. If the stream drops without a `done` event, the client must assume the response is incomplete and may not have been saved.

::img[Stream failure and recovery flow]{src="https://assets.hack2hire.com/post/69d6f527c4c1bc791ee229e3/81dc4c77-ced0-4a41-af15-fc17fb686182_20260409.svg"}

The recovery contract is straightforward. After a stream failure, the client sends a GET request to the conversation history endpoint. If the assistant message appears in history, it was persisted before the drop and the client can display it. If it does not appear, the client re-sends the original message. The server treats this as a new inference request: it assembles context (which now does not include the failed response, because it was never saved), runs inference again, and opens a new stream. There is no server-side buffering of partial responses. The persistence boundary is the completed turn, not the individual token.

This design means the server can crash or restart mid-generation without corrupting conversation state. The only cost of failure is wasted GPU work on the interrupted response. The client retries, gets a fresh answer, and the conversation remains consistent.

> [!TIP]
> The streaming response is not just a UX trick. It reshapes the API contract (the server returns partial results before knowing the full outcome), the failure recovery model (stream is best-effort, stored history is truth), and the load-balancing strategy (the server commits to a long-lived connection with uncertain GPU cost). A strong interview answer presents this as a deliberate architectural choice, not just "we stream because it looks nice."

## 7. Other Considerations

### Safety guardrails pipeline and latency budget

Every request passes through two safety checkpoints: an input classifier that screens user prompts before inference and an output filter that scans generated text before delivery. The placement of these filters in the pipeline directly affects TTFT and overall latency.

The input classifier runs synchronously on the pre-inference path. It must be fast (under 20 ms) to stay within the TTFT budget. A lightweight text classifier handles common violations such as jailbreak patterns and obvious policy violations. Requests that pass move to inference. Requests that fail receive an immediate error response with no GPU cost incurred.

The output filter is trickier. Running it synchronously on every token would add intolerable latency to the stream. Running it only after full generation means the user sees the complete response before moderation catches a violation. The practical middle ground is chunked output filtering: batch the last N tokens and run the filter every 50 to 100 tokens. If a violation is detected mid-stream, the server sends an error event, truncates the response, and does not persist the violating content. This adds a small delay to the streaming cadence but catches problems before the full response is delivered.

### Multi-model routing and gradual rollout

When deploying a new model version, the system cannot switch all traffic at once. A bad model version could produce lower-quality responses, violate safety boundaries in new ways, or have different latency characteristics that break the TTFT budget.

The inference orchestrator supports routing rules that assign a percentage of traffic to each model version. A canary rollout starts with 1 to 5 percent of requests going to the new version while the rest stay on the current one. The routing decision is made per-request at dispatch time, not per-user, so the system can quickly shift traffic back if latency or safety metrics degrade.

Active conversations are pinned to the model version that started them. Switching models mid-conversation would change the model's behavior and potentially confuse context handling. The conversation's model field stores which version generated its history, and the orchestrator respects this when dispatching follow-up turns.

### Conversation summarization and extended context

For long-running sessions where early context matters, the newest-first truncation strategy described in the context window management deep dive silently drops information the model needs. Summarization (compressing older turns into a shorter summary) extends effective conversation memory without exceeding the token limit. The mechanics of the token budget, truncation thresholds, and caching are covered in that deep dive. The operational question here is cost: each summary refresh requires its own inference call, so free-tier users may have summarization disabled entirely to save GPU cost while paid-tier users get periodic automatic summaries.

### Cost management and tier-based throttling

GPU compute dominates operational cost. A single inference request generating 300 tokens consumes GPU-seconds that cost meaningfully more than the CPU and storage resources for the rest of the request lifecycle. Cost management is not an afterthought but an architectural concern that shapes admission control, scheduling priority, and the user-facing product tiers.

The system enforces two layers of throttling. Request-rate limits cap how many inference requests a user can make per minute (for example, 10 per minute for free tier, 60 for paid). Token-budget limits cap total tokens generated per day (for example, 50K tokens per day for free tier). Both limits are checked from Redis counters before any GPU work begins, ensuring that over-quota requests never consume inference capacity.

When the GPU cluster approaches capacity, the admission control layer in the inference orchestrator applies priority scheduling. Paid-tier requests are served first. Free-tier requests are queued, and if the queue exceeds a depth threshold, free-tier requests are rejected with a 429 response and a retry-after header. This ensures paying customers see consistent TTFT even during peak load while free-tier users experience graceful degradation rather than system-wide failure.

## 8. Interviewer expectations

### Junior

A junior candidate should identify that a ChatGPT-like system needs a database for conversation storage and some way to call a language model for responses. Expect a basic client-server model where the client sends a message and waits for the full response to come back. They may not initially think about streaming, but should be coachable toward it when asked what happens while the user waits for 20 seconds of generation. A simple conversations and messages data model is sufficient at this level. The candidate should recognize that GPU inference is slow and expensive when prompted about cost and latency.

### Intermediate

An intermediate candidate should propose streaming as the delivery mechanism and sketch the basic SSE contract: the server opens a stream and pushes token deltas until generation completes. They should separate the API layer from the inference layer and describe a context assembly step that fetches conversation history before calling the model. Expect a reasonable data model with conversations and messages tables, and an understanding that rate limiting matters because GPU compute is expensive. Strong intermediate answers will identify that the inference engine batches requests for efficiency, even if they do not fully explain continuous batching mechanics or KV-cache management.

### Senior

A senior candidate should drive the conversation toward GPU scheduling and continuous batching as the defining engineering challenge. They should defend SSE over WebSocket for unidirectional token streaming and explain the TTFT budget breakdown: what happens between the user pressing send and the first token arriving. Expect a clear streaming recovery contract where the stream is best-effort and stored history is truth. The strongest answers separate the fast pre-inference path from GPU-bound work, explain admission control and tier-based priority scheduling under load, and discuss where safety guardrails sit in the pipeline and how they affect latency. They should also articulate the context window management tradeoff between truncation and summarization, and explain why the persistence boundary is the completed turn rather than individual tokens.
