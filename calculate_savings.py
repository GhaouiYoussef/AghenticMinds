def calculate_gemini_savings():
    # Pricing for Gemini 1.5 Flash (assuming similar tier for "2.5" or using current Flash pricing as baseline)
    # Current Gemini 1.5 Flash Pricing (approximate, per 1M tokens):
    # Input: $0.075 per 1M tokens (for prompts <= 128k)
    # Input: $0.15 per 1M tokens (for prompts > 128k)
    # Output: $0.30 per 1M tokens
    
    # Let's assume a scenario:
    # A long conversation that reaches 100,000 tokens of history.
    # We want to see the cost of the NEXT turn with and without optimization.
    
    # Scenario Parameters
    history_tokens = 100_000
    new_input_tokens = 100  # User asks a new question
    output_tokens = 500     # Model generates a response
    
    # Optimization Parameters
    compression_ratio = 4   # 4x compression (10k -> 2.5k)
    # In our proposed model: 
    # We compress H_old. Let's say H_recent is negligible for this high-level calc (or say 1k tokens).
    # So we compress ~99k tokens down to ~25k tokens.
    
    # Cost WITHOUT Optimization (Standard RAG/Chat)
    # We send 100k + 100 tokens as input.
    input_cost_per_1m_high_context = 0.15 # > 128k tier usually triggers higher, but let's use standard for 100k
    # Actually 100k is < 128k, so let's use the lower tier $0.075
    input_cost_per_1m = 0.075
    output_cost_per_1m = 0.30
    
    cost_no_opt_input = ((history_tokens + new_input_tokens) / 1_000_000) * input_cost_per_1m
    cost_no_opt_output = (output_tokens / 1_000_000) * output_cost_per_1m
    total_cost_no_opt = cost_no_opt_input + cost_no_opt_output
    
    # Cost WITH Optimization
    # 1. One-time cost to summarize (Input: 100k, Output: 25k)
    # This happens once every 100k tokens roughly.
    cost_summarize_input = (history_tokens / 1_000_000) * input_cost_per_1m
    cost_summarize_output = ((history_tokens / compression_ratio) / 1_000_000) * output_cost_per_1m
    one_time_summarization_cost = cost_summarize_input + cost_summarize_output
    
    # 2. Cost of the NEXT turn (Input: 25k (summary) + 100 (new), Output: 500)
    compressed_history = history_tokens / compression_ratio
    cost_opt_input = ((compressed_history + new_input_tokens) / 1_000_000) * input_cost_per_1m
    cost_opt_output = (output_tokens / 1_000_000) * output_cost_per_1m
    total_cost_opt_turn = cost_opt_input + cost_opt_output
    
    print(f"--- Gemini Flash Cost Analysis (per turn at 100k context) ---")
    print(f"Assumed Pricing: Input ${input_cost_per_1m}/1M, Output ${output_cost_per_1m}/1M")
    print(f"\n1. Standard Approach (No Optimization):")
    print(f"   Input Tokens: {history_tokens + new_input_tokens:,}")
    print(f"   Cost per turn: ${total_cost_no_opt:.6f}")
    
    print(f"\n2. Optimized Approach (4x Compression):")
    print(f"   Compressed History: {compressed_history:,} tokens")
    print(f"   Input Tokens: {compressed_history + new_input_tokens:,}")
    print(f"   Cost per turn: ${total_cost_opt_turn:.6f}")
    
    savings_per_turn = total_cost_no_opt - total_cost_opt_turn
    print(f"\n--- Savings ---")
    print(f"   Savings per turn: ${savings_per_turn:.6f}")
    print(f"   % Savings on Input Cost: {((cost_no_opt_input - cost_opt_input)/cost_no_opt_input)*100:.2f}%")
    
    # Breakeven Analysis
    # How many turns does it take to recover the summarization cost?
    turns_to_breakeven = one_time_summarization_cost / savings_per_turn
    print(f"\n--- Breakeven ---")
    print(f"   One-time Summarization Cost: ${one_time_summarization_cost:.6f}")
    print(f"   Turns to recover cost: {turns_to_breakeven:.1f} turns")
    print(f"   (After {int(turns_to_breakeven)+1} turns, you are purely saving money)")

if __name__ == "__main__":
    calculate_gemini_savings()
