"""
Unit tests for the memory service.
"""

from datetime import datetime, timedelta

import pytest

from src.models.research_models import Conversation
from src.services.memory_service import MemoryService


class TestMemoryService:
    """Tests for the MemoryService class."""

    @pytest.fixture
    def memory_service(self):
        """Create a memory service instance for testing."""
        service = MemoryService()
        service.memory_enabled = True
        service.ttl_seconds = 3600  # 1 hour TTL for testing
        return service

    @pytest.mark.asyncio
    async def test_create_conversation(self, memory_service):
        """Test creating a new conversation."""
        # Act
        conversation_id = await memory_service.create_conversation()

        # Assert
        assert conversation_id is not None
        assert isinstance(conversation_id, str)
        assert conversation_id in memory_service.conversations
        assert isinstance(memory_service.conversations[conversation_id], Conversation)

    @pytest.mark.asyncio
    async def test_add_entry(self, memory_service):
        """Test adding an entry to a conversation."""
        # Arrange
        conversation_id = await memory_service.create_conversation()
        query = "Tell me about the Flatiron Building"
        response = "The Flatiron Building is a landmark in NYC..."
        landmark_ids = ["LP-00001"]
        landmark_names = ["Flatiron Building"]

        # Act
        result = await memory_service.add_entry(
            conversation_id=conversation_id,
            query=query,
            response=response,
            landmark_ids=landmark_ids,
            landmark_names=landmark_names,
        )

        # Assert
        assert result is True
        assert len(memory_service.conversations[conversation_id].entries) == 1
        entry = memory_service.conversations[conversation_id].entries[0]
        assert entry.query == query
        assert entry.response == response
        assert entry.landmark_ids == landmark_ids
        assert entry.landmark_names == landmark_names

    @pytest.mark.asyncio
    async def test_get_conversation_history(self, memory_service):
        """Test getting conversation history."""
        # Arrange
        conversation_id = await memory_service.create_conversation()
        query1 = "Tell me about the Flatiron Building"
        response1 = "The Flatiron Building is a landmark in NYC..."
        query2 = "When was it built?"
        response2 = "It was completed in 1902."

        await memory_service.add_entry(conversation_id, query1, response1)
        await memory_service.add_entry(conversation_id, query2, response2)

        # Act
        history = await memory_service.get_conversation_history(conversation_id)

        # Assert
        assert len(history) == 2
        assert history[0]["query"] == query1
        assert history[0]["response"] == response1
        assert history[1]["query"] == query2
        assert history[1]["response"] == response2

    @pytest.mark.asyncio
    async def test_delete_conversation(self, memory_service):
        """Test deleting a conversation."""
        # Arrange
        conversation_id = await memory_service.create_conversation()

        # Act
        result = await memory_service.delete_conversation(conversation_id)

        # Assert
        assert result is True
        assert conversation_id not in memory_service.conversations

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, memory_service):
        """Test cleaning up expired conversations."""
        # Arrange
        conversation_id = await memory_service.create_conversation()

        # Manipulate the updated_at timestamp to make it expired
        memory_service.conversations[conversation_id].updated_at = datetime.now() - timedelta(
            seconds=memory_service.ttl_seconds * 2
        )

        # Act
        memory_service._cleanup_expired()

        # Assert
        assert conversation_id not in memory_service.conversations

    @pytest.mark.asyncio
    async def test_memory_disabled(self):
        """Test behavior when memory is disabled."""
        # Arrange
        service = MemoryService()
        service.memory_enabled = False

        # Act
        conversation_id = await service.create_conversation()
        add_result = await service.add_entry(conversation_id, "query", "response")
        history = await service.get_conversation_history(conversation_id)
        delete_result = await service.delete_conversation(conversation_id)

        # Assert
        assert conversation_id is not None
        assert add_result is True
        assert history == []
        assert delete_result is True
        assert len(service.conversations) == 0
