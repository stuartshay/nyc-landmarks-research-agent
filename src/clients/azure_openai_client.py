"""
Client for interacting with Azure OpenAI Service.
Provides text generation capabilities using GPT models.
"""

import logging
from typing import Dict, List, Optional

import openai
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import settings

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI Service."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
        use_azure_identity: bool = False,
    ):
        """
        Initialize the Azure OpenAI client.

        Args:
            api_key: Azure OpenAI API key. If not provided, uses the key from settings.
            endpoint: Azure OpenAI URL. If not provided, uses URL from settings.
            deployment: Deployment name/model to use. If not provided, uses
                the deployment from settings.
            use_azure_identity: Whether to use Azure Identity for authentication
                instead of API key.
        """
        self.endpoint = endpoint or str(settings.AZURE_OPENAI_ENDPOINT)
        self.deployment = deployment or settings.AZURE_OPENAI_DEPLOYMENT

        if use_azure_identity:
            # Use Azure Identity (Managed Identity or other credential types)
            logger.info("Using Azure Identity for authentication")
            azure_credential = DefaultAzureCredential()

            # Create a token provider function
            def token_provider() -> str:
                token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
                return str(token.token)

            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token_provider=token_provider,
                api_version="2023-05-15",
            )
        else:
            # Use API key authentication
            api_key = api_key or settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("API key is required for Azure OpenAI client")

            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=api_key,
                api_version="2023-05-15",
            )

        logger.info(f"Initialized Azure OpenAI client with deployment: " f"{self.deployment}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
        reraise=True,
    )
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop: Optional[List[str]] = None,
    ) -> str:
        """
        Generate text using the Azure OpenAI service.

        Args:
            prompt: The prompt to generate text from
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter (0.0-1.0)
            stop: Optional list of strings that will stop generation if encountered

        Returns:
            Generated text as a string

        Raises:
            openai.APIError: If the API request fails
            ValueError: For invalid parameters
        """
        try:
            # Add system message if provided
            # Create properly typed message list for OpenAI API
            messages: List[Dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add user message
            messages.append({"role": "user", "content": prompt})

            logger.debug(f"Generating text with prompt length: {len(prompt)}")

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                stream=False,
            )  # Extract the generated text
            if hasattr(response, "choices") and response.choices and len(response.choices) > 0:
                generated_text: str = ""
                if hasattr(response.choices[0], "message") and response.choices[0].message:
                    if hasattr(response.choices[0].message, "content"):
                        content = response.choices[0].message.content
                        generated_text = str(content) if content is not None else ""

                logger.debug(f"Generated text of length: {len(generated_text)}")
                return generated_text

            return ""

        except openai.APIError as e:
            logger.error(f"Azure OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in text generation: {str(e)}")
            raise ValueError(f"Error generating text: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError)),
        reraise=True,
    )
    async def generate_research_report(
        self,
        query: str,
        context: str,
        system_instructions: str,
        max_tokens: int = 2000,
        temperature: float = 0.5,
    ) -> str:
        """
        Generate a research report about a landmark.

        Args:
            query: The research query
            context: Context information for the report
            system_instructions: System instructions for the model
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation

        Returns:
            Generated research report
        """
        try:
            # Split long text for readability
            intro_text = "You are an expert on NYC landmarks and architecture,"
            task_text = "tasked with creating a detailed research report"
            query_intro = f'based on the following query: "{query}"'
            prompt_template = f"""
{intro_text}
{task_text}
{query_intro}

{system_instructions}

CONTEXT INFORMATION:
{context}

USER QUERY: {query}

Your response should be a well-structured, educational research report that:
1. Directly addresses the query with accurate information
2. Synthesizes information from multiple sources
3. Highlights architectural, historical, and cultural significance
4. Cites relevant passages when appropriate
5. Is formatted in clear paragraphs with appropriate headings
6. Uses a professional, educational tone suitable for a heritage organization

Respond with a comprehensive research report formatted in markdown.
"""

            result = await self.generate_text(prompt=prompt_template, max_tokens=max_tokens, temperature=temperature)
            return str(result)

        except Exception as e:
            logger.error(f"Error generating research report: {str(e)}")
            # Return empty string to match the function's return type
            return ""
