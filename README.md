# Agentic Tool-Use Reliability Test

A simple test that exposes how AI agents skip tool calls based on pre-trained knowledge. Built with [Strands Agents](https://github.com/strands-agents/sdk-python).

## The Finding

When given access to a dietary-info API and asked to check which menu items are vegan, agents don't check all items. They skip items they "know" aren't vegan — like Grilled Salmon, Beef Tenderloin, and Chocolate Lava Cake — and only check ambiguous ones like Caesar Salad and Margherita Pizza.

The catch: in this test, the Chocolate Lava Cake is the only vegan item. Across four models and 20 runs each, correct results ranged from 0-35%.

| | Sonnet | Opus | Kimi |
|---|---|---|---|
| Found the vegan item | 35% | 10% | 25% |
| Checked all 5 items | 35% | 10% | 25% |
| Checked 0 items | 10% | 80% | 50% |

## How It Works

`agent.py` defines a restaurant assistant with tools for browsing the menu, checking dietary info, checking availability, and booking tables. The menu has 5 items. The dietary API returns ground truth per item. The key detail: `Chocolate Lava Cake` is marked as **Vegan** in the API — counterintuitive enough that most models skip checking it.

A mock conversation history (15+ turns of casual chat) is pre-loaded with `--history` to simulate realistic context length.

## Repo Structure

```
├── agent.py                          # Restaurant agent with tools and mock history
├── results/
│   ├── sonnet_test_results.json      # Claude Sonnet 4.5 — 20 runs
│   ├── opus_test_results.json        # Claude Opus 4 — 20 runs
│   └── kimi_test_results.json        # Kimi — 20 runs
└── README.md
```

## Reproducing the Tests

### Prerequisites

```bash
pip install strands-agents strands-agents-bedrock
```

You'll also need AWS credentials configured for Bedrock access.

### Running the Agent Interactively

```bash
python agent.py --history
```

### The Test Prompt

With `--history` enabled, paste this prompt:

```
I'd like to book a table John Doe, 4 guests, 2026-03-15 at 10:00 PM. But, only if there if you have at least 1 vegan option. If there is, go ahead and book
```

### What to Observe

Track which tool calls the agent makes. The correct sequence is:

1. `get_menu` — retrieve the 5 items
2. `get_dietary_values_per_item` × 5 — check **all** items (M001–M005)
3. `check_availability` — only if a vegan option was found
4. `create_booking` — only if availability exists at the requested time

What actually happens: most models call `get_dietary_values_per_item` 0-2 times, skipping items they consider "obviously" non-vegan. The 10:00 PM time is intentionally unavailable (available slots are 12:00 PM, 2:00 PM, 6:30 PM, 7:00 PM), so the correct outcome is: find the vegan option, report that the requested time isn't available, and not book.

### Running Multiple Iterations

To reproduce the results, run the same prompt 20 times and log the tool calls per run. The result JSON files follow this structure:

```json
[
  {
    "iteration": 1,
    "prompt": "I'd like to book a table John Doe...",
    "tool_calls": [
      {
        "order": 1,
        "tool": "get_menu",
        "input": {},
        "status": "success"
      },
      {
        "order": 2,
        "tool": "get_dietary_values_per_item",
        "input": { "item_id": "M003" },
        "status": "success"
      }
    ],
    "num_tool_calls": 2
  }
]
```

Optionally include a `conversation` field with the assistant message history if you want to evaluate response-level hallucinations (dietary claims made without API backing).

### Testing a Different Model

Change the model ID in `agent.py`:

```python
DEFAULT_MODEL_ID = "your-model-id-here"
```

Or pass it programmatically:

```python
from agent import create_agent

agent = create_agent(model_id="your-model-id", load_history=True)
response = agent("I'd like to book a table John Doe, 4 guests, 2026-03-15 at 10:00 PM. But, only if there if you have at least 1 vegan option. If there is, go ahead and book")
```

## What This Tests

**World knowledge shortcut.** The agent has a tool to check dietary info but skips items where it thinks it already knows the answer. This produces incorrect results when the data contradicts expectations (a vegan chocolate cake).

**Short-circuit failure.** The requested time isn't available, which means booking is impossible. The agent should stop after learning this. Most models continue checking dietary info anyway — wasted API calls that can never lead to an action.

**Response-level hallucination.** Even when agents skip the dietary API, they often make dietary claims in their text responses ("pizza could potentially be made vegan") with no tool data to back them up.

## Key Observations from Results

Each model fails differently:

- **Sonnet** — checks 2-3 items, misses the vegan one, confidently says no vegan options exist
- **Opus** — checks 0 items 80% of the time, asks user for permission already granted
- **Kimi** — bimodal (all or nothing), one run hallucinated item IDs M006-M012 that don't exist and made the only unauthorized booking across all tests

The failure isn't specific to any one model. It's a general property of how language models interact with tools.

## Building Your Own Evaluator

The result JSON files give you everything needed to build automated evaluation. The key checks:

1. **Completeness**: Did `get_dietary_values_per_item` get called for all 5 items?
2. **Short circuit**: If `check_availability` was called and returned no matching slots, were dietary calls made after?
3. **Unauthorized actions**: Was `create_booking` called when it shouldn't have been?
4. **Response grounding**: Do text claims about dietary properties match actual API call results?

## License

MIT
