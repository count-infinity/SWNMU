# GUI World Builder Requirements Document

## Project Overview
This document outlines the requirements for implementing a web-based world builder GUI integrated into the Evennia Django application for the SWNMU (Stars Without Number MUD) project.

## Functional Requirements

### Core Features

#### 1. Visual Room Editor
- **Drag & Drop Interface**: Users can drag room objects onto a canvas and position them spatially
- **Room Creation**: Click/drag to create new rooms on the canvas
- **Room Selection**: Click to select individual rooms or multi-select with Ctrl+click
- **Room Movement**: Drag selected rooms to reposition them on the canvas
- **Visual Representation**: Rooms displayed as boxes/nodes with basic information (name, ID)

#### 2. Exit Management
- **Visual Exit Creation**: Click and drag between rooms to create exits
- **Bidirectional Exits**: Option to automatically create return exits
- **Exit Types**: Support for different exit types (door, portal, hidden, etc.)
- **Exit Properties**: Set exit names, descriptions, and special attributes
- **Visual Exit Display**: Lines/arrows connecting rooms showing exit relationships

#### 3. Room Property Management
- **Room Descriptions**: Rich text editor for room descriptions
- **Room Attributes**: Interface to set custom attributes (key-value pairs)
- **Room Tags**: Tag management system for categorization
- **Room Types**: Support for different room typeclasses
- **Room Scripts**: Ability to attach scripts to rooms

#### 4. Project Management
- **Save/Load Designs**: Persistent storage of world designs in database
- **Version Control**: Track changes and allow rollback to previous versions
- **Project Templates**: Pre-built templates for common area types
- **Import/Export**: JSON-based format for sharing designs

#### 5. Export System
- **Python Script Generation**: Generate batch creation scripts
- **Preview Mode**: Show generated Python code before export
- **Incremental Updates**: Generate scripts for only changed elements
- **Dependency Resolution**: Handle creation order for interconnected objects

### User Interface Requirements

#### 1. Main Canvas
- **Zoomable Interface**: Pan and zoom on large world designs
- **Grid System**: Optional snap-to-grid for precise positioning  
- **Minimap**: Overview of entire design with current viewport indicator
- **Canvas Tools**: Hand tool (pan), select tool, room creation tool, exit creation tool

#### 2. Property Panels
- **Room Properties Panel**: Collapsible panel showing selected room details
- **Exit Properties Panel**: Edit exit properties when exit is selected
- **Design Properties Panel**: Overall design settings and metadata
- **Layer Management**: Organize rooms into logical layers

#### 3. Navigation & Controls
- **Toolbar**: Primary tools for room/exit creation and manipulation
- **Context Menus**: Right-click menus for quick actions
- **Keyboard Shortcuts**: Standard shortcuts (Ctrl+Z undo, Delete, etc.)
- **Status Bar**: Show current tool, selected objects count, design status

### Technical Requirements

#### 1. Django Integration
- **Web Views**: Django views serving the GUI interface
- **REST API**: API endpoints for CRUD operations on designs
- **Authentication**: Integration with Evennia's user system
- **Permissions**: Builder/Admin role-based access control

#### 2. Frontend Technology Stack
- **JavaScript Framework**: Modern JS framework (React/Vue/vanilla)
- **Canvas Library**: HTML5 Canvas or SVG-based drawing library
- **UI Components**: Component library for consistent interface
- **State Management**: Client-side state management for undo/redo

#### 3. Data Model
- **Design Model**: Django model storing world design metadata
- **Room Data**: JSON field storing room positions and properties
- **Exit Data**: JSON field storing exit connections and properties
- **Version Tracking**: Timestamp and user tracking for changes

#### 4. Export Engine
- **Template System**: Jinja2 templates for Python script generation
- **Evennia Integration**: Generate code using Evennia's creation patterns
- **Validation**: Verify design integrity before export
- **Error Handling**: Clear error messages for invalid designs

## Non-Functional Requirements

### Performance
- **Canvas Performance**: Smooth interaction with 100+ rooms
- **Load Times**: Initial load under 3 seconds
- **Save Performance**: Auto-save without blocking UI
- **Memory Usage**: Efficient client-side memory management

### Usability
- **Learning Curve**: Intuitive interface for non-technical builders
- **Responsive Design**: Work on desktop browsers (mobile secondary)
- **Accessibility**: Basic keyboard navigation support
- **Error Prevention**: Validation to prevent invalid connections

### Reliability
- **Data Integrity**: Prevent corruption of design data
- **Auto-Save**: Periodic automatic saving of work
- **Backup System**: Daily backups of design database
- **Error Recovery**: Graceful handling of network/server errors

## Integration Requirements

### Evennia MUD Integration
- **Typeclass Support**: Support for SWNMU custom room typeclasses
- **Attribute System**: Integration with Evennia's attribute system
- **Tag System**: Support for Evennia's tagging system
- **Script Integration**: Support for attaching room scripts

### SWNMU Specific Features
- **SWN Room Types**: Support for sci-fi room categories (Bridge, Engineering, etc.)
- **Lighting System**: Integration with the project's lighting mechanics
- **Behavior System**: Support for room behaviors from the SWNMU framework
- **Event Integration**: Rooms can trigger/respond to game events

## User Stories

### Primary Users: World Builders
1. **As a builder**, I want to visually lay out connected rooms so I can design intuitive area layouts
2. **As a builder**, I want to set room properties through forms so I don't need to remember command syntax
3. **As a builder**, I want to save my work so I can continue designing across multiple sessions
4. **As a builder**, I want to export my design so I can build it in the actual game world

### Secondary Users: Admin/Developers
1. **As an admin**, I want to review designs before they're built so I can maintain world quality
2. **As a developer**, I want to extend the tool so I can add custom property types
3. **As an admin**, I want to backup designs so I don't lose builder work

## Success Criteria
- Builders can create a 10-room area in under 15 minutes
- Exported scripts execute without errors in Evennia
- Tool reduces room creation time by 50% compared to manual commands
- Zero data loss during normal operation
- Positive feedback from builder community

## Future Enhancements (Out of Scope)
- Character/NPC placement and editing
- Item/object placement within rooms
- Advanced scripting/programming interface
- Real-time collaborative editing
- Mobile app version
- 3D visualization mode

## Technical Constraints
- Must work within Evennia's Django architecture
- No external database dependencies beyond Django ORM
- Compatible with existing SWNMU typeclass system
- Maintainable by single developer
- No breaking changes to existing game systems

## Deliverables
1. Django app with GUI interface
2. REST API for design management
3. Export engine with Python script generation
4. User documentation
5. Developer documentation for extensions
6. Test suite covering core functionality