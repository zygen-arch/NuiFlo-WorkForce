import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface TeamSpace {
  id: string;
  team_id: number;
  name: string;
  description?: string;
  settings: {
    storage: {
      type: string;
      size_gb: number;
    };
    quotas: {
      monthly_budget: number;
      execution_limit: number;
    };
  };
  storage_config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface SpaceContextType {
  currentSpace: TeamSpace | null;
  availableSpaces: TeamSpace[];
  switchSpace: (spaceId: string) => void;
  refreshSpaces: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

const SpaceContext = createContext<SpaceContextType | undefined>(undefined);

interface SpaceProviderProps {
  children: ReactNode;
}

export const SpaceProvider: React.FC<SpaceProviderProps> = ({ children }) => {
  const [currentSpace, setCurrentSpace] = useState<TeamSpace | null>(null);
  const [availableSpaces, setAvailableSpaces] = useState<TeamSpace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSpaces = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/v1/spaces/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch spaces');
      }

      const data = await response.json();
      const spaces = data.spaces || [];
      setAvailableSpaces(spaces);
      
      // Auto-select first space if none selected
      if (!currentSpace && spaces.length > 0) {
        setCurrentSpace(spaces[0]);
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch spaces');
      console.error('Error fetching spaces:', err);
    } finally {
      setLoading(false);
    }
  };

  const switchSpace = (spaceId: string) => {
    const space = availableSpaces.find(s => s.id === spaceId);
    if (space) {
      setCurrentSpace(space);
      // Store in localStorage for persistence
      localStorage.setItem('current_space_id', spaceId);
    }
  };

  const refreshSpaces = async () => {
    await fetchSpaces();
  };

  useEffect(() => {
    fetchSpaces();
  }, []);

  useEffect(() => {
    // Restore current space from localStorage
    const savedSpaceId = localStorage.getItem('current_space_id');
    if (savedSpaceId && availableSpaces.length > 0) {
      const space = availableSpaces.find(s => s.id === savedSpaceId);
      if (space) {
        setCurrentSpace(space);
      }
    }
  }, [availableSpaces]);

  const value: SpaceContextType = {
    currentSpace,
    availableSpaces,
    switchSpace,
    refreshSpaces,
    loading,
    error,
  };

  return (
    <SpaceContext.Provider value={value}>
      {children}
    </SpaceContext.Provider>
  );
};

export const useSpace = (): SpaceContextType => {
  const context = useContext(SpaceContext);
  if (context === undefined) {
    throw new Error('useSpace must be used within a SpaceProvider');
  }
  return context;
};

// Hook for space-aware API calls
export const useSpaceApi = () => {
  const { currentSpace } = useSpace();
  
  const spaceApi = {
    get: async (endpoint: string) => {
      if (!currentSpace) {
        throw new Error('No space selected');
      }
      
      const response = await fetch(`/api/v1/spaces/${currentSpace.id}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      return response.json();
    },
    
    post: async (endpoint: string, data: any) => {
      if (!currentSpace) {
        throw new Error('No space selected');
      }
      
      const response = await fetch(`/api/v1/spaces/${currentSpace.id}${endpoint}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      return response.json();
    },
    
    put: async (endpoint: string, data: any) => {
      if (!currentSpace) {
        throw new Error('No space selected');
      }
      
      const response = await fetch(`/api/v1/spaces/${currentSpace.id}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      return response.json();
    },
    
    delete: async (endpoint: string) => {
      if (!currentSpace) {
        throw new Error('No space selected');
      }
      
      const response = await fetch(`/api/v1/spaces/${currentSpace.id}${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      return response.json();
    },
  };
  
  return spaceApi;
}; 