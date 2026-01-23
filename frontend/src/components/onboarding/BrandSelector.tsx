'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productsAPI } from '@/lib/api/products';
import { Spinner } from '@/components/ui/Spinner';
import { Input } from '@/components/ui/Input';

interface BrandSelectorProps {
  initialBrands?: string[];
  onChange: (brands: string[]) => void;
}

export function BrandSelector({
  initialBrands = [],
  onChange,
}: BrandSelectorProps) {
  const [selectedBrands, setSelectedBrands] = useState<string[]>(initialBrands);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: brands, isLoading } = useQuery({
    queryKey: ['brands'],
    queryFn: () => productsAPI.getBrands(),
    staleTime: 10 * 60 * 1000,
  });

  useEffect(() => {
    onChange(selectedBrands);
  }, [selectedBrands, onChange]);

  const toggleBrand = (brand: string) => {
    setSelectedBrands((prev) =>
      prev.includes(brand)
        ? prev.filter((b) => b !== brand)
        : [...prev, brand]
    );
  };

  const filteredBrands = brands?.filter((brand) =>
    brand.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          Select Preferred Brands
        </h3>
        <p className="text-sm text-text-secondary">
          Choose brands you trust or want to explore
        </p>
      </div>

      <Input
        type="text"
        placeholder="Search brands..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      <div className="max-h-96 overflow-y-auto scrollbar-hide">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {filteredBrands?.map((brand) => {
            const isSelected = selectedBrands.includes(brand);
            return (
              <button
                key={brand}
                onClick={() => toggleBrand(brand)}
                className={`p-4 rounded-lg border transition-all duration-200 text-left ${
                  isSelected
                    ? 'bg-purple-structural border-purple-structural-light shadow-glow text-white'
                    : 'glass-card hover:border-purple-structural-light hover:shadow-glow-sm text-text-primary'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{brand}</span>
                  {isSelected && (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {selectedBrands.length > 0 && (
        <div className="glass-card p-4">
          <p className="text-sm text-text-secondary mb-2">
            Selected ({selectedBrands.length}):
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedBrands.map((brand) => (
              <span
                key={brand}
                className="px-3 py-1 bg-purple-structural text-white text-sm rounded-full"
              >
                {brand}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
