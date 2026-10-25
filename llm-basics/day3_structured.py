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
import json

from pydantic import BaseModel, Field, ValidationError
from typing import Literal

from common import MODEL, client, failed, passed


class Contact(BaseModel):
    name: str = Field(description="Name of the email sender")
    email: str | None = Field(description="Email ID of the email sender, null if not mentioned")
    company: str | None = Field(description="Company of the email sender, null if not mentioned")
    phone: str | None = Field(description="Phone number of the email sender, null if not mentioned")
    intent: Literal["sales", "support", "partnership", "other"] = Field(description="The sender's intent for emailing. Assign the email to one of the four categories based on the content or ask in the email. sales = Interested in buying the product. support = Wants support with the product. partnership = Asking about a business partnership. other = None of the other intents")

class JSONOutputError(Exception):
    """Raised when there is an error in the output json"""

def extract_contact(email_text: str) -> Contact:
    """Extract a Contact from one email using client.messages.parse."""
    try: 
        response = client.messages.parse(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": email_text}],
            output_format=Contact,
        )
        
    except ValidationError as error:
        raise JSONOutputError("The output gave an error in the form of refusal or max_tokens") from error

    if response.stop_reason == "end_turn":
        return response.parsed_output
    raise JSONOutputError(f"The output gave an error: {response.stop_reason}")


def extract_by_hand(email_text: str) -> dict:
    """Same task WITHOUT structured outputs: ask for JSON in the prompt, then json.loads.

    Do this to feel why structured outputs exist. Note how often it breaks (or doesn't).
    """
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Generate a JSON output from this input email where the field are name, email, company, phone, intent. Email, company, phone, are to be set to null if not mentioned. Assign the email to one of the four categories based on the content or ask in the email. sales = Interested in buying the product. support = Wants support with the product. partnership = Asking about a business partnership. other = None of the other intents. Only return the json in the format I asked for. Add nothing else in the output. <email> {email_text} </email>"}],
    )

    if message.stop_reason == "end_turn":
        json_string = ''.join(res.text for res in message.content if res.type == "text")
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise JSONOutputError("The JSON output gave an error while parsing") from e
    raise JSONOutputError(f"The output gave an error: {message.stop_reason}")
    

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
    print("\nBy hand:", extract_by_hand(emails[2]))
    passed("Day 3 structured outputs")


if __name__ == "__main__":
    check()
