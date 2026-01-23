'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { useProfile } from '@/lib/hooks/useProfile';
import { BudgetSelector } from '@/components/onboarding/BudgetSelector';
import { CategorySelector } from '@/components/onboarding/CategorySelector';
import { BrandSelector } from '@/components/onboarding/BrandSelector';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { storage } from '@/lib/utils/storage';

export default function PreferencesPage() {
  const [step, setStep] = useState(1);
  const [budgetMin, setBudgetMin] = useState(500);
  const [budgetMax, setBudgetMax] = useState(2000);
  const [categories, setCategories] = useState<string[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { updateBudget, updatePreferences, isUpdating } = useProfile();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  const handleBudgetChange = (min: number, max: number) => {
    setBudgetMin(min);
    setBudgetMax(max);
  };

  const handleNext = () => {
    if (step === 1) {
      if (budgetMin >= budgetMax) {
        setError('Invalid budget range');
        return;
      }
      setError(null);
      setStep(2);
    } else if (step === 2) {
      if (categories.length === 0) {
        setError('Please select at least one category');
        return;
      }
      setError(null);
      setStep(3);
    }
  };

  const handleBack = () => {
    setError(null);
    setStep(step - 1);
  };

  const handleComplete = async () => {
    if (brands.length === 0) {
      setError('Please select at least one brand');
      return;
    }

    setError(null);

    try {
      await updateBudget({ budget_min: budgetMin, budget_max: budgetMax });
      await updatePreferences({
        preferred_categories: categories,
        preferred_brands: brands,
      });

      storage.setOnboardingComplete(true);
      router.push('/chat');
    } catch (err: any) {
      setError(err?.message || 'Failed to save preferences');
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-3xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gradient mb-2">Set Your Preferences</h1>
          <p className="text-text-secondary">
            Help us personalize your shopping experience
          </p>
        </div>

        <div className="mb-8">
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-2 rounded-full transition-all duration-300 ${
                  s === step
                    ? 'w-12 bg-purple-structural'
                    : s < step
                    ? 'w-8 bg-purple-structural/50'
                    : 'w-8 bg-glass'
                }`}
              />
            ))}
          </div>
          <p className="text-center text-sm text-text-muted mt-3">
            Step {step} of 3
          </p>
        </div>

        <div className="glass-card p-8 mb-6">
          {step === 1 && (
            <BudgetSelector
              initialMin={budgetMin}
              initialMax={budgetMax}
              onChange={handleBudgetChange}
            />
          )}

          {step === 2 && (
            <CategorySelector
              initialCategories={categories}
              onChange={setCategories}
            />
          )}

          {step === 3 && (
            <BrandSelector initialBrands={brands} onChange={setBrands} />
          )}

          {error && (
            <div className="mt-6 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          {step > 1 ? (
            <Button variant="ghost" onClick={handleBack} disabled={isUpdating}>
              Back
            </Button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <Button variant="primary" onClick={handleNext}>
              Next
            </Button>
          ) : (
            <Button
              variant="primary"
              onClick={handleComplete}
              isLoading={isUpdating}
            >
              Complete Setup
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
