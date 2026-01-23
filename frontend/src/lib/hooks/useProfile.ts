'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { usersAPI } from '@/lib/api/users';
import { useAuth } from './useAuth';
import type {
  UpdateProfileRequest,
  UpdateBudgetRequest,
  UpdatePreferencesRequest,
  Profile,
} from '@/types';

const QUERY_KEYS = {
  profile: ['profile'] as const,
};

export function useProfile() {
  const { isAuthenticated, updateProfile: updateAuthProfile } = useAuth();
  const queryClient = useQueryClient();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: QUERY_KEYS.profile,
    queryFn: async () => {
      const response = await usersAPI.getProfile();
      return response.profile;
    },
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: UpdateProfileRequest) => usersAPI.updateProfile(data),
    onMutate: async (newData) => {
      await queryClient.cancelQueries({ queryKey: QUERY_KEYS.profile });
      const previousProfile = queryClient.getQueryData<Profile>(QUERY_KEYS.profile);

      if (previousProfile) {
        queryClient.setQueryData<Profile>(QUERY_KEYS.profile, {
          ...previousProfile,
          ...newData,
        });
      }

      return { previousProfile };
    },
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(QUERY_KEYS.profile, updatedProfile);
      updateAuthProfile(updatedProfile);
    },
    onError: (error, variables, context) => {
      if (context?.previousProfile) {
        queryClient.setQueryData(QUERY_KEYS.profile, context.previousProfile);
      }
    },
  });

  const updateBudgetMutation = useMutation({
    mutationFn: (data: UpdateBudgetRequest) => usersAPI.updateBudget(data),
    onMutate: async (newData) => {
      await queryClient.cancelQueries({ queryKey: QUERY_KEYS.profile });
      const previousProfile = queryClient.getQueryData<Profile>(QUERY_KEYS.profile);

      if (previousProfile) {
        queryClient.setQueryData<Profile>(QUERY_KEYS.profile, {
          ...previousProfile,
          ...newData,
        });
      }

      return { previousProfile };
    },
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(QUERY_KEYS.profile, updatedProfile);
      updateAuthProfile(updatedProfile);
    },
    onError: (error, variables, context) => {
      if (context?.previousProfile) {
        queryClient.setQueryData(QUERY_KEYS.profile, context.previousProfile);
      }
    },
  });

  const updatePreferencesMutation = useMutation({
    mutationFn: (data: UpdatePreferencesRequest) => usersAPI.updatePreferences(data),
    onMutate: async (newData) => {
      await queryClient.cancelQueries({ queryKey: QUERY_KEYS.profile });
      const previousProfile = queryClient.getQueryData<Profile>(QUERY_KEYS.profile);

      if (previousProfile) {
        queryClient.setQueryData<Profile>(QUERY_KEYS.profile, {
          ...previousProfile,
          ...newData,
        });
      }

      return { previousProfile };
    },
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(QUERY_KEYS.profile, updatedProfile);
      updateAuthProfile(updatedProfile);
    },
    onError: (error, variables, context) => {
      if (context?.previousProfile) {
        queryClient.setQueryData(QUERY_KEYS.profile, context.previousProfile);
      }
    },
  });

  return {
    profile: data,
    isLoading,
    error,
    refetch,
    updateProfile: updateProfileMutation.mutate,
    updateBudget: updateBudgetMutation.mutate,
    updatePreferences: updatePreferencesMutation.mutate,
    isUpdating:
      updateProfileMutation.isPending ||
      updateBudgetMutation.isPending ||
      updatePreferencesMutation.isPending,
  };
}
