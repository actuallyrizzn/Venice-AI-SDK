Perfect. I’ll compile a modular reference guide for VeniceAPI’s LLM, focusing on Chat Completions and adjacent API calls, using Python SDK examples when available and falling back to cURL where necessary. I’ll also include authentication setup and error-handling best practices so it’s fully reusable in future AI coding workflows within Sanctum’s Letta framework.

I’ll get started and will let you know when the guide is ready for review.

# VeniceAPI LLM Chat Completions Integration Guide (Sanctum Letta)

This guide provides a modular reference for using **VeniceAPI’s LLM Chat Completions** within the Sanctum Letta framework. It focuses on chat completion endpoints and related features (streaming, function calling, context handling, etc.), with Python SDK-style examples (and cURL equivalents where appropriate). Each section covers a specific aspect of the API for clarity and future reusability.

## Authentication and API Key Setup

Before calling the Venice LLM API, you must **authenticate** using an API key:

- **Obtaining an API Key:** Log in to the [Venice API dashboard](https://venice.ai/settings/api) and generate a new API key. (Navigate to *Settings -> API Keys -> Generate New API Key*.) Save this key securely – it will be used for all API requests ([How to use Venice API](https://venice.ai/blog/how-to-use-venice-api#:~:text=How%20to%20generate%20a%20Venice,API%20Key)).
- **Using the API Key:** Venice uses **Bearer token authentication**. Include an HTTP header `Authorization: Bearer <your-api-key>` with every request ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=required)). For example, in a Python request you can set: 

  ```python
  import os, requests
  API_KEY = os.getenv("VENICE_API_KEY")  # assume your key is stored in an env var
  headers = {"Authorization": f"Bearer {API_KEY}"}
  ```
  ```bash
  # Equivalent cURL example (replace <your-api-key> with the actual key):
  curl -H "Authorization: Bearer <your-api-key>" https://api.venice.ai/api/v1/models
  ```
- **Security Considerations:** Treat your API key like a password. **Do not hard-code it** in client-side code or repositories. Instead, use environment variables or secure vaults to inject the key into your application. Also, restrict access and rotate the key if you suspect compromise.
- **Permissions:** Ensure your account has the required tier (e.g. Explorer or Paid) for the endpoints you use. If your key is invalid or inactive, requests will be rejected with a 401/403 error (e.g. `AUTHENTICATION_FAILED` or `UNAUTHORIZED`) ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=Error%20Code%20HTTP%20Status%20Message,400%20Invalid%20model%20specified)).

## Listing Available Models (Choosing an LLM)

You will need a **model ID** to specify which LLM to use for chat completions. Venice provides an endpoint to list available models:

- **Endpoint:** `GET /api/v1/models` (no request body needed). This returns a JSON list of model objects and their capabilities ([Venice API Docs: /models](https://docs.venice.ai/api-reference/endpoint/models/list#:~:text=,)).
- **Usage:** You can call this once at startup to pick a model:
  ```python
  resp = requests.get("https://api.venice.ai/api/v1/models", headers=headers)
  models = resp.json().get("data", [])
  for m in models:
      if m["type"] == "text":
          print(m["id"], "-> supports function calling?", m["model_spec"]["capabilities"]["supportsFunctionCalling"])
  ```
  ```bash
  # cURL example to fetch models list
  curl --request GET \
       --url https://api.venice.ai/api/v1/models \
       --header "Authorization: Bearer <your-api-key>"
  ```
- **Selecting a Model:** Identify the `id` of the text model you want (e.g. `"mistral-31-24b"` or `"llama-3.3-70b"`). The model listing also shows capabilities like `supportsFunctionCalling` or `supportsWebSearch` ([Venice API Docs: /models](https://docs.venice.ai/api-reference/endpoint/models/list#:~:text=,false)), which is useful if you plan to use advanced features (ensure the chosen model supports them).
- For chat completion, **use text models** (image models are for image generation and not relevant here). In the examples below, we’ll assume a text model ID such as `llama-3.3-70b`. 

## Chat Completions API Overview

The **Chat Completions** endpoint generates model responses given a conversation context. Key details include:

- **Endpoint URL:** `POST https://api.venice.ai/api/v1/chat/completions` ([Quickstart](https://docs.venice.ai/overview/getting-started#:~:text=curl%20,system))  
- **Purpose:** Send a sequence of messages (chat history and prompt) and receive the assistant’s reply.
- **Request Structure:** JSON body with at least the following required fields:
  - `model` (string, required): The ID of the model to use (from the models list) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=model)).
  - `messages` (array, required): The conversation messages so far (including the latest user query). Each message is an object with a `role` and `content` ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=messages)).
- **Response Structure:** On success (HTTP 200), you'll get a JSON with:
  - `id`: a unique request ID (e.g. `"chatcmpl-abc123"`) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=id)).
  - `object`: type of object (should be `"chat.completion"`) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=object)).
  - `created`: timestamp of request ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=created)).
  - `model`: the model ID that generated the response ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=model)).
  - `choices`: a list of completion choices. Each choice has:
    - `index`: index of the choice (0 for the first) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=choices)).
    - `message`: the assistant’s message object containing the model’s reply. For a normal chat completion, `message.role` will be `"assistant"` and `message.content` holds the generated answer text ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=The%20assistant%20message%20contains%20the,response%20from%20the%20LLM)) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=choices)).
    - `finish_reason`: reason generation stopped (e.g. `"stop"` or `"length"`) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=choices)).
  - `usage`: token usage stats – how many tokens were in the prompt, completion, and total ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=usage)) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=usage)) (helpful for monitoring costs/limits).
- **Stateless Operation:** Each call is independent. The API does not maintain conversation state between requests. To continue a conversation, you must include prior messages in the `messages` list on each request (see **Message Roles and Context** below).

### Example – Basic Chat Completion Request

Below is an example of using the chat completion API with a simple system instruction and one user prompt:

**Python Example:**

```python
import requests

url = "https://api.venice.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama-3.3-70b",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about AI."}
    ]
}
response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result["choices"][0]["message"]["content"])
```

**cURL Equivalent:**

```bash
curl --request POST \
  --url https://api.venice.ai/api/v1/chat/completions \
  --header "Authorization: Bearer <your-api-key>" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "llama-3.3-70b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Tell me about AI."}
    ]
  }'
```

In this example, the API will return an assistant response in `result["choices"][0]["message"]["content"]`. The system message sets the assistant’s behavior, and the user message is the prompt. (By default, Venice will also include its own system prompt to guide the model, as noted below.)

## Message Roles and Conversation Context

The `messages` list in the request represents the conversation history. Each message has a **role** and **content**:

- **Roles:** Venice supports four roles: `"user"`, `"assistant"`, `"system"`, and `"tool"` ([How to use Venice API](https://venice.ai/blog/how-to-use-venice-api#:~:text=4,identified%20in%20the%20earlier%20section)).
  - `user`: A message from the end-user. This is typically the prompt or question you want answered. (Multiple user turns can be in history.)
  - `assistant`: A message from the AI assistant. These are previous answers given by the model. Include these to provide context for the next response.
  - `system`: A directive or context setting for the assistant. Usually, the conversation begins with a system message like `"You are a helpful assistant"` to establish tone or restrictions.
  - `tool`: A special role for tool/function interactions (see **Function Calling** section). It represents output from an external tool back to the assistant.
- **Conversation History:** To manage context or threads, **pass the prior messages** in each request. The messages should appear in chronological order. For example, to continue a dialogue, include the initial system prompt, then alternating user/assistant messages, and finally the latest user query. The model will consider all these messages as the conversation so far ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=A%20list%20of%20messages%20comprising,and%20processed%20by%20the%20model)). There is no separate conversation ID; you control context by what you send.
- **Message Content:** `content` can be plain text for user/assistant/system messages. (Venice also supports certain non-text content types like images or structured data if the model allows, but those are beyond basic usage.)
- **Max Context Length:** Each model has a maximum context length (in tokens) – e.g., some support very large contexts (the model list shows `availableContextTokens` for each model). If the total tokens of your provided messages plus expected reply exceed this, you might get an error or truncated output. Manage history by removing or summarizing older messages if necessary.

## Controlling the Completion Output (Parameters)

Venice’s chat completion API supports various parameters to shape or constrain the model’s output. These are optional fields in the JSON body of the request:

- **Temperature:** `temperature` (float, 0 to 2, default ~0.15) – Randomness in output. Higher values produce more varied responses, lower values yield more deterministic output. Generally adjust either `temperature` **or** `top_p`, not both ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=number)).
- **Top-p (Nucleus Sampling):** `top_p` (float, 0 to 1, default 0.9) – Limits consideration to a subset of tokens with a cumulative probability <= top_p. For example, `top_p: 0.1` means only the top 10% probability tokens are considered ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=top_p)). Lowering top_p makes output more focused.
- **Top-k:** `top_k` (integer, >=0) – Limits consideration to the top k highest-probability tokens at each step. For example, `top_k: 40` considers the 40 most likely tokens ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=top_k)). A value of 0 disables top-k filtering.
- **Min Probability (`min_p`):** (float, 0 to 1) – Filters out any token with probability below this threshold ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=min_p)). This ensures a minimum likelihood for each token chosen.
- **Presence Penalty:** `presence_penalty` (float, -2.0 to 2.0, default 0) – Positive values **encourage new topics** by penalizing tokens that have already appeared in the conversation ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=presence_penalty)). This makes the model less likely to repeat itself or loop on the same subject.
- **Frequency Penalty:** `frequency_penalty` (float, -2.0 to 2.0, default 0) – Positive values penalize more frequent tokens ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=Number%20between%20,repeat%20the%20same%20line%20verbatim)), reducing repetition of the **exact same text**.
- **Repetition Penalty:** `repetition_penalty` (float, >= 1.0, default 1.0) – A multiplicative penalty where >1.0 discourages any token from being used again. (1.0 means no penalty.)
- **Max Tokens:** *Deprecated* `max_tokens` vs **Preferred** `max_completion_tokens`:
  - `max_completion_tokens` (int) – The maximum number of tokens the model can generate **for the completion** ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=max_completion_tokens)). This caps the length of the assistant’s reply (including any internal reasoning tokens if applicable). Set this to control cost and output length.
  - (The older `max_tokens` field served a similar purpose but is deprecated in favor of `max_completion_tokens` ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=integer)).)
- **Number of Choices:** `n` (int, default 1) – How many response **choices** to generate ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=default%3A1)). If >1, the response will contain multiple entries in the `choices` list. Note that you will be billed for all tokens generated across all choices.
- **Stop Sequences:** `stop` (string or array of strings) – Up to 4 sequences at which the model will stop generating further tokens ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=stop)). For example, you can instruct the model to stop when it outputs “\nUser:” or some end-of-answer token. You can also use `stop_token_ids` for specifying exact token IDs to stop on, if needed ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=stop_token_ids)).
- **User Identifier:** `user` (string) – An arbitrary identifier for the end-user or conversation, for logging/monitoring. Venice accepts this field (for OpenAI compatibility) but does not use it in generation ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=user)). It can be included for audit or tracking, e.g., `"user": "session_12345"`.

You can mix and match these parameters to get the desired behavior. For example, to get a concise answer without rambles, you might set a lower `max_completion_tokens`, moderate temperature, and use a stop sequence like `"\n"` to cut off after a sentence or two.

## Venice-Specific Features (Web Search and Personas)

VeniceAPI offers some unique extensions via the `venice_parameters` object in the request. These can enhance or modify the model’s behavior:

- **Web Search Integration:** Setting `venice_parameters.enable_web_search` to `"on"` or `"auto"` can allow the model to perform a web search for relevant information ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=venice_parameters)). 
  - `"on"` forces a web search query, `"auto"` lets the model decide when to search, and `"off"` (default) disables searching. 
  - If enabled and the model uses it, the response will include cited sources (either in the first streaming chunk or in the final response) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=Enable%20web%20search%20for%20this,in%20the%20non%20streaming%20response)). The citations appear in `venice_parameters.web_search_citations` in the response, containing titles, URLs, and excerpts ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=venice_parameters)) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=%5B%20%7B%20,sky%20most%20of%20the%20time)).
  - *Use case:* For factual questions, the model can retrieve live information. Ensure the model supports web search (see model capabilities `supportsWebSearch`) before enabling this.
- **Venice System Prompt:** By default, Venice adds its own hidden system instructions to every request to guide the model (for consistency, safety, etc.). You can control this with `venice_parameters.include_venice_system_prompt` (boolean, default `true`) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=venice_parameters)). 
  - If `true`, the model gets the Venice-provided system prompt *in addition* to any system message you supply. If you prefer to fully customize the system instructions and not include Venice’s defaults, set this to `false`.
  - Typically, leaving it `true` is recommended unless you have a specific reason to override the default behavior.
- **Character Personas:** Venice allows using predefined personas (characters) by specifying `venice_parameters.character_slug` ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=venice_parameters)). A “character” in Venice is essentially a preset personality or role for the assistant (with its own system prompt and style).
  - Example: `"character_slug": "venice"` might invoke a default Venice persona. Public characters can be found in Venice’s documentation or UI.
  - If provided, the model will behave as that character. This is an alternative to writing a detailed system prompt yourself. (You can still include a custom system message alongside it.)
  - If the slug is invalid or not found, you’ll get a 404 error (`CHARACTER_NOT_FOUND`) ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=%60INVALID_REQUEST%20%60400%20Invalid%20request%20parameters,found%20from%20the%20provided%20character_slug)).
- **Dynamic Temperature Scaling:** Venice supports `min_temp` and `max_temp` to dynamically adjust the temperature during generation ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=max_temp)) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=min_temp)). These define a range within which the model may anneal the temperature (useful for certain advanced decoding strategies). In most simple use cases, you can stick to a fixed `temperature` value and not use these.

Include any of these `venice_parameters` fields in the request JSON as needed. For example:

```json
"venice_parameters": {
    "enable_web_search": "auto",
    "include_venice_system_prompt": true,
    "character_slug": "venice"
}
```

This would allow the model to decide on web searches, keep the default system prompt, and use the “venice” persona’s style.

## Streaming Responses (Real-time Token Streaming)

The Chat Completions API can stream the response tokens incrementally, which is useful for real-time applications (showing the answer as it’s being generated, like ChatGPT’s streaming output):

- **Enabling Streaming:** Set the request parameter `"stream": true` ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=stream)). By default, `stream` is false and you get the entire completion after it’s done. With `true`, the API will send back a stream of partial results.
- **How Streaming Works:** The response will be sent as a series of data chunks (Server-Sent Events). Each chunk typically contains a partial message (some tokens that the model has generated so far) and a similar JSON structure, except the object might be labeled as a `"chat.completion.chunk"`. The stream ends with a special `[DONE]` message (no more data after that), similar to OpenAI’s protocol.
- **Reading the Stream (Python):** You can use the `requests` library to iterate over an event stream. For example: 

  ```python
  import json
  stream_data = {
      "model": "llama-3.3-70b",
      "messages": [...],
      "stream": True
  }
  with requests.post(url, headers=headers, json=stream_data, stream=True) as resp:
      for line in resp.iter_lines():
          if line:
              decoded = line.decode('utf-8')
              # Each line is an SSE "data: ..." payload
              if decoded.startswith("data: "):
                  data = decoded[len("data: "):]
                  if data == "[DONE]":
                      break  # end of stream
                  chunk = json.loads(data)
                  # Process the chunk (which will have a structure similar to a full response)
                  partial_text = chunk["choices"][0]["message"].get("content", "")
                  print(partial_text, end="", flush=True)
  ```
  This will print tokens as they arrive. In a real app, you might append these to build the full message.
- **Including Usage in Stream:** By default, token usage info is given only in the final full response. If you want usage statistics as part of the streamed events, set `"stream_options": { "include_usage": true }` ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=stream_options)) in the request. This will intersperse an event containing the `usage` object (prompt/completion token counts) near the end of the stream.
- **Client Considerations:** When streaming, be prepared to handle partial JSON. Each `data:` chunk from the server will contain a JSON fragment (e.g., a few tokens in `"choices"[0]["delta"]["content"]` if following OpenAI’s format, or directly in `"message":{"content": "..."}"` in Venice’s case). Always check for the `"[DONE]"` sentinel to know when to stop listening.
- **Citations in Streaming:** If using web search, any citations from the search may be delivered in the **first chunk** of the stream (as part of the assistant’s message content or a separate field), since the model often finds info before generating the rest ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=default%3Aoff)). Ensure your stream handling captures that first chunk properly.

Streaming enables responsive UIs and can reduce latency perceived by the user. Keep in mind that streaming a large response can still take as long as a non-streamed request to fully complete; it just allows you to start processing output sooner.

## Function Calling and Tool Use

Venice’s chat API supports **function calling** (referred to as "tools" in the API) to enable the model to invoke external functions or actions. This is similar to OpenAI’s function calling, allowing the model to output a structured request for a tool, which your code can execute and then return the result back to the model. 

Key points for using function calling:

- **Defining Available Functions:** In the request, include a `tools` field – an array of tool definitions. Currently, the only supported tool type is **functions** ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=object%5B%5D%20)). Each entry in `tools` should define one function the model is allowed to call. The format for each function uses a JSON structure:
  ```json
  "tools": [
    {
      "function": {
        "name": "<function_name>",
        "description": "<what the function does>",
        "parameters": {
          // JSON Schema defining function arguments
        }
      }
    }
  ]
  ``` 
  **Name** and **parameters** are required for each function ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=tools)). The `parameters` should be a JSON Schema object describing the expected arguments (keys, types, required fields). Optionally include a description for better model understanding.
  
  Example definition:
  ```json
  "tools": [
    {
      "function": {
        "name": "get_weather",
        "description": "Lookup current weather for a city",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City name"},
            "units": {"type": "string", "enum": ["metric","imperial"]}
          },
          "required": ["location"]
        }
      }
    }
  ]
  ```
  This would allow the model to call a function `get_weather` with a JSON argument containing a location and optional units.
- **Model Requirements:** Ensure the model supports function calling. Most Venice text models do (the model listing will show `"supportsFunctionCalling": true` for those models ([Venice API Docs: /models](https://docs.venice.ai/api-reference/endpoint/models/list#:~:text=,false))). If not, the model will ignore the `tools` or fail to use them. Models also may have a default mode or trait enabling this (e.g., some models have a trait `function_calling_default` pre-activated ([Venice API Docs: /models](https://docs.venice.ai/api-reference/endpoint/models/list#:~:text=,Instruct%22%20%7D))).
- **Invoking a Function (API Flow):** The workflow is analogous to OpenAI’s:
  1. **User prompt is sent** along with the function definitions (`tools`). 
  2. **Model response**: If the model decides a function is needed, it will produce a special response indicating a tool/function call *instead of* a final answer. In Venice’s response, this might appear as the assistant’s message content containing a JSON payload or as a structured entry in `choices.message.tool_calls` ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=choices)). For example, the model might return something that indicates `get_weather` should be called with certain arguments.
  3. **Detect function call**: Your application needs to check the response. If the `role` of the message is `"assistant"` but the `content` is empty and instead a function call is present (or if `tool_calls` array is non-empty), then the model is requesting a tool. Extract the function name and parameters. *(In OpenAI, this is `response["choices"][0]["message"]["function_call"]`. In Venice, look for the `tool_calls` structure. For instance, `response["choices"][0]["message"]["tool_calls"][0]` might contain `{ "function": { "name": "...", "parameters": {...} } }`.)*
  4. **Execute the function** in your external code using those parameters. Get the result (e.g., actual weather data).
  5. **Return result to model**: Send a *follow-up* chat completion request, appending a new message with `role: "tool"`. The content of this tool message should contain the function result (typically formatted as the function’s return value or output). You may also include the function name in the message (some frameworks use `name` field to indicate which tool is responding). For example:
     ```json
     {"role": "tool", "name": "get_weather", "content": "{\"temperature\": 22, \"unit\": \"C\"}"}
     ```
     This informs the model of the outcome of its function call.
  6. **Model continues**: The next response from the model (assistant) will ideally use the function result and produce a final answer to the user. 

- **Parallel Tool Calls:** Venice has an option `parallel_tool_calls` (boolean, default true) ([Venice API Docs: /chat/completions](https://docs.venice.ai/api-reference/endpoint/chat/completions#:~:text=parallel_tool_calls)). When true, the model *could* request multiple function calls in parallel (or in one response). In practice, most use cases involve one function at a time, but this setting exists for advanced scenarios. You can set it to `false` to force the model to call at most one function at once (i.e., require sequential tool use).
- **Example Usage:** Suppose the user asks, *“What’s the weather in Paris and could you plot a chart of the temperatures?”* If you provided both a `get_weather` and a `plot_chart` function in `tools`, a capable model might return a function call for `get_weather` with `{"location": "Paris"}`. You execute it, get a result (e.g., JSON with forecast), then include a tool message with that data. The model might then call `plot_chart` with the data, etc. Finally, it would produce an answer describing the weather and displaying the chart (if such capabilities exist). This multi-step interaction is enabled by the function calling feature.
- **OpenAI Compatibility:** The design of Venice’s function calling is intended to be **compatible with OpenAI’s format**, so that frameworks like Letta can use it. In fact, Letta requires that any OpenAI-style endpoints it connects to support function calls ([OpenAI-compatible endpoint | Letta](https://docs.letta.com/guides/server/providers/openai-proxy#:~:text=To%20use%20OpenAI,endpoints%20must%20support%20function%2Ftool%20calling)). If you point Letta’s OpenAI proxy settings to Venice (by setting `OPENAI_API_BASE=https://api.venice.ai/api/v1` and using your Venice API key as `OPENAI_API_KEY`), Letta can invoke Venice for chat completions. The function definitions (`functions` in OpenAI, `tools` in Venice) and function call responses are handled in a similar way. Always ensure the JSON schema for parameters is well-defined, as the model will generate arguments to match that schema.

In summary, **function calling** allows your LLM agent to perform actions (like database queries, calculations, web browsing, etc.) during a conversation. Venice’s API gives you the hooks to implement this in a step-by-step manner. Be prepared to capture the model’s function call request, execute it, and then continue the conversation with the results.

## Error Handling and Retry Strategies

When integrating the Venice LLM API, robust error handling is important for a smooth developer and user experience. Here are common error scenarios, how to catch them in Python, and strategies to handle or retry:

- **HTTP Errors and Codes:** Venice returns standard HTTP error codes with a JSON body containing an `error` object. For example, a 400 Bad Request might return:
  ```json
  { "error": { "code": "INVALID_REQUEST", "message": "Invalid request parameters", "status": 400 } }
  ```
  Some common error codes include:
  - **401 Unauthorized:** API key missing, invalid, or inactive. For instance, `AUTHENTICATION_FAILED` (bad key) or `AUTHENTICATION_FAILED_INACTIVE_KEY` (key is valid but subscription lapsed) ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=Error%20Code%20HTTP%20Status%20Message,400%20Invalid%20model%20specified)).
  - **403 Forbidden:** The key is valid but not allowed to access a resource (e.g., hitting an endpoint not enabled for your tier, shown as `UNAUTHORIZED` in the error code) ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=API.,400%20Invalid%20model%20specified)).
  - **404 Not Found:** Often returned if you specify a non-existent resource, such as an unknown `model` ID or a wrong URL. For example, `MODEL_NOT_FOUND` for a bad model name, or `CHARACTER_NOT_FOUND` if a character slug is invalid ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=%60INVALID_REQUEST%20%60400%20Invalid%20request%20parameters,found%20from%20the%20provided%20character_slug)).
  - **400 Bad Request:** The input JSON is malformed or fields are invalid. `INVALID_REQUEST` covers generic issues like missing required fields, and `INVALID_MODEL` if the model ID is not recognized ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=%60UNAUTHORIZED%20%60403%20Unauthorized%20access,be%20found%20from%20the%20provided)). You should fix the request rather than retrying as-is.
  - **415 Unsupported Media Type:** Usually if `Content-Type: application/json` header is missing or wrong ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=%60INVALID_CONTENT_TYPE%20%60415%20Invalid%20content%20type,400%20Invalid%20image%20format)). Ensure you set the content type for POST requests sending JSON.
  - **429 Too Many Requests:** Rate limit exceeded. The response code is 429 with error `RATE_LIMIT_EXCEEDED` ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=,404%20Specified%20model%20not%20found)). This indicates you’ve hit the per-minute or daily limit for your tier or key.
  - **500/503 Server Errors:** These indicate an issue on Venice’s side processing the request. E.g., `INFERENCE_FAILED` (a model inference error) ([Error Codes](https://docs.venice.ai/api-reference/error-codes#:~:text=%60RATE_LIMIT_EXCEEDED%20%60429%20Rate%20limit%20exceeded,500%20Image%20upscaling%20failed%20error)) or `UNKNOWN_ERROR`. These are usually transient.
- **Catching Errors in Python:** If using the `requests` library, a non-200 status will not throw an exception by default. You should check `response.status_code`. For example:
  ```python
  resp = requests.post(url, headers=headers, json=data)
  if resp.status_code != 200:
      err = resp.json().get("error", {})
      code = err.get("code"); msg = err.get("message")
      print(f"Request failed: {code} - {msg}")
      # handle according to code...
  else:
      result = resp.json()
      # process result normally
  ```
  Alternatively, you can use `resp.raise_for_status()` in a try/except to catch HTTPError exceptions. The error response JSON can then be inspected as above.
- **Retry Logic:** For certain errors, especially *429 Rate Limit* or *5xx Server errors*, implementing a retry with backoff is recommended:
  - **Rate Limits (429):** If you get a 429, examine the response headers. Venice may include `Retry-After` or you might simply implement an exponential backoff. For instance, wait a few seconds and try again. On each subsequent 429, increase the wait time (e.g., 1s, then 2s, then 4s...). Do not spam retries, as that can worsen the problem. Also consider logging these events or alerting the user that the system is busy. Rate limit errors mean you’re sending too many requests or using too many tokens per minute ([Rate Limits](https://docs.venice.ai/api-reference/rate-limiting#:~:text=)) – you may need to optimize usage or upgrade your plan if they occur frequently.
  - **Transient 500 Errors:** If `INFERENCE_FAILED` or a network error occurs, you can catch it and retry the request after a brief delay. Often one retry is enough if it was a momentary glitch. If it consistently fails for the same input, there may be an issue with that model or input (you might try a different model or simplify the prompt in such cases).
  - **Network Timeouts:** Set reasonable timeouts on your HTTP requests and catch `requests.exceptions.Timeout`. A hung request might indicate a problem; you can retry after timeout, but if it persists, check Venice status page or your network.
- **No Retry for Client Errors:** For 400-series errors other than 429, do **not** automatically retry – first fix the request. E.g., if you get `INVALID_MODEL`, double-check the model ID string; if `INVALID_REQUEST`, ensure all required fields are present and types are correct.
- **Logging and Monitoring:** It’s good practice to log error details (status code, error code, message, and request ID if available) for debugging. The `id` in the error response (if provided) can help Venice support trace the issue in their logs.
- **Thread Safety and Idempotence:** The chat completion endpoint is generally idempotent (same input yields same output, aside from randomness), so retrying a request that didn’t succeed should be safe. Just be cautious with function calling loops – ensure you don’t double-execute a function unintentionally if a network retry happens during a tool call exchange.

By handling errors gracefully, your integration will be more robust. For instance, in a production app using Letta with Venice: you could wrap the completion call in a function that catches exceptions and returns an error message to the user or triggers a retry with a delay. Many frameworks will allow you to plug in custom logic for retries or fallbacks (like switching to a simpler model if a complex one fails).

## Conclusion and Best Practices

Integrating VeniceAPI’s LLM into Sanctum Letta involves using the chat completions endpoint with proper authentication and then leveraging the rich feature set (streaming, function calls, etc.) as needed:

- Always test your requests with the specific model you plan to use – different models might have slight differences (e.g., in how they utilize system prompts or tools).
- Use the **Python examples** provided as a starting point for your implementation, and refer to the cURL examples or official documentation for any fields you’re unsure about.
- Keep the guide handy as a **modular reference**: you can refer to the Authentication section when setting up keys, the Chat Completions section when constructing prompts, and so on, without wading through unrelated API parts (embeddings, file uploads, etc. are intentionally omitted as they’re not needed for basic LLM interaction).

By following this guide, you can confidently integrate VeniceAPI’s chat AI capabilities into the Letta framework (or any other AI orchestration framework) and build powerful, stateful LLM applications. For more details, always consult the [official Venice API documentation](https://docs.venice.ai) and the Letta docs for provider integration, and keep an eye on version changes or new features (Venice’s API may evolve with new parameters or capabilities over time).

