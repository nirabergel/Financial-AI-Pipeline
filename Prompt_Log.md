# Gemini AI Prompt Engineering Log

During the development of the pipeline, the prompt sent to Gemini 3 Flash required several iterations to ensure reliable, structured JSON outputs, especially when handling unstructured and noisy text.

## Iteration 1: The Basic Approach (Failed)
**Prompt Used:**
> Read the following document and give me a summary. Also, tell me what type of document it is, what the sentiment is, and extract any names, dates, or amounts. Return the result in JSON.

**Result/Issue:**
Gemini returned the data, but the JSON schema was inconsistent. Sometimes it nested the entities, sometimes it didn't. It also included Markdown formatting (`````json ````) which broke the n8n JSON parser in the next node.

---

## Iteration 2: Enforcing Structure (Partial Success)
**Prompt Used:**
> You are a document intelligence assistant. Analyze the document text and return a valid JSON object. 
> Use these fields: summary, classification, sentiment, entities (people, organizations, dates, amounts), action_items, and confidence_score.

**Result/Issue:**
Better. The structure was mostly consistent. However, the model invented its own categories for the `classification` field (e.g., calling an invoice a "billing statement"). This broke the downstream Python logic which expected specific keywords.

---

## Iteration 3: The Production Prompt (Final & Successful)
To fix the category hallucinations and support the new Vision capability (passing graphs/charts from PDFs), the prompt was locked down with strict enums and precise output instructions.

**Final Prompt Used:**
> You are a document intelligence assistant. Analyze the following document text and return ONLY a valid JSON object with these exact fields:
> 
> {
>   "summary": "2-3 sentence summary of the document",
>   "classification": "one of: [invoice, report, contract, ticket, article, other]",
>   "sentiment": "one of: [positive, neutral, negative]",
>   "entities": {
>     "people": ["list of person names"],
>     "organizations": ["list of org names"],
>     "dates": ["list of dates mentioned"],
>     "amounts": ["list of monetary amounts"]
>   },
>   "action_items": ["list of recommended actions"],
>   "confidence_score": 0.0 to 1.0
> }
> 
> IMPORTANT: Return raw JSON only. Do not wrap in markdown code blocks.

**Why this works:**
1. **Strict Enums:** Forcing `classification` and `sentiment` into specific arrays prevents downstream routing errors in the Python API.
2. **Format Control:** The "raw JSON only" instruction ensures the output can be cleanly evaluated by n8n's expression engine without regex cleanup.
3. **Multi-Modal Ready:** By keeping the text prompt focused on structure, we successfully allowed the Gemini Vision model to simultaneously process embedded base64 images to populate the `amounts` and `summary` fields when analyzing charts.