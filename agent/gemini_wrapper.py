"""
LangChain-compatible wrapper for Google Gemini.
"""

import asyncio
import os
import re
from typing import Any, Dict, Iterator, List, Optional, Sequence, Union
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

import google.generativeai as genai


class GeminiChat(BaseChatModel):
    """LangChain-compatible wrapper for Google Gemini."""
    
    model_name: str = "gemini-1.5-flash"
    gemini_model: Any = None  # Will be set in __init__
    bound_tools: List[BaseTool] = []  # Store bound tools
    
    def __init__(self, model_name: str = "gemini-1.5-flash", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        
        # Configure Gemini with API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(self.model_name)
    
    @property
    def _llm_type(self) -> str:
        return "gemini"
    
    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, "BaseTool"]],
        **kwargs: Any,
    ) -> "GeminiChat":
        """Bind tools to the model. Returns a new instance with tools bound."""
        # Create a new instance with the same configuration
        new_instance = self.__class__(
            model_name=self.model_name,
            **kwargs
        )
        
        # Convert tools to BaseTool instances if needed
        bound_tools = []
        for tool in tools:
            if isinstance(tool, BaseTool):
                bound_tools.append(tool)
            else:
                # Handle other tool formats if needed
                bound_tools.append(tool)
        
        new_instance.bound_tools = bound_tools
        return new_instance
    
    def _parse_and_execute_tools(self, text: str) -> str:
        """Parse tool calls from text and execute them."""
        if not self.bound_tools:
            return text
        
        # Create tool map for easy lookup
        tool_map = {tool.name: tool for tool in self.bound_tools}
        
        # Pattern to match tool calls like: tool_name(param="value") or tool_name("value")
        tool_pattern = r'(\w+)\(([^)]*)\)'
        
        def execute_tool_call(match):
            tool_name = match.group(1)
            params_str = match.group(2).strip()
            
            if tool_name not in tool_map:
                return f"Tool '{tool_name}' not found"
            
            try:
                # Parse parameters
                params = {}
                if params_str:
                    # Handle different parameter formats:
                    # 1. key="value" format
                    param_matches = re.findall(r'(\w+)="([^"]*)"', params_str)
                    for key, value in param_matches:
                        params[key] = value
                    
                    # 2. Just quoted string (assume it's the first parameter)
                    if not params and params_str.startswith('"') and params_str.endswith('"'):
                        # Get the tool's expected parameter name by inspecting
                        tool = tool_map[tool_name]
                        if tool_name == "search_servers":
                            params["query"] = params_str.strip('"')
                        elif tool_name == "connect_server":
                            params["server_id"] = params_str.strip('"')
                    
                    # 3. Just a string without quotes (assume it's the first parameter)  
                    if not params and params_str and not '=' in params_str:
                        if tool_name == "search_servers":
                            params["query"] = params_str.strip('"')
                        elif tool_name == "connect_server":
                            params["server_id"] = params_str.strip('"')
                
                # Execute the tool (handle both sync and async)
                tool = tool_map[tool_name]
                
                # Check if we're in an async context and tool has _arun
                if hasattr(tool, '_arun'):
                    # We need to run the async version, but can't use asyncio.run() 
                    # from within an event loop. Let's use the sync version instead.
                    result = tool._run(**params)
                else:
                    result = tool._run(**params)
                
                return f"\n**Tool Result ({tool_name}):**\n{result}\n"
                
            except Exception as e:
                return f"\n**Tool Error ({tool_name}):**\n{str(e)}\n"
        
        # Replace tool calls with their results
        result_text = re.sub(tool_pattern, execute_tool_call, text)
        return result_text

    def _format_messages(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a text prompt for Gemini."""
        formatted_parts = []
        
        # Add tool usage instructions if tools are bound
        if self.bound_tools:
            tool_descriptions = [
                "You have access to these tools. To use a tool, write the tool name with parameters:",
                "- search_servers(query=\"your search term\")",
                "- connect_server(server_id=\"server_id_from_search\")",
                "- connect_to_playwright_server() for web browsing",
                "",
                "Available tools:"
            ]
            for tool in self.bound_tools:
                tool_descriptions.append(f"- {tool.name}: {tool.description}")
            tool_descriptions.append("")  # Empty line
            formatted_parts.extend(tool_descriptions)
        
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_parts.append(f"Assistant: {message.content}")
            elif isinstance(message, SystemMessage):
                formatted_parts.append(f"System: {message.content}")
            else:
                formatted_parts.append(f"User: {message.content}")
        
        return "\n\n".join(formatted_parts)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response using Gemini."""
        
        # Format messages for Gemini
        prompt = self._format_messages(messages)
        
        try:
            # Generate content using Gemini
            response = self.gemini_model.generate_content(prompt)
            
            # Extract text from response
            if response.text:
                # Parse and execute any tool calls in the response
                processed_text = self._parse_and_execute_tools(response.text)
                message = AIMessage(content=processed_text)
            else:
                message = AIMessage(content="")
            
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
            
        except Exception as e:
            # Handle any errors gracefully
            error_message = AIMessage(content=f"Error generating response: {str(e)}")
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async version of _generate (for now, just calls sync version)."""
        return self._generate(messages, stop, run_manager, **kwargs)
