import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import psutil
from fastapi import Request, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_db

logger = logging.getLogger(__name__)


class HealthChecker:
    def __init__(self):
        self.startup_time = time.time()

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
                "uptime": time.time() - self.startup_time,
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"error": "Failed to get system health"}

    def check_database_health(self, db: Session) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # Test basic connectivity
            result = db.execute(text("SELECT 1")).scalar()
            if result != 1:
                return {"status": "unhealthy", "error": "Database query failed"}

            # Test table existence
            table_check = db.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'players'
            """
                )
            ).scalar()

            # Get player count
            player_count = db.execute(text("SELECT COUNT(*) FROM players")).scalar()

            return {
                "status": "healthy",
                "tables_exist": table_check > 0,
                "player_count": player_count,
                "connection_pool": "active",
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    def check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health"""
        try:
            from services import cache

            # Test cache operations
            test_key = "health_check"
            test_value = {"status": "ok"}

            cache.set(test_key, test_value, ttl=60)
            retrieved = cache.get(test_key)
            cache.delete(test_key)

            return {
                "status": "healthy" if retrieved == test_value else "unhealthy",
                "operations": "read/write/delete",
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


health_checker = HealthChecker()


class RequestMetrics:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.max_response_times = 1000  # Keep last 1000 response times

    def record_request(self, response_time: float, status_code: int):
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1

        self.response_times.append(response_time)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        if not self.response_times:
            return {
                "request_count": self.request_count,
                "error_count": self.error_count,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
            }

        avg_time = sum(self.response_times) / len(self.response_times)
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0

        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": round(error_rate, 2),
            "avg_response_time": round(avg_time, 3),
            "min_response_time": round(min(self.response_times), 3),
            "max_response_time": round(max(self.response_times), 3),
        }


metrics = RequestMetrics()


@asynccontextmanager
async def request_timing_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    metrics.record_request(process_time, response.status_code)

    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)

    return response


async def monitoring_middleware(request: Request, call_next):
    """Middleware to track request metrics"""
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        metrics.record_request(process_time, response.status_code)
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        metrics.record_request(process_time, 500)
        logger.error(f"Request failed: {e}")
        raise
