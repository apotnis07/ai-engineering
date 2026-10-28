"""Day 5: Prompt caching: send the same long prefix twice and measure the savings.

Read first: docs.claude.com → "Prompt caching".

Things to notice while you read:
- Caching is a PREFIX match: tools → system → messages. Change one byte early and
  everything after it misses the cache.
- Mark the end of the reusable part with "cache_control": {"type": "ephemeral"}
  (on a system text block), or pass cache_control at the top level of the request.
- There's a minimum prefix length (a few thousand tokens). Shorter prefixes silently don't cache.
- Check usage.cache_creation_input_tokens (written) and usage.cache_read_input_tokens (hit).

Before you start: put any long text (at least ~6,000 words) in data/long_doc.txt.
A public-domain book chapter from gutenberg.org works well.

Done when: the second call reads from the cache and PASS prints the savings.
"""

from datetime import datetime
from pathlib import Path

from common import MODEL, client, failed, passed

# Reuse your Day 4 helpers. Finish Day 4 first.
from day4_cost import cost_usd, log_call

DOC = Path("data/long_doc.txt")
SYSTEM_PROMPT = f"You are an expert on the following document. Answer any questions relating to it. <doc>{DOC.read_text()}</doc>"

def ask_about_doc(question: str, use_cache: bool):
    """Ask a question about the document, which goes in the system prompt.

    With use_cache=True, mark the system block with cache_control.
    Keep the system text byte-for-byte identical between calls.
    """
    
    system_block = [
        {
            "type" : "text",
            "text" : SYSTEM_PROMPT,
        }
    ]

    if use_cache:
        system_block[0]["cache_control"] = {"type" : "ephemeral"}

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_block,
        messages=[{"role" : "user", "content" : question}],
    )

    return response


def break_the_cache() -> None:
    """Experiment: put a timestamp at the START of the system prompt and show the cache misses.

    This is the most common real-world caching bug.
    """
    system_block = [
        {
            "type" : "text",
            "text" : datetime.now().isoformat(timespec="seconds"),
        },
        {
            "type" : "text",
            "text" : SYSTEM_PROMPT,
            "cache_control" : {"type" : "ephemeral"}
        }
    ]
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_block,
        messages=[{"role": "user", "content": "What is the main theme?"}]
    )

    print(response.usage)

    if not response.usage.cache_read_input_tokens:
        print("Cache broken")
    
def check() -> None:
    if not DOC.exists() or len(DOC.read_text().split()) < 6000:
        return failed("setup", "put at least ~6,000 words in data/long_doc.txt first")

    first = ask_about_doc("Summarize this in one sentence.", use_cache=True)
    second = ask_about_doc("What is the main theme?", use_cache=True)
    for label, r in [("cache write", first), ("cache read", second)]:
        log_call(label, r)
        print(label, r.usage)

    if not second.usage.cache_read_input_tokens:
        return failed("cache hit", "second call didn't read from the cache; is the prefix identical and long enough?")

    uncached = ask_about_doc("What is the main theme?", use_cache=False)
    log_call("no cache", uncached)
    saved = 1 - cost_usd(second.usage) / cost_usd(uncached.usage)
    print(f"Cached call was {saved:.0%} cheaper than the uncached one.")
    break_the_cache()
    passed("Day 5 prompt caching")


if __name__ == "__main__":
    check()
