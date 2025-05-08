# AIEmbedder Interface Blueprint

## 1. Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│  AIEmbedder                                    [_] [X]  │
├─────────────────────────────────────────────────────────┤
│  [File]  [Settings]  [Help]                            │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │                 │  │                             │  │
│  │  Input Panel    │  │      Processing Panel       │  │
│  │                 │  │                             │  │
│  │  [Select Input] │  │  Cleaning Level: [Medium ▼] │  │
│  │  [Select Output]│  │  Chunk Size:    [400   ▼]   │  │
│  │                 │  │  Overlap:       [50    ▼]   │  │
│  │                 │  │                             │  │
│  │                 │  │  [x] Remove Stopwords       │  │
│  │                 │  │  [x] GPU Acceleration       │  │
│  │                 │  │  [x] Create Vector DB       │  │
│  └─────────────────┘  └─────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Progress Panel                     │  │
│  │  [=====================] 75%                    │  │
│  │  Processing: document1.html                     │  │
│  │  Status: Cleaning text...                       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Log Panel                          │  │
│  │  2024-03-19 14:30:15 - Starting processing...   │  │
│  │  2024-03-19 14:30:16 - Processing HTML file...  │  │
│  │  2024-03-19 14:30:17 - Cleaning text...         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  [Start Processing]        [Stop]        [Settings]    │
└─────────────────────────────────────────────────────────┘
```

## 2. Component Specifications

### 2.1 Input Panel
- **Purpose**: File and folder selection
- **Components**:
  - Input Folder Selection Button
  - Output Folder Selection Button
  - Current Path Display
  - File Count Display

### 2.2 Processing Panel
- **Purpose**: Configuration of processing parameters
- **Components**:
  - Cleaning Level Dropdown
    - Light
    - Medium
    - Aggressive
  - Chunk Size Input
    - Range: 200-400
    - Default: 400
  - Chunk Overlap Input
    - Range: 50-100
    - Default: 50
  - Checkboxes
    - Remove Stopwords
    - GPU Acceleration
    - Create Vector DB

### 2.3 Progress Panel
- **Purpose**: Display processing status
- **Components**:
  - Overall Progress Bar
  - Current File Progress
  - Status Text
  - Time Remaining

### 2.4 Log Panel
- **Purpose**: Display processing logs
- **Components**:
  - Log Text Area
  - Auto-scroll
  - Log Level Filter
  - Clear Button

## 3. Menu Structure

### 3.1 File Menu
```
File
├── Open Input Folder
├── Open Output Folder
├── Save Configuration
├── Load Configuration
└── Exit
```

### 3.2 Settings Menu
```
Settings
├── Processing
│   ├── Cleaning Level
│   ├── Chunk Size
│   └── Overlap
├── Database
│   ├── Collection Name
│   └── GPU Settings
└── Interface
    ├── Theme
    └── Log Level
```

### 3.3 Help Menu
```
Help
├── Documentation
├── About
└── Check for Updates
```

## 4. Dialog Windows

### 4.1 Settings Dialog
```
┌─────────────────────────────────────────┐
│  Settings                        [_] [X] │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Processing  │  │    Database     │   │
│  │             │  │                 │   │
│  │ [Settings]  │  │ [Settings]      │   │
│  │             │  │                 │   │
│  └─────────────┘  └─────────────────┘   │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ Interface   │  │    Advanced     │   │
│  │             │  │                 │   │
│  │ [Settings]  │  │ [Settings]      │   │
│  │             │  │                 │   │
│  └─────────────┘  └─────────────────┘   │
│                                         │
│  [Save]                    [Cancel]      │
└─────────────────────────────────────────┘
```

### 4.2 Progress Dialog
```
┌─────────────────────────────────────────┐
│  Processing                     [_] [X]  │
├─────────────────────────────────────────┤
│  Overall Progress:                      │
│  [========================] 75%         │
│                                        │
│  Current File: document1.html          │
│  [====================] 60%             │
│                                        │
│  Status: Cleaning text...              │
│  Time Remaining: 2 minutes             │
│                                        │
│  [Stop]              [Minimize]        │
└─────────────────────────────────────────┘
```

## 5. Event Handling

### 5.1 User Actions
- File/Folder Selection
- Configuration Changes
- Process Start/Stop
- Settings Modification
- Log Interaction

### 5.2 System Events
- Processing Progress
- Error Notifications
- Status Updates
- Completion Events

## 6. Error Handling

### 6.1 Error Dialogs
```
┌─────────────────────────────────────────┐
│  Error                          [_] [X]  │
├─────────────────────────────────────────┤
│  Error processing file:                 │
│  document1.html                        │
│                                        │
│  Reason: Invalid HTML structure        │
│                                        │
│  [Retry]  [Skip]  [Stop Processing]    │
└─────────────────────────────────────────┘
```

### 6.2 Status Messages
- Success: Green
- Warning: Yellow
- Error: Red
- Info: Blue

## 7. Theme Support

### 7.1 Light Theme
- Background: White
- Text: Dark Gray
- Accents: Blue
- Borders: Light Gray

### 7.2 Dark Theme
- Background: Dark Gray
- Text: Light Gray
- Accents: Light Blue
- Borders: Medium Gray

## 8. Responsive Design

### 8.1 Window Sizing
- Minimum: 800x600
- Default: 1024x768
- Maximum: Screen Size

### 8.2 Component Scaling
- Proportional scaling
- Maintain aspect ratios
- Preserve readability

## 9. Accessibility

### 9.1 Keyboard Navigation
- Tab order
- Shortcut keys
- Focus indicators

### 9.2 Screen Reader Support
- Alt text
- ARIA labels
- Focus management

## 10. Internationalization

### 10.1 Language Support
- English (default)
- Configurable language files
- RTL support

### 10.2 Date/Time Formats
- Locale-specific
- Configurable
- Time zone support 