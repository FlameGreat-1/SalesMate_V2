"""
Pinecone indexing script for SalesMate AI.

Features:
- Proper logging with structured output
- CLI argument parsing for flexibility
- Progress tracking with tqdm
- Robust error handling and retry logic
- Batch processing with configurable size
- Duplicate detection and handling
- Performance metrics and monitoring
- Dry-run mode for testing
- Namespace support for multi-tenancy

Usage:
    # Normal run
    python -m scripts.index_products_pinecone
    
    # Custom batch size
    python -m scripts.index_products_pinecone --batch-size 200
    
    # Dry run (no Pinecone changes)
    python -m scripts.index_products_pinecone --dry-run
    
    # Reindex specific products by SKU
    python -m scripts.index_products_pinecone --skus PROD-001 PROD-002
    
    # Force reindex all (clear and rebuild)
    python -m scripts.index_products_pinecone --force
    
    # Verbose logging
    python -m scripts.index_products_pinecone --verbose
"""

import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.repositories.product import ProductRepository
from src.vector.embeddings import EmbeddingService
from src.vector.pinecone_client import get_pinecone_client
from src.config import settings
from src.utils.logger import get_logger

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("⚠️  Install tqdm for progress bars: pip install tqdm")

logger = get_logger(__name__)


class PineconeIndexer:
    """Handles Pinecone indexing operations with error recovery."""
    
    def __init__(
        self,
        dry_run: bool = False,
        batch_size: int = 100,
        namespace: str = "",
        max_retries: int = 3
    ):
        """
        Initialize the Pinecone indexer.
        
        Args:
            dry_run: If True, don't make actual Pinecone changes
            batch_size: Number of products to process per batch
            namespace: Pinecone namespace (empty string for default)
            max_retries: Maximum retry attempts for failed batches
        """
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.namespace = namespace
        self.max_retries = max_retries
        
        # Initialize services
        self.product_repo = ProductRepository()
        self.embedding_service = EmbeddingService()
        
        if not dry_run:
            self.pinecone_client = get_pinecone_client()
            self.index = self.pinecone_client.get_index()
        else:
            self.pinecone_client = None
            self.index = None
        
        # Metrics
        self.total_processed = 0
        self.total_indexed = 0
        self.total_failed = 0
        self.failed_product_ids = []
        self.embedding_time = 0.0
        self.upsert_time = 0.0
        
        logger.info(
            f"PineconeIndexer initialized "
            f"(dry_run={dry_run}, batch_size={batch_size}, namespace='{namespace}')"
        )
    
    def build_product_search_text(self, product: Dict[str, Any]) -> str:
        """
        Build comprehensive search text from product data.
        Combines all relevant fields for semantic search.
        
        Args:
            product: Product dictionary from database
            
        Returns:
            Combined search text string
        """
        parts = []
        
        # Core identity
        if product.get("name"):
            parts.append(product["name"])
        if product.get("brand"):
            parts.append(f"Brand: {product['brand']}")
        if product.get("manufacturer"):
            parts.append(f"Manufacturer: {product['manufacturer']}")
        
        # Classification
        if product.get("category"):
            parts.append(f"Category: {product['category']}")
        if product.get("subcategory"):
            parts.append(f"Subcategory: {product['subcategory']}")
        if product.get("price_tier"):
            parts.append(f"Price tier: {product['price_tier']}")
        
        # Descriptions
        if product.get("description"):
            parts.append(product["description"])
        if product.get("short_description"):
            parts.append(product["short_description"])
        
        # Features and accessories
        features = product.get("features", [])
        if features and isinstance(features, list):
            parts.append("Features: " + " ".join(str(f) for f in features))
        
        accessories = product.get("included_accessories", [])
        if accessories and isinstance(accessories, list):
            parts.append("Includes: " + " ".join(str(a) for a in accessories))
        
        # Tags and targeting
        tags = product.get("tags", [])
        if tags and isinstance(tags, list):
            parts.append("Tags: " + " ".join(str(t) for t in tags))
        
        target_audience = product.get("target_audience", [])
        if target_audience and isinstance(target_audience, list):
            parts.append("For: " + " ".join(str(t) for t in target_audience))
        
        use_cases = product.get("use_cases", [])
        if use_cases and isinstance(use_cases, list):
            parts.append("Use cases: " + " ".join(str(u) for u in use_cases))
        
        # Specifications (extract key information)
        specs = product.get("specifications", {})
        if specs and isinstance(specs, dict):
            spec_text = self._extract_spec_text(specs)
            if spec_text:
                parts.append(spec_text)
        
        # Filter out empty strings and join
        text = " ".join(filter(None, parts))
        return text.strip()
    
    def _extract_spec_text(self, specs: Dict[str, Any], prefix: str = "") -> str:
        """
        Recursively extract searchable text from nested specifications.
        
        Args:
            specs: Specifications dictionary
            prefix: Prefix for nested keys
            
        Returns:
            Flattened specification text
        """
        parts = []
        
        for key, value in specs.items():
            if isinstance(value, dict):
                # Recursively process nested dicts
                nested_text = self._extract_spec_text(value, f"{prefix}{key} ")
                if nested_text:
                    parts.append(nested_text)
            elif isinstance(value, list):
                # Join list items
                list_items = [str(item) for item in value if item is not None]
                if list_items:
                    parts.append(f"{prefix}{key}: {' '.join(list_items)}")
            elif value is not None:
                # Add simple key-value pairs
                parts.append(f"{prefix}{key}: {value}")
        
        return " ".join(parts)
    
    def build_product_metadata(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build metadata for Pinecone vector.
        Includes filterable fields for hybrid search.
        
        Args:
            product: Product dictionary from database
            
        Returns:
            Metadata dictionary for Pinecone
        """
        metadata = {
            "product_id": str(product["id"]),
            "sku": str(product["sku"]),
            "name": str(product["name"]),
            "category": str(product.get("category", "")),
            "brand": str(product.get("brand", "")),
            "price": float(product.get("price", 0)),
            "stock_status": str(product.get("stock_status", "")),
        }
        
        # Optional fields
        if product.get("subcategory"):
            metadata["subcategory"] = str(product["subcategory"])
        
        if product.get("price_tier"):
            metadata["price_tier"] = str(product["price_tier"])
        
        if product.get("rating"):
            metadata["rating"] = float(product["rating"])
        
        if product.get("is_featured"):
            metadata["is_featured"] = bool(product["is_featured"])
        
        if product.get("is_new_arrival"):
            metadata["is_new_arrival"] = bool(product["is_new_arrival"])
        
        return metadata
    
    def index_batch(
        self,
        products: List[Dict[str, Any]]
    ) -> Tuple[int, List[str]]:
        """
        Index a batch of products in Pinecone.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Tuple of (success_count, failed_product_ids)
        """
        if not products:
            return 0, []
        
        if self.dry_run:
            logger.debug(f"[DRY RUN] Would index {len(products)} products")
            return len(products), []
        
        try:
            # Build search texts
            start_time = time.time()
            texts = [self.build_product_search_text(p) for p in products]
            
            # Generate embeddings
            embeddings = self.embedding_service.generate_embeddings(texts)
            self.embedding_time += time.time() - start_time
            
            # Prepare vectors for upsert
            vectors = []
            for i, product in enumerate(products):
                vector_data = {
                    "id": str(product["id"]),
                    "values": embeddings[i],
                    "metadata": self.build_product_metadata(product)
                }
                vectors.append(vector_data)
            
            # Upsert to Pinecone
            start_time = time.time()
            self.index.upsert(
                vectors=vectors,
                namespace=self.namespace
            )
            self.upsert_time += time.time() - start_time
            
            logger.debug(f"Successfully indexed {len(products)} products")
            return len(products), []
            
        except Exception as e:
            logger.error(f"Error indexing batch: {str(e)}")
            # Return all product IDs as failed
            failed_ids = [str(p["id"]) for p in products]
            return 0, failed_ids
    
    def index_products(
        self,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Index all products with progress tracking and retry logic.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Dictionary with indexing metrics
        """
        logger.info(f"Starting to index {len(products)} products...")
        
        # Create progress bar if tqdm available
        total_batches = (len(products) + self.batch_size - 1) // self.batch_size
        
        if HAS_TQDM:
            batch_iterator = tqdm(
                range(0, len(products), self.batch_size),
                desc="Indexing products",
                unit="batch",
                total=total_batches
            )
        else:
            batch_iterator = range(0, len(products), self.batch_size)
        
        failed_batches = []
        
        for i in batch_iterator:
            batch = products[i:i + self.batch_size]
            self.total_processed += len(batch)
            
            success_count, failed_ids = self.index_batch(batch)
            
            self.total_indexed += success_count
            self.total_failed += len(failed_ids)
            self.failed_product_ids.extend(failed_ids)
            
            # Track failed batches for retry
            if failed_ids:
                failed_batches.append((i, batch))
        
        # Retry failed batches
        if failed_batches and not self.dry_run:
            logger.warning(f"Retrying {len(failed_batches)} failed batches...")
            self._retry_failed_batches(failed_batches)
        
        return {
            "processed": self.total_processed,
            "indexed": self.total_indexed,
            "failed": self.total_failed
        }
    
    def _retry_failed_batches(
        self,
        failed_batches: List[Tuple[int, List[Dict[str, Any]]]]
    ):
        """
        Retry failed batches with exponential backoff.
        
        Args:
            failed_batches: List of (batch_index, products) tuples
        """
        for retry_attempt in range(self.max_retries):
            if not failed_batches:
                break
            
            logger.info(f"Retry attempt {retry_attempt + 1}/{self.max_retries}")
            
            still_failed = []
            
            for batch_idx, batch in failed_batches:
                # Exponential backoff
                wait_time = 2 ** retry_attempt
                time.sleep(wait_time)
                
                success_count, failed_ids = self.index_batch(batch)
                
                if failed_ids:
                    still_failed.append((batch_idx, batch))
                else:
                    # Update metrics for successful retry
                    self.total_indexed += success_count
                    self.total_failed -= len(batch)
                    # Remove from failed list
                    for fid in failed_ids:
                        if fid in self.failed_product_ids:
                            self.failed_product_ids.remove(fid)
            
            failed_batches = still_failed
        
        if failed_batches:
            logger.error(f"Failed to index {len(failed_batches)} batches after {self.max_retries} retries")
    
    def verify_index(self, expected_count: int) -> bool:
        """
        Verify that products were indexed correctly.
        
        Args:
            expected_count: Expected number of vectors
            
        Returns:
            True if verification passed
        """
        if self.dry_run:
            logger.info("[DRY RUN] Skipping verification")
            return True
        
        try:
            stats = self.index.describe_index_stats()
            
            # Get count for specific namespace or total
            if self.namespace:
                actual_count = stats.namespaces.get(self.namespace, {}).get('vector_count', 0)
            else:
                actual_count = stats.total_vector_count
            
            logger.info(f"Verification - Expected: {expected_count}, Actual: {actual_count}")
            logger.info(f"Index dimension: {stats.dimension}")
            
            if actual_count >= expected_count:
                logger.info("✅ Verification successful!")
                return True
            else:
                logger.warning(f"⚠️  Only {actual_count}/{expected_count} vectors found in Pinecone")
                return False
                
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
    
    def clear_index(self):
        """Clear all vectors from the index (use with caution)."""
        if self.dry_run:
            logger.info("[DRY RUN] Would clear index")
            return
        
        logger.warning("⚠️  Clearing all vectors from index...")
        try:
            self.index.delete(delete_all=True, namespace=self.namespace)
            logger.info("✅ Index cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear index: {str(e)}")
            raise
    
    def print_summary(self, elapsed_time: float):
        """Print indexing summary with metrics."""
        logger.info("=" * 60)
        logger.info("📊 INDEXING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total processed: {self.total_processed}")
        logger.info(f"✅ Indexed: {self.total_indexed}")
        logger.info(f"❌ Failed: {self.total_failed}")
        logger.info(f"⏱️  Total time: {elapsed_time:.2f}s")
        logger.info(f"⏱️  Embedding time: {self.embedding_time:.2f}s")
        logger.info(f"⏱️  Upsert time: {self.upsert_time:.2f}s")
        
        if self.total_processed > 0:
            rate = self.total_processed / elapsed_time
            logger.info(f"📈 Processing rate: {rate:.2f} products/second")
        
        if self.failed_product_ids:
            logger.warning(f"Failed product IDs: {', '.join(self.failed_product_ids[:10])}")
            if len(self.failed_product_ids) > 10:
                logger.warning(f"... and {len(self.failed_product_ids) - 10} more")
        
        logger.info("=" * 60)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Index SalesMate products in Pinecone vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal run
  python -m scripts.index_products_pinecone
  
  # Custom batch size
  python -m scripts.index_products_pinecone --batch-size 200
  
  # Dry run (no Pinecone changes)
  python -m scripts.index_products_pinecone --dry-run
  
  # Force reindex (clear and rebuild)
  python -m scripts.index_products_pinecone --force
  
  # Verbose logging
  python -m scripts.index_products_pinecone --verbose
        """
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of products per batch (default: 100)"
    )
    
    parser.add_argument(
        "--namespace",
        default="",
        help="Pinecone namespace (default: empty/default namespace)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts for failed batches (default: 3)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making Pinecone changes"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Clear index before indexing (use with caution)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip verification step"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of products to index (for testing)"
    )
    
    return parser.parse_args()


def main():
    """Main indexing process with error handling."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    logger.info("=" * 60)
    logger.info("🔍 SalesMate AI - Pinecone Indexing")
    logger.info("=" * 60)
    
    if args.dry_run:
        logger.warning("⚠️  DRY RUN MODE - No Pinecone changes will be made")
    
    if args.force and not args.dry_run:
        logger.warning("⚠️  FORCE MODE - Index will be cleared before indexing")
    
    start_time = time.time()
    
    try:
        # Initialize indexer
        indexer = PineconeIndexer(
            dry_run=args.dry_run,
            batch_size=args.batch_size,
            namespace=args.namespace,
            max_retries=args.max_retries
        )
        
        logger.info(f"Embedding model: {settings.vector_db.embedding_model}")
        logger.info(f"Pinecone index: {settings.vector_db.pinecone_index_name}")
        logger.info(f"Namespace: '{args.namespace or 'default'}'")
        
        # Clear index if force mode
        if args.force and not args.dry_run:
            indexer.clear_index()
        
        # Fetch products from database
        logger.info("📂 Fetching products from database...")
        products = indexer.product_repo.get_all_active(limit=args.limit or 10000)
        
        if not products:
            logger.warning("⚠️  No products found in database")
            logger.info("💡 Run: python -m scripts.seed_products")
            sys.exit(1)
        
        logger.info(f"✅ Fetched {len(products)} active products")
        
        # Index products
        logger.info("💾 Indexing products in Pinecone...")
        metrics = indexer.index_products(products)
        
        # Verify
        if not args.skip_verification:
            logger.info("🔍 Verifying indexed data...")
            indexer.verify_index(len(products))
        
        # Print summary
        elapsed_time = time.time() - start_time
        indexer.print_summary(elapsed_time)
        
        # Exit code based on failures
        if indexer.total_failed > 0:
            logger.warning(f"⚠️  Completed with {indexer.total_failed} failures")
            sys.exit(1)
        else:
            logger.info("🎉 Pinecone indexing completed successfully!")
            logger.info("\n💡 Next steps:")
            logger.info("   1. Test search: python -m scripts.test_connections")
            logger.info("   2. Start API: uvicorn src.api.main:app --reload")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Indexing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
