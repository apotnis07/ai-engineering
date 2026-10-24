"""Day 2: Streaming responses to the terminal.

Read first: docs.claude.com → "Streaming messages".

Things to notice while you read:
- `client.messages.stream(...)` is a context manager (`with ... as stream:`).
- `stream.text_stream` yields text pieces as they arrive.
- `stream.get_final_message()` gives you the complete response (with usage) at the end.
- Streaming doesn't make the answer faster overall. It makes the FIRST words arrive sooner.

Done when: PASS prints, and the chat streams word by word.
"""

import time

from anthropic import omit

from common import MODEL, client, failed, passed


def stream_reply(messages: list[dict], system: str | None = None) -> tuple[str, float, object]:
    """Stream a reply to the terminal as it arrives.

    Returns (full_text, seconds_to_first_token, final_message).
    - Print each piece with print(piece, end="", flush=True).
    - Record time.perf_counter() before the call and when the first piece arrives.
    """
    start_time = time.perf_counter()
    with client.messages.stream(
        model=MODEL,
        max_tokens=500,
        system=system if system else omit,
        messages=messages,
    ) as stream:
        end_time = time.perf_counter()
        for i, text in enumerate(stream.text_stream):
            if i == 0:
                end_time = time.perf_counter()
            print(text, end="", flush=True)
        message = stream.get_final_message()
        full_text = stream.get_final_text()
    return (full_text, end_time - start_time, message)

def compare_latency(prompt: str) -> None:
    """Print time-to-first-token (streaming) vs total time (non-streaming) for one prompt."""
    start_time_NS = time.perf_counter()
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    end_time_NS = time.perf_counter()
    non_streaming_time = end_time_NS - start_time_NS


    start_time = time.perf_counter()
    _, ttft, _ = stream_reply([{"role": "user", "content": prompt}])
    end_time = time.perf_counter()

    total_streaming_time = end_time - start_time

    print(f"\nnon-streaming total: {non_streaming_time:.2f}s")
    print(f"streaming TTFT: {ttft:.2f}s")
    print(f"streaming total: {total_streaming_time:.2f}s")

def chat() -> None:
    """Day 1's chat loop, but streaming. Reuse your Day 1 logic."""
    history: list[dict] = []
    while True:
        user_input = input("\n>")
        if user_input == "quit":    
            break
        history.append({"role": "user", "content": user_input})
        _, _, final = stream_reply(history)
        history.append({"role": "assistant", "content": final.content})

def check() -> None:
    text, ttft, final = stream_reply([{"role": "user", "content": "Count from 1 to 20, comma separated."}])
    if "20" not in text:
        return failed("stream text", "didn't receive the full text")
    if not (0 < ttft < 30):
        return failed("time to first token", f"got {ttft}")
    if final.usage.output_tokens <= 0:
        return failed("final message", "no usage on final message")
    print(f"\nTime to first token: {ttft:.2f}s")
    compare_latency("Explain what an API is in 150 words.")
    passed("Day 2 streaming")


if __name__ == "__main__":
    check()
    chat()
