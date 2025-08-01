import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { FolderIcon, SettingsIcon, ActivityIcon, CreditCardIcon } from 'lucide-react';

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

interface SpaceSelectorProps {
  currentSpaceId?: string;
  onSpaceChange: (spaceId: string) => void;
  className?: string;
}

export const SpaceSelector: React.FC<SpaceSelectorProps> = ({
  currentSpaceId,
  onSpaceChange,
  className = ""
}) => {
  const [spaces, setSpaces] = useState<TeamSpace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSpaces();
  }, []);

  const fetchSpaces = async () => {
    try {
      setLoading(true);
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
      setSpaces(data.spaces || []);
      
      // Auto-select first space if none selected
      if (!currentSpaceId && data.spaces && data.spaces.length > 0) {
        onSpaceChange(data.spaces[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch spaces');
    } finally {
      setLoading(false);
    }
  };

  const currentSpace = spaces.find(space => space.id === currentSpaceId);

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
        <span className="text-sm text-gray-600">Loading spaces...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`text-red-600 text-sm ${className}`}>
        Error: {error}
      </div>
    );
  }

  if (spaces.length === 0) {
    return (
      <div className={`text-gray-500 text-sm ${className}`}>
        No spaces available
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Space Selector */}
      <div className="flex items-center space-x-2">
        <FolderIcon className="h-4 w-4 text-gray-600" />
        <Select value={currentSpaceId} onValueChange={onSpaceChange}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder="Select workspace..." />
          </SelectTrigger>
          <SelectContent>
            {spaces.map((space) => (
              <SelectItem key={space.id} value={space.id}>
                <div className="flex items-center space-x-2">
                  <FolderIcon className="h-4 w-4" />
                  <span>{space.name}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Current Space Info */}
      {currentSpace && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center space-x-2">
              <FolderIcon className="h-5 w-5" />
              <span>{currentSpace.name}</span>
              <Badge variant="secondary" className="ml-auto">
                {currentSpace.settings.storage.type}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {currentSpace.description && (
              <p className="text-sm text-gray-600">{currentSpace.description}</p>
            )}
            
            {/* Space Stats */}
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <CreditCardIcon className="h-4 w-4 text-gray-500" />
                <span>Budget: ${currentSpace.settings.quotas.monthly_budget}</span>
              </div>
              <div className="flex items-center space-x-2">
                <ActivityIcon className="h-4 w-4 text-gray-500" />
                <span>Limit: {currentSpace.settings.quotas.execution_limit} exec</span>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex space-x-2 pt-2">
              <Button variant="outline" size="sm" className="flex-1">
                <SettingsIcon className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" className="flex-1">
                <ActivityIcon className="h-4 w-4 mr-2" />
                Activity
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}; 