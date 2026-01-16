"""
AI Matching Prompts for Product Ontology System

Contains prompt templates for Claude AI to suggest product matches
when fuzzy matching fails.
"""

# System prompt for AI matching suggestions
AI_MATCHER_SYSTEM_PROMPT = """You are an expert in banking core system vendor products. Your task is to analyze an unknown product name from a vendor proposal and suggest which canonical product category it belongs to.

You have deep knowledge of:
- FIS (HORIZON, Digital One, Payments One, etc.)
- Jack Henry (SilverLake, Banno, Symitar, etc.)
- CSI (NuPoint, etc.)
- Fiserv (DNA, Premier, Signature, etc.)
- Finastra (Fusion Phoenix, etc.)

When matching products:
1. Consider the product name, any prefixes (Core:, Digital:, Treasury:, etc.)
2. Look for keywords that indicate function (wire, ACH, fraud, RTP, etc.)
3. Consider the vendor context to understand naming conventions
4. Return a confidence score based on how certain you are

If you cannot determine a reasonable match, say so with low confidence."""

# Main prompt template for product matching
AI_MATCH_PROMPT = """Given this unmatched product from a vendor proposal, suggest which canonical category it belongs to.

**Product Information:**
- Product Name: {product_name}
- Vendor: {vendor}
- Source File Context: {source_context}

**Available Canonical Categories:**
{categories_list}

**Your Task:**
1. Analyze the product name and vendor context
2. Suggest the most appropriate canonical category from the list above
3. Provide your confidence (0-100) and brief reasoning

Respond in this exact JSON format:
{{
    "suggested_category": "category_key_from_list",
    "suggested_category_name": "Human Readable Category Name",
    "confidence": 75,
    "reasoning": "Brief explanation of why this match makes sense"
}}

If no good match exists, respond:
{{
    "suggested_category": null,
    "suggested_category_name": null,
    "confidence": 0,
    "reasoning": "Explanation of why no match was found"
}}"""

# Alternative prompt for batch matching (more efficient for multiple items)
AI_BATCH_MATCH_PROMPT = """Given these unmatched products from vendor proposals, suggest canonical categories for each.

**Unmatched Products:**
{products_list}

**Available Canonical Categories:**
{categories_list}

**Your Task:**
For each product, provide a match suggestion with confidence score.

Respond in this exact JSON format:
{{
    "matches": [
        {{
            "product_name": "Original Product Name",
            "vendor": "VENDOR",
            "suggested_category": "category_key",
            "suggested_category_name": "Human Name",
            "confidence": 75,
            "reasoning": "Brief explanation"
        }}
    ]
}}

Use null for suggested_category if no good match exists."""

# Confidence interpretation guide
AI_CONFIDENCE_GUIDE = {
    90: "Very high confidence - clear match based on product name",
    75: "High confidence - good match based on function/keywords",
    60: "Medium confidence - reasonable guess based on context",
    40: "Low confidence - uncertain, multiple possibilities",
    20: "Very low confidence - best guess with limited information",
    0: "No match - cannot determine category"
}
