import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import time
from functools import lru_cache
import logging
from biodb_analyzer.ai.schema_validator import SchemaValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalysisCache:
    """
    Cache system for Ollama analysis results with schema validation
    """
    def __init__(self, 
                 cache_dir: str = "cache", 
                 max_size_mb: int = 500, 
                 max_age_seconds: int = 86400,  # 24 hours
                 confidence_threshold: float = 0.95):
        """
        Initialize the cache
        
        Args:
            cache_dir: Directory to store cached results
            max_size_mb: Maximum cache size in megabytes
            max_age_seconds: Maximum age of cached results in seconds
            confidence_threshold: Minimum confidence level for cached results
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.max_age_seconds = max_age_seconds
        self.confidence_threshold = confidence_threshold
        self._initialize_cache()
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'current_size_mb': 0,
            'invalidations': 0
        }

    def _initialize_cache(self) -> None:
        """Create cache directory if it doesn't exist"""
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, 
                       prompt: str, 
                       analysis_type: str, 
                       schema_hash: str) -> str:
        """
        Generate a unique cache key for the prompt
        
        Args:
            prompt: The prompt to cache
            analysis_type: Type of analysis
            schema_hash: Hash of the database schema
            
        Returns:
            Hashed cache key
        """
        key = f"{analysis_type}_{schema_hash}_{prompt}"
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a given key"""
        return self.cache_dir / f"{key}.json"

    def _check_cache_size(self) -> None:
        """Check and enforce cache size limits"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        current_size_mb = total_size / (1024 * 1024)
        
        if current_size_mb > self.max_size_mb:
            # Implement LRU eviction
            files = sorted(
                self.cache_dir.glob("*.json"),
                key=lambda f: f.stat().st_atime
            )
            
            while current_size_mb > self.max_size_mb:
                oldest_file = files.pop(0)
                oldest_file.unlink()
                current_size_mb = sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / (1024 * 1024)
                self._cache_stats['evictions'] += 1

        self._cache_stats['current_size_mb'] = current_size_mb

    def _is_cache_valid(self, cache_file: Path) -> bool:
        """
        Check if cache entry is still valid based on age and confidence
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_file.exists():
            return False
            
        # Check age
        age = time.time() - cache_file.stat().st_mtime
        if age > self.max_age_seconds:
            return False
            
        try:
            with open(cache_file, 'r') as f:
                result = json.load(f)
                # Check confidence
                if 'confidence' in result and result['confidence'] < self.confidence_threshold:
                    return False
                return True
        except Exception:
            return False

    def get(self, 
            prompt: str, 
            analysis_type: str, 
            schema_validator: SchemaValidator) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result with schema validation
        
        Args:
            prompt: The prompt to retrieve
            analysis_type: Type of analysis
            schema_validator: Schema validator instance
            
        Returns:
            Cached result if available and valid, None otherwise
        """
        schema_hash = hashlib.sha256(str(schema_validator.schema).encode()).hexdigest()
        key = self._get_cache_key(prompt, analysis_type, schema_hash)
        cache_file = self._get_cache_file(key)
        
        if self._is_cache_valid(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    result = json.load(f)
                    self._cache_stats['hits'] += 1
                    return result
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
                cache_file.unlink()
        
        self._cache_stats['misses'] += 1
        return None

    def store(self, 
              prompt: str, 
              analysis_type: str, 
              result: Dict[str, Any], 
              schema_validator: SchemaValidator) -> None:
        """
        Store analysis result in cache with schema validation
        
        Args:
            prompt: The prompt used
            analysis_type: Type of analysis
            result: Analysis result to cache
            schema_validator: Schema validator instance
        """
        schema_hash = hashlib.sha256(str(schema_validator.schema).encode()).hexdigest()
        key = self._get_cache_key(prompt, analysis_type, schema_hash)
        cache_file = self._get_cache_file(key)
        
        try:
            # Add schema validation to result
            result['schema_valid'] = schema_validator.validate_analysis(prompt)
            
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
            self._check_cache_size()
        except Exception as e:
            logger.error(f"Error storing cache: {str(e)}")
            if cache_file.exists():
                cache_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._cache_stats

    def clear(self) -> None:
        """Clear the entire cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        self._cache_stats['current_size_mb'] = 0
        self._cache_stats['evictions'] = 0
        self._cache_stats['invalidations'] = 0
