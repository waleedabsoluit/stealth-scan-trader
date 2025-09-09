"""
Request Logging Middleware
Logs all HTTP requests with timing and status
"""
import time
import json
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
import logging

logger = logging.getLogger(__name__)


class LoggingRoute(APIRoute):
    """Custom route class that logs requests"""
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()
            
            # Log request
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'client': request.client.host if request.client else None
            }
            
            logger.info(f"Request started: {json.dumps(log_data)}")
            
            try:
                response: Response = await original_route_handler(request)
                process_time = time.time() - start_time
                
                # Log response
                log_data.update({
                    'status_code': response.status_code,
                    'process_time': round(process_time * 1000, 2),  # ms
                    'success': 200 <= response.status_code < 400
                })
                
                logger.info(f"Request completed: {json.dumps(log_data)}")
                
                # Add timing header
                response.headers["X-Process-Time"] = str(process_time)
                return response
                
            except Exception as e:
                process_time = time.time() - start_time
                log_data.update({
                    'error': str(e),
                    'process_time': round(process_time * 1000, 2),
                    'success': False
                })
                logger.error(f"Request failed: {json.dumps(log_data)}")
                raise
        
        return custom_route_handler