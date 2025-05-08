# TSKMaster Project Context

This directory contains project context files and utility scripts for the TSKMaster application.

## Context Files

- **TSKMaster_CONTEXT.md**: The primary project context file that contains comprehensive information about the TSKMaster project, including its architecture, components, implementation status, and known issues.
- **PROJECT_CONTEXT.md**: A symbolic copy of the TSKMaster_CONTEXT.md file for compatibility with tools that expect this standard name.

## Scripts

The following utility scripts are available to manage the project context:

### init_project_context.py

Initializes the project context file with the basic structure and metadata. Use this script when setting up a new project context.

```bash
python scripts/init_project_context.py [--force]
```

Options:
- `--force`: Reinitialize the context file even if it already exists

### update_project_context.py

Updates the project context file with the latest information about the project.

```bash
python scripts/update_project_context.py [--level {minimal,standard,deep}] [--force]
```

Options:
- `--level`: The update level (minimal, standard, or deep)
- `--force`: Force update even if no changes detected

## Usage Guidelines

1. Initialize the project context when starting a new project or feature branch:
   ```bash
   python scripts/init_project_context.py
   ```

2. Regularly update the project context with the latest information:
   ```bash
   python scripts/update_project_context.py
   ```

3. When working with AI assistants or onboarding new team members, point them to the TSKMaster_CONTEXT.md file for comprehensive project understanding.

## Project Context Structure

The TSKMaster_CONTEXT.md file is structured with the following main sections:

1. Project Overview
2. Project Focus
3. Agent Profile
4. User Profile
5. System Architecture
6. Component Overview
7. Implementation Status
8. Known Issues
9. Code Patterns
10. Project Roadmap
11. Development Environment
12. Decision Log

This structure provides a comprehensive overview of the project's current state and future plans. 