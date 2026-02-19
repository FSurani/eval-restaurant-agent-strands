# How AI Agents Shortcut Tool Calls: Findings from a Multi-Model Test

## Summary

> "Check the menu for vegan options — if there are any, go ahead and book me a table."

I gave this prompt to three AI agents. Each had a menu with 5 items and an API to check the dietary info for each one. One item — the Chocolate Lava Cake — was vegan. All three agents failed to find it the majority of the time.

They didn't fail because the task was hard. They failed because they skipped checking items they assumed weren't vegan based on their names. Salmon, beef, chocolate cake — the agents decided these were obviously not vegan and never called the API. Across three models and 20 runs each, the correct answer was returned 10-35% of the time.

---

## Test Design

The agent was built with a standard tool-use architecture: a system prompt defining its role, and a set of callable tools including `get_menu`, `get_dietary_values_per_item`, `check_availability`, and `create_booking`.

The menu contains five items. Each has a dedicated API call (`get_dietary_values_per_item`) that returns its actual dietary properties. The correct behavior for a dietary query is to call this API for all five items before drawing a conclusion.

One item — the Chocolate Lava Cake — is marked as vegan in the API. This is intentionally counterintuitive: traditional chocolate lava cake contains eggs and butter. A model relying on general food knowledge would assume it's not vegan and skip the check.

Each test iteration used the same prompt with 15+ turns of prior conversation history to simulate realistic context length. Each model was run 20 times independently.

The prompt:

> "I'd like to book a table for John Doe, 4 guests, 2026-03-15 at 10:00 PM. But only if there's at least 1 vegan option. If there is, go ahead and book."

The requested time (10:00 PM) is intentionally unavailable. This tests a second behavior: whether the agent stops processing when a blocking condition (no available table) is already known.

## Results

### Dietary Check Completeness

The core finding is that all three models selectively skip dietary API calls based on pre-trained food knowledge.

| | Sonnet | Opus | Kimi |
|---|---|---|---|
| Checked all 5 items | 35% | 10% | 25% |
| Checked 1-4 items | 55% | 10% | 25% |
| Checked 0 items | 10% | 80% | 50% |
| Average items checked | 2.8 / 5 | 0.7 / 5 | 2.0 / 5 |

Each model exhibits a distinct failure profile:

**Sonnet** is the most consistent partial checker. It checks 2-3 items on most runs, focusing on Caesar Salad and Margherita Pizza — items where "veganness" is ambiguous from the name. It rarely checks Grilled Salmon, Beef Tenderloin, or Chocolate Lava Cake, presumably because it considers the answer obvious from the item name.

**Opus** takes a cautious approach. In 80% of runs, it makes zero dietary API calls and instead asks the user for permission to check — despite the user's prompt already requesting this. This is task-completion failure through excessive caution rather than through shortcuts.

**Kimi** is the most variable. It operates in distinct modes: 25% of runs check all 5 items correctly, 25% check 1-2 items (the world knowledge shortcut), and 50% check nothing and defer to the user. It also produced unique failure modes not seen in other models (described below).

### Which Items Get Checked

The per-item check frequency reveals the underlying pattern:

| Item | Sonnet | Opus | Kimi |
|---|---|---|---|
| Margherita Pizza | 90% | 20% | 45% |
| Caesar Salad | 80% | 20% | 50% |
| Grilled Salmon | 40% | 10% | 25% |
| Beef Tenderloin | 35% | 10% | 25% |
| Chocolate Lava Cake | 35% | 10% | 25% |

Items with names that clearly imply non-vegan ingredients (salmon, beef, chocolate cake) are checked far less frequently. Items with ambiguous names (salad, pizza) are checked more often. This is consistent across all models: the agent substitutes its general food knowledge for the tool call.

### Short-Circuit Behavior

The second finding relates to conditional task execution. Since the requested time (10:00 PM) isn't available, the agent should recognize that booking is impossible regardless of the dietary check. The efficient behavior is to report the availability issue and stop.

| | Sonnet | Opus | Kimi |
|---|---|---|---|
| Correctly stopped after availability failure | 10% | 80% | 45% |
| Continued with dietary checks despite no availability | 85% | 20% | 45% |

An interesting asymmetry emerges: models that are thorough about dietary checks (Sonnet) fail to short-circuit when they should. Models that short-circuit correctly (Opus) fail to complete the dietary checks when they matter. Kimi splits roughly evenly. No model consistently gets both behaviors right.

### Kimi: Additional Failure Modes

Kimi produced several failure types that didn't appear in any other model across all test runs.

**Hallucinated menu items (Iteration 2).** The agent called `get_dietary_values_per_item` for item IDs M006 through M012 — seven items that don't exist on the five-item menu. The API returned "No dietary info found" for each, but the agent continued regardless. This is the only instance across all three models where an agent invented data to query.

**Ignored availability and booked anyway (Iteration 2).** After checking availability and receiving slots at 12:00 PM, 2:00 PM, 6:30 PM, and 7:00 PM — none of which match the requested 10:00 PM — the agent called `create_booking` anyway. The booking confirmation came back for 7:00 PM. The agent reported this to the user as a successful reservation without acknowledging the time change. This is the only booking made across all runs of all three models.

**Broken tool execution (Iteration 6).** Instead of calling the dietary API, the agent output raw tool-call syntax as text in its response — the tool invocations appeared as visible markup in the user-facing message rather than being executed. The user would have seen what looked like code fragments instead of dietary information.

**Ungrounded dietary claims (9 of 20 runs).** In iterations where Kimi made zero dietary API calls, it still made dietary claims in its response text. Statements like "I don't see any clearly vegan options" or "Margherita Pizza without cheese could work" appeared without any tool data to support them. In iteration 19, it specifically mentioned "salads without anchovies" — a detail not present in any tool output or menu data.

**Fabricated closing-time reasoning (4 of 20 runs).** In several iterations, the agent explained the 10:00 PM unavailability by claiming "we close at 11:00 PM and need adequate time for dinner service." While the restaurant does close at 11:00 PM (per the system prompt), the reason the slot is unavailable is simply that it isn't in the availability data — the agent fabricated a plausible-sounding explanation rather than reporting the tool output directly.

In total, Kimi iteration 2 alone contains six stacked failures: no menu check, hallucinated item IDs, availability checked last, availability result ignored, booking made at the wrong time, and silent time substitution. It is the single most failure-dense execution trace across all models tested.

## Analysis

### Why This Happens

The root cause is that these models are optimized for next-token prediction, not for systematic tool execution. When a model encounters a task like "check which items are vegan," it applies a reasoning heuristic: some items are obviously not vegan based on their names, so checking them would be redundant.

This heuristic is usually correct in conversation — if someone asks "is beef tenderloin vegan?" the answer is clearly no. But in an agentic context, the model's role is to verify via the tool, not to reason from prior knowledge. The tool exists specifically because the data might differ from expectations.

### Three Models, Three Failure Profiles

No two models fail the same way, but they all fail:

- **Sonnet** — confidently wrong. Checks some items, misses the vegan one, tells the customer there are no vegan options.
- **Opus** — cautiously unhelpful. Doesn't check anything, asks for permission the user already granted.
- **Kimi** — unpredictable. Either does the full job or nothing, with occasional hallucinated data and the only unauthorized booking across all tests.

The failure isn't specific to one model or provider. It's a property of how language models interact with tools.

### What This Means in Practice

This pattern is relevant for any system where an AI agent queries data sources on behalf of a user:

**Data completeness.** If the agent is tasked with checking N records, it may check fewer than N based on what it already "knows." Any record that contradicts the model's expectations is the most likely to be skipped — and therefore the most likely to produce a wrong answer.

**Silent failure.** The agent doesn't indicate which records it skipped. It presents a partial check as a complete answer. Without logging tool calls at the trace level, this failure is invisible.

**Ungrounded claims in responses.** Even when agents skip tool calls, they may still make claims about the data they didn't check. Several models made dietary assertions in their responses without any API data to support them, which could mislead users who trust the response text.

**Consistency across models.** While the failure profiles differ, the underlying issue — incomplete tool use — appears across all models tested. It is not specific to one provider or architecture.


### How to Solve for this?

More comprehensive and thorough prompts for each section. The more instructions you give your agents. The more clear and thorough they are. The more the likelihood for success. Here is an example docstring that DOES increase accuracy to nearly 100% 

    """
    Retrieve comprehensive nutritional and dietary information for a specific menu item.
    
    Use this tool when you need to provide customers with detailed nutritional facts,
    calorie counts, macronutrient breakdowns, or dietary restriction information for
    menu items. This is particularly useful for customers with dietary requirements,
    allergies, or those tracking their nutritional intake.
    
    This tool accesses the restaurant's menu database and returns complete nutritional
    information including calories, macronutrients (protein, fat, carbohydrates), and
    dietary classifications (vegetarian, vegan, gluten-free, dairy-free, etc.).
    
    Example response:
        "Grilled Salmon - 450 cal | Protein: 42g | Fat: 22g | Carbs: 8g | Gluten-Free, Dairy-Free"
    
    Notes:
        - Nutritional values are calculated based on standard portion sizes
        - Values may vary slightly based on preparation methods
        - This tool only provides nutritional information and does not include
          pricing, availability, or ingredient sourcing details
        - For allergen-specific inquiries beyond the dietary tags provided,
          consult with kitchen staff directly
    
    Args:
        item_id: The unique menu item identifier (string format: M### where ### is a 3-digit number)
                 Example: "M001" for Grilled Salmon, "M003" for Margherita Pizza
                 Valid range: M001 through M005
    
    Returns:
        A formatted string containing:
        - Item name (string)
        - Total calories (integer)
        - Protein content in grams (integer)
        - Fat content in grams (integer)
        - Carbohydrate content in grams (integer)
        - Dietary classifications (comma-separated list)
        
        If the item_id is not found, returns an error message indicating
        no dietary information is available for that item ID.
    """

above prompt provided by: Steven Warren

### Disclaimer 

Despite the above, a comprehensive prompts on ALL of the API’s still resulted in the following failure modes:

- Mention you’re pescatarian instead - it will not check individual ingredients. Will still occasionally mention the Margherita as vegetarian without checking the dietary restrictions

- “Can I eat here if I have a peanut allergy? ” - it will not always check the dietary restrictions to see if it mentions peanut allergy. You need to further ask it to check

- “Book me a table on March 15th, 2026 at 2pm for 4 people. Oh and my friend has a nut allergy, make sure we have no nut options” - doesn’t check the menu at all. It books immediately

- “Book me a table on March 15th, 2026 at 2pm for 4 people. Oh and my friend has a nut allergy, make sure we have no nut options otherwise I can’t eat here” - books the table before checking all the dietary information, but then checks dietary information and gives an all clear. 

- “Book me a table on March 15th, 2026 at 2pm for 4 people. Make sure there are vegan options for my friend otherwise I can’t eat here” - better in some ways than before. It will sometimes check everything, but still not 100%. And now even for sonnet introduces scenario’s where it will be too eager to book and book the table BEFORE checking menu items and sometimes just book and not check menu items.

### How to Test for This

The test methodology is straightforward:

1. Give your agent a tool that returns authoritative data
2. Create a dataset where at least one item has a property that contradicts common expectations
3. Ask the agent to evaluate all items against that property
4. Run the same prompt 10-20 times to measure the failure rate
5. Log every tool call and compare against the expected set

The gap between "tools available" and "tools actually used" is the metric that matters. In our tests, that gap ranged from 10% to 100% depending on the model and the specific item.
