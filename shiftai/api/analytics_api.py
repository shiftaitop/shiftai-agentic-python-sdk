"""
API for analytics operations.
Provides methods for submitting feedback and retrieving analytics data.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from ..http import HttpClient
from ..models import (
    FeedbackSubmissionRequest,
    FeedbackSubmissionResponse,
    DashboardMetricsDTO,
    TopAgentDTO,
    TopUserDTO,
    UserAnalyticsDTO,
    ProjectAnalyticsResponseDTO,
)


class AnalyticsApi:
    """API for analytics operations."""
    
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
    
    async def submit_feedback(
        self,
        message_id: UUID,
        like: Optional[bool] = None,
        dislike: Optional[bool] = None,
        feedback: Optional[str] = None,
        regeneration: Optional[bool] = None,
    ) -> FeedbackSubmissionResponse:
        """
        Submit feedback for a BOT message.
        
        POST /api/analytics/data
        
        Args:
            message_id: The ID of the BOT message that received feedback (required)
            like: Like feedback indicator (optional)
            dislike: Dislike feedback indicator (optional)
            feedback: Optional text feedback or comments (optional)
            regeneration: Indicates if user requested to regenerate (optional)
            
        Returns:
            FeedbackSubmissionResponse
            
        Raises:
            ValueError: If message_id is missing or API key is not configured
            ApiException: If the API request fails
        """
        self._http_client.ensure_authenticated()

        if message_id is None:
            raise ValueError("message_id is required")
        
        request = FeedbackSubmissionRequest(
            messageId=message_id,
            like=like,
            dislike=dislike,
            feedback=feedback,
            regeneration=regeneration
        )
        
        return await self._http_client.post(
            "/api/analytics/data",
            request,
            FeedbackSubmissionResponse
        )
    
    async def get_dashboard(self) -> DashboardMetricsDTO:
        """
        Get dashboard metrics.

        GET /api/analytics/dashboard

        Returns:
            DashboardMetricsDTO with dashboard metrics
        """
        self._http_client.ensure_authenticated()

        return await self._http_client.get(
            "/api/analytics/dashboard",
            DashboardMetricsDTO
        )
    
    async def get_top_agents(self, limit: int = 5) -> List[TopAgentDTO]:
        """
        Get top agents by query count.

        GET /api/analytics/top-agents?limit={limit}

        Args:
            limit: Maximum number of results to return (default: 5)

        Returns:
            List of top agents
        """
        self._http_client.ensure_authenticated()

        return await self._http_client.get_list(
            f"/api/analytics/top-agents?limit={limit}",
            TopAgentDTO
        )
    
    async def get_top_users(self, limit: int = 5) -> List[TopUserDTO]:
        """
        Get top users by activity.

        GET /api/analytics/top-users?limit={limit}

        Args:
            limit: Maximum number of results to return (default: 5)

        Returns:
            List of top users
        """
        self._http_client.ensure_authenticated()

        return await self._http_client.get_list(
            f"/api/analytics/top-users?limit={limit}",
            TopUserDTO
        )
    
    async def get_user_analytics(self) -> List[UserAnalyticsDTO]:
        """
        Get user analytics table.

        GET /api/analytics/user-analytics

        Returns:
            List of user analytics
        """
        self._http_client.ensure_authenticated()

        return await self._http_client.get_list(
            "/api/analytics/user-analytics",
            UserAnalyticsDTO
        )
    
    async def get_project_data(self, top_limit: int = 10) -> ProjectAnalyticsResponseDTO:
        """
        Get project analytics data.

        GET /api/analytics/project-data?topLimit={topLimit}

        Args:
            top_limit: Maximum number of top users/agents to return (default: 10)

        Returns:
            ProjectAnalyticsResponseDTO with project analytics
        """
        self._http_client.ensure_authenticated()

        return await self._http_client.get(
            f"/api/analytics/project-data?topLimit={top_limit}",
            ProjectAnalyticsResponseDTO
        )
    
    async def get_all(self, top_limit: int = 5) -> Dict[str, Any]:
        """
        Get all analytics (admin - no auth required).
        
        GET /api/analytics/all?topLimit={topLimit}
        
        Args:
            top_limit: Maximum number of results to return (default: 5)
            
        Returns:
            Dictionary with all analytics data
        """
        return await self._http_client.get_map_without_auth(
            f"/api/analytics/all?topLimit={top_limit}"
        )
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize analytics (admin - no auth required).
        
        POST /api/analytics/initialize
        
        Returns:
            Dictionary with initialization result
        """
        return await self._http_client.post_map_without_auth(
            "/api/analytics/initialize",
            None
        )

