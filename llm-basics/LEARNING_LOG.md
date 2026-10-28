# Learning log

Two or three lines a day: what surprised you, what broke, what you'd do differently.

## Day 1 — Messages
get_text() loops over the blocks instead of grabbing content[0].
The newer models may include a thinking block along with text.
The system parameter is a top-level field to apply instructions from the start.
A {"role" : "system", "content: "..."} can be passed in the newer models to change the system instruction mid-conversation. A system message that carries content cannot be the first entry in messages.
For passing optional arguments like effort and system to the messages API, use an inline if-else condition. This checks if the kwarg is truthy(not empty). 
The system, output_config(effort) parameters do not accept None. So whenever the kwarg is not passed we use omit instead. Think of omit = act as if I never passed this argument. Using system=None does not mean not passing a value. 

What surprised me:
In the history list, if you only append user responses and not assistant responses then claude still answers but based only on your questions and not its own responses. This can be a quiet failure.
Why context window gets bloated after long conversations makes more sense now.

What broke:
If you don't put chat() in a while loop it only works for 1 turn 
The API calls are stateless. So, if you don't pass in the history it will not remember the previous conversation. 

Worth exploring:
Seeing that the context window gets bloated, why do we not save the history as a summarized compacted version of the response. Like maybe the user response could be small in length, but the assistant response tends to be longer. So, could we not summarize it like /compact in claude code before appending it to history. Could save tokens. But might also take tokens in the actual task of summarizing it. So there might be a balance to this. Like summarize the assistant response if its more than 1000 output tokens. Because that 1000 output tokens would be added as input tokens in the next turn. But the /compact would be a one time effort

## Day 2 — Streaming
stream.get_full_text() is equivalent to the get_text() method from day 1 done by SDK.
for text in stream.text_stream is only delta.text from content_block_delta events;
for event in stream is all the raw SSE events

What surprised me:
By streaming it saves so much time to the first token. Making the AI integrated app that much more user friendly.
Does non-streaming and streaming total take same time on average? Streaming lowers TTFT, but not total time (one run is noisy).

What broke:
Reuse functions wherever possible to limit the lines of code
Wrote input and history outside the while loop. This would cause the chat to never quit as "quit" cannot be written after the first turn. Only adds user, assistant, assistant, ...
When appending content to assistant, all the message content is supposed to be passed.

## Day 3 — Structured outputs
The field description is the actual prompt. Claude will be looking at that when assigning values to the fields.


The first part of the process is the API constraints what claude can generate(json matching the schema)
Pydantic(via parse()) does the "validation" for the output JSON with the BaseModel. In actuality it takes the output and creates a new structured output and then tries to fit it. If it is not able to it raise the ValidationError. The client.messages.parse itself raises the error so it is enclosed in a try/except block. 

raise...from err is a way to chain exceptions and hence call your own exception.
parse() validates eagerly and raises ValidationError on truncation(max_tokens) 
The code should handle stop reason like refusal and max_tokens gracefully as these errors are prioritized over the structured output.
We did not handle it gracefully today but we did make it fail loudly with a clear message which is a good practice.

The extract_by_hand gave a correct output in the cases I ran today. But that can be flaky and hence structured output is preferred.
## Day 4 — Tokens and cost
The count_tokens() method estimates input tokens so that we can estimate how much an input or a prompt would cost before sending it
It can also estimate for images and pdfs but url is not supported and should be given in the base64 format
csv.DictWriter handles the dict writing very well. It maps dict keys to columns, and writeheader() writes the header row for you.
input token cost is usually far less than output token cost considering not a long context, so rather than focusing on making the prompt small, try to make the output short
datetime.now().isoformat(timespec="seconds")  # 2026-10-26T14:03:12 is a ISO 8601 standard format and spreadsheets and pandas parse it without help

What broke:
usage["input_tokens"] raised TypeError because usage is a Pydantic object, and count_tokens returned an object instead of an int

## Day 5 — Prompt caching
You can cache for 5m or 1h. 1h is paid.
When you cache for 5m, for example, the time starts from when you first send a request. So, if a thinking block takes 4 minutes to answer you only have about a minute of cache ttl.
That does not mean the conversation has to last for 5 mins for the messages to stay cached. The 5 minutes renew after every turn within the 5m window. 
So the chat can go on for hours, but messages should not be more than 5m apart.
When within cached window ttft is faster.
The cost of prefix(previous messages in memory) is ~10% of input price.
cache_read_input_tokens are required though to read the cache. --> available to view in response.usage
Caching makes the tokens you resend cheaper.


Setup
P: tokens in the prefix you reuse (the document, or the chat history)
c: normal input price per token
w: cache-write multiplier. It’s 1.25 in your PRICES (0.125 ÷ 0.10 for Haiku)
r: cache-read multiplier. It’s 0.1 for Haiku and 0.05 for Opus in your PRICES
n: number of calls that reuse the prefix

Output tokens and the new question at the end cost the same either way, so they cancel out of the comparison.

Case 1: every call lands within the TTL
No cache:   n · P · c
Cache:      P · c · (w + (n − 1) · r)      ← 1 write, then n−1 reads
Caching wins when

w + (n − 1)·r  <  n      →      n  >  (w − r) / (1 − r)

With Haiku’s numbers: (1.25 − 0.1) / (1 − 0.1) = 1.28, so caching pays off from the 2nd call. A prefix used once costs 25% more (w − 1), and one reuse already puts you ahead.

n_calls	  No cache	Cache	Saving
1	        1.00	1.25	−25%
2	        2.00	1.35	33%
5	        5.00	1.65	67%
20	        20.00	3.15	84%
∞		            	    → 1 − r = 90%

Case 2: some calls arrive after the cache expired

Let p be the fraction of calls that land within the TTL of the previous one. Each call is either a hit (r) or a rewrite (w):

expected cost per call (cache) = p·r + (1 − p)·w
caching wins when  p·r + (1 − p)·w < 1   →   p  >  (w − 1) / (w − r)

Haiku: 0.25 / 1.15 ≈ 22%. If more than about 1 in 5 calls arrives within 5 minutes of the previous one, caching is cheaper on average.


Automatic caching vs Explicit 
For system prompts, both types of caching cache it.
But the order of caching is tools -> system -> messages

So say a cache with user A and messages M is built and all the users share the same system prompt we would get tools -> system -> Msg(A) with automatic caching
but with explicit system caching tools -> system

In the case of automatic caching of A, the next messages in A's chat window would cache hit. But they won't in B's window. 
Whereas the explicit system cache would hit in B.

Situation	            Without the system breakpoint	    With it
Next turn, same chat	hits B	                            hits B
Brand-new chat, 
same system prompt	    miss: pays to write everything	    hits A, writes only the messages
An earlier message	    miss	                            hits A
edited


Key takeaway: Place cache_control on the last block whose prefix is identical across the requests you want to share a cache. In a growing conversation the final block works as long as each turn adds fewer than 20 blocks: earlier content never changes, so the next request's lookback finds the prior write. For a prompt with a varying suffix (timestamps, per-request context, the incoming message), place the breakpoint at the end of the static prefix, not on the varying block.

