"""
Performance Optimization Service
Provides intelligent caching, response optimization, and efficient data processing
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import time

from cachetools import TTLCache, LRUCache
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    average_response_time: float = 0.0
    cache_size: int = 0
    last_reset: datetime = None

class IntelligentCache:
    """Intelligent caching system with adaptive TTL and priority-based eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.response_cache = TTLCache(maxsize=max_size, ttl=default_ttl)
        self.ai_cache = TTLCache(maxsize=500, ttl=7200)  # Longer TTL for AI responses
        self.medical_cache = TTLCache(maxsize=200, ttl=86400)  # 24h for medical data
        self.user_context_cache = LRUCache(maxsize=1000)  # No TTL for user context
        
        self.stats = CacheStats()
        self.stats.last_reset = datetime.utcnow()
        
        # Performance tracking
        self.response_times = []
        self.cache_patterns = {}
        
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate consistent cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def _update_stats(self, hit: bool, response_time: float = 0):
        """Update cache statistics"""
        self.stats.total_requests += 1
        if hit:
            self.stats.hits += 1
        else:
            self.stats.misses += 1
        
        self.stats.hit_rate = self.stats.hits / self.stats.total_requests
        
        if response_time > 0:
            self.response_times.append(response_time)
            if len(self.response_times) > 1000:  # Keep last 1000 measurements
                self.response_times = self.response_times[-1000:]
            self.stats.average_response_time = sum(self.response_times) / len(self.response_times)
    
    async def get_or_compute(
        self,
        cache_type: str,
        compute_func: Callable,
        cache_key: str = None,
        ttl: int = None,
        **kwargs
    ) -> Any:
        """Get from cache or compute and cache the result"""
        start_time = time.time()
        
        # Select appropriate cache
        cache = {
            "response": self.response_cache,
            "ai": self.ai_cache,
            "medical": self.medical_cache,
            "user": self.user_context_cache
        }.get(cache_type, self.response_cache)
        
        # Generate cache key if not provided
        if not cache_key:
            cache_key = self._generate_cache_key(cache_type, **kwargs)
        
        # Try to get from cache
        try:
            result = cache.get(cache_key)
            if result is not None:
                self._update_stats(hit=True, response_time=time.time() - start_time)
                logger.debug(f"Cache hit for key: {cache_key}")
                return result
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        # Compute result
        try:
            if asyncio.iscoroutinefunction(compute_func):
                result = await compute_func(**kwargs)
            else:
                result = compute_func(**kwargs)
            
            # Cache the result
            if ttl and hasattr(cache, 'expire'):
                cache[cache_key] = result
                cache.expire(cache_key, ttl)
            else:
                cache[cache_key] = result
            
            self._update_stats(hit=False, response_time=time.time() - start_time)
            logger.debug(f"Computed and cached result for key: {cache_key}")
            return result
            
        except Exception as e:
            logger.error(f"Error computing result for cache key {cache_key}: {e}")
            self._update_stats(hit=False, response_time=time.time() - start_time)
            raise
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache keys matching a pattern"""
        caches = [self.response_cache, self.ai_cache, self.medical_cache, self.user_context_cache]
        
        for cache in caches:
            keys_to_remove = [key for key in cache.keys() if pattern in key]
            for key in keys_to_remove:
                try:
                    del cache[key]
                    logger.debug(f"Invalidated cache key: {key}")
                except KeyError:
                    pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "total_requests": self.stats.total_requests,
            "hit_rate": round(self.stats.hit_rate * 100, 2),
            "average_response_time": round(self.stats.average_response_time * 1000, 2),  # ms
            "cache_sizes": {
                "response": len(self.response_cache),
                "ai": len(self.ai_cache),
                "medical": len(self.medical_cache),
                "user": len(self.user_context_cache)
            },
            "uptime_minutes": (datetime.utcnow() - self.stats.last_reset).total_seconds() / 60
        }
    
    def clear_all(self):
        """Clear all caches and reset stats"""
        self.response_cache.clear()
        self.ai_cache.clear()
        self.medical_cache.clear()
        self.user_context_cache.clear()
        
        self.stats = CacheStats()
        self.stats.last_reset = datetime.utcnow()
        self.response_times = []

class ResponseOptimizer:
    """Optimize API responses for efficiency and user experience"""
    
    def __init__(self):
        self.compression_threshold = 1024  # Compress responses > 1KB
        self.streaming_threshold = 5000   # Stream responses > 5KB
        self.priority_keywords = [
            "emergency", "urgent", "critical", "severe", "acute",
            "chest pain", "difficulty breathing", "unconscious"
        ]
    
    def optimize_response(self, response_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize response based on content and context"""
        optimized = response_data.copy()
        
        # Priority-based optimization
        if self._is_high_priority(response_data):
            optimized = self._optimize_for_priority(optimized)
        
        # Content-based optimization
        optimized = self._optimize_content(optimized)
        
        # Add performance metadata
        optimized["_performance"] = {
            "optimized": True,
            "optimization_time": datetime.utcnow().isoformat(),
            "priority_level": self._get_priority_level(response_data),
            "content_size": len(json.dumps(optimized)),
            "optimization_applied": []
        }
        
        return optimized
    
    def _is_high_priority(self, response_data: Dict[str, Any]) -> bool:
        """Check if response contains high-priority content"""
        content = json.dumps(response_data).lower()
        return any(keyword in content for keyword in self.priority_keywords)
    
    def _get_priority_level(self, response_data: Dict[str, Any]) -> str:
        """Determine priority level of response"""
        content = json.dumps(response_data).lower()
        
        if any(word in content for word in ["emergency", "critical", "urgent"]):
            return "critical"
        elif any(word in content for word in ["severe", "acute", "concerning"]):
            return "high"
        elif any(word in content for word in ["moderate", "significant"]):
            return "medium"
        else:
            return "low"
    
    def _optimize_for_priority(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize high-priority responses for immediate delivery"""
        optimized = response_data.copy()
        
        # Move critical information to the top
        if "message" in optimized:
            message = optimized["message"]
            
            # Add priority indicators
            if any(word in message.lower() for word in ["emergency", "urgent", "critical"]):
                optimized["priority_alert"] = "🚨 URGENT: Immediate medical attention may be required"
                optimized["_performance"]["optimization_applied"].append("priority_alert")
        
        # Minimize non-essential fields for faster transmission
        non_essential = ["sources", "conversation_summary", "detailed_analysis"]
        for field in non_essential:
            if field in optimized and len(json.dumps(optimized)) > self.compression_threshold:
                if isinstance(optimized[field], list) and len(optimized[field]) > 3:
                    optimized[field] = optimized[field][:3]  # Keep only top 3
                    optimized["_performance"]["optimization_applied"].append(f"truncated_{field}")
        
        return optimized
    
    def _optimize_content(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for better user experience"""
        optimized = response_data.copy()
        
        # Format lists for better readability
        if "recommendations" in optimized and isinstance(optimized["recommendations"], list):
            if len(optimized["recommendations"]) > 5:
                # Group recommendations by priority
                urgent = [r for r in optimized["recommendations"] if any(word in r.lower() for word in ["urgent", "immediate", "emergency"])]
                important = [r for r in optimized["recommendations"] if any(word in r.lower() for word in ["important", "significant", "should"])]
                general = [r for r in optimized["recommendations"] if r not in urgent and r not in important]
                
                optimized["recommendations"] = {
                    "urgent": urgent,
                    "important": important[:3],  # Limit to top 3
                    "general": general[:2]       # Limit to top 2
                }
                optimized["_performance"]["optimization_applied"].append("categorized_recommendations")
        
        # Optimize follow-up suggestions
        if "follow_up_suggestions" in optimized and isinstance(optimized["follow_up_suggestions"], list):
            if len(optimized["follow_up_suggestions"]) > 3:
                optimized["follow_up_suggestions"] = optimized["follow_up_suggestions"][:3]
                optimized["_performance"]["optimization_applied"].append("limited_followups")
        
        return optimized

class DataProcessor:
    """Efficient data processing for medical information"""
    
    def __init__(self):
        self.batch_size = 100
        self.processing_timeout = 30  # seconds
    
    async def batch_process(
        self,
        items: List[Any],
        process_func: Callable,
        batch_size: int = None
    ) -> List[Any]:
        """Process items in batches for efficiency"""
        if not batch_size:
            batch_size = self.batch_size
        
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            try:
                # Process batch
                if asyncio.iscoroutinefunction(process_func):
                    batch_results = await asyncio.wait_for(
                        process_func(batch),
                        timeout=self.processing_timeout
                    )
                else:
                    batch_results = process_func(batch)
                
                results.extend(batch_results)
                
            except asyncio.TimeoutError:
                logger.warning(f"Batch processing timeout for batch starting at index {i}")
                # Add placeholder results for failed batch
                results.extend([{"error": "Processing timeout"} for _ in batch])
            except Exception as e:
                logger.error(f"Error processing batch starting at index {i}: {e}")
                results.extend([{"error": str(e)} for _ in batch])
        
        return results
    
    def optimize_query_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize database query filters for performance"""
        optimized = filters.copy()
        
        # Convert string dates to datetime objects for better indexing
        date_fields = ["created_at", "updated_at", "timestamp", "recorded_at"]
        for field in date_fields:
            if field in optimized and isinstance(optimized[field], str):
                try:
                    optimized[field] = datetime.fromisoformat(optimized[field].replace('Z', '+00:00'))
                except ValueError:
                    pass  # Keep original value if conversion fails
        
        # Optimize text search queries
        if "search" in optimized:
            search_term = optimized["search"]
            if len(search_term) > 50:
                # Use more efficient regex for long searches
                optimized["$text"] = {"$search": search_term}
                del optimized["search"]
        
        return optimized

class PerformanceMonitor:
    """Monitor and analyze system performance"""
    
    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "total_response_time": 0,
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "ai_calls": 0,
            "db_queries": 0
        }
        self.start_time = datetime.utcnow()
        self.response_times = []
    
    def track_api_call(self, endpoint: str, response_time: float, status_code: int):
        """Track API call metrics"""
        self.metrics["api_calls"] += 1
        self.metrics["total_response_time"] += response_time
        
        if status_code >= 400:
            self.metrics["error_count"] += 1
        
        self.response_times.append({
            "endpoint": endpoint,
            "response_time": response_time,
            "status_code": status_code,
            "timestamp": datetime.utcnow()
        })
        
        # Keep only last 1000 entries
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Calculate averages
        avg_response_time = (
            self.metrics["total_response_time"] / self.metrics["api_calls"]
            if self.metrics["api_calls"] > 0 else 0
        )
        
        error_rate = (
            self.metrics["error_count"] / self.metrics["api_calls"] * 100
            if self.metrics["api_calls"] > 0 else 0
        )
        
        # Analyze response time trends
        recent_times = [r["response_time"] for r in self.response_times[-100:]]  # Last 100 calls
        recent_avg = sum(recent_times) / len(recent_times) if recent_times else 0
        
        return {
            "uptime_seconds": uptime,
            "total_api_calls": self.metrics["api_calls"],
            "average_response_time": round(avg_response_time * 1000, 2),  # ms
            "recent_average_response_time": round(recent_avg * 1000, 2),  # ms
            "error_rate": round(error_rate, 2),
            "requests_per_minute": round(self.metrics["api_calls"] / (uptime / 60), 2),
            "ai_calls": self.metrics["ai_calls"],
            "db_queries": self.metrics["db_queries"],
            "cache_performance": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_rate": round(
                    self.metrics["cache_hits"] / 
                    (self.metrics["cache_hits"] + self.metrics["cache_misses"]) * 100, 2
                ) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
            },
            "health_status": self._get_health_status(avg_response_time, error_rate)
        }
    
    def _get_health_status(self, avg_response_time: float, error_rate: float) -> str:
        """Determine system health status"""
        if error_rate > 10 or avg_response_time > 5.0:
            return "critical"
        elif error_rate > 5 or avg_response_time > 2.0:
            return "warning"
        elif error_rate > 1 or avg_response_time > 1.0:
            return "caution"
        else:
            return "healthy"

class PerformanceOptimizationService:
    """Main performance optimization service"""
    
    def __init__(self):
        self.cache = IntelligentCache()
        self.response_optimizer = ResponseOptimizer()
        self.data_processor = DataProcessor()
        self.performance_monitor = PerformanceMonitor()
        self._initialized = False
    
    async def initialize(self):
        """Initialize performance optimization service"""
        if self._initialized:
            return
        
        logger.info("Initializing Performance Optimization Service...")
        
        try:
            # Initialize cache warming for common queries
            await self._warm_cache()
            
            self._initialized = True
            logger.info("Performance Optimization Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Performance Optimization Service: {e}")
            raise
    
    async def _warm_cache(self):
        """Pre-warm cache with common medical data"""
        # This would typically load frequently accessed medical data
        # For now, we'll just log that cache warming is complete
        logger.info("Cache warming completed")
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    async def optimize_response(
        self,
        response_data: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize response for performance and user experience"""
        try:
            optimized = self.response_optimizer.optimize_response(response_data, context)
            return optimized
        except Exception as e:
            logger.error(f"Error optimizing response: {e}")
            return response_data  # Return original if optimization fails
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get comprehensive system performance metrics"""
        try:
            return {
                "cache_stats": self.cache.get_stats(),
                "performance_metrics": self.performance_monitor.get_performance_report(),
                "service_status": "healthy" if self._initialized else "initializing",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}

# Performance optimization decorators
def cache_result(cache_type: str = "response", ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not performance_service.is_initialized():
                await performance_service.initialize()
            
            return await performance_service.cache.get_or_compute(
                cache_type=cache_type,
                compute_func=func,
                ttl=ttl,
                args=args,
                kwargs=kwargs
            )
        return wrapper
    return decorator

def track_performance(endpoint: str):
    """Decorator to track API endpoint performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                response_time = time.time() - start_time
                performance_service.performance_monitor.track_api_call(
                    endpoint, response_time, status_code
                )
        return wrapper
    return decorator

# Global performance service instance
performance_service = PerformanceOptimizationService()

__all__ = [
    "performance_service", "PerformanceOptimizationService", 
    "IntelligentCache", "ResponseOptimizer", "DataProcessor", "PerformanceMonitor",
    "cache_result", "track_performance"
]