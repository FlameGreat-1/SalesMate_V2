import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { formatCurrency, formatPercentage } from '@/lib/utils/formatters';
import type { Product } from '@/types';

interface ProductCardProps {
  product: Product;
  onClick?: () => void;
}

export function ProductCard({ product, onClick }: ProductCardProps) {
  return (
    <Card hover onClick={onClick} className="max-w-sm">
      <CardContent>
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h4 className="text-base font-semibold text-text-primary mb-1 line-clamp-2">
              {product.name}
            </h4>
            <p className="text-sm text-text-secondary mb-2">
              {product.brand}
            </p>
          </div>
          {product.discount_percentage > 0 && (
            <Badge variant="success" size="sm">
              -{formatPercentage(product.discount_percentage)}
            </Badge>
          )}
        </div>

        <p className="text-sm text-text-secondary mb-4 line-clamp-2">
          {product.short_description}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-text-primary">
              {formatCurrency(product.price, product.currency)}
            </span>
            {product.discount_percentage > 0 && (
              <span className="text-sm text-text-muted line-through">
                {formatCurrency(product.original_price, product.currency)}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-sm text-text-secondary">
              {product.rating.toFixed(1)} ({product.review_count})
            </span>
          </div>
        </div>

        {product.stock_status === 'in_stock' ? (
          <Badge variant="success" size="sm" className="mt-3">
            In Stock
          </Badge>
        ) : (
          <Badge variant="error" size="sm" className="mt-3">
            Out of Stock
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
