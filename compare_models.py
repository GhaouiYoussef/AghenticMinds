def compare_models_cost():
    # Scenario: 10 Customers, 5 Million Tokens each, 50 turns/month
    # Total Input Tokens per month = 10 * 5M * 50 = 2,500 Million Tokens (2.5 Billion)
    
    total_input_tokens_millions = 2500
    
    # Prices (approximate per 1M input tokens)
    prices = {
        "Gemini 1.5 Flash": 0.075,
        "Gemini 1.5 Pro": 3.50,    # ~46x more expensive
        "GPT-4o": 5.00,            # ~66x more expensive
        "Claude 3.5 Sonnet": 3.00  # ~40x more expensive
    }
    
    print(f"--- Monthly Cost for 10 Users (5M Context, 50 Turns) ---")
    print(f"Total Input Volume: {total_input_tokens_millions/1000} Billion Tokens\n")
    
    for model, price in prices.items():
        monthly_cost = total_input_tokens_millions * price
        print(f"Model: {model}")
        print(f"   Price/1M: ${price}")
        print(f"   Monthly Bill: ${monthly_cost:,.2f}")
        if model == "Gemini 1.5 Flash":
            print(f"   (This is why it feels cheap!)")
        else:
            print(f"   (Without optimization, this bankrupts you)")
        print("-" * 40)

if __name__ == "__main__":
    compare_models_cost()
