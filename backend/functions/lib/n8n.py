"""
n8n API Client and Tool Definitions

This module provides integration with n8n API for workflow automation.
Includes Pydantic models for type safety and tool definitions for LLM function calling.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import requests
import logging

log = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for n8n API
# ============================================================================

class N8nNode(BaseModel):
    """Represents an n8n node."""
    name: str
    displayName: str
    description: Optional[str] = None
    icon: Optional[str] = None
    iconUrl: Optional[str] = None


class N8nSearchNodesResponse(BaseModel):
    """Response from n8n node search."""
    nodes: List[N8nNode]
    total: int


class N8nWorkflowTemplate(BaseModel):
    """Represents an n8n workflow template."""
    id: int
    name: str
    description: Optional[str] = None
    workflow: Dict[str, Any]


# ============================================================================
# Tool Schemas (for LLM Function Calling)
# ============================================================================

class SearchNodesParams(BaseModel):
    """Parameters for searching n8n nodes."""
    query: str = Field(
        description="Search query to find n8n nodes (e.g., 'http', 'database', 'slack')"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=50
    )


class SearchTemplatesParams(BaseModel):
    """Parameters for searching n8n templates."""
    query: str = Field(
        description="Search query to find workflow templates"
    )
    limit: int = Field(
        default=5,
        description="Maximum number of templates to return",
        ge=1,
        le=20
    )


class CreateWorkflowParams(BaseModel):
    """Parameters for creating an n8n workflow."""
    name: str = Field(
        description="Name for the new workflow"
    )
    nodes: List[str] = Field(
        description="List of node names to include in the workflow"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description for the workflow"
    )


class ExecuteWorkflowParams(BaseModel):
    """Parameters for executing an n8n workflow."""
    workflow_id: str = Field(
        description="ID of the workflow to execute"
    )
    input_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional input data for the workflow"
    )


# ============================================================================
# n8n API Client
# ============================================================================

class N8nClient:
    """
    Client for interacting with n8n API.

    Example:
        client = N8nClient(base_url="http://localhost:5678", api_key="your-key")
        nodes = client.search_nodes("http")
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize n8n client.

        Args:
            base_url: Base URL of n8n instance (e.g., "http://localhost:5678")
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({
                'X-N8N-API-KEY': api_key
            })

    def search_nodes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for n8n nodes.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of node information
        """
        try:
            # Note: This endpoint might vary based on n8n version
            # Adjust based on your n8n API documentation
            response = self.session.get(
                f"{self.base_url}/api/v1/nodes",
                params={'search': query, 'limit': limit},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Filter and format results
            nodes = []
            for node in data.get('data', [])[:limit]:
                nodes.append({
                    'name': node.get('name', ''),
                    'displayName': node.get('displayName', ''),
                    'description': node.get('description', ''),
                    'icon': node.get('icon'),
                })

            return nodes

        except requests.exceptions.RequestException as e:
            log.error(f"Error searching nodes: {e}")
            return []

    def search_templates(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for workflow templates.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of template information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/workflows/templates",
                params={'search': query, 'limit': limit},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            templates = data.get('data', [])[:limit]

            return [
                {
                    'id': t.get('id'),
                    'name': t.get('name'),
                    'description': t.get('description'),
                }
                for t in templates
            ]

        except requests.exceptions.RequestException as e:
            log.error(f"Error searching templates: {e}")
            return []

    def create_workflow(
        self,
        name: str,
        nodes: List[str],
        description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            nodes: List of node names to include
            description: Optional description

        Returns:
            Created workflow info or None on error
        """
        try:
            workflow_data = {
                'name': name,
                'nodes': [{'type': node} for node in nodes],
                'connections': {},
            }

            if description:
                workflow_data['settings'] = {'description': description}

            response = self.session.post(
                f"{self.base_url}/api/v1/workflows",
                json=workflow_data,
                timeout=10
            )
            response.raise_for_status()

            return response.json().get('data')

        except requests.exceptions.RequestException as e:
            log.error(f"Error creating workflow: {e}")
            return None

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of workflow to execute
            input_data: Optional input data

        Returns:
            Execution result or None on error
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                json={'data': input_data or {}},
                timeout=30
            )
            response.raise_for_status()

            return response.json().get('data')

        except requests.exceptions.RequestException as e:
            log.error(f"Error executing workflow: {e}")
            return None


# ============================================================================
# Tool Definitions for LLM
# ============================================================================

def get_n8n_tools() -> List[Dict[str, Any]]:
    """
    Get OpenAI-compatible tool definitions for n8n operations.

    Returns:
        List of tool definitions in OpenAI format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "search_nodes",
                "description": "Search for available n8n nodes by keyword. Use this to find nodes for building workflows.",
                "parameters": SearchNodesParams.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_templates",
                "description": "Search for n8n workflow templates. Use this to find pre-built workflows.",
                "parameters": SearchTemplatesParams.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_workflow",
                "description": "Create a new n8n workflow with specified nodes. Use after searching for appropriate nodes.",
                "parameters": CreateWorkflowParams.model_json_schema()
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_workflow",
                "description": "Execute an existing n8n workflow by ID. Use after creating or identifying a workflow.",
                "parameters": ExecuteWorkflowParams.model_json_schema()
            }
        }
    ]
