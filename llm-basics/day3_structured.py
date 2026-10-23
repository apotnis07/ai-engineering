"""Day 3: Structured outputs: JSON that matches a schema.

Read first: docs.claude.com → "Structured outputs". Also the Pydantic "Models" page.

Things to notice while you read:
- `client.messages.parse(..., output_format=YourPydanticModel)` constrains the output to
  your schema and returns `response.parsed_output` as a validated instance.
- The lower-level form is `output_config={"format": {...json schema...}}` on messages.create.
  (Old tutorials use a top-level `output_format=` on create: that's deprecated.)
- Field descriptions in your schema act like instructions to the model.

Done when: PASS prints for all sample emails in data/emails.txt.
"""

from pathlib import Path

from pydantic import BaseModel, Field

from common import MODEL, client, failed, passed


class Contact(BaseModel):
    # TODO: add fields. Suggested: name (str), email (str | None), company (str | None),
    # phone (str | None), intent (one of "sales", "support", "partnership", "other").
    # Use Field(description=...) to tell the model what each field means.
    # Hint for intent: typing.Literal["sales", "support", "partnership", "other"]
    pass


def extract_contact(email_text: str) -> Contact:
    """Extract a Contact from one email using client.messages.parse."""
    # TODO
    raise NotImplementedError


def extract_by_hand(email_text: str) -> dict:
    """Same task WITHOUT structured outputs: ask for JSON in the prompt, then json.loads.

    Do this to feel why structured outputs exist. Note how often it breaks (or doesn't).
    """
    # TODO
    raise NotImplementedError


def check() -> None:
    emails = Path("data/emails.txt").read_text().split("\n---\n")
    expected = [("Priya Raman", "sales"), ("Tom Becker", "support"), ("Ana Silva", "partnership")]
    for email, (name, intent) in zip(emails, expected):
        c = extract_contact(email)
        print(c.model_dump())
        if name.split()[0] not in c.name:
            return failed("name", f"expected {name}, got {c.name}")
        if c.intent != intent:
            return failed("intent", f"expected {intent} for {name}, got {c.intent}")
    print("\nBy hand:", extract_by_hand(emails[0]))
    passed("Day 3 structured outputs")


if __name__ == "__main__":
    check()
