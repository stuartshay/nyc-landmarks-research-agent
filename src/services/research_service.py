"""
Research service for the NYC Landmarks Research Agent.
Provides methods for generating research reports about NYC landmarks.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.clients.azure_openai_client import AzureOpenAIClient
from src.clients.landmark_metadata_client import LandmarkMetadataClient
from src.clients.vectorstore_client import VectorStoreClient
from src.models.api_models import LandmarkImage, ResearchResponse, SourceDocument
from src.models.research_models import (
    CONVERSATION_PROMPT_TEMPLATE,
    RESEARCH_PROMPT_TEMPLATE,
    ResearchContext,
    SourcePassage,
)
from src.services.landmark_service import LandmarkService
from src.services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class ResearchService:
    """Service for generating research reports about NYC landmarks."""

    def __init__(
        self,
        vector_client: Optional[VectorStoreClient] = None,
        landmark_client: Optional[LandmarkMetadataClient] = None,
        memory_service: Optional[MemoryService] = None,
        openai_client: Optional[AzureOpenAIClient] = None,
    ):
        """
        Initialize the research service.

        Args:
            vector_client: Optional VectorStoreClient instance to use
            landmark_client: Optional LandmarkMetadataClient instance to use
            memory_service: Optional MemoryService instance to use
            openai_client: Optional AzureOpenAIClient instance to use
        """
        self.vector_client = vector_client or VectorStoreClient()
        self.landmark_client = landmark_client or LandmarkMetadataClient()
        self.memory_service = memory_service or MemoryService()
        self.openai_client = openai_client or AzureOpenAIClient()
        self.landmark_service = LandmarkService(landmark_client=self.landmark_client)
        logger.info("Research service initialized")

    async def _initialize_conversation(self, conversation_id: Optional[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Initialize or retrieve an existing conversation.

        Args:
            conversation_id: Optional existing conversation ID

        Returns:
            Tuple of (conversation_id, conversation_history)
        """
        if not conversation_id:
            conversation_id = await self.memory_service.create_conversation()
            logger.debug(f"Created new conversation with ID {conversation_id}")
            conversation_history = []
        else:
            logger.debug(f"Using existing conversation with ID {conversation_id}")
            conversation_history = await self.memory_service.get_conversation_history(conversation_id)

        return conversation_id, conversation_history

    async def _process_landmarks(
        self, landmark_id: Optional[str], landmark_names: List[str], landmark_ids: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Process landmarks and ensure the specified landmark is included.

        Args:
            landmark_id: Optional specific landmark ID
            landmark_names: Current list of landmark names
            landmark_ids: Current list of landmark IDs

        Returns:
            Updated tuple of (landmark_names, landmark_ids)
        """
        if landmark_id and landmark_id not in landmark_ids:
            landmark_ids.append(landmark_id)

            # Try to get the landmark name if possible
            landmark_detail = await self.landmark_service.get_landmark_details(landmark_id)
            if landmark_detail:
                landmark_name = landmark_detail.name
                if landmark_name not in landmark_names:
                    landmark_names.append(landmark_name)

        return landmark_names, landmark_ids

    async def _get_primary_landmark_name(self, landmark_id: Optional[str]) -> Optional[str]:
        """
        Get the name of the primary landmark.

        Args:
            landmark_id: The ID of the primary landmark

        Returns:
            The name of the primary landmark or None
        """
        primary_landmark_name = None
        if landmark_id:
            landmark_detail = await self.landmark_service.get_landmark_details(landmark_id)
            if landmark_detail:
                primary_landmark_name = landmark_detail.name

        return primary_landmark_name

    async def _get_related_landmarks(
        self, landmark_ids: List[str], primary_landmark_id: Optional[str]
    ) -> List[Dict[str, str]]:
        """
        Get details for related landmarks.

        Args:
            landmark_ids: List of landmark IDs
            primary_landmark_id: ID of the primary landmark to exclude

        Returns:
            List of related landmark dictionaries with id and name
        """
        related_landmarks = []
        for lid in landmark_ids[:5]:  # Limit to 5 related landmarks
            if lid != primary_landmark_id:  # Don't include the primary landmark
                ld = await self.landmark_service.get_landmark_details(lid)
                if ld:
                    related_landmarks.append({"id": lid, "name": ld.name})

        return related_landmarks

    async def _create_and_save_response(
        self,
        conversation_id: str,
        query: str,
        generated_text: str,
        images: List[LandmarkImage],
        sources: List[SourceDocument],
        landmark_id: Optional[str],
        primary_landmark_name: Optional[str],
        related_landmarks: List[Dict[str, str]],
        suggested_queries: List[str],
        landmark_ids: List[str],
        landmark_names: List[str],
    ) -> ResearchResponse:
        """
        Create the response object and save it to memory.

        Args:
            Multiple parameters for constructing the response

        Returns:
            The complete ResearchResponse object
        """
        # Create the response object
        response = ResearchResponse(
            conversation_id=conversation_id,
            query=query,
            report=generated_text,
            images=images,
            sources=sources,
            landmark_id=landmark_id,
            landmark_name=primary_landmark_name,
            related_landmarks=related_landmarks,
            suggested_queries=suggested_queries,
        )

        # Save to memory
        await self.memory_service.add_entry(
            conversation_id=conversation_id,
            query=query,
            response=generated_text,
            landmark_ids=landmark_ids,
            landmark_names=landmark_names,
            sources_used=[s.dict() for s in sources],
        )

        return response

    async def generate_report(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        landmark_id: Optional[str] = None,
        max_sources: int = 5,
        include_images: bool = True,
    ) -> ResearchResponse:
        """
        Generate a research report about NYC landmarks based on the query.

        Args:
            query: The research query
            conversation_id: Optional conversation ID for context
            landmark_id: Optional specific landmark ID to focus on
            max_sources: Maximum number of sources to include
            include_images: Whether to include images in the response

        Returns:
            ResearchResponse with the generated report
        """
        start_time = datetime.now()
        logger.info(f"Generating research report for query: {query}")

        # Create conversation or use existing one
        conversation_id, conversation_history = await self._initialize_conversation(conversation_id)

        try:
            # Build research context
            context = await self._build_research_context(
                query=query,
                conversation_id=conversation_id,
                landmark_id=landmark_id,
                conversation_history=conversation_history,
            )

            # Generate the research report
            generated_text = await self._generate_research_text(context)

            # Process the generated text to extract any referenced landmarks
            landmark_names, landmark_ids = self._extract_landmarks_from_text(generated_text)

            # Process landmarks to ensure specific landmark is included
            landmark_names, landmark_ids = await self._process_landmarks(landmark_id, landmark_names, landmark_ids)

            # Get images if requested
            images = []
            if include_images and landmark_ids:
                primary_landmark_id = landmark_id or landmark_ids[0]
                images = await self._get_landmark_images(primary_landmark_id)

            # Create response
            sources = self._prepare_sources(context.relevant_passages, max_sources)

            # Get primary landmark name
            primary_landmark_name = await self._get_primary_landmark_name(landmark_id)

            # Get related landmarks
            related_landmarks = await self._get_related_landmarks(landmark_ids, landmark_id)

            # Suggest follow-up questions
            suggested_queries = self._generate_suggested_queries(query, generated_text)

            # Create and save the response
            response = await self._create_and_save_response(
                conversation_id=conversation_id,
                query=query,
                generated_text=generated_text,
                images=images,
                sources=sources,
                landmark_id=landmark_id,
                primary_landmark_name=primary_landmark_name,
                related_landmarks=related_landmarks,
                suggested_queries=suggested_queries,
                landmark_ids=landmark_ids,
                landmark_names=landmark_names,
            )

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Generated report in {elapsed:.2f} seconds")

            return response

        except Exception as e:
            logger.error(f"Error generating research report: {str(e)}")
            raise ValueError(f"Failed to generate research report: {str(e)}")

    async def get_conversation_history(self, conversation_id: str) -> List[ResearchResponse]:
        """
        Get history of a research conversation.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            List of ResearchResponse objects for the conversation
        """
        try:
            history = await self.memory_service.get_conversation_history(conversation_id)
            responses = []

            for entry in history:
                response = ResearchResponse(
                    conversation_id=conversation_id,
                    query=entry["query"],
                    report=entry["response"],
                    timestamp=datetime.now(),  # We don't have the original timestamp
                    images=[],  # Empty list since we don't have image data from history
                    sources=[],  # Empty list since we don't have source data from history
                    landmark_id=None,  # We don't know the landmark ID
                    landmark_name=None,  # We don't know the landmark name
                    related_landmarks=[],  # Empty list since we don't have related landmarks data
                    suggested_queries=[],  # Empty list since we don't have suggested queries data
                )
                responses.append(response)

            return responses
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            raise ValueError(f"Failed to retrieve conversation history: {str(e)}")

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: ID of the conversation to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            return await self.memory_service.delete_conversation(conversation_id)
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False

    async def _build_research_context(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        landmark_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> ResearchContext:
        """
        Build the research context for generating a report.

        Args:
            query: The research query
            conversation_id: Optional conversation ID
            landmark_id: Optional landmark ID
            conversation_history: Optional conversation history

        Returns:
            ResearchContext object with all the data needed for the report
        """
        # Get vector search results
        vector_results = await self._search_vectors(query, landmark_id)

        # Get landmark info if we have a landmark ID
        landmark_info = None
        if landmark_id:
            landmark_detail = await self.landmark_service.get_landmark_details(landmark_id)
            if landmark_detail:
                landmark_info = landmark_detail

        # Create the research context
        context = ResearchContext(
            query=query,
            conversation_id=conversation_id,
            landmark_id=landmark_id,
            relevant_passages=vector_results,
            landmark_info=landmark_info,
            conversation_history=conversation_history or [],
            images=[],  # Images will be added later if needed
        )

        return context

    async def _search_vectors(
        self, query: str, landmark_id: Optional[str] = None, top_k: int = 10
    ) -> List[SourcePassage]:
        """
        Search for relevant passages in the vector database.

        Args:
            query: The query to search for
            landmark_id: Optional landmark ID to filter by
            top_k: Maximum number of results to return

        Returns:
            List of SourcePassage objects
        """
        try:
            logger.debug(f"Searching vectors for query: {query}, landmark_id: {landmark_id}")

            # Call the vector store client
            results = await asyncio.to_thread(
                self.vector_client.query,
                query_text=query,
                top_k=top_k,
                landmark_id=landmark_id,
                min_score=0.6,  # Only include reasonably relevant results
            )

            passages = []
            for item in results.get("results", []):
                try:
                    passage = SourcePassage(
                        text=item.get("text", ""),
                        source_id=item.get("id", ""),
                        source_title=item.get("metadata", {}).get("title"),
                        page_number=item.get("metadata", {}).get("page"),
                        chunk_id=item.get("id"),
                        relevance_score=item.get("score", 0.0),
                        landmark_id=item.get("metadata", {}).get("landmark_id"),
                        metadata=item.get("metadata", {}),
                    )
                    passages.append(passage)
                except Exception as e:
                    logger.warning(f"Error converting vector result to source passage: {str(e)}")
                    continue

            logger.debug(f"Found {len(passages)} relevant passages")
            return passages
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            return []

    async def _generate_research_text(self, context: ResearchContext) -> str:
        """
        Generate the research report text using the OpenAI client.

        Args:
            context: Research context with all the data needed

        Returns:
            Generated text for the research report
        """
        try:
            # Prepare context information for the prompt
            passages_text = "\n\n".join(
                [
                    f"PASSAGE {i+1} [Source: {p.source_title or 'Unknown'}, "
                    + f"Page: {p.page_number or 'N/A'}, "
                    + f"Relevance: {p.relevance_score:.2f}]:\n{p.text}"
                    for i, p in enumerate(context.relevant_passages)
                ]
            )

            landmark_info_text = ""
            if context.landmark_info:
                landmark_info_text = f"""
LANDMARK INFORMATION:
ID: {context.landmark_info.lpc_id}
Name: {context.landmark_info.name}
Borough: {context.landmark_info.location.borough}
Designation Date: {context.landmark_info.designation.designation_date}
"""

            conversation_history_text = ""
            if context.conversation_history:
                history_items = []
                for i, entry in enumerate(context.conversation_history):
                    history_items.append(f"USER QUERY {i+1}: {entry['query']}")
                    history_items.append(f"ASSISTANT RESPONSE {i+1}: {entry['response']}")
                conversation_history_text = "\n\n".join(history_items)

            # Combine all context information
            context_text = f"""
{landmark_info_text}

RELEVANT PASSAGES:
{passages_text}

{conversation_history_text if conversation_history_text else ""}
"""

            # Choose the appropriate prompt template
            if context.conversation_history:
                prompt_template = CONVERSATION_PROMPT_TEMPLATE
                system_instructions = """
You must build on the previous conversation and provide a coherent continuation.
Focus on answering the new query while maintaining context from the previous exchanges.
"""
            else:
                prompt_template = RESEARCH_PROMPT_TEMPLATE
                system_instructions = """
You are tasked with creating an educational research report about NYC landmarks.
Focus on providing accurate, well-structured information based on the provided context.
Cite relevant passages when appropriate using [Source: Name, Page: X] format.
"""

            # Generate the research report
            if context.conversation_history:
                generated_text = await self.openai_client.generate_text(
                    prompt=prompt_template.format(
                        query=context.query, context=context_text, conversation_history=conversation_history_text
                    ),
                    system_prompt=system_instructions,
                    max_tokens=2000,
                    temperature=0.5,
                )
            else:
                generated_text = await self.openai_client.generate_research_report(
                    query=context.query,
                    context=context_text,
                    system_instructions=system_instructions,
                    max_tokens=2000,
                    temperature=0.5,
                )

            return str(generated_text)
        except Exception as e:
            logger.error(f"Error generating research text: {str(e)}")
            raise ValueError(f"Failed to generate research report: {str(e)}")

    async def _get_landmark_images(self, landmark_id: str) -> List[LandmarkImage]:
        """
        Get images for a landmark.

        Args:
            landmark_id: ID of the landmark

        Returns:
            List of LandmarkImage objects
        """
        try:
            logger.debug(f"Getting images for landmark {landmark_id}")
            landmark_photos = await self.landmark_service.get_landmark_photos(landmark_id)

            # Convert to API response format
            images = []
            for photo in landmark_photos:
                try:
                    image = LandmarkImage(
                        url=photo.url,  # Pass as HttpUrl, not str
                        caption=photo.description,
                        year=photo.year,
                        source=photo.source,
                        is_historical=photo.is_historical,
                    )
                    images.append(image)
                except Exception as e:
                    logger.warning(f"Error converting photo to image: {str(e)}")
                    continue

            logger.debug(f"Found {len(images)} images for landmark {landmark_id}")
            return images
        except Exception as e:
            logger.error(f"Error getting landmark images for {landmark_id}: {str(e)}")
            return []

    def _prepare_sources(self, passages: List[SourcePassage], max_sources: int) -> List[SourceDocument]:
        """
        Prepare source documents for the response.

        Args:
            passages: List of relevant passages
            max_sources: Maximum number of sources to include

        Returns:
            List of SourceDocument objects
        """
        sources: List[SourceDocument] = []
        seen_source_ids = set()

        # Sort by relevance score
        sorted_passages = sorted(passages, key=lambda p: p.relevance_score, reverse=True)

        for passage in sorted_passages:
            if len(sources) >= max_sources:
                break

            # Avoid duplicate sources
            if passage.source_id in seen_source_ids:
                continue

            seen_source_ids.add(passage.source_id)

            # Create source document
            source = SourceDocument(
                source_id=passage.source_id,
                source_type="pdf",  # Assuming all sources are PDFs
                title=passage.source_title,
                content=passage.text,
                page=passage.page_number,
                relevance_score=passage.relevance_score,
                metadata={"landmark_id": passage.landmark_id, **({} if not passage.metadata else passage.metadata)},
            )
            sources.append(source)

        return sources

    def _extract_landmarks_from_text(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract landmark names and IDs from generated text.

        Args:
            text: Generated text to analyze

        Returns:
            Tuple of (landmark_names, landmark_ids)
        """
        # This is a simplified implementation
        # In a real system, this would use NLP techniques or pattern matching

        # Placeholder implementation - would need to be replaced with actual extraction logic
        landmark_names: List[str] = []
        landmark_ids: List[str] = []

        # Simple regex pattern for LPC IDs like LP-00001
        import re

        lpc_pattern = r"LP-\d{5}"
        ids = re.findall(lpc_pattern, text)
        for lpc_id in ids:
            if lpc_id not in landmark_ids:
                landmark_ids.append(lpc_id)

        # For landmark names, we would need more sophisticated NER
        # This is just a placeholder

        return landmark_names, landmark_ids

    def _generate_suggested_queries(self, original_query: str, report_text: str) -> List[str]:
        """
        Generate suggested follow-up queries based on the original query and generated report.

        Args:
            original_query: The original research query
            report_text: The generated research report

        Returns:
            List of suggested follow-up queries
        """
        # This is a simplified implementation
        # In a real system, this would use NLP techniques or a separate LLM call

        # Placeholder implementation with common follow-up patterns
        suggestions: List[str] = [
            "What is the architectural style of this landmark?",
            "When was this landmark designated?",
            "Who was the architect of this landmark?",
            "What are some similar landmarks in New York City?",
            "What is the historical significance of this landmark?",
        ]

        # Filter to just 3 suggestions
        return suggestions[:3]
