"""
Memory service for the NYC Landmarks Research Agent.
Provides conversation memory capabilities for maintaining context in research conversations.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.config import settings
from src.models.research_models import Conversation, MemoryEntry

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing conversation memory.

    This is an in-memory implementation. For production use, this would be
    replaced with a persistent storage solution (e.g., Redis, MongoDB).
    """

    def __init__(self):
        """Initialize the memory service."""
        self.conversations: Dict[str, Conversation] = {}
        self.ttl_seconds = settings.MEMORY_TTL_SECONDS
        self.memory_enabled = settings.ENABLE_MEMORY
        logger.info(f"Memory service initialized (enabled={self.memory_enabled}, ttl={self.ttl_seconds}s)")

    async def create_conversation(self) -> str:
        """
        Create a new conversation and return its ID.

        Returns:
            String conversation ID
        """
        if not self.memory_enabled:
            logger.debug("Memory disabled, returning dummy ID")
            return str(uuid.uuid4())

        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = Conversation(id=conversation_id, landmark_focus=None)
        logger.debug(f"Created conversation {conversation_id}")
        return conversation_id

    async def add_entry(
        self,
        conversation_id: str,
        query: str,
        response: str,
        landmark_ids: Optional[List[str]] = None,
        landmark_names: Optional[List[str]] = None,
        sources_used: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Add an entry to a conversation.

        Args:
            conversation_id: ID of the conversation to add to
            query: User query
            response: Agent response
            landmark_ids: Optional list of landmark IDs mentioned
            landmark_names: Optional list of landmark names mentioned
            sources_used: Optional list of sources used in the response

        Returns:
            True if successful, False otherwise
        """
        if not self.memory_enabled:
            logger.debug("Memory disabled, skipping entry addition")
            return True

        self._cleanup_expired()

        if conversation_id not in self.conversations:
            logger.warning(f"Conversation {conversation_id} not found, creating new conversation")
            self.conversations[conversation_id] = Conversation(id=conversation_id, landmark_focus=None)

        entry = MemoryEntry(
            conversation_id=conversation_id,
            query=query,
            response=response,
            landmark_ids=landmark_ids or [],
            landmark_names=landmark_names or [],
            sources_used=sources_used or [],
        )

        self.conversations[conversation_id].entries.append(entry)
        self.conversations[conversation_id].updated_at = datetime.now()

        if landmark_ids and not self.conversations[conversation_id].landmark_focus:
            # If this is the first entry with a landmark focus, set it
            self.conversations[conversation_id].landmark_focus = landmark_ids[0]

        logger.debug(
            f"Added entry to conversation {conversation_id}, "
            f"entries: {len(self.conversations[conversation_id].entries)}"
        )
        return True

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            Conversation if found, None otherwise
        """
        if not self.memory_enabled:
            logger.debug("Memory disabled, returning None for conversation")
            return None

        self._cleanup_expired()

        conversation = self.conversations.get(conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            return None

        return conversation

    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get the history of a conversation as a list of query/response pairs.

        Args:
            conversation_id: ID of the conversation to retrieve

        Returns:
            List of dictionaries with 'query' and 'response' keys
        """
        if not self.memory_enabled:
            logger.debug("Memory disabled, returning empty history")
            return []

        self._cleanup_expired()

        conversation = self.conversations.get(conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            return []

        history = []
        for entry in conversation.entries:
            history.append({"query": entry.query, "response": entry.response})

        return history

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation by ID.

        Args:
            conversation_id: ID of the conversation to delete

        Returns:
            True if successfully deleted, False otherwise
        """
        if not self.memory_enabled:
            logger.debug("Memory disabled, skipping deletion")
            return True

        if conversation_id not in self.conversations:
            logger.warning(f"Conversation {conversation_id} not found for deletion")
            return False

        del self.conversations[conversation_id]
        logger.debug(f"Deleted conversation {conversation_id}")
        return True

    def _cleanup_expired(self):
        """Clean up expired conversations based on TTL."""
        if not self.memory_enabled:
            return

        now = datetime.now().timestamp()
        expired_conversations = []

        for conversation_id, conversation in self.conversations.items():
            updated_timestamp = conversation.updated_at.timestamp()
            age_seconds = now - updated_timestamp

            if age_seconds > self.ttl_seconds:
                expired_conversations.append(conversation_id)

        for conversation_id in expired_conversations:
            logger.debug(f"Removing expired conversation {conversation_id}")
            del self.conversations[conversation_id]

        if expired_conversations:
            logger.info(f"Cleaned up {len(expired_conversations)} expired conversations")
