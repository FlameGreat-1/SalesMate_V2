'use client';

import { useState, useEffect } from 'react';
import { formatCurrency } from '@/lib/utils/formatters';
import { validateBudget } from '@/lib/utils/validators';

interface BudgetSelectorProps {
  initialMin?: number;
  initialMax?: number;
  onChange: (min: number, max: number) => void;
}

export function BudgetSelector({
  initialMin = 500,
  initialMax = 2000,
  onChange,
}: BudgetSelectorProps) {
  const [minBudget, setMinBudget] = useState(initialMin);
  const [maxBudget, setMaxBudget] = useState(initialMax);
  const [error, setError] = useState<string | null>(null);

  const MIN_VALUE = 0;
  const MAX_VALUE = 10000;

  useEffect(() => {
    const validation = validateBudget(minBudget, maxBudget);
    if (!validation.isValid) {
      setError(validation.error || null);
    } else {
      setError(null);
      onChange(minBudget, maxBudget);
    }
  }, [minBudget, maxBudget, onChange]);

  const handleMinChange = (value: number) => {
    setMinBudget(value);
  };

  const handleMaxChange = (value: number) => {
    setMaxBudget(value);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          Set Your Budget Range
        </h3>
        <p className="text-sm text-text-secondary">
          Help us find products within your price range
        </p>
      </div>

      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="text-center">
            <p className="text-sm text-text-secondary mb-1">Minimum</p>
            <p className="text-2xl font-bold text-text-primary">
              {formatCurrency(minBudget)}
            </p>
          </div>
          <div className="text-text-muted">—</div>
          <div className="text-center">
            <p className="text-sm text-text-secondary mb-1">Maximum</p>
            <p className="text-2xl font-bold text-text-primary">
              {formatCurrency(maxBudget)}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Minimum Budget
            </label>
            <input
              type="range"
              min={MIN_VALUE}
              max={MAX_VALUE}
              step={50}
              value={minBudget}
              onChange={(e) => handleMinChange(Number(e.target.value))}
              className="w-full h-2 bg-glass rounded-lg appearance-none cursor-pointer accent-purple-structural"
            />
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Maximum Budget
            </label>
            <input
              type="range"
              min={MIN_VALUE}
              max={MAX_VALUE}
              step={50}
              value={maxBudget}
              onChange={(e) => handleMaxChange(Number(e.target.value))}
              className="w-full h-2 bg-glass rounded-lg appearance-none cursor-pointer accent-purple-structural"
            />
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
