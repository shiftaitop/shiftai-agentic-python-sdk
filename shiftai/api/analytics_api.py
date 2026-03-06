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
    FeedbackDTO,
    LatestFeedbacksRequest,
    LatestFeedbackItemResponse,
    LatestFeedbacksResponse,
    DashboardMetricsDTO,
    TopAgentDTO,
    TopUserDTO,
    UserAnalyticsDTO,
    ProjectAnalyticsResponseDTO,
    UserPreferenceUpdateRequest,
    UserPreferenceListRequest,
    UserPreferenceListAllRequest,
    UserPreferenceItemResponse,
    UserPreferenceListResponse,
    UserPreferencesPayload,
)


class AnalyticsApi:
    """API for analytics operations."""
    
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
    
    async def submit_feedback(
        self,
        message_id: UUID,
        feedback_title: str,
        feedback: str,
        liked: Optional[bool] = None,
        disliked: Optional[bool] = None,
        regeneration: Optional[bool] = None,
    ) -> FeedbackSubmissionResponse:
        """
        Submit feedback for a BOT message (multiple feedback per message allowed).

        POST /api/analytics/data

        Args:
            message_id: The ID of the BOT message that received feedback (required)
            feedback_title: Title for the feedback (required)
            feedback: Feedback content (required)
            liked: Like rating (optional)
            disliked: Dislike rating (optional)
            regeneration: User requested regeneration (optional)

        Returns:
            FeedbackSubmissionResponse with feedbackId and submittedAt

        Raises:
            ValueError: If message_id, feedback_title or feedback is missing
            ApiException: If the API request fails
        """
        self._http_client.ensure_authenticated()

        if message_id is None:
            raise ValueError("message_id is required")
        if not feedback_title or not feedback_title.strip():
            raise ValueError("feedback_title is required")
        if not feedback or not feedback.strip():
            raise ValueError("feedback is required")

        request = FeedbackSubmissionRequest(
            messageId=message_id,
            feedbackTitle=feedback_title.strip(),
            feedback=feedback.strip(),
            liked=liked,
            disliked=disliked,
            regeneration=regeneration,
        )

        return await self._http_client.post(
            "/api/analytics/data",
            request,
            FeedbackSubmissionResponse,
        )

    async def get_message_feedback(self, message_id: UUID) -> List[FeedbackDTO]:
        """
        Get all feedback submissions for a specific BOT message (most recent first).

        GET /api/analytics/messages/{messageId}/feedback

        Args:
            message_id: UUID of the BOT message (required)

        Returns:
            List of FeedbackDTO, ordered by submittedAt descending

        Raises:
            ValueError: If message_id is missing
            ApiException: If the API request fails
        """
        self._http_client.ensure_authenticated()

        if message_id is None:
            raise ValueError("message_id is required")

        return await self._http_client.get_list(
            f"/api/analytics/messages/{message_id}/feedback",
            FeedbackDTO,
        )

    async def get_latest_feedbacks(
        self,
        timeperiod: Optional[int] = None,
    ) -> LatestFeedbacksResponse:
        """
        Get latest feedback submissions for the project, most recent first.

        POST /api/platform/feedbacks/latest

        Args:
            timeperiod: Optional. None or omitted = all feedbacks.
                        N (e.g. 24) = only feedbacks from the last N hours.

        Returns:
            LatestFeedbacksResponse with .feedbacks (list) and optional .message
            (e.g. when timeperiod is set and there are no feedbacks in that window).
        """
        self._http_client.ensure_authenticated()

        body: Dict[str, Any] = {} if timeperiod is None else {"timeperiod": timeperiod}
        data = await self._http_client.post_map("/api/platform/feedbacks/latest", body)

        if isinstance(data, list):
            items = [
                LatestFeedbackItemResponse(
                    **self._http_client._filter_known_fields(item, LatestFeedbackItemResponse)
                )
                for item in data
            ]
            return LatestFeedbacksResponse(feedbacks=items)
        if isinstance(data, dict):
            msg = data.get("message")
            raw_list = data.get("feedbacks", [])
            items = [
                LatestFeedbackItemResponse(
                    **self._http_client._filter_known_fields(item, LatestFeedbackItemResponse)
                )
                for item in raw_list
            ]
            return LatestFeedbacksResponse(message=msg, feedbacks=items)
        return LatestFeedbacksResponse(feedbacks=[])

    async def update_user_preference(
        self,
        request: UserPreferenceUpdateRequest,
    ) -> UserPreferenceItemResponse:
        """
        Update one user preference item (or remove with value 'DELETE').

        POST /api/analytics/user-preferences/update

        Args:
            request: profileId, category (USER_PERSONAL|METRICS|CALCULATION), index (0-based), value (text or 'DELETE')

        Returns:
            UserPreferenceItemResponse with updatedAt set.
        """
        self._http_client.ensure_authenticated()
        if request.profileId is None:
            raise ValueError("profileId is required")
        if not request.category or not request.category.strip():
            raise ValueError("category is required")
        if request.index is None or request.index < 0:
            raise ValueError("index must be a non-negative integer")
        if request.value is None or (isinstance(request.value, str) and not request.value.strip()):
            raise ValueError("value is required and cannot be blank")
        data = await self._http_client.post_map("/api/analytics/user-preferences/update", request)
        return self._parse_user_preference_item(data)

    async def list_user_preferences_by_email(self, email: str) -> UserPreferenceListResponse:
        """
        List preferences for one user by email.

        POST /api/analytics/user-preferences/list

        Args:
            email: User email in the tenant (required).

        Returns:
            UserPreferenceListResponse with userpreferences list.
        """
        self._http_client.ensure_authenticated()
        if not email or not email.strip():
            raise ValueError("email is required")
        request = UserPreferenceListRequest(email=email.strip())
        data = await self._http_client.post_map("/api/analytics/user-preferences/list", request)
        return self._parse_user_preference_list_response(data)

    async def list_all_user_preferences(
        self,
        limit: Optional[int] = None,
    ) -> UserPreferenceListResponse:
        """
        List all user preferences in the tenant with optional limit.

        POST /api/analytics/user-preferences/list/all

        Args:
            limit: Max profiles to return (default 50, max 500). Omit or None for default.

        Returns:
            UserPreferenceListResponse with userpreferences list.
        """
        self._http_client.ensure_authenticated()
        body: Dict[str, Any] = {} if limit is None else {"limit": limit}
        data = await self._http_client.post_map("/api/analytics/user-preferences/list/all", body)
        return self._parse_user_preference_list_response(data)

    def _parse_user_preference_item(self, data: Dict[str, Any]) -> UserPreferenceItemResponse:
        """
        Build UserPreferenceItemResponse from one item dict (update 200 body or list element).
        Normalizes userPreferences dict to UserPreferencesPayload so callers get a consistent type.
        """
        if not isinstance(data, dict):
            return UserPreferenceItemResponse()
        filtered = self._http_client._filter_known_fields(data, UserPreferenceItemResponse)
        up = filtered.get("userPreferences")
        if isinstance(up, dict):
            filtered["userPreferences"] = UserPreferencesPayload(
                **self._http_client._filter_known_fields(up, UserPreferencesPayload)
            )
        return UserPreferenceItemResponse(**filtered)

    def _parse_user_preference_list_response(self, data: Any) -> UserPreferenceListResponse:
        """Build UserPreferenceListResponse from raw API response (key 'userpreferences')."""
        if not isinstance(data, dict):
            return UserPreferenceListResponse(userpreferences=[])
        raw_list = data.get("userpreferences", [])
        items: List[UserPreferenceItemResponse] = []
        for item in raw_list:
            if isinstance(item, dict):
                items.append(self._parse_user_preference_item(item))
        return UserPreferenceListResponse(userpreferences=items)

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

