"""
API for platform conversation operations.
Provides methods for retrieving and managing conversations.
"""

from typing import List, Dict, Any
from uuid import UUID
from ..http import HttpClient
from ..models import (
    ConversationMessageResponse,
    ConversationSummaryResponse,
    GetConversationsByEmailRequest,
    DeleteConversationRequest,
)


class ConversationsApi:
    """API for platform conversation operations."""
    
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
    
    async def get_messages_by_conversation_id(
        self,
        conversation_id: UUID
    ) -> List[ConversationMessageResponse]:
        """
        Get all messages for a specific conversation.
        
        POST /api/platform/conversation/getmessages
        
        Returns simplified message format with essential fields only (no deeply nested objects).
        Each message includes generatedContext (for all messages) and ragContext (for BOT messages only).
        
        Args:
            conversation_id: UUID of the conversation (required)
            
        Returns:
            List of simplified message responses for the conversation
            
        Raises:
            ValueError: If conversation_id is missing or API key is not configured
            ApiException: If the API request fails
        """
        self._http_client.ensure_authenticated()

        if conversation_id is None:
            raise ValueError("conversation_id is required")
        
        request = {
            "conversationId": str(conversation_id)
        }
        
        return await self._http_client.post_list(
            "/api/platform/conversation/getmessages",
            request,
            ConversationMessageResponse
        )
    
    async def get_all_conversations(
        self
    ) -> List[ConversationSummaryResponse]:
        """
        Get all conversation IDs for the authenticated project.

        GET /api/platform/conversations/all

        Returns:
            List of conversation summaries with conversation ID, start time, and end time
        """
        self._http_client.ensure_authenticated()

        return await self._http_client.get_list(
            "/api/platform/conversations/all",
            ConversationSummaryResponse
        )
    
    async def get_user_conversations(
        self,
        username: str
    ) -> List[ConversationSummaryResponse]:
        """
        Get all conversations for a specific user within the authenticated project.
        
        POST /api/platform/conversations/user
        
        Retrieves all conversations associated with a username in your project.
        Each conversation includes conversation ID, username, agent name, start time, and end time.
        
        Args:
            username: Username to retrieve conversations for (required)
            
        Returns:
            List of conversation summaries for the user
            
        Raises:
            ValueError: If username is missing or API key is not configured
            ApiException: If the API request fails
        """
        self._http_client.ensure_authenticated()

        if not username or not username.strip():
            raise ValueError("username is required")
        
        request = {
            "username": username.strip()
        }
        
        return await self._http_client.post_list(
            "/api/platform/conversations/user",
            request,
            ConversationSummaryResponse
        )
    
    async def get_conversations_by_email(
        self,
        email: str,
    ) -> List[ConversationSummaryResponse]:
        """
        Get all conversations for a specific user by email within the authenticated project.

        POST /api/platform/conversations/email

        Args:
            email: User's email address (required)

        Returns:
            List of conversation summaries for the user

        Raises:
            ValueError: If email is missing or API key is not configured
            ApiException: If the API request fails
        """
        self._http_client.ensure_authenticated()

        if not email or not email.strip():
            raise ValueError("email is required")

        request = GetConversationsByEmailRequest(email=email.strip())

        return await self._http_client.post_list(
            "/api/platform/conversations/email",
            request,
            ConversationSummaryResponse,
        )

    async def delete_conversation(
        self,
        conversation_id: UUID,
    ) -> Dict[str, Any]:
        """
        Delete a conversation.

        POST /api/platform/conversation/delete

        Args:
            conversation_id: UUID of the conversation to delete (required)

        Returns:
            Dict with:
              - On success (200): success, message, timestamp
              - On errors (4xx/5xx): error, message, status, timestamp
        """
        self._http_client.ensure_authenticated()

        if conversation_id is None:
            raise ValueError("conversation_id is required")

        request = DeleteConversationRequest(conversationId=conversation_id)

        return await self._http_client.post_map(
            "/api/platform/conversation/delete",
            request,
        )

