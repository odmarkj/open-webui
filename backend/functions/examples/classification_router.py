"""
title: Smart Classification Router
description: Automatically classifies user prompts and routes them with optimized system prompts and settings
requirements: openai
author: Assistant
version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Callable, Any
from openai import OpenAI
import json

# Import classification system
from lib.classification import (
    get_classification_config,
    classify_and_get_config,
    get_all_classifications,
    ClassificationType,
    LLMModel
)


class Pipe:
    """
    Smart Classification Router

    This Pipe demonstrates the classification system by:
    1. Detecting the type of user prompt (Question, Code_Generation, etc.)
    2. Automatically applying optimal system prompts
    3. Using appropriate temperature and token settings
    4. Routing to the right model type

    This is useful for:
    - Creating adaptive AI assistants
    - Optimizing responses based on request type
    - Maintaining consistent quality across different task types
    """

    class Valves(BaseModel):
        """Configuration for the Smart Classification Router."""

        # LLM Configuration
        llm_base_url: str = Field(
            default="http://localhost:8000/v1",
            description="Base URL for LLM API (OpenAI-compatible endpoint)"
        )
        llm_api_key: str = Field(
            default="EMPTY",
            description="API key for LLM (use 'EMPTY' for local instances)"
        )

        # Model mapping for different LLM types
        model_general: str = Field(
            default="gpt-3.5-turbo",
            description="Model for general tasks"
        )
        model_code: str = Field(
            default="gpt-4",
            description="Model for code tasks"
        )
        model_reasoning: str = Field(
            default="gpt-4",
            description="Model for reasoning tasks"
        )
        model_creative: str = Field(
            default="gpt-4",
            description="Model for creative tasks"
        )
        model_fast: str = Field(
            default="gpt-3.5-turbo",
            description="Model for fast, simple tasks"
        )

        # Router Configuration
        auto_classify: bool = Field(
            default=True,
            description="Automatically classify prompts (if false, uses general config)"
        )
        show_classification: bool = Field(
            default=True,
            description="Show detected classification in response"
        )
        use_optimized_settings: bool = Field(
            default=True,
            description="Use optimized temperature and token settings per classification"
        )

        # Fallback settings
        default_temperature: float = Field(
            default=0.7,
            ge=0.0,
            le=2.0,
            description="Default temperature when not using optimized settings"
        )
        default_max_tokens: int = Field(
            default=2000,
            ge=100,
            le=8000,
            description="Default max tokens when not using optimized settings"
        )

        # Classification override (for testing specific classifications)
        force_classification: str = Field(
            default="",
            description="Force a specific classification (leave empty for auto-detection)"
        )

    def __init__(self):
        """Initialize the Smart Classification Router."""
        self.name = "Smart Classification Router"
        self.valves = self.Valves()

    def _get_model_for_llm_type(self, llm_model: LLMModel) -> str:
        """
        Map LLMModel enum to actual model name based on valves configuration.

        Args:
            llm_model: The LLMModel type

        Returns:
            str: Actual model name to use
        """
        model_mapping = {
            LLMModel.GENERAL: self.valves.model_general,
            LLMModel.FAST: self.valves.model_fast,
            LLMModel.CODE: self.valves.model_code,
            LLMModel.REASONING: self.valves.model_reasoning,
            LLMModel.CREATIVE: self.valves.model_creative,
            LLMModel.MATH: self.valves.model_reasoning,
            LLMModel.ANALYSIS: self.valves.model_general,
            LLMModel.EMBEDDING: self.valves.model_fast,
            LLMModel.CHAT: self.valves.model_fast,
        }
        return model_mapping.get(llm_model, self.valves.model_general)

    def _classify_prompt(self, prompt: str) -> Optional[str]:
        """
        Classify the user prompt using a simple LLM call.

        In a production system, you would:
        1. Use a specialized classification model
        2. Use embeddings + similarity search
        3. Use keyword matching + rules
        4. Cache classifications for similar prompts

        Args:
            prompt: User's input prompt

        Returns:
            Classification type or None
        """
        if not self.valves.auto_classify:
            return None

        # If force_classification is set, use that
        if self.valves.force_classification:
            return self.valves.force_classification

        # Simple heuristic-based classification (in production, use ML model)
        # This is a simplified approach - replace with actual ML classification
        prompt_lower = prompt.lower()

        # Code-related keywords
        if any(word in prompt_lower for word in [
            "write code", "python", "javascript", "sql", "function", "script",
            "programming", "debug", "syntax error", "refactor"
        ]):
            if any(word in prompt_lower for word in ["explain", "what does", "how does"]):
                return "Code_Explanation"
            return "Code_Generation"

        # Question indicators
        if prompt.strip().endswith("?"):
            if any(word in prompt_lower for word in ["opinion", "think", "feel"]):
                return "Opinion"
            if any(word in prompt_lower for word in ["what is", "who is", "when did", "where is", "why is"]):
                return "Question"
            if any(word in prompt_lower for word in ["how can i", "how do i", "advice", "tips", "help me"]):
                return "Advice"

        # Creative tasks
        if any(word in prompt_lower for word in [
            "write a story", "write a poem", "creative", "imagine", "story about"
        ]):
            return "Creative_Writing"

        # Summarization
        if any(word in prompt_lower for word in ["summarize", "summary", "tl;dr", "key points"]):
            return "Summarization"

        # Translation
        if any(word in prompt_lower for word in ["translate", "translation", "in spanish", "in french"]):
            return "Translation"

        # Math
        if any(word in prompt_lower for word in ["solve", "calculate", "derivative", "integral", "equation"]):
            return "Math_Problem"

        # Analysis
        if any(word in prompt_lower for word in ["analyze", "analysis", "trends", "patterns", "data"]):
            return "Data_Analysis"

        # Comparison
        if any(word in prompt_lower for word in ["compare", "vs", "versus", "difference between", "better"]):
            return "Comparison"

        # Explanation
        if any(word in prompt_lower for word in ["explain", "what is", "how does"]):
            return "Explanation"

        # Default to Instruction for imperative commands
        if prompt.strip().startswith(("write", "create", "generate", "make", "design", "build")):
            return "Instruction"

        # Default to general question
        return "Question"

    async def pipe(
        self,
        body: dict,
        __user__: dict,
        __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Process user messages with automatic classification and routing.

        Args:
            body: Request body containing messages
            __user__: User information dictionary
            __event_emitter__: Optional event emitter for status updates

        Returns:
            str: Response from the LLM
        """

        # Extract messages
        messages = body.get("messages", [])
        if not messages:
            return "No messages provided."

        # Get the last user message for classification
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            return "No user message found."

        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": "Classifying prompt...",
                    "done": False
                },
            })

        # Classify the prompt
        classification = self._classify_prompt(user_message)

        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": f"Classification: {classification}",
                    "done": True
                },
            })

        # Get configuration for this classification
        config = get_classification_config(classification)

        if not config:
            # Fallback to general configuration
            config = get_classification_config("Question")

        # Determine model to use
        model = self._get_model_for_llm_type(config.llm_model)

        # Determine settings
        if self.valves.use_optimized_settings:
            temperature = config.temperature
            max_tokens = config.max_tokens
        else:
            temperature = self.valves.default_temperature
            max_tokens = self.valves.default_max_tokens

        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "description": f"Using {config.llm_model.value} model (T={temperature})",
                    "done": False
                },
            })

        # Modify messages to include optimized system prompt
        # Remove any existing system message
        filtered_messages = [msg for msg in messages if msg.get("role") != "system"]

        # Add our optimized system prompt
        optimized_messages = [
            {"role": "system", "content": config.system_prompt}
        ] + filtered_messages

        # Create OpenAI client
        client = OpenAI(
            base_url=self.valves.llm_base_url,
            api_key=self.valves.llm_api_key
        )

        try:
            # Call LLM with optimized settings
            response = client.chat.completions.create(
                model=model,
                messages=optimized_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            result = response.choices[0].message.content

            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": "Response generated successfully",
                        "done": True
                    },
                })

            # Optionally show classification info
            if self.valves.show_classification:
                classification_info = (
                    f"\n\n---\n"
                    f"**Classification**: {classification}\n"
                    f"**Model Type**: {config.llm_model.value}\n"
                    f"**Model**: {model}\n"
                    f"**Temperature**: {temperature}\n"
                    f"**Description**: {config.description}"
                )
                result += classification_info

            return result

        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            print(error_msg)

            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"Error: {str(e)}",
                        "done": True
                    },
                })

            return f"❌ {error_msg}\n\nPlease check:\n" \
                   f"- LLM is running at {self.valves.llm_base_url}\n" \
                   f"- Model '{model}' is available\n" \
                   f"- Configuration in Valves is correct"


# Example usage and testing
if __name__ == "__main__":
    # This section shows how to use the classification system directly

    # Example 1: Get configuration for code generation
    print("=== Example 1: Code Generation Configuration ===")
    config = get_classification_config("Code_Generation")
    print(f"Model: {config.llm_model}")
    print(f"Temperature: {config.temperature}")
    print(f"System Prompt: {config.system_prompt[:100]}...")
    print()

    # Example 2: Classify and get full config
    print("=== Example 2: Full Classification ===")
    result = classify_and_get_config(
        user_input="Write a Python function to calculate factorial",
        classification="Code_Generation"
    )
    print(f"Classification: {result['classification']}")
    print(f"Formatted Prompt: {result['prompt'][:100]}...")
    print()

    # Example 3: List all classifications
    print("=== Example 3: All Classifications ===")
    all_classifications = get_all_classifications()
    print(f"Total: {len(all_classifications)} classifications")
    print(f"First 10: {', '.join(all_classifications[:10])}")
