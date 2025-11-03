"""
Classification System for Prompt Types

Maps user input classifications to optimal LLM configurations including:
- Recommended model type
- Master prompt template
- System prompt for the model

Usage:
    from lib.classification import ClassificationConfig, get_classification_config

    config = get_classification_config("Code_Generation")
    print(config.llm_model)
    print(config.system_prompt)
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from enum import Enum


class LLMModel(str, Enum):
    """Recommended LLM models for different task types."""

    # General purpose models
    GENERAL = "general"  # Standard chat model (GPT-4, Claude 3.5 Sonnet, etc.)
    FAST = "fast"  # Faster model for simple tasks (GPT-3.5, Claude Haiku, etc.)

    # Specialized models
    CODE = "code"  # Code-specialized (GPT-4, Claude 3.5 Sonnet, Codex, etc.)
    REASONING = "reasoning"  # Strong reasoning (GPT-4, Claude 3 Opus, o1, etc.)
    CREATIVE = "creative"  # Creative writing (GPT-4, Claude 3.5 Sonnet, etc.)
    MATH = "math"  # Mathematical reasoning (GPT-4, Claude, specialized math models)
    ANALYSIS = "analysis"  # Data analysis (GPT-4, Claude 3.5 Sonnet, etc.)

    # Specific use cases
    EMBEDDING = "embedding"  # For classification/sentiment (smaller models)
    CHAT = "chat"  # Conversational (optimized for dialogue)


class ClassificationType(str, Enum):
    """All supported classification types."""

    QUESTION = "Question"
    INSTRUCTION = "Instruction"
    SUMMARIZATION = "Summarization"
    TRANSLATION = "Translation"
    CODE_GENERATION = "Code_Generation"
    CODE_EXPLANATION = "Code_Explanation"
    CREATIVE_WRITING = "Creative_Writing"
    MATH_PROBLEM = "Math_Problem"
    REASONING = "Reasoning"
    DATA_ANALYSIS = "Data_Analysis"
    CHAT_SOCIAL = "Chat_Social"
    OPINION = "Opinion"
    ADVICE = "Advice"
    CLARIFICATION_REQUEST = "Clarification_Request"
    SELF_REFERENCE = "Self_Reference"
    JOKE_HUMOR = "Joke_Humor"
    SUMMARIZE_EMAIL = "Summarize_Email"
    EXTRACT_ENTITIES = "Extract_Entities"
    REWRITE_PARAPHRASE = "Rewrite_Paraphrase"
    FORMAT_CONVERSION = "Format_Conversion"
    ROLEPLAY = "Roleplay"
    SENTIMENT_ANALYSIS = "Sentiment_Analysis"
    CLASSIFICATION = "Classification"
    COMPARISON = "Comparison"
    EXPLANATION = "Explanation"
    LEGAL_QUERY = "Legal_Query"
    MEDICAL_QUERY = "Medical_Query"
    FINANCIAL_ADVICE = "Financial_Advice"
    TECHNICAL_SUPPORT = "Technical_Support"
    ACADEMIC_HELP = "Academic_Help"
    CAREER_COUNSELING = "Career_Counseling"


class ClassificationConfig(BaseModel):
    """Configuration for a specific classification type."""

    classification: ClassificationType = Field(
        description="The classification type"
    )
    description: str = Field(
        description="Description of this classification"
    )
    llm_model: LLMModel = Field(
        description="Recommended LLM model type for this classification"
    )
    master_prompt: str = Field(
        description="Master prompt template for handling this type of request"
    )
    system_prompt: str = Field(
        description="System prompt to guide the model's behavior"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Recommended temperature setting"
    )
    max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Recommended max tokens for response"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Example inputs for this classification"
    )


# Classification configurations mapped to each type
CLASSIFICATION_CONFIGS: Dict[ClassificationType, ClassificationConfig] = {

    ClassificationType.QUESTION: ClassificationConfig(
        classification=ClassificationType.QUESTION,
        description="A general factual or informational query",
        llm_model=LLMModel.GENERAL,
        master_prompt="Answer the following question accurately and concisely:\n\n{input}",
        system_prompt="You are a knowledgeable assistant that provides accurate, factual answers to questions. Be concise but thorough. Cite sources when possible.",
        temperature=0.3,
        max_tokens=1000,
        examples=[
            "What is the capital of France?",
            "Who invented the telephone?",
            "When did World War II end?",
            "Why is the sky blue?"
        ]
    ),

    ClassificationType.INSTRUCTION: ClassificationConfig(
        classification=ClassificationType.INSTRUCTION,
        description="A request to perform a task or generate content",
        llm_model=LLMModel.GENERAL,
        master_prompt="Complete the following task:\n\n{input}",
        system_prompt="You are a helpful assistant that follows instructions carefully. Execute tasks step-by-step and provide clear, actionable output.",
        temperature=0.7,
        max_tokens=2000,
        examples=[
            "Write a poem about the ocean.",
            "Create a daily workout plan for beginners.",
            "Design a logo for a coffee shop.",
            "Generate interview questions for a data analyst role."
        ]
    ),

    ClassificationType.SUMMARIZATION: ClassificationConfig(
        classification=ClassificationType.SUMMARIZATION,
        description="Asks for a summary or concise version of text",
        llm_model=LLMModel.FAST,
        master_prompt="Summarize the following text concisely:\n\n{input}",
        system_prompt="You are an expert at extracting key information and creating concise summaries. Focus on main points and important details. Use bullet points when appropriate.",
        temperature=0.3,
        max_tokens=500,
        examples=[
            "Summarize this article in two sentences.",
            "Give me a TL;DR of this Reddit post.",
            "Summarize this meeting transcript in bullet points."
        ]
    ),

    ClassificationType.TRANSLATION: ClassificationConfig(
        classification=ClassificationType.TRANSLATION,
        description="Requests conversion between languages",
        llm_model=LLMModel.GENERAL,
        master_prompt="Translate the following:\n\n{input}",
        system_prompt="You are a professional translator. Provide accurate translations that preserve meaning, tone, and cultural context. When relevant, note any nuances or alternative translations.",
        temperature=0.3,
        max_tokens=1000,
        examples=[
            "Translate this to Spanish: Hello, how are you?",
            "Translate this sentence to Mandarin Chinese.",
            "Convert this formal text into casual tone."
        ]
    ),

    ClassificationType.CODE_GENERATION: ClassificationConfig(
        classification=ClassificationType.CODE_GENERATION,
        description="Requests programming output or code snippets",
        llm_model=LLMModel.CODE,
        master_prompt="Generate code for the following request:\n\n{input}\n\nProvide clean, well-commented code with explanations.",
        system_prompt="You are an expert programmer. Write clean, efficient, well-documented code. Include comments explaining key logic. Follow best practices and common conventions for the language being used.",
        temperature=0.2,
        max_tokens=3000,
        examples=[
            "Write a Python script to scrape a webpage.",
            "Write a SQL query to find all customers from California.",
            "Create a REST API endpoint in Express.js."
        ]
    ),

    ClassificationType.CODE_EXPLANATION: ClassificationConfig(
        classification=ClassificationType.CODE_EXPLANATION,
        description="Asks to explain or debug a piece of code",
        llm_model=LLMModel.CODE,
        master_prompt="Explain or debug the following code:\n\n{input}",
        system_prompt="You are a code reviewer and educator. Explain code clearly, point out issues, suggest improvements, and teach best practices. Break down complex logic into understandable parts.",
        temperature=0.3,
        max_tokens=2000,
        examples=[
            "Explain what this function does.",
            "Fix the syntax error in this Python code.",
            "Explain how recursion works in simple terms.",
            "Refactor this JavaScript for better readability."
        ]
    ),

    ClassificationType.CREATIVE_WRITING: ClassificationConfig(
        classification=ClassificationType.CREATIVE_WRITING,
        description="Prompts for imaginative or artistic writing",
        llm_model=LLMModel.CREATIVE,
        master_prompt="Create the following creative content:\n\n{input}",
        system_prompt="You are a creative writer with a vivid imagination. Craft engaging, original content with strong narrative voice. Use descriptive language and compelling storytelling techniques.",
        temperature=0.9,
        max_tokens=3000,
        examples=[
            "Write a sci-fi short story set on Mars.",
            "Generate a scary short story with a twist ending.",
            "Write a limerick about AI taking over the world.",
            "Generate a tagline for an eco-friendly startup."
        ]
    ),

    ClassificationType.MATH_PROBLEM: ClassificationConfig(
        classification=ClassificationType.MATH_PROBLEM,
        description="Mathematical computation or reasoning",
        llm_model=LLMModel.MATH,
        master_prompt="Solve the following mathematical problem step-by-step:\n\n{input}",
        system_prompt="You are a mathematics expert. Show your work step-by-step, explain your reasoning, and verify your answer. Use clear mathematical notation.",
        temperature=0.1,
        max_tokens=1500,
        examples=[
            "Solve 2x² + 5x − 3 = 0.",
            "What is the derivative of x² + 3x?",
            "Calculate the area of a circle with radius 5."
        ]
    ),

    ClassificationType.REASONING: ClassificationConfig(
        classification=ClassificationType.REASONING,
        description="Logic or chain-of-thought type reasoning requests",
        llm_model=LLMModel.REASONING,
        master_prompt="Use logical reasoning to analyze:\n\n{input}\n\nThink step-by-step and explain your reasoning.",
        system_prompt="You are a logical reasoning expert. Break down complex problems into steps, identify patterns, and draw valid conclusions. Show your reasoning process clearly.",
        temperature=0.3,
        max_tokens=2000,
        examples=[
            "If all A are B and some B are C, what can we infer?",
            "If 5 people can paint a wall in 2 hours, how long for 10 people?"
        ]
    ),

    ClassificationType.DATA_ANALYSIS: ClassificationConfig(
        classification=ClassificationType.DATA_ANALYSIS,
        description="Analytical or statistical computation",
        llm_model=LLMModel.ANALYSIS,
        master_prompt="Analyze the following data:\n\n{input}\n\nProvide insights, patterns, and actionable recommendations.",
        system_prompt="You are a data analyst. Examine data critically, identify trends and patterns, perform statistical analysis, and provide clear insights with supporting evidence.",
        temperature=0.3,
        max_tokens=2500,
        examples=[
            "Analyze this CSV for trends in revenue.",
            "Identify outliers in this dataset.",
            "What patterns can you find in this sales data?"
        ]
    ),

    ClassificationType.CHAT_SOCIAL: ClassificationConfig(
        classification=ClassificationType.CHAT_SOCIAL,
        description="Conversational, small-talk, or social chat",
        llm_model=LLMModel.CHAT,
        master_prompt="{input}",
        system_prompt="You are a friendly, engaging conversational partner. Be warm, personable, and natural. Match the user's tone and energy. Keep responses concise for casual chat.",
        temperature=0.8,
        max_tokens=500,
        examples=[
            "How's your day going?",
            "Good morning! How are you today?",
            "What's your favorite movie?"
        ]
    ),

    ClassificationType.OPINION: ClassificationConfig(
        classification=ClassificationType.OPINION,
        description="Seeks a subjective perspective",
        llm_model=LLMModel.GENERAL,
        master_prompt="Provide a balanced perspective on:\n\n{input}",
        system_prompt="You are a thoughtful analyst who presents multiple perspectives. Acknowledge the complexity of subjective topics. Present different viewpoints fairly while being clear about limitations in having personal opinions as an AI.",
        temperature=0.7,
        max_tokens=1500,
        examples=[
            "What's your opinion on AI ethics?",
            "What do you think about remote work?"
        ]
    ),

    ClassificationType.ADVICE: ClassificationConfig(
        classification=ClassificationType.ADVICE,
        description="Seeks guidance, recommendations, or suggestions",
        llm_model=LLMModel.GENERAL,
        master_prompt="Provide helpful advice for:\n\n{input}",
        system_prompt="You are a helpful advisor. Provide practical, actionable advice. Consider multiple approaches and their trade-offs. Be supportive but realistic. Encourage seeking professional help for serious issues.",
        temperature=0.6,
        max_tokens=1500,
        examples=[
            "How can I get better at public speaking?",
            "How do I overcome procrastination?",
            "I feel anxious before interviews. Any tips?"
        ]
    ),

    ClassificationType.CLARIFICATION_REQUEST: ClassificationConfig(
        classification=ClassificationType.CLARIFICATION_REQUEST,
        description="Asks about how the model works or to clarify its behavior",
        llm_model=LLMModel.GENERAL,
        master_prompt="Clarify the following about the AI system:\n\n{input}",
        system_prompt="You are transparent about AI capabilities and limitations. Clearly explain how you work, what you can and cannot do, and any relevant constraints. Be accurate and honest.",
        temperature=0.3,
        max_tokens=800,
        examples=[
            "What kind of data are you trained on?",
            "What model are you based on?",
            "Can you access the internet?"
        ]
    ),

    ClassificationType.SELF_REFERENCE: ClassificationConfig(
        classification=ClassificationType.SELF_REFERENCE,
        description="Prompts about the model itself or its identity",
        llm_model=LLMModel.GENERAL,
        master_prompt="{input}",
        system_prompt="You are self-aware as an AI assistant. Answer questions about yourself honestly and clearly. Explain your nature, capabilities, and limitations without pretending to be human.",
        temperature=0.3,
        max_tokens=600,
        examples=[
            "Who are you?",
            "Do you like working with humans?",
            "Who created you?"
        ]
    ),

    ClassificationType.JOKE_HUMOR: ClassificationConfig(
        classification=ClassificationType.JOKE_HUMOR,
        description="Requests or shares humor",
        llm_model=LLMModel.CREATIVE,
        master_prompt="Create humor for:\n\n{input}",
        system_prompt="You are a witty, humorous assistant. Generate clever, appropriate jokes. Use wordplay, timing, and context. Keep humor light and inclusive.",
        temperature=0.9,
        max_tokens=500,
        examples=[
            "Tell me a funny joke about computers.",
            "Tell a dad joke about engineers."
        ]
    ),

    ClassificationType.SUMMARIZE_EMAIL: ClassificationConfig(
        classification=ClassificationType.SUMMARIZE_EMAIL,
        description="Summarize an email or message thread",
        llm_model=LLMModel.FAST,
        master_prompt="Summarize the following email for key points:\n\n{input}",
        system_prompt="You are an executive assistant. Extract key action items, important information, and critical dates from emails. Use bullet points for clarity. Prioritize actionable information.",
        temperature=0.2,
        max_tokens=500,
        examples=[
            "Summarize this email for key points.",
            "Summarize this PDF report for the executive team."
        ]
    ),

    ClassificationType.EXTRACT_ENTITIES: ClassificationConfig(
        classification=ClassificationType.EXTRACT_ENTITIES,
        description="Pull specific entities like names or dates from text",
        llm_model=LLMModel.EMBEDDING,
        master_prompt="Extract entities from the following text:\n\n{input}",
        system_prompt="You are an information extraction specialist. Identify and extract specific entities (names, dates, locations, organizations, etc.) accurately. Format results clearly.",
        temperature=0.1,
        max_tokens=800,
        examples=[
            "Extract all company names from this paragraph.",
            "Extract all phone numbers from this document."
        ]
    ),

    ClassificationType.REWRITE_PARAPHRASE: ClassificationConfig(
        classification=ClassificationType.REWRITE_PARAPHRASE,
        description="Reformulate text while preserving meaning",
        llm_model=LLMModel.GENERAL,
        master_prompt="Rewrite the following text:\n\n{input}",
        system_prompt="You are a skilled editor. Rewrite text while preserving original meaning. Adjust tone, style, or complexity as requested. Maintain factual accuracy.",
        temperature=0.5,
        max_tokens=1500,
        examples=[
            "Rewrite this paragraph in simpler language.",
            "Convert this formal text into casual tone."
        ]
    ),

    ClassificationType.FORMAT_CONVERSION: ClassificationConfig(
        classification=ClassificationType.FORMAT_CONVERSION,
        description="Change structure or format of content",
        llm_model=LLMModel.CODE,
        master_prompt="Convert the format:\n\n{input}",
        system_prompt="You are a data transformation specialist. Convert content between formats accurately. Preserve all information and maintain proper syntax for the target format.",
        temperature=0.1,
        max_tokens=2000,
        examples=[
            "Convert this list into a JSON array.",
            "Convert this markdown into HTML format."
        ]
    ),

    ClassificationType.ROLEPLAY: ClassificationConfig(
        classification=ClassificationType.ROLEPLAY,
        description="Model should assume a persona or role",
        llm_model=LLMModel.CREATIVE,
        master_prompt="Assume the requested role and respond:\n\n{input}",
        system_prompt="You are a versatile actor who can assume different personas convincingly. Stay in character, use appropriate language and knowledge for the role, and provide helpful responses from that perspective.",
        temperature=0.8,
        max_tokens=2000,
        examples=[
            "Act as a travel agent planning my trip.",
            "Pretend to be a chef and suggest a dinner recipe.",
            "Act as my mentor for public speaking.",
            "Act as a travel planner for a trip to Japan."
        ]
    ),

    ClassificationType.SENTIMENT_ANALYSIS: ClassificationConfig(
        classification=ClassificationType.SENTIMENT_ANALYSIS,
        description="Determine tone or emotional sentiment",
        llm_model=LLMModel.EMBEDDING,
        master_prompt="Analyze the sentiment of:\n\n{input}",
        system_prompt="You are a sentiment analysis expert. Identify emotional tone, positivity/negativity, and intensity. Provide clear labels (positive, negative, neutral, mixed) with confidence levels and supporting evidence.",
        temperature=0.1,
        max_tokens=500,
        examples=[
            "Is this review positive or negative?",
            "Is this review positive or negative: 'I loved the service!'",
            "Determine the tone of this tweet."
        ]
    ),

    ClassificationType.CLASSIFICATION: ClassificationConfig(
        classification=ClassificationType.CLASSIFICATION,
        description="Label content or text according to rules",
        llm_model=LLMModel.EMBEDDING,
        master_prompt="Classify the following:\n\n{input}",
        system_prompt="You are a classification specialist. Analyze input and assign appropriate categories based on defined criteria. Explain your reasoning and confidence level.",
        temperature=0.1,
        max_tokens=500,
        examples=[
            "Classify this tweet as spam or not spam.",
            "Classify these emails as spam or not.",
            "Is this email phishing? 'Click here to verify your account.'"
        ]
    ),

    ClassificationType.COMPARISON: ClassificationConfig(
        classification=ClassificationType.COMPARISON,
        description="Compare two or more things",
        llm_model=LLMModel.ANALYSIS,
        master_prompt="Compare the following:\n\n{input}",
        system_prompt="You are a comparison analyst. Evaluate items across multiple dimensions. Present pros/cons, similarities/differences clearly. Support comparisons with specific evidence. Be balanced and objective.",
        temperature=0.3,
        max_tokens=2000,
        examples=[
            "Compare the performance of GPT-4 and Llama-3.",
            "Compare the speed of GPT-4 and Claude 3.",
            "Which is better for graphics, Nvidia or AMD?"
        ]
    ),

    ClassificationType.EXPLANATION: ClassificationConfig(
        classification=ClassificationType.EXPLANATION,
        description="Explains a concept or process",
        llm_model=LLMModel.GENERAL,
        master_prompt="Explain the following:\n\n{input}",
        system_prompt="You are an expert educator. Explain concepts clearly using analogies, examples, and structured breakdowns. Adjust complexity to the audience. Use diagrams or step-by-step descriptions when helpful.",
        temperature=0.4,
        max_tokens=2000,
        examples=[
            "Explain quantum computing in simple terms.",
            "Explain blockchain like I'm five.",
            "List key steps in building a REST API."
        ]
    ),

    ClassificationType.LEGAL_QUERY: ClassificationConfig(
        classification=ClassificationType.LEGAL_QUERY,
        description="Legal questions or policy interpretation",
        llm_model=LLMModel.REASONING,
        master_prompt="Address the following legal query:\n\n{input}",
        system_prompt="You provide general legal information (not legal advice). Explain legal concepts clearly, note jurisdictional variations, and always recommend consulting a qualified attorney for specific legal matters.",
        temperature=0.2,
        max_tokens=2000,
        examples=[
            "What's the difference between a will and a trust?",
            "Explain GDPR compliance for businesses."
        ]
    ),

    ClassificationType.MEDICAL_QUERY: ClassificationConfig(
        classification=ClassificationType.MEDICAL_QUERY,
        description="Health or medical information",
        llm_model=LLMModel.REASONING,
        master_prompt="Provide medical information for:\n\n{input}",
        system_prompt="You provide general medical information (not medical advice). Share factual health information, but always emphasize the importance of consulting healthcare professionals for diagnosis or treatment. Be cautious and responsible.",
        temperature=0.2,
        max_tokens=1500,
        examples=[
            "What are common symptoms of vitamin D deficiency?",
            "Is it safe to combine ibuprofen and acetaminophen?"
        ]
    ),

    ClassificationType.FINANCIAL_ADVICE: ClassificationConfig(
        classification=ClassificationType.FINANCIAL_ADVICE,
        description="Money management or investing questions",
        llm_model=LLMModel.REASONING,
        master_prompt="Provide financial information for:\n\n{input}",
        system_prompt="You provide general financial information (not personalized financial advice). Explain financial concepts, common strategies, and considerations. Always recommend consulting a qualified financial advisor for specific investment decisions.",
        temperature=0.3,
        max_tokens=2000,
        examples=[
            "How can I start saving for retirement?",
            "How should I diversify my investment portfolio?"
        ]
    ),

    ClassificationType.TECHNICAL_SUPPORT: ClassificationConfig(
        classification=ClassificationType.TECHNICAL_SUPPORT,
        description="Troubleshooting or tech-help questions",
        llm_model=LLMModel.CODE,
        master_prompt="Provide technical support for:\n\n{input}",
        system_prompt="You are a technical support specialist. Diagnose issues systematically, provide step-by-step troubleshooting, and explain technical concepts clearly. Ask clarifying questions when needed.",
        temperature=0.3,
        max_tokens=2000,
        examples=[
            "My Wi-Fi keeps disconnecting — what can I do?",
            "How can I fix a blue screen error on Windows?"
        ]
    ),

    ClassificationType.ACADEMIC_HELP: ClassificationConfig(
        classification=ClassificationType.ACADEMIC_HELP,
        description="Homework, essay, or research assistance",
        llm_model=LLMModel.GENERAL,
        master_prompt="Provide academic assistance for:\n\n{input}",
        system_prompt="You are an educational tutor. Help students learn by guiding them through problems, explaining concepts, and encouraging critical thinking. Don't just give answers—help them understand the process.",
        temperature=0.4,
        max_tokens=2000,
        examples=[
            "Explain photosynthesis for a high-school project.",
            "Describe the water cycle for a science project."
        ]
    ),

    ClassificationType.CAREER_COUNSELING: ClassificationConfig(
        classification=ClassificationType.CAREER_COUNSELING,
        description="Career planning and job advice",
        llm_model=LLMModel.GENERAL,
        master_prompt="Provide career guidance for:\n\n{input}",
        system_prompt="You are a career counselor. Provide practical career advice, industry insights, and skill development recommendations. Be encouraging while realistic. Consider current market trends.",
        temperature=0.5,
        max_tokens=1500,
        examples=[
            "What skills do I need to become a data scientist?"
        ]
    ),
}


def get_classification_config(classification: str) -> Optional[ClassificationConfig]:
    """
    Get the configuration for a specific classification type.

    Args:
        classification: The classification type (string)

    Returns:
        ClassificationConfig if found, None otherwise

    Example:
        >>> config = get_classification_config("Code_Generation")
        >>> print(config.llm_model)
        LLMModel.CODE
    """
    try:
        classification_type = ClassificationType(classification)
        return CLASSIFICATION_CONFIGS.get(classification_type)
    except ValueError:
        return None


def get_all_classifications() -> List[str]:
    """
    Get a list of all supported classification types.

    Returns:
        List of classification type names
    """
    return [c.value for c in ClassificationType]


def classify_and_get_config(user_input: str, classification: str) -> dict:
    """
    Get the full configuration for processing a user input.

    Args:
        user_input: The user's input text
        classification: The classified type

    Returns:
        Dictionary with configuration and formatted prompt

    Example:
        >>> result = classify_and_get_config(
        ...     "Write a Python function to sort a list",
        ...     "Code_Generation"
        ... )
        >>> print(result["system_prompt"])
        >>> print(result["prompt"])
    """
    config = get_classification_config(classification)

    if not config:
        return {
            "error": f"Unknown classification: {classification}",
            "available_classifications": get_all_classifications()
        }

    return {
        "classification": config.classification,
        "description": config.description,
        "llm_model": config.llm_model,
        "system_prompt": config.system_prompt,
        "prompt": config.master_prompt.format(input=user_input),
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "examples": config.examples
    }


# Mapping of classifications to their descriptions (from CSV)
CLASSIFICATION_DESCRIPTIONS: Dict[str, str] = {
    "Question": "A general factual or informational query.",
    "Instruction": "A request to perform a task or generate content.",
    "Summarization": "Asks for a summary or concise version of text.",
    "Translation": "Requests conversion between languages.",
    "Code_Generation": "Requests programming output or code snippets.",
    "Code_Explanation": "Asks to explain or debug a piece of code.",
    "Creative_Writing": "Prompts for imaginative or artistic writing.",
    "Math_Problem": "Mathematical computation or reasoning.",
    "Reasoning": "Logic or chain-of-thought type reasoning requests.",
    "Data_Analysis": "Analytical or statistical computation.",
    "Chat_Social": "Conversational, small-talk, or social chat.",
    "Opinion": "Seeks a subjective perspective.",
    "Advice": "Seeks guidance, recommendations, or suggestions.",
    "Clarification_Request": "Asks about how the model works or to clarify its behavior.",
    "Self_Reference": "Prompts about the model itself or its identity.",
    "Joke_Humor": "Requests or shares humor.",
    "Summarize_Email": "Summarize an email or message thread.",
    "Extract_Entities": "Pull specific entities like names or dates from text.",
    "Rewrite_Paraphrase": "Reformulate text while preserving meaning.",
    "Format_Conversion": "Change structure or format of content.",
    "Roleplay": "Model should assume a persona or role.",
    "Sentiment_Analysis": "Determine tone or emotional sentiment.",
    "Classification": "Label content or text according to rules.",
    "Comparison": "Compare two or more things.",
    "Explanation": "Explains a concept or process.",
    "Legal_Query": "Legal questions or policy interpretation.",
    "Medical_Query": "Health or medical information.",
    "Financial_Advice": "Money management or investing questions.",
    "Technical_Support": "Troubleshooting or tech-help questions.",
    "Academic_Help": "Homework, essay, or research assistance.",
    "Career_Counseling": "Career planning and job advice.",
}
