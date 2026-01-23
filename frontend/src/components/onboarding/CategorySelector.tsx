'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productsAPI } from '@/lib/api/products';
import { Spinner } from '@/components/ui/Spinner';

interface CategorySelectorProps {
  initialCategories?: string[];
  onChange: (categories: string[]) => void;
}

export function CategorySelector({
  initialCategories = [],
  onChange,
}: CategorySelectorProps) {
  const [selectedCategories, setSelectedCategories] = useState<string[]>(initialCategories);

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => productsAPI.getCategories(),
    staleTime: 10 * 60 * 1000,
  });

  useEffect(() => {
    onChange(selectedCategories);
  }, [selectedCategories, onChange]);

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  };

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
          Select Product Categories
        </h3>
        <p className="text-sm text-text-secondary">
          Choose the types of products you're interested in
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {categories?.map((category) => {
          const isSelected = selectedCategories.includes(category);
          return (
            <button
              key={category}
              onClick={() => toggleCategory(category)}
              className={`p-4 rounded-lg border transition-all duration-200 text-left ${
                isSelected
                  ? 'bg-purple-structural border-purple-structural-light shadow-glow text-white'
                  : 'glass-card hover:border-purple-structural-light hover:shadow-glow-sm text-text-primary'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium capitalize">{category}</span>
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

      {selectedCategories.length === 0 && (
        <p className="text-sm text-text-muted text-center">
          Select at least one category to continue
        </p>
      )}
    </div>
  );
}
