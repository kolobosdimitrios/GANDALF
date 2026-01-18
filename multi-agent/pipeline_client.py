"""
Pipeline Client

HTTP client for communicating with the GANDALF Pipeline AI Agent Service.

Provides methods to execute each step of the 4-step pipeline:
1. Lexical Analysis
2. Semantic Analysis
3. Coverage Scoring
4. CTC Generation
"""

import os
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class PipelineClient:
    """
    Client for the GANDALF Pipeline AI Agent Service.

    Communicates via HTTP with the pipeline agent service.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        timeout: int = 120
    ):
        """
        Initialize the pipeline client.

        Args:
            endpoint: Pipeline agent service endpoint (default: from env or localhost:8080)
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint or os.getenv(
            'GANDALF_PIPELINE_ENDPOINT',
            'http://localhost:8080'
        )
        self.timeout = timeout

        logger.info(f"PipelineClient initialized: endpoint={self.endpoint}")

    def _make_request(
        self,
        path: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make HTTP POST request to pipeline service.

        Args:
            path: API path (e.g., '/pipeline/step1')
            payload: Request payload

        Returns:
            Response as dictionary

        Raises:
            Exception: If request fails
        """
        url = f"{self.endpoint}{path}"
        logger.info(f"Making request to {url}")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                logger.info(f"Request successful")

                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Pipeline request failed: {e.response.status_code} {e.response.text}")

        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Pipeline request failed: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def execute_step_1_lexical(
        self,
        user_message: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Step 1: Lexical Analysis.

        Args:
            user_message: User's intent/request
            context: Optional context

        Returns:
            Lexical report with telemetry
        """
        logger.info("Executing Step 1: Lexical Analysis")

        payload = {
            "user_message": user_message,
            "context": context
        }

        return self._make_request("/pipeline/step1", payload)

    def execute_step_2_semantic(
        self,
        user_message: str,
        lexical_report: Dict,
        context: Optional[Dict] = None,
        user_answers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Step 2: Semantic Analysis.

        Args:
            user_message: User's intent/request
            lexical_report: Output from Step 1
            context: Optional context
            user_answers: Optional user answers to questions

        Returns:
            Semantic frame with telemetry
        """
        logger.info("Executing Step 2: Semantic Analysis")

        payload = {
            "user_message": user_message,
            "lexical_report": lexical_report,
            "context": context,
            "user_answers": user_answers
        }

        return self._make_request("/pipeline/step2", payload)

    def execute_step_3_coverage(
        self,
        semantic_frame: Dict,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Step 3: Coverage Scoring & Questions.

        Args:
            semantic_frame: Output from Step 2
            context: Optional context

        Returns:
            Coverage report with telemetry
        """
        logger.info("Executing Step 3: Coverage Scoring")

        payload = {
            "semantic_frame": semantic_frame,
            "context": context
        }

        return self._make_request("/pipeline/step3", payload)

    def execute_step_4_ctc(
        self,
        semantic_frame: Dict,
        coverage_report: Dict,
        user_answers: Optional[Dict] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute Step 4: CTC Generation.

        Args:
            semantic_frame: Output from Step 2
            coverage_report: Output from Step 3
            user_answers: Optional user answers to blocking questions
            context: Optional context

        Returns:
            CTC with telemetry
        """
        logger.info("Executing Step 4: CTC Generation")

        payload = {
            "semantic_frame": semantic_frame,
            "coverage_report": coverage_report,
            "user_answers": user_answers,
            "context": context
        }

        return self._make_request("/pipeline/step4", payload)

    def check_health(self) -> Dict[str, Any]:
        """
        Check pipeline service health.

        Returns:
            Health status with telemetry
        """
        url = f"{self.endpoint}/health"
        logger.info(f"Checking health at {url}")

        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise Exception(f"Pipeline service unavailable: {str(e)}")

    def get_telemetry(self) -> Dict[str, Any]:
        """
        Get telemetry data from pipeline service.

        Returns:
            Telemetry data with cost breakdown
        """
        url = f"{self.endpoint}/telemetry"
        logger.info(f"Getting telemetry from {url}")

        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Telemetry request failed: {e}")
            raise Exception(f"Could not retrieve telemetry: {str(e)}")

    def __repr__(self) -> str:
        return f"PipelineClient(endpoint={self.endpoint})"
