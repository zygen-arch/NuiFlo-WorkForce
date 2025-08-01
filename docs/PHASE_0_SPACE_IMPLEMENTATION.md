# 🔥 PHASE 0: Team Spaces Foundation - Implementation Plan

**CRITICAL: Must complete before major team feature development to avoid retrofit pain**

---

## 🎯 **Why Phase 0 is Blocking**

### **Current Risk:**
- Existing team features are built without space awareness
- Adding spaces later = massive refactoring of:
  - Database relationships
  - API endpoints
  - RLS policies
  - Frontend components
  - Business logic

### **Phase 0 Solution:**
- Add space foundation NOW while team features are still basic
- All future development is space-native from start
- Clean migration path for existing data

---

## 📊 **Current State Analysis**

### **✅ What We Have (Space-Agnostic):**
- Basic team CRUD operations
- Role management within teams
- Team execution framework
- User authentication
- Simple RLS based on team ownership

### **🔄 What Needs Space Migration:**
```
Database Tables:     teams, roles, team_executions, task_executions
API Endpoints:       All /api/v1/teams/* endpoints  
RLS Policies:        All ownership-based policies
Frontend:            Team list, team detail, team creation
Business Logic:      Team service, execution service
```

---

## 🏗️ **Phase 0 Implementation Steps**

### **Step 1: Database Schema Migration (Week 1)**

#### **1.1 Create Team Spaces Table:**
```sql
-- Create team_spaces table
CREATE TABLE team_spaces (
    id VARCHAR(50) PRIMARY KEY DEFAULT ('space_' || generate_random_uuid()),
    team_id INTEGER UNIQUE NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    settings JSONB DEFAULT '{
        "storage": {"type": "local", "size_gb": 10},
        "quotas": {"monthly_budget": 500, "execution_limit": 1000},
        "permissions": {"default_agent_access": ["read", "write"]}
    }',
    storage_config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_team_spaces_team_id ON team_spaces(team_id);
CREATE INDEX idx_team_spaces_created_at ON team_spaces(created_at);
```

#### **1.2 Add Space ID to Existing Tables:**
```sql
-- Add space_id columns (nullable first for migration)
ALTER TABLE teams ADD COLUMN space_id VARCHAR(50);
ALTER TABLE roles ADD COLUMN space_id VARCHAR(50);
ALTER TABLE team_executions ADD COLUMN space_id VARCHAR(50);
ALTER TABLE task_executions ADD COLUMN space_id VARCHAR(50);

-- Add indexes
CREATE INDEX idx_teams_space_id ON teams(space_id);
CREATE INDEX idx_roles_space_id ON roles(space_id);
CREATE INDEX idx_team_executions_space_id ON team_executions(space_id);
CREATE INDEX idx_task_executions_space_id ON task_executions(space_id);
```

#### **1.3 Data Migration Script:**
```sql
-- Create spaces for existing teams
INSERT INTO team_spaces (id, team_id, name, settings)
SELECT 
    'space_' || t.id,
    t.id,
    t.name || ' Space',
    jsonb_build_object(
        'storage', jsonb_build_object('type', 'local', 'size_gb', 10),
        'quotas', jsonb_build_object('monthly_budget', t.monthly_budget, 'execution_limit', 1000)
    )
FROM teams t;

-- Update existing records with space_id
UPDATE teams SET space_id = 'space_' || id;
UPDATE roles SET space_id = (SELECT space_id FROM teams WHERE teams.id = roles.team_id);
UPDATE team_executions SET space_id = (SELECT space_id FROM teams WHERE teams.id = team_executions.team_id);
UPDATE task_executions SET space_id = (SELECT space_id FROM team_executions WHERE team_executions.id = task_executions.team_execution_id);

-- Make space_id NOT NULL after migration
ALTER TABLE teams ALTER COLUMN space_id SET NOT NULL;
ALTER TABLE roles ALTER COLUMN space_id SET NOT NULL;
ALTER TABLE team_executions ALTER COLUMN space_id SET NOT NULL;
ALTER TABLE task_executions ALTER COLUMN space_id SET NOT NULL;

-- Add foreign key constraints
ALTER TABLE teams ADD CONSTRAINT fk_teams_space_id FOREIGN KEY (space_id) REFERENCES team_spaces(id);
ALTER TABLE roles ADD CONSTRAINT fk_roles_space_id FOREIGN KEY (space_id) REFERENCES team_spaces(id);
ALTER TABLE team_executions ADD CONSTRAINT fk_team_executions_space_id FOREIGN KEY (space_id) REFERENCES team_spaces(id);
ALTER TABLE task_executions ADD CONSTRAINT fk_task_executions_space_id FOREIGN KEY (space_id) REFERENCES team_spaces(id);
```

### **Step 2: Update RLS Policies (Week 1)**

#### **2.1 Space-Based RLS Policies:**
```sql
-- Drop existing team-based policies
DROP POLICY IF EXISTS "Users can view own teams" ON teams;
DROP POLICY IF EXISTS "Users can modify own teams" ON teams;
-- ... drop all existing policies

-- Create space-aware policies
CREATE POLICY "Users can access teams in their spaces" ON teams
FOR ALL USING (
    space_id IN (
        SELECT ts.id FROM team_spaces ts
        JOIN teams t ON ts.team_id = t.id
        WHERE t.auth_owner_id = auth.uid()
    )
);

CREATE POLICY "Users can access roles in their spaces" ON roles
FOR ALL USING (
    space_id IN (
        SELECT ts.id FROM team_spaces ts
        JOIN teams t ON ts.team_id = t.id
        WHERE t.auth_owner_id = auth.uid()
    )
);

-- Similar policies for executions
CREATE POLICY "Users can access executions in their spaces" ON team_executions
FOR ALL USING (
    space_id IN (
        SELECT ts.id FROM team_spaces ts
        JOIN teams t ON ts.team_id = t.id
        WHERE t.auth_owner_id = auth.uid()
    )
);

CREATE POLICY "Users can access task executions in their spaces" ON task_executions
FOR ALL USING (
    space_id IN (
        SELECT ts.id FROM team_spaces ts
        JOIN teams t ON ts.team_id = t.id
        WHERE t.auth_owner_id = auth.uid()
    )
);

-- Space management policies
CREATE POLICY "Users can manage their team spaces" ON team_spaces
FOR ALL USING (
    team_id IN (
        SELECT id FROM teams WHERE auth_owner_id = auth.uid()
    )
);
```

### **Step 3: Backend API Migration (Week 2)**

#### **3.1 Space Models:**
```python
# workforce_api/workforce_api/models/space.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class TeamSpace(Base):
    __tablename__ = "team_spaces"
    
    id = Column(String(50), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    settings = Column(JSON, default={})
    storage_config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="space", uselist=False)
```

#### **3.2 Update Team Model:**
```python
# workforce_api/workforce_api/models/team.py
class Team(Base):
    __tablename__ = "teams"
    
    # ... existing fields
    space_id = Column(String(50), ForeignKey("team_spaces.id"), nullable=False)
    
    # Relationships
    space = relationship("TeamSpace", back_populates="team", uselist=False)
    # ... existing relationships
```

#### **3.3 Space-Aware Team Service:**
```python
# workforce_api/workforce_api/services/team_service.py
class TeamService:
    @staticmethod
    def create_team_with_space(team_data: TeamCreate, user_id: str, db: Session):
        """Create team and associated space together"""
        
        # Create team
        team = Team(
            name=team_data.name,
            description=team_data.description,
            monthly_budget=team_data.monthly_budget,
            auth_owner_id=user_id
        )
        db.add(team)
        db.flush()  # Get team.id
        
        # Create associated space
        space = TeamSpace(
            id=f"space_{team.id}",
            team_id=team.id,
            name=f"{team_data.name} Space",
            settings={
                "storage": {"type": "local", "size_gb": 10},
                "quotas": {"monthly_budget": float(team_data.monthly_budget)},
            }
        )
        db.add(space)
        
        # Link team to space
        team.space_id = space.id
        
        # Create roles with space_id
        for role_data in team_data.roles:
            role = Role(
                team_id=team.id,
                space_id=space.id,  # Add space_id
                title=role_data.title,
                # ... other fields
            )
            db.add(role)
        
        db.commit()
        return team
```

#### **3.4 Space API Endpoints:**
```python
# workforce_api/workforce_api/api/v1/spaces.py
from fastapi import APIRouter, Depends, HTTPException
from ...models.space import TeamSpace
from ...core.auth import get_current_user

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.get("/{space_id}")
def get_space(space_id: str, current_user = Depends(get_current_user)):
    """Get space details"""
    pass

@router.put("/{space_id}/storage")
def configure_space_storage(space_id: str, storage_config: dict):
    """Configure external storage for space"""
    pass

@router.get("/{space_id}/billing")
def get_space_billing(space_id: str):
    """Get space billing and usage metrics"""
    pass
```

### **Step 4: Frontend Migration (Week 2-3)**

#### **4.1 Space Context Provider:**
```typescript
// src/contexts/SpaceContext.tsx
interface SpaceContextType {
  currentSpace: TeamSpace | null;
  availableSpaces: TeamSpace[];
  switchSpace: (spaceId: string) => void;
  loading: boolean;
}

export const SpaceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentSpace, setCurrentSpace] = useState<TeamSpace | null>(null);
  const [availableSpaces, setAvailableSpaces] = useState<TeamSpace[]>([]);
  
  // Load user's accessible spaces
  useEffect(() => {
    loadUserSpaces();
  }, []);
  
  return (
    <SpaceContext.Provider value={{ currentSpace, availableSpaces, switchSpace }}>
      {children}
    </SpaceContext.Provider>
  );
};
```

#### **4.2 Space Selector Component:**
```typescript
// src/components/SpaceSelector.tsx
export const SpaceSelector: React.FC = () => {
  const { currentSpace, availableSpaces, switchSpace } = useSpace();
  
  return (
    <Select
      value={currentSpace?.id}
      onValueChange={switchSpace}
      placeholder="Select workspace..."
    >
      {availableSpaces.map(space => (
        <SelectItem key={space.id} value={space.id}>
          <div className="flex items-center space-x-2">
            <FolderIcon className="w-4 h-4" />
            <span>{space.name}</span>
          </div>
        </SelectItem>
      ))}
    </Select>
  );
};
```

#### **4.3 Update Team API Calls:**
```typescript
// src/api/workforceApi.ts
export const workforceApi = {
  // Space-aware team operations
  async getTeamsInSpace(spaceId: string): Promise<Team[]> {
    return apiClient.get(`/api/v1/spaces/${spaceId}/teams`);
  },
  
  async createTeamInSpace(spaceId: string, teamData: TeamCreate): Promise<Team> {
    return apiClient.post(`/api/v1/spaces/${spaceId}/teams`, teamData);
  },
  
  // Space management
  async getSpace(spaceId: string): Promise<TeamSpace> {
    return apiClient.get(`/api/v1/spaces/${spaceId}`);
  },
  
  async configureSpaceStorage(spaceId: string, config: StorageConfig): Promise<void> {
    return apiClient.put(`/api/v1/spaces/${spaceId}/storage`, config);
  }
};
```

---

## 🧪 **Phase 0 Testing Strategy**

### **Migration Testing:**
- ✅ **Data Integrity**: Verify all existing teams have spaces
- ✅ **RLS Security**: Confirm users can't access other users' spaces
- ✅ **API Compatibility**: Existing endpoints still work
- ✅ **Frontend Functionality**: Current UI works with space context

### **New Feature Testing:**
- ✅ **Space Creation**: New teams automatically get spaces
- ✅ **Space Isolation**: Data doesn't leak between spaces
- ✅ **Space Management**: Can configure space settings
- ✅ **Performance**: No significant slowdown from space queries

---

## 🎯 **Phase 0 Success Criteria**

### **✅ Migration Complete When:**
1. All existing teams have associated spaces
2. All API endpoints are space-aware
3. RLS policies enforce space boundaries
4. Frontend has space selector and context
5. No functionality regression from pre-space state

### **✅ Ready for Phase 1 When:**
1. Space foundation is solid and tested
2. New team features can be built space-native
3. Storage configuration framework is ready
4. Billing can be easily associated with spaces

---

**The key insight: Spending 2-3 weeks on Phase 0 saves months of refactoring later and enables all advanced features to be built correctly from the start.** 🚀 