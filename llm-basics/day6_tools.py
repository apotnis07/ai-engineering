"""Day 6: Define 3 tools as JSON schemas and write the Python behind them.

Read first: docs.claude.com → "Tool use" (overview and "Define tools").

Things to notice while you read:
- A tool definition is just data: name, description, input_schema (JSON Schema).
  The model never runs anything. It only ASKS you to run something.
- The description is the prompt. Say what the tool does, when to use it and what it returns.
- When the model wants a tool, the response has stop_reason "tool_use" and a `tool_use`
  block with an id, a name and an input dict.
- tool_choice {"type": "any"} / {"type": "tool", ...} return a 400 on Opus 5.5. Use the
  default "auto" and ask for the tool in the prompt.

No API key needed for weather: Open-Meteo is free (open-meteo.com/en/docs and
open-meteo.com/en/docs/geocoding-api). City name → lat/long → current temperature.
Plain `urllib.request` and `json` from the standard library are enough here.

Done when: PASS prints. Today the model only asks for a tool. Tomorrow you answer it.
"""

import ast
from pathlib import Path

import requests

from common import MODEL, client, failed, passed

DATA_DIR = Path("data")

# TODO: three dicts, one per tool: "calculator", "get_weather", "read_file".
# Each input_schema is {"type": "object", "properties": {...}, "required": [...]}.
TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Evaluate an arithmetic expression and return the result as a string. "
            "Use this for any arithmetic, including steps inside a larger task, "
            "instead of working it out yourself."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "The arithmetic expression with operands and operators like +, -, /, * ."
                        "For example an expression could be (2 + 3) * 4 ."
                        "It does not support ** (powers) and sqrt(...) function, along with negative numbers like -3."
                    ),
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "Given the city, return the temperature in the city in degree celsius at this instant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The name of the city"}
            },
            "required": ["city"],
        },
    },
    {
        "name": "read_file",
        "description": (
            "Read a text file from the data folder and return its full contents. "
            "Use this when the user mentions a file or asks about what's in one."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "File name relative to the data folder, e.g. emails.txt. "
                        "Do not include the folder name itself. "
                        "Only files inside the data folder can be read."
                    ),
                }
            },
            "required": ["path"],
        },
    },
]


def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression like "(2 + 3) * 4" and return the result as a string.

    Never call bare eval() on text from a model. Why not? Look at the `ast` module.
    Raise ValueError on anything that isn't arithmetic.
    """
    try:
        tree = ast.parse(expression, mode="eval")

    except SyntaxError as e:
        raise ValueError(
            "The expression cannot be parsed to an arithmetic expression"
        ) from e

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise ValueError("Division by zero")

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right

        raise ValueError(f"not allowed: {type(node).__name__}")

    return str(evaluate(tree))


def get_weather(city: str) -> str:
    """Return the current temperature for a city, e.g. "Mumbai: 31.2°C".

    Raise ValueError if the geocoder finds no such city.
    """
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    response = requests.get(geocoding_url, params={"name": city, "count": 1})
    res = response.json()
    try:
        lat = res["results"][0]["latitude"]
        long = res["results"][0]["longitude"]
        country = res["results"][0].get("country", "")

    except KeyError as e:
        raise ValueError(f"{city} is not a valid city") from e

    forecast_url = "https://api.open-meteo.com/v1/forecast"

    response = requests.get(
        forecast_url,
        params={"latitude": lat, "longitude": long, "current": "temperature_2m"},
    )
    res = response.json()
    try:
        temp = res["current"]["temperature_2m"]
        unit = res["current_units"]["temperature_2m"]
        place = f"{city}, {country}" if country else city
        result = f"{place}: {temp}{unit}"
    except KeyError as e:
        raise ValueError(f"Weather data unavailable for {city}, {country}") from e

    return result


def read_file(path: str) -> str:
    """Return the text of a file inside DATA_DIR.

    Raise PermissionError for anything outside it, like "../.env". Resolve the path
    first (see Path.resolve and Path.is_relative_to): the model picks this argument.
    """
    absolutePath = (DATA_DIR / path).resolve()

    if absolutePath.is_relative_to(DATA_DIR.resolve()):
        return absolutePath.read_text()
    else:
        raise PermissionError("Only files inside data/ can be read.")


TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_weather": get_weather,
    "read_file": read_file,
}


def run_tool(name: str, tool_input: dict) -> str:
    """Look up the function by name and call it with the model's input dict."""
    return TOOL_FUNCTIONS[name](**tool_input)


def check() -> None:
    names = {tool.get("name") for tool in TOOLS}
    if names != set(TOOL_FUNCTIONS):
        return failed(
            "schemas",
            f"expected tools {sorted(TOOL_FUNCTIONS)}, found {sorted(map(str, names))}",
        )

    if run_tool("calculator", {"expression": "(2 + 3) * 4"}) not in ("20", "20.0"):
        return failed("calculator", "(2 + 3) * 4 should be 20")
    try:
        calculator("__import__('os').getcwd()")
        return failed(
            "calculator", "that wasn't arithmetic; it should raise ValueError"
        )
    except ValueError:
        pass

    print(run_tool("get_weather", {"city": "Mumbai"}))
    try:
        get_weather("Xqzzyplorp")
        return failed("get_weather", "a made-up city should raise ValueError")
    except ValueError:
        pass

    if "@" not in run_tool("read_file", {"path": "emails.txt"}):
        return failed("read_file", "data/emails.txt should come back with its text")
    try:
        read_file("../.env")
        return failed(
            "read_file", "../.env is outside data/; it should raise PermissionError"
        )
    except PermissionError:
        pass

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": "Use the calculator tool: what is 1234 * 5678?"}
        ],
    )
    print(response.stop_reason, [block.type for block in response.content])
    calls = [block for block in response.content if block.type == "tool_use"]
    if response.stop_reason != "tool_use" or not calls or calls[0].name != "calculator":
        return failed(
            "model", "the model didn't ask for the calculator; improve the description"
        )
    print("The model asked for:", calls[0].name, calls[0].input)
    passed("Day 6 tools")


if __name__ == "__main__":
    check()
