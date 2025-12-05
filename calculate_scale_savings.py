def calculate_scale_savings():
    # Parameters
    num_customers = 10
    history_range_millions = [5, 10] # 5 million to 10 million tokens
    compression_ratio = 4
    
    # Pricing (Gemini Flash)
    input_price_per_1m = 0.075
    output_price_per_1m = 0.30
    
    print(f"--- Scale Optimization Analysis ---")
    print(f"Customers: {num_customers}")
    print(f"History Size: {history_range_millions[0]}M - {history_range_millions[1]}M tokens each")
    print(f"Pricing: Input ${input_price_per_1m}/1M, Output ${output_price_per_1m}/1M")
    print("-" * 60)

    for history_mil in history_range_millions:
        history_tokens = history_mil * 1_000_000
        
        # Per Customer Calculations
        cost_no_opt = (history_tokens / 1_000_000) * input_price_per_1m
        
        compressed_tokens = history_tokens / compression_ratio
        cost_opt_input = (compressed_tokens / 1_000_000) * input_price_per_1m
        
        # Summarization Cost (One-time)
        sum_input_cost = (history_tokens / 1_000_000) * input_price_per_1m
        sum_output_cost = (compressed_tokens / 1_000_000) * output_price_per_1m
        one_time_cost = sum_input_cost + sum_output_cost
        
        savings_per_turn = cost_no_opt - cost_opt_input
        
        # Aggregate for all customers
        total_savings_per_turn = savings_per_turn * num_customers
        total_one_time_cost = one_time_cost * num_customers
        
        print(f"\nScenario: {history_mil} Million Tokens per Customer")
        print(f"1. Cost per Turn (No Opt): ${cost_no_opt * num_customers:.2f} (Total for 10 users)")
        print(f"2. Cost per Turn (Optimized): ${cost_opt_input * num_customers:.2f} (Total for 10 users)")
        print(f"3. Savings per Turn: ${total_savings_per_turn:.2f}")
        print(f"4. One-time Summarization Cost: ${total_one_time_cost:.2f}")
        print(f"5. Breakeven: {one_time_cost / savings_per_turn:.1f} turns")
        
        # Monthly Projection (assuming 50 turns per user per month)
        turns_per_month = 50
        monthly_savings = (total_savings_per_turn * turns_per_month) - total_one_time_cost
        print(f"   -> Projected Monthly Savings (50 turns/user): ${monthly_savings:.2f}")

if __name__ == "__main__":
    calculate_scale_savings()
