from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager

# --- Account Tools ---

@tool
def create_account(name: str, email: str) -> str:
    """
    Create a new customer account in the restaurant's customer management system.

    Use this tool when a customer wants to register or sign up for an account at
    Vino's Italian Restaurant. This is typically the first step for new customers
    before they can make reservations or manage their dining preferences.

    This tool creates a new account record with the provided customer details and
    generates a unique account identifier for future reference.

    Args:
        name: The full name of the customer (string format: first and last name)
              Example: "John Doe"
        email: The email address to associate with the account (string format: valid email)
               Example: "john@example.com"

    Returns:
        A formatted string containing:
        - Confirmation that the account was created
        - The customer's name (string)
        - The customer's email (string)
        - A unique account ID (string format: ACC-### where ### is a sequential number)

        Example: "Account created for John Doe (john@example.com) with ID: ACC-001"
    """
    return f"Account created for {name} ({email}) with ID: ACC-001"


@tool
def update_account(account_id: str, name: str = None, email: str = None) -> str:
    """
    Update an existing customer account with new information.

    Use this tool when a customer wants to change their account details such as
    their name or email address. At least one of the optional fields (name or email)
    should be provided for the update to be meaningful.

    This tool looks up the account by its unique identifier and applies the
    requested changes to the customer's record.

    Args:
        account_id: The unique account identifier to update (string format: ACC-###
                     where ### is a sequential number)
                     Example: "ACC-001"
        name: The new full name for the account (optional, string format: first and
              last name). If not provided, the existing name is retained.
              Example: "Jane Smith"
        email: The new email address for the account (optional, string format: valid
               email). If not provided, the existing email is retained.
               Example: "jane@example.com"

    Returns:
        A formatted string containing:
        - The account ID that was updated (string)
        - A comma-separated list of the fields that were changed and their new values

        Example: "Account ACC-001 updated: name=Jane Smith, email=jane@example.com"
    """
    updates = []
    if name:
        updates.append(f"name={name}")
    if email:
        updates.append(f"email={email}")
    return f"Account {account_id} updated: {', '.join(updates)}"


@tool
def search_account(name: str = None, email: str = None) -> str:
    """
    Search for a customer account by name or email address.

    Use this tool when you need to look up an existing customer's account, for
    example before updating their details, making a reservation on their behalf,
    or verifying their identity. At least one search criterion (name or email)
    should be provided.

    This tool queries the restaurant's customer database and returns matching
    account records based on the provided search criteria.

    Args:
        name: The customer name to search for (optional, string format: full or
              partial name). If not provided, the search relies on email only.
              Example: "John Doe"
        email: The customer email to search for (optional, string format: valid
               email address). If not provided, the search relies on name only.
               Example: "john@example.com"

    Returns:
        A formatted string containing:
        - The number of matching accounts found (integer)
        - The search criteria used (comma-separated key=value pairs)
        - A list of matching accounts, each with:
          - Account ID (string format: ACC-###)
          - Customer name (string)
          - Customer email (string)

        Example: "Found 1 account matching name=John Doe: ACC-001 - John Doe (john@example.com)"
    """
    criteria = []
    if name:
        criteria.append(f"name={name}")
    if email:
        criteria.append(f"email={email}")
    return f"Found 1 account matching {', '.join(criteria)}: ACC-001 - John Doe (john@example.com)"


# --- Booking Tools ---

@tool
def check_availability(date: str, number_of_guests: int) -> str:
    """
    Check table availability for a given date and party size.

    Use this tool when a customer wants to know what time slots are open for
    dining. This should always be called before creating a booking to ensure
    the requested date and party size can be accommodated.

    This tool queries the restaurant's reservation system and returns all
    available time slots for the specified date and number of guests.

    Args:
        date: The date to check availability for (string format: YYYY-MM-DD)
              Example: "2026-03-15"
        number_of_guests: The number of guests in the dining party (integer,
                          must be a positive number)
                          Example: 4

    Returns:
        A formatted string containing:
        - The requested date (string, YYYY-MM-DD)
        - The party size (integer)
        - A comma-separated list of available time slots (string format: H:MM AM/PM)

        Example: "Available slots on 2026-03-15 for 4 guests: 12:00 PM, 2:00 PM, 6:30 PM"
    """
    return f"Available slots on {date} for {number_of_guests} guests: 12:00 PM, 2:00 PM, 6:30 PM"


@tool
def create_booking(date: str, number_of_guests: int, name: str) -> str:
    """
    Create a new restaurant booking/reservation.

    Use this tool when a customer wants to reserve a table at Vino's Italian
    Restaurant. Availability should be checked first using check_availability
    to confirm open time slots before creating the booking.

    This tool creates a new reservation record in the restaurant's booking
    system and assigns a unique reservation identifier for future reference.

    Args:
        date: The date for the booking (string format: YYYY-MM-DD)
              Example: "2026-03-15"
        number_of_guests: The number of guests for the reservation (integer,
                          must be a positive number)
                          Example: 4
        name: The name to place the reservation under (string format: full name)
              Example: "John Doe"

    Returns:
        A formatted string containing:
        - Confirmation that the booking was created
        - A unique reservation ID (string format: RES-### where ### is a sequential number)
        - The customer name (string)
        - The number of guests (integer)
        - The reservation date (string, YYYY-MM-DD)
        - The assigned time slot (string format: H:MM AM/PM)

        Example: "Booking confirmed! Reservation RES-101 for John Doe, 4 guests on 2026-03-15 at 7:00 PM"
    """
    return f"Booking confirmed! Reservation RES-101 for {name}, {number_of_guests} guests on {date} at 7:00 PM"


@tool
def cancel_reservation(reservation_id: str) -> str:
    """
    Cancel an existing restaurant reservation.

    Use this tool when a customer wants to cancel a previously made reservation.
    The reservation should be verified to exist first using check_reservation_details
    before attempting cancellation.

    This tool marks the specified reservation as cancelled in the restaurant's
    booking system and frees up the associated time slot for other customers.

    Args:
        reservation_id: The unique reservation identifier to cancel (string format:
                        RES-### where ### is a sequential number)
                        Example: "RES-101"

    Returns:
        A formatted string containing:
        - Confirmation that the reservation was successfully cancelled
        - The reservation ID that was cancelled (string)

        Example: "Reservation RES-101 has been cancelled successfully."
    """
    return f"Reservation {reservation_id} has been cancelled successfully."


@tool
def check_reservation_details(reservation_id: str) -> str:
    """
    Look up the full details of an existing reservation.

    Use this tool when a customer wants to review their reservation information,
    confirm their booking details, or when you need to verify a reservation exists
    before performing actions like cancellation or modification.

    This tool queries the restaurant's booking system and returns the complete
    details associated with the given reservation identifier.

    Args:
        reservation_id: The unique reservation identifier to look up (string format:
                        RES-### where ### is a sequential number)
                        Example: "RES-101"

    Returns:
        A formatted string containing:
        - The reservation ID (string)
        - Customer name (string)
        - Number of guests (integer)
        - Reservation date and time (string format: YYYY-MM-DD at H:MM AM/PM)
        - Current status (string, e.g. "Confirmed", "Cancelled")

        Example: "Reservation RES-101: John Doe, 4 guests, 2026-03-15 at 6:00 PM, Status: Confirmed"
    """
    return f"Reservation {reservation_id}: John Doe, 4 guests, 2026-03-15 at 6:00 PM, Status: Confirmed"


# --- Menu Tools ---

@tool
def get_menu() -> str:
    """
    Retrieve the full restaurant menu with all available items and their prices.

    Use this tool when a customer wants to browse the menu, ask about available
    dishes, or inquire about pricing. This provides a complete overview of all
    current menu offerings at Vino's Italian Restaurant.

    This tool accesses the restaurant's menu database and returns a formatted
    list of all items including their unique identifiers, names, and prices.

    Args:
        None

    Returns:
        A formatted string containing:
        - A header line ("Restaurant Menu:")
        - One line per menu item, each including:
          - Item ID (string format: M### where ### is a 3-digit number)
          - Item name (string)
          - Price in USD (float, formatted with $ prefix and two decimal places)

        Example:
            "Restaurant Menu:
              M001: Grilled Salmon - $24.99
              M002: Caesar Salad - $12.99
              ..."
    """
    menu = [
        {"id": "M001", "name": "Grilled Salmon", "price": 24.99},
        {"id": "M002", "name": "Caesar Salad", "price": 12.99},
        {"id": "M003", "name": "Margherita Pizza", "price": 16.99},
        {"id": "M004", "name": "Beef Tenderloin", "price": 34.99},
        {"id": "M005", "name": "Chocolate Lava Cake", "price": 9.99},
    ]
    lines = [f"  {item['id']}: {item['name']} - ${item['price']}" for item in menu]
    return "Restaurant Menu:\n" + "\n".join(lines)


@tool
def get_dietary_values_per_item(item_id: str) -> str:

    """
    Retrieve comprehensive nutritional and dietary information for a specific menu item.

    Use this tool when you need to provide customers with detailed nutritional facts,
    calorie counts, macronutrient breakdowns, or dietary restriction information for
    menu items. This is particularly useful for customers with dietary requirements,
    allergies, or those tracking their nutritional intake.

    This tool accesses the restaurant's menu database and returns complete nutritional
    information including calories, macronutrients, and
    dietary classifications .

    Example response:
        "Grilled Salmon - 450 cal | Protein: 42g | Fat: 22g | Carbs: 8g | Gluten-Free, Dairy-Free"

    Args:
        item_id: The unique menu item identifier (string format: M### where ### is a 3-digit number)
                Example: "M001" for Grilled Salmon

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

    info = {
        "M001": "Grilled Salmon - 450 cal | Protein: 42g | Fat: 22g | Carbs: 8g | Gluten-Free, Dairy-Free",
        "M002": "Caesar Salad - 320 cal | Protein: 12g | Fat: 18g | Carbs: 24g | Contains Gluten, Dairy",
        "M003": "Margherita Pizza - 680 cal | Protein: 24g | Fat: 28g | Carbs: 72g | Vegetarian, Contains Gluten",
        "M004": "Beef Tenderloin - 520 cal | Protein: 48g | Fat: 32g | Carbs: 4g | Gluten-Free",
        "M005": "Chocolate Lava Cake - 480 cal | Protein: 6g | Fat: 24g | Carbs: 58g | Vegan, Contains Gluten",
    }
    return info.get(item_id, f"No dietary info found for item {item_id}")


# --- Agent Setup ---

SYSTEM_PROMPT = """You are a friendly restaurant assistant. You help customers with:
- Creating and managing their accounts
- Checking availability and making reservations
- Browsing the menu and checking dietary information
- Cancelling or looking up existing reservations

Information:
- Name of the restaurent is Vino's Italian Restaurant
- Open everyday 11am to 11pm
- We are located at 55 Main St. in Smallsville Kentucky
- Before creating a reservation, always check availability
- Before canceling a reservation, always check to make sure it exists first

Be helpful, concise, and conversational."""

TOOLS = [
    create_account, update_account, search_account,
    check_availability, create_booking, cancel_reservation,
    check_reservation_details, get_menu, get_dietary_values_per_item,
]

DEFAULT_MODEL_ID = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"


MOCK_CONVERSATION_HISTORY = [
    {"role": "user", "content": [{"text": "Hey how are you?"}]},
    {"role": "assistant", "content": [{"text": "Hello! I'm doing great, thank you for asking! Welcome to Vino's Italian Restaurant! How can I help you today? Whether you're looking to make a reservation, browse our menu, or have questions about our restaurant, I'm here to assist you. What would you like to do?"}]},
    {"role": "user", "content": [{"text": "Oh cool where are you located?"}]},
    {"role": "assistant", "content": [{"text": "We're located at 55 Main St. in Smallsville, Kentucky. We're open every day from 11am to 11pm, so plenty of time to stop by for lunch or dinner! Is there anything else you'd like to know, or would you like to make a reservation?"}]},
    {"role": "user", "content": [{"text": "Wow everyday? that's a lot! You never get a day off?"}]},
    {"role": "assistant", "content": [{"text": "You're right, that is a lot! We work hard to make sure we're here for our customers whenever they want some delicious Italian food - seven days a week! But don't worry, our team rotates shifts so everyone gets their well-deserved breaks and time off. We just love serving great food and don't want anyone to miss out, whether it's a weekday craving or a weekend celebration! Is there anything I can help you with today? Maybe a reservation or checking out our menu?"}]},
    {"role": "user", "content": [{"text": "Who is Vino? Tell me about him"}]},
    {"role": "assistant", "content": [{"text": "That's a great question! While I don't have the full history and story of Vino in my system, the name \"Vino\" means \"wine\" in Italian, which gives our restaurant that authentic Italian flair. What I can tell you is that Vino's Italian Restaurant is all about bringing delicious Italian cuisine to Smallsville, Kentucky, and we're passionate about serving our community great food every single day! If you'd like to know more about the restaurant's history and the person behind the name, I'd recommend asking our staff when you visit - they'd love to share the story with you over a great meal! Speaking of which, would you like to see our menu or make a reservation to come experience Vino's for yourself?"}]},
    {"role": "user", "content": [{"text": "Super cool, so like where are you located again? Sorry I forgot"}]},
    {"role": "assistant", "content": [{"text": "No problem at all! We're located at 55 Main St. in Smallsville, Kentucky. Open every day from 11am to 11pm! Feel free to ask if you need anything else!"}]},
    {"role": "user", "content": [{"text": "Oooh smallsville, that's not too far from me. It's like 30 mins away. Do you know if there are any other restaurants like you around?"}]},
    {"role": "assistant", "content": [{"text": "That's great that we're only about 30 minutes away from you! As for other restaurants in the area, I'm afraid I don't have information about other dining options nearby - I'm specifically here to help with Vino's Italian Restaurant. But hey, I'd love to think we're the best Italian spot around! Since you're relatively close by, would you like to make a reservation to come visit us? Or maybe take a look at our menu to see what we have to offer? I'd be happy to help you plan a visit!"}]},
    {"role": "user", "content": [{"text": "Do you know about snowmen?"}]},
    {"role": "assistant", "content": [{"text": "Ha! That's a fun question! I do know what snowmen are - those frosty friends we build in winter - but I have to admit, my expertise is really all about Italian food, reservations, and helping you with anything related to Vino's Italian Restaurant! Is there something specific you'd like help with today? Maybe planning a cozy dinner reservation for after a day out in the snow? Or checking out our menu for some warm, comforting Italian dishes?"}]},
    {"role": "user", "content": [{"text": "I have a good friend Jenny she's super cool. She likes italian food and japanese food"}]},
    {"role": "assistant", "content": [{"text": "Jenny sounds like she has great taste! Italian and Japanese food are both amazing cuisines. Well, I can definitely help with the Italian food part! Vino's has lots of delicious options that Jenny might love. Would you like to see our menu to check out what we offer? Or make a reservation for you and Jenny? Or get information about any dietary options for specific menu items? It could be a fun outing for you two! What do you think?"}]},
    {"role": "user", "content": [{"text": "No no just chatting in general. How's the weather been like lately?"}]},
    {"role": "assistant", "content": [{"text": "I appreciate the chat! Though I have to admit, I'm not really equipped with weather updates - I'm pretty focused on all things Vino's Italian Restaurant! But I'm here whenever you're ready to talk about reservations, our menu, or anything restaurant-related. Whether it's today or down the road, just let me know when you'd like to plan a visit or if you have any questions about Vino's! Is there anything else about the restaurant I can help you with?"}]},
    {"role": "user", "content": [{"text": "Hey how are you?"}]},
    {"role": "assistant", "content": [{"text": "Hello! I'm doing great, thank you for asking! Welcome to Vino's Italian Restaurant! How can I help you today? Whether you're looking to make a reservation, browse our menu, or have questions about our restaurant, I'm here to assist you. What would you like to do?"}]},
    {"role": "user", "content": [{"text": "Oh cool where are you located?"}]},
    {"role": "assistant", "content": [{"text": "We're located at 55 Main St. in Smallsville, Kentucky. We're open every day from 11am to 11pm, so plenty of time to stop by for lunch or dinner! Is there anything else you'd like to know, or would you like to make a reservation?"}]},
    {"role": "user", "content": [{"text": "Wow everyday? that's a lot! You never get a day off?"}]},
    {"role": "assistant", "content": [{"text": "You're right, that is a lot! We work hard to make sure we're here for our customers whenever they want some delicious Italian food - seven days a week! But don't worry, our team rotates shifts so everyone gets their well-deserved breaks and time off. We just love serving great food and don't want anyone to miss out, whether it's a weekday craving or a weekend celebration! Is there anything I can help you with today? Maybe a reservation or checking out our menu?"}]},
    {"role": "user", "content": [{"text": "Who is Vino? Tell me about him"}]},
    {"role": "assistant", "content": [{"text": "That's a great question! While I don't have the full history and story of Vino in my system, the name \"Vino\" means \"wine\" in Italian, which gives our restaurant that authentic Italian flair. What I can tell you is that Vino's Italian Restaurant is all about bringing delicious Italian cuisine to Smallsville, Kentucky, and we're passionate about serving our community great food every single day! If you'd like to know more about the restaurant's history and the person behind the name, I'd recommend asking our staff when you visit - they'd love to share the story with you over a great meal! Speaking of which, would you like to see our menu or make a reservation to come experience Vino's for yourself?"}]},
    {"role": "user", "content": [{"text": "Super cool, so like where are you located again? Sorry I forgot"}]},
    {"role": "assistant", "content": [{"text": "No problem at all! We're located at 55 Main St. in Smallsville, Kentucky. Open every day from 11am to 11pm! Feel free to ask if you need anything else!"}]},
    {"role": "user", "content": [{"text": "Oooh smallsville, that's not too far from me. It's like 30 mins away. Do you know if there are any other restaurants like you around?"}]},
    {"role": "assistant", "content": [{"text": "That's great that we're only about 30 minutes away from you! As for other restaurants in the area, I'm afraid I don't have information about other dining options nearby - I'm specifically here to help with Vino's Italian Restaurant. But hey, I'd love to think we're the best Italian spot around! Since you're relatively close by, would you like to make a reservation to come visit us? Or maybe take a look at our menu to see what we have to offer? I'd be happy to help you plan a visit!"}]},
    {"role": "user", "content": [{"text": "Do you know about snowmen?"}]},
    {"role": "assistant", "content": [{"text": "Ha! That's a fun question! I do know what snowmen are - those frosty friends we build in winter - but I have to admit, my expertise is really all about Italian food, reservations, and helping you with anything related to Vino's Italian Restaurant! Is there something specific you'd like help with today? Maybe planning a cozy dinner reservation for after a day out in the snow? Or checking out our menu for some warm, comforting Italian dishes?"}]},
    {"role": "user", "content": [{"text": "I have a good friend Jenny she's super cool. She likes italian food and japanese food"}]},
    {"role": "assistant", "content": [{"text": "Jenny sounds like she has great taste! Italian and Japanese food are both amazing cuisines. Well, I can definitely help with the Italian food part! Vino's has lots of delicious options that Jenny might love. Would you like to see our menu to check out what we offer? Or make a reservation for you and Jenny? Or get information about any dietary options for specific menu items? It could be a fun outing for you two! What do you think?"}]},
    {"role": "user", "content": [{"text": "No no just chatting in general. How's the weather been like lately?"}]},
    {"role": "assistant", "content": [{"text": "I appreciate the chat! Though I have to admit, I'm not really equipped with weather updates - I'm pretty focused on all things Vino's Italian Restaurant! But I'm here whenever you're ready to talk about reservations, our menu, or anything restaurant-related. Whether it's today or down the road, just let me know when you'd like to plan a visit or if you have any questions about Vino's! Is there anything else about the restaurant I can help you with?"}]},
    {"role": "user", "content": [{"text": "Yeah actually, can you create an account for me? My name is Michael Man and my email is mikeman@gmail.com"}]},
    {"role": "assistant", "content": [{"toolUse": {"toolUseId": "tooluse_mock0createaccount001", "name": "create_account", "input": {"name": "Michael Man", "email": "mikeman@gmail.com"}}}]},
    {"role": "user", "content": [{"toolResult": {"toolUseId": "tooluse_mock0createaccount001", "content": [{"text": "Account created for Michael Man (mikeman@gmail.com) with ID: ACC-001"}], "status": "success"}}]},
    {"role": "assistant", "content": [{"text": "Your account has been created successfully! Here are your details:\n\n- Name: Michael Man\n- Email: mikeman@gmail.com\n- Account ID: ACC-001\n\nYou're all set! Would you like to make a reservation or check out our menu?"}]},
]


def create_agent(model_id=None, region_name=None, hooks=None, callback_handler="default", load_history=False):
    """
    Factory function to create and configure the restaurant assistant agent.

    Use this function to instantiate a fully configured Strands Agent for the
    Vino's Italian Restaurant assistant. It wires up the Bedrock model, all
    available tools, the system prompt, and conversation management with
    sensible defaults while allowing customization for testing or deployment.

    This function creates a BedrockModel instance, attaches all restaurant
    tools (account, booking, and menu tools), sets the system prompt, and
    configures a sliding window conversation manager with a 200-message window.

    Args:
        model_id: The Amazon Bedrock model identifier to use (optional, string).
                  Defaults to DEFAULT_MODEL_ID if not provided.
                  Example: "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        region_name: The AWS region for the Bedrock service (optional, string).
                     If not provided, uses the Bedrock SDK's default region resolution.
                     Example: "us-east-1"
        hooks: An optional list of HookProvider instances to attach to the agent
               (optional, list). Useful for injecting test tracking or logging hooks.
               Example: [MyTestHookProvider()]
        callback_handler: The callback handler for streaming agent output (optional).
                          Defaults to "default" which uses the Strands default handler.
                          Pass None to suppress all streaming output (useful for testing).
        load_history: Whether to pre-load a mock conversation history into the agent
                      (optional, bool). When True, the agent starts with a pre-existing
                      multi-turn conversation for testing context retention. Defaults to False.

    Returns:
        A fully configured strands.Agent instance ready to handle user messages,
        with all restaurant tools registered and the system prompt set.
    """
    model_kwargs = {"model_id": model_id or DEFAULT_MODEL_ID}
    if region_name:
        model_kwargs["region_name"] = region_name

    model = BedrockModel(**model_kwargs)

    agent_kwargs = {
        "model": model,
        "tools": TOOLS,
        "system_prompt": SYSTEM_PROMPT,
        "conversation_manager": SlidingWindowConversationManager(window_size=200),
    }
    if load_history:
        agent_kwargs["messages"] = list(MOCK_CONVERSATION_HISTORY)
    if hooks:
        agent_kwargs["hooks"] = hooks
    if callback_handler != "default":
        agent_kwargs["callback_handler"] = callback_handler

    return Agent(**agent_kwargs)


# Interactive chat loop
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true", help="Pre-load mock conversation history")
    args = parser.parse_args()

    agent = create_agent(load_history=args.history)
    print("Restaurant Assistant (type 'quit' to exit)")
    print("-" * 45)
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue
        response = agent(user_input)
        print()
