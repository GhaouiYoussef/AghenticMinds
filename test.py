import google.genai as genai
genai.configure(api_key="YOUR_API_KEY")

SYSTEM_PROMPT_CACHE_ID = None

def init_cache():
    global SYSTEM_PROMPT_CACHE_ID

    model = genai.GenerativeModel("gemini-3-pro-preview")

    cache = model.caches.create(
        display_name="global-system-prompt",
        contents=[
            {
                "role": "system",
                "parts": [
                    {"text": "You are a helpful assistant following strict safety rules."}
                ]
            }
        ],
        ttl_seconds=3600  # 1 hour
    )

    SYSTEM_PROMPT_CACHE_ID = cache["id"]

# Call once on server startup
init_cache()
