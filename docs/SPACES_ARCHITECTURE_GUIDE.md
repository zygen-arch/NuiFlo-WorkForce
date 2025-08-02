# Team Spaces Architecture Guide

## 🏗️ **Conceptual Overview**

### **What is a Team Space?**
A **Team Space** is a virtual boundary that defines the scope of AI agent operations, resource management, and collaboration within NuiFlo WorkForce. Think of it as a "workspace" or "project environment" where teams operate.

### **Why Team Spaces?**
- **Resource Isolation**: Each space has its own storage, quotas, and settings
- **Security Boundaries**: Agents can only access resources within their assigned space
- **Scalability**: Multiple teams can operate independently
- **Cost Management**: Track usage and budgets per space
- **Future-Proofing**: Foundation for advanced features (S3 storage, cross-space references)

## 🎯 **Core Concepts**

### **Space Hierarchy**
```
User Account
├── Space A (Team Alpha)
│   ├── Teams: [Team Alpha]
│   ├── Roles: [Developer, Tester, Manager]
│   ├── Storage: 10GB local + S3 bucket
│   └── Quotas: $500/month, 1000 executions
└── Space B (Team Beta)
    ├── Teams: [Team Beta]
    ├── Roles: [Analyst, Researcher]
    ├── Storage: 5GB local
    └── Quotas: $200/month, 500 executions
```

### **Space-Aware Operations**
- **Teams**: Belong to a specific space
- **Roles**: Scoped to a space
- **Executions**: Tracked within space context
- **Storage**: Isolated per space
- **Billing**: Aggregated per space

## 🔌 **API Endpoints Overview**

### **Space Management APIs**

#### **1. Get User Spaces**
```http
GET /api/v1/spaces/
```
**Purpose**: List all spaces accessible to the current user
**Context**: Dashboard overview, space switching
**Response**: List of spaces with basic info (name, description, status)

#### **2. Get Specific Space**
```http
GET /api/v1/spaces/{space_id}
```
**Purpose**: Get detailed information about a specific space
**Context**: Space settings page, space details view
**Response**: Full space configuration (settings, storage, quotas)

#### **3. Update Space**
```http
PUT /api/v1/spaces/{space_id}
```
**Purpose**: Update space configuration (name, description, settings)
**Context**: Space settings page, admin panel
**Response**: Updated space information

#### **4. Configure Storage**
```http
PUT /api/v1/spaces/{space_id}/storage
```
**Purpose**: Configure external storage (S3, Azure) for the space
**Context**: Advanced space settings, storage management
**Response**: Updated storage configuration

#### **5. Get Space Billing**
```http
GET /api/v1/spaces/{space_id}/billing
```
**Purpose**: Get usage and billing information for the space
**Context**: Billing dashboard, cost tracking
**Response**: Usage metrics, cost breakdown

#### **6. Get Space Activity**
```http
GET /api/v1/spaces/{space_id}/activity
```
**Purpose**: Get recent activity and executions within the space
**Context**: Activity feed, monitoring dashboard
**Response**: List of recent activities, executions, events

#### **7. Delete Space**
```http
DELETE /api/v1/spaces/{space_id}
```
**Purpose**: Delete a space and all its associated data
**Context**: Admin panel, space management
**Response**: 204 No Content

## 🎨 **Frontend Integration Points**

### **1. Space Context Provider**
**Purpose**: Global state management for the currently selected space
**Key Functions**:
- `currentSpaceId`: Currently active space
- `setCurrentSpaceId()`: Switch between spaces
- `refreshSpaces()`: Reload space list
- `currentSpace`: Full space object

### **2. Space Selector Component**
**Purpose**: UI for switching between available spaces
**Features**:
- Dropdown with space list
- Current space indicator
- Space creation button
- Quick space info display

### **3. Space-Aware Components**
**Pattern**: All team/role/execution components should be space-aware
**Implementation**:
- Pass `spaceId` to API calls
- Filter data by current space
- Show space context in UI
- Handle space switching gracefully

## 🔄 **Data Flow Architecture**

### **Space Selection Flow**
```
User selects space
    ↓
SpaceContext updates currentSpaceId
    ↓
All API calls include space context
    ↓
Components re-render with space-filtered data
    ↓
UI shows space-specific information
```

### **API Call Pattern**
```typescript
// All API calls should include space context
const response = await fetch(`/api/v1/teams/?space_id=${currentSpaceId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## 🎯 **Key Implementation Considerations**

### **1. Space Switching**
- **Preserve State**: Don't lose user's work when switching spaces
- **Clear Context**: Reset team/role data when switching
- **Loading States**: Show loading while fetching space data
- **Error Handling**: Handle cases where user loses access to space

### **2. Space Permissions**
- **Access Control**: Users may have different permissions per space
- **Admin Functions**: Some users can manage space settings
- **Read-Only**: Some users may only view space data
- **Graceful Degradation**: Hide features user can't access

### **3. Space Creation**
- **Onboarding Flow**: Guide users through space setup
- **Default Settings**: Provide sensible defaults
- **Validation**: Ensure space names are unique per user
- **Templates**: Offer space templates for common use cases

### **4. Space Management**
- **Settings Page**: Comprehensive space configuration
- **Storage Management**: External storage setup
- **Billing Dashboard**: Usage tracking and cost management
- **Activity Monitoring**: Real-time space activity

## 🚀 **Future Integration Points**

### **Phase 2: Enhanced Team Management**
- Teams will be space-scoped
- Team creation will automatically assign to current space
- Team settings will include space-specific configurations

### **Phase 3: Advanced Storage**
- S3/Azure integration per space
- Large dataset handling
- Cross-space data sharing (optional)

### **Phase 4: Vision-to-Team**
- Space-aware vision processing
- Space-specific AI model configurations
- Cross-space collaboration features

## 📊 **Monitoring & Analytics**

### **Space Metrics**
- **Usage**: API calls, executions, storage used
- **Performance**: Response times, error rates
- **Cost**: Token usage, external API costs
- **Activity**: User actions, team interactions

### **Space Health**
- **Storage**: Available space, quota usage
- **Quotas**: Execution limits, budget tracking
- **Performance**: Response times, error rates
- **Security**: Access patterns, permission changes

## 🔐 **Security Considerations**

### **Space Isolation**
- **Data Segregation**: Ensure data doesn't leak between spaces
- **Permission Boundaries**: Users can only access their assigned spaces
- **API Security**: Validate space ownership in all endpoints
- **Audit Logging**: Track all space-related actions

### **Access Control**
- **Space Ownership**: Who can manage each space
- **Team Access**: Which teams can operate in which spaces
- **Role Permissions**: Different permissions per space
- **Cross-Space Access**: Future feature for collaboration

---

## 🎯 **Implementation Priority**

### **Phase 1 (Current)**
1. ✅ **Space Context Provider** - Global state management
2. ✅ **Space Selector** - Basic space switching
3. ✅ **Space-Aware API Calls** - Include space context
4. ✅ **Space Settings Page** - Basic configuration

### **Phase 2 (Next)**
1. **Enhanced Space Management** - Advanced settings
2. **Space Analytics** - Usage tracking and metrics
3. **Space Templates** - Pre-configured space types
4. **Cross-Space Features** - Collaboration capabilities

This architecture provides a solid foundation for scalable, secure, and user-friendly team management in NuiFlo WorkForce. 