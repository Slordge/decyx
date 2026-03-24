# config.py
# @runtime Jython

OLLAMA_API_URL = "http://192.168.56.1:11434/v1/chat/completions"
OLLAMA_MODELS = ["qwen3-coder:30b"]

# Set to True to enable fast selection and skip prompt confirmation windows
SKIP_PROMPT_CONFIRMATION = False

# Default window dimensions
DEFAULT_WINDOW_WIDTH = 750
DEFAULT_WINDOW_HEIGHT = 500

# Prompt Templates
PROMPTS = {
    "rename_retype": (
        u"Analyze the following decompiled C function code and its variables. Provide the following:\n"
        u"1. A suggested concise and descriptive name for the function.\n"
        u"2. Suggested new names and data types for each variable, including globals if applicable.\n\n"
        u"Respond with a JSON object containing only 'function_name' and 'variables' fields. The 'variables' field should be an array of objects, each containing 'old_name', 'new_name', and 'new_type'.\n\n"
        u"Do not include any explanations or additional text in the response.\n Only the required JSON object should be returned.\n\n"
    ),
    "explanation": (
        u"Provide a brief detailed explanation of the following decompiled C function code and its variables. "
        u"The explanation should be in-depth but concise, incorporating any meaningful names where applicable.\n\n"
        u"Respond with a plain text explanation, without any formatting.\n\n Do not include reasoning steps or the thought process, only the final explanation.\n\n"
        u"You are given the calling function for additional context, but only give your explanation for the provided function code and variables.\n\n"
    ),
    "line_comments": (
        u"Analyze the following decompiled C function code annotated with addresses. Provide concise, meaningful comments "
        u"**only** for important lines or sections of the code. Focus on explaining the purpose or significance of each "
        u"important operation.\n\n"
        u"Respond with a JSON object where each key is the address (as a string) and the value is the suggested "
        u"comment for that line. Only include addresses that need comments.\n\n"
        u"Example format:\n"
        u"{\n"
        u"  \"0x401000\": \"Initialize the device object\",\n"
        u"  \"0x401010\": \"Check OS version for compatibility\",\n"
        u"  \"0x401020\": \"Create symbolic link for the device\"\n"
        u"}\n\n Do not include any explanations or additional text in the response, only the required JSON object.\n\n"
    )
}

# Global variable patterns
GLOBAL_VARIABLE_PATTERNS = [
    r'\bDAT_[0-9a-fA-F]+\b', # Default Ghidra pattern
    r'\bg_\w+\b' # Most likely renamed by our script
]