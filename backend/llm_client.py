import os
import time
import httpx # S-Tier Fix: Robust timeouts
import google.generativeai as genai
from openai import OpenAI
from groq import Groq, RateLimitError # S-Tier Fix: Handling 429s
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, provider="gemini", api_key=None, model_name=None, base_url=None):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url

        # Defaults if not provided
        if not self.provider:
            self.provider = "gemini"
        
        if self.provider == "gemini":
            if not self.api_key:
                self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                print("WARNING: GEMINI_API_KEY missing.")
            else:
                genai.configure(api_key=self.api_key)
            
            if not self.model_name:
                self.model_name = "gemini-flash-latest"

        elif self.provider == "groq":
            if not self.api_key:
                self.api_key = os.getenv("GROQ_API_KEY")
            
            if not self.api_key:
                 print("WARNING: GROQ_API_KEY missing.")
            
            # S-TIER FIX: Set explicit 60s timeout to prevent 'Request timed out' crashes
            self.client = Groq(
                api_key=self.api_key,
                timeout=httpx.Timeout(60.0, connect=10.0)
            )
            
            if not self.model_name:
                self.model_name = "llama-3.1-70b-versatile"

        elif self.provider in ["openai", "local"]:
            if not self.api_key and self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            
            # For local, api_key might be irrelevant but string required
            if not self.api_key and self.provider == "local":
                self.api_key = "lm-studio" 

            if not self.base_url and self.provider == "local":
                 # Default to standard local port if not set
                self.base_url = "http://localhost:1234/v1"

            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            if not self.model_name:
                self.model_name = "gpt-4o" if self.provider == "openai" else "local-model"

    def complete_chat(self, messages, temperature=0.7, json_response=False, stop=None):
        if self.provider == "gemini":
            return self._complete_gemini(messages, temperature, json_response, stop)
        elif self.provider in ["openai", "local"]:
            return self._complete_openai(messages, temperature, json_response, stop)
        elif self.provider == "groq":
            return self._complete_groq(messages, temperature, json_response, stop)
        else:
             raise ValueError(f"Unknown provider: {self.provider}")

    def _complete_openai(self, messages, temperature, json_response, stop):
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        if stop:
            kwargs["stop"] = stop
        if json_response and self.provider == "openai":
             # "local" might not support json_object mode
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _complete_groq(self, messages, temperature, json_response, stop):
        # S-TIER FIX: Retry logic for Rate Limits
        max_retries = 3
        current_try = 0
        
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        if stop:
            kwargs["stop"] = stop
        if json_response:
             kwargs["response_format"] = {"type": "json_object"}

        while current_try < max_retries:
            try:
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            
            except RateLimitError:
                wait_time = 20 * (current_try + 1)
                print(f"[LLMClient] Rate Limit Hit. Cooling down for {wait_time}s...")
                time.sleep(wait_time)
                current_try += 1
            
            except Exception as e:
                print(f"[LLMClient] Groq Error: {e}. Retrying ({current_try + 1}/{max_retries})...")
                time.sleep(2) # Short pause for transient errors
                current_try += 1
                
        print("[LLMClient] Max retries reached. Returning None.")
        return None

    def _complete_gemini(self, messages, temperature, json_response, stop):
        system_instruction = None
        gemini_history = []
        last_message = ""
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                if system_instruction is None: system_instruction = content
                else: system_instruction += f"\n{content}"
            elif role == "user":
                gemini_history.append({"role": "user", "parts": [content]})
                last_message = content
            elif role == "assistant":
                gemini_history.append({"role": "model", "parts": [content]})

        if gemini_history and gemini_history[-1]["role"] == "user":
            gemini_history.pop() # Remove last user msg to send it as trigger
        else:
            last_message = "continue"

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )
        
        config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json" if json_response else "text/plain",
            stop_sequences=stop if stop else []
        )

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(last_message, generation_config=config)
        return response.text