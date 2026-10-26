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
