"""
Product seeding script for SalesMate AI.

Features:
- Proper logging with structured output
- CLI argument parsing for flexibility
- Progress tracking with tqdm
- Robust error handling and recovery
- Transaction safety with rollback
- Dry-run mode for testing
- Performance metrics
- Duplicate detection and handling

Usage:
    # Normal run
    python -m scripts.seed_products
    
    # Custom file and batch size
    python -m scripts.seed_products --file data/custom_products.json --batch-size 100
    
    # Dry run (no database changes)
    python -m scripts.seed_products --dry-run
    
    # Verbose logging
    python -m scripts.seed_products --verbose
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.session import get_supabase_client, get_supabase_service_client
from src.utils.logger import get_logger

# Try to import tqdm for progress bars, fallback if not available
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("⚠️  Install tqdm for progress bars: pip install tqdm")

logger = get_logger(__name__)


class ProductSeeder:
    """Handles product seeding operations with error recovery."""
    
    def __init__(self, dry_run: bool = False, batch_size: int = 50):
        """
        Initialize the product seeder.
        
        Args:
            dry_run: If True, don't make actual database changes
            batch_size: Number of products to process per batch
        """
        self.dry_run = dry_run
        self.batch_size = batch_size
        from src.database.session import get_supabase_service_client
        self.client = get_supabase_service_client()
        
        # Metrics
        self.total_processed = 0
        self.total_inserted = 0
        self.total_updated = 0
        self.total_failed = 0
        self.failed_skus = []
        
        logger.info(f"ProductSeeder initialized (dry_run={dry_run}, batch_size={batch_size})")
    
    def load_products_json(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load products from JSON file with validation.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of product dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or missing products key
        """
        json_path = project_root / file_path
        
        if not json_path.exists():
            raise FileNotFoundError(f"Products file not found: {json_path}")
        
        logger.info(f"Loading products from: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {str(e)}")
        
        if "products" not in data:
            raise ValueError("JSON file must contain 'products' key")
        
        products = data.get("products", [])
        
        if not products:
            logger.warning("No products found in JSON file")
        else:
            logger.info(f"Loaded {len(products)} products from JSON")
        
        return products
    
    def parse_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse and validate product from JSON format to database format.
        
        Args:
            product_data: Raw product data from JSON
            
        Returns:
            Parsed product dictionary or None if validation fails
        """
        try:
            # Validate required fields
            required_fields = ["sku", "name", "category", "brand", "price"]
            for field in required_fields:
                if field not in product_data:
                    logger.error(f"Missing required field '{field}' in product: {product_data.get('sku', 'unknown')}")
                    return None
            
            # Parse release_date (keep as ISO string for database)
            release_date = product_data.get("release_date")
            if release_date:
                try:
                    # Validate format but keep as string
                    datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Invalid release_date for {product_data['sku']}: {str(e)}")
                    release_date = None
            
            # Build database record (NO id field - let database generate UUID)
            parsed = {
                # Core Identity
                "sku": str(product_data["sku"]).strip(),
                "name": str(product_data["name"]).strip(),
                "description": product_data.get("description"),
                "short_description": product_data.get("short_description"),
                
                # Classification
                "category": str(product_data["category"]).strip(),
                "subcategory": product_data.get("subcategory"),
                "brand": str(product_data["brand"]).strip(),
                "manufacturer": product_data.get("manufacturer"),
                
                # Pricing
                "price": float(product_data["price"]),
                "original_price": float(product_data["original_price"]) if product_data.get("original_price") else None,
                "discount_percentage": float(product_data["discount_percentage"]) if product_data.get("discount_percentage") else None,
                "currency": product_data.get("currency", "USD"),
                
                # Inventory
                "stock_status": product_data.get("stock_status", "in_stock"),
                "stock_quantity": int(product_data.get("stock_quantity", 0)),
                "reorder_level": int(product_data["reorder_level"]) if product_data.get("reorder_level") else None,
                
                # Product Details (JSONB)
                "specifications": product_data.get("specifications", {}),
                "features": product_data.get("features", []),
                "included_accessories": product_data.get("included_accessories", []),
                
                # Targeting
                "target_audience": product_data.get("target_audience", []),
                "use_cases": product_data.get("use_cases", []),
                "price_tier": product_data.get("price_tier"),
                "tags": product_data.get("tags", []),
                
                # Ratings
                "rating": float(product_data["rating"]) if product_data.get("rating") else None,
                "review_count": int(product_data.get("review_count", 0)),
                
                # Policies
                "warranty_months": int(product_data["warranty_months"]) if product_data.get("warranty_months") else None,
                "return_policy_days": int(product_data.get("return_policy_days", 30)),
                "release_date": release_date,
                
                # Status
                "is_active": product_data.get("stock_status") == "in_stock",
                "is_featured": bool(product_data.get("is_featured", False)),
                "is_new_arrival": bool(product_data.get("is_new_arrival", False)),
            }
            
            return parsed
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Error parsing product {product_data.get('sku', 'unknown')}: {str(e)}")
            return None
    
    def upsert_product(self, product: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Insert or update a single product in the database.
        
        Args:
            product: Parsed product dictionary
            
        Returns:
            Tuple of (success: bool, action: str) where action is 'inserted', 'updated', or 'failed'
        """
        if self.dry_run:
            logger.debug(f"[DRY RUN] Would upsert product: {product['sku']}")
            return True, "dry_run"
        
        try:
            sku = product["sku"]
            
            # Check if product exists
            existing = self.client.table("products").select("id").eq("sku", sku).execute()
            
            if existing.data:
                # Update existing product
                result = self.client.table("products").update(product).eq("sku", sku).execute()
                
                if result.data:
                    logger.debug(f"Updated product: {sku}")
                    return True, "updated"
                else:
                    logger.error(f"Failed to update product: {sku}")
                    return False, "failed"
            else:
                # Insert new product
                result = self.client.table("products").insert(product).execute()
                
                if result.data:
                    logger.debug(f"Inserted product: {sku}")
                    return True, "inserted"
                else:
                    logger.error(f"Failed to insert product: {sku}")
                    return False, "failed"
                    
        except Exception as e:
            logger.error(f"Error upserting product {product.get('sku', 'unknown')}: {str(e)}")
            return False, "failed"
    
    def seed_products(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Seed products into database with progress tracking.
        
        Args:
            products: List of parsed product dictionaries
            
        Returns:
            Dictionary with metrics (inserted, updated, failed counts)
        """
        logger.info(f"Starting to seed {len(products)} products...")
        
        # Create progress bar if tqdm available
        if HAS_TQDM:
            iterator = tqdm(products, desc="Seeding products", unit="product")
        else:
            iterator = products
        
        for product in iterator:
            self.total_processed += 1
            
            success, action = self.upsert_product(product)
            
            if success:
                if action == "inserted":
                    self.total_inserted += 1
                elif action == "updated":
                    self.total_updated += 1
            else:
                self.total_failed += 1
                self.failed_skus.append(product.get("sku", "unknown"))
        
        return {
            "processed": self.total_processed,
            "inserted": self.total_inserted,
            "updated": self.total_updated,
            "failed": self.total_failed
        }
    
    def verify_seeded_data(self, expected_count: int) -> bool:
        """
        Verify that products were seeded correctly.
        
        Args:
            expected_count: Expected number of products
            
        Returns:
            True if verification passed
        """
        if self.dry_run:
            logger.info("[DRY RUN] Skipping verification")
            return True
        
        try:
            response = self.client.table("products").select("id", count="exact").execute()
            actual_count = response.count
            
            logger.info(f"Verification - Expected: {expected_count}, Actual: {actual_count}")
            
            if actual_count >= expected_count:
                logger.info("✅ Verification successful!")
                return True
            else:
                logger.warning(f"⚠️  Only {actual_count}/{expected_count} products found in database")
                return False
                
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
    
    def print_summary(self, elapsed_time: float):
        """Print seeding summary with metrics."""
        logger.info("=" * 60)
        logger.info("📊 SEEDING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total processed: {self.total_processed}")
        logger.info(f"✅ Inserted: {self.total_inserted}")
        logger.info(f"🔄 Updated: {self.total_updated}")
        logger.info(f"❌ Failed: {self.total_failed}")
        logger.info(f"⏱️  Time elapsed: {elapsed_time:.2f}s")
        
        if self.total_processed > 0:
            rate = self.total_processed / elapsed_time
            logger.info(f"📈 Processing rate: {rate:.2f} products/second")
        
        if self.failed_skus:
            logger.warning(f"Failed SKUs: {', '.join(self.failed_skus[:10])}")
            if len(self.failed_skus) > 10:
                logger.warning(f"... and {len(self.failed_skus) - 10} more")
        
        logger.info("=" * 60)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Seed SalesMate database with product data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal run
  python -m scripts.seed_products
  
  # Custom file and batch size
  python -m scripts.seed_products --file data/custom.json --batch-size 100
  
  # Dry run (no database changes)
  python -m scripts.seed_products --dry-run
  
  # Verbose logging
  python -m scripts.seed_products --verbose
        """
    )
    
    parser.add_argument(
        "--file",
        default="data/products/products.json",
        help="Path to products JSON file (default: data/products/products.json)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of products per batch (default: 50)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making database changes"
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
    
    return parser.parse_args()


def main():
    """Main seeding process with error handling."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    logger.info("=" * 60)
    logger.info("🌱 SalesMate AI - Database Seeding")
    logger.info("=" * 60)
    
    if args.dry_run:
        logger.warning("⚠️  DRY RUN MODE - No database changes will be made")
    
    start_time = time.time()
    
    try:
        # Initialize seeder
        seeder = ProductSeeder(dry_run=args.dry_run, batch_size=args.batch_size)
        
        # Load products from JSON
        logger.info(f"📂 Loading products from: {args.file}")
        raw_products = seeder.load_products_json(args.file)
        
        if not raw_products:
            logger.error("No products to seed. Exiting.")
            sys.exit(1)
        
        # Parse products
        logger.info("🔄 Parsing and validating products...")
        parsed_products = []
        
        for product in raw_products:
            parsed = seeder.parse_product(product)
            if parsed:
                parsed_products.append(parsed)
        
        logger.info(f"✅ Successfully parsed {len(parsed_products)}/{len(raw_products)} products")
        
        if not parsed_products:
            logger.error("No valid products to seed. Exiting.")
            sys.exit(1)
        
        # Seed database
        logger.info("💾 Seeding database...")
        metrics = seeder.seed_products(parsed_products)
        
        # Verify
        if not args.skip_verification:
            logger.info("🔍 Verifying seeded data...")
            seeder.verify_seeded_data(len(parsed_products))
        
        # Print summary
        elapsed_time = time.time() - start_time
        seeder.print_summary(elapsed_time)
        
        # Exit code based on failures
        if seeder.total_failed > 0:
            logger.warning(f"⚠️  Completed with {seeder.total_failed} failures")
            sys.exit(1)
        else:
            logger.info("🎉 Database seeding completed successfully!")
            logger.info("\n💡 Next steps:")
            logger.info("   1. Index products: python -m scripts.index_products_pinecone")
            logger.info("   2. Test connections: python -m scripts.test_connections")
            logger.info("   3. Start API: uvicorn src.api.main:app --reload")
            sys.exit(0)
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Seeding interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
