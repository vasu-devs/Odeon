import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

class LLMClient:
    def __init__(self):
        # Assumes GEMINI_API_KEY is in environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in env.")
        else:
            genai.configure(api_key=api_key)
        
        # User requested Gemini 2.0 Flash. 
        # Note: Exact model name for 2.0 Flash might be 'gemini-2.0-flash-exp' during preview, 
        # or we fallback to 'gemini-1.5-flash' if 2.0 isn't public yet. 
        # Using 'gemini-2.0-flash-exp' as requested.
        self.model_name = "gemini-flash-latest" 
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 32,
        }

    def complete_chat(self, messages, temperature=0.7, json_response=False):
        """
        Wrapper for chat completions using Gemini.
        messages: list of {"role": "...", "content": "..."}
        """
        try:
            # Convert OpenAI-style messages to Gemini history if needed, 
            # or just use the generative model's chat method.
            # Gemini typically expects a specific structure or just a prompt for simple cases.
            # For simplicity in this wrapper, we'll concatenate for a single prompt 
            # or use the chat session if we were maintaining state here.
            # Given the calling code passes a full history list every time, 
            # we should probably construct a fresh chat session or format it as a prompt.
            
            # Simple conversion for stateless "complete_chat":
            # Just send the last message? No, we need context.
            # We'll map "system" to a system instruction if possible, but the python sdk 
            # handles system instructions in the model config or we can prepend it.
            
            system_instruction = None
            gemini_history = []
            
            last_message = ""
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    # Prepend to history or use as system instruction
                    # For simplicty, let's just make it the first part of context if logic permits,
                    # but Gemini 1.5+ supports system_instruction argument in GenerativeModel.
                    if system_instruction is None:
                        system_instruction = content
                    else:
                        system_instruction += f"\n{content}"
                elif role == "user":
                    gemini_history.append({"role": "user", "parts": [content]})
                    last_message = content
                elif role == "assistant":
                    gemini_history.append({"role": "model", "parts": [content]})

            # If the last message in history is the one we want to send, pop it?
            # The standard pattern is `chat.send_message(last_user_msg)`.
            # If the list ends with assistant, we have nothing to answer.
            # Assuming the caller appended the user message last.
            
            if gemini_history and gemini_history[-1]["role"] == "user":
                last_user_parts = gemini_history.pop()
                last_message = last_user_parts["parts"][0]
            else:
                # If no user message at end, maybe it's a pure generation (unlikely in this app flow)
                last_message = "continue"

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            
            config = self.generation_config.copy()
            config["temperature"] = temperature
            if json_response:
                config["response_mime_type"] = "application/json"

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(last_message, generation_config=config)
            
            return response.text
        except Exception as e:
            print(f"CRITICAL LLM ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None
