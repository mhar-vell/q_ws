# Project Documentation

Centralized documentation for the Robust Mobile Manipulator Control project.

## Directory Structure

```
docs/
├── README.md                          # This file - documentation index
├── phases/                            # Phase-specific documentation
│   ├── PHASE_ALGORITHM_CORE.md       # Algorithm core phase details
│   └── PHASE3_DOCUMENTATION_COMPLETE.md # Phase 3 completion report
└── repository_management/             # Repository organization docs
    ├── REPOSITORY_OPTIMIZATION_ANALYSIS.md # Optimization analysis
    └── STRUCTURE.md                   # Repository structure overview
```

---

## Documentation Categories

### 1. Phase Documentation (`phases/`)

Phase-specific implementation reports and completion summaries.

#### Available Documents:
- **PHASE_ALGORITHM_CORE.md** - Algorithm core phase implementation
  - DQN and Q-Learning algorithms
  - Training sessions and checkpoints
  - Performance metrics

- **PHASE3_DOCUMENTATION_COMPLETE.md** - Documentation phase completion
  - All README files created
  - Module documentation (simulation, planning, config)
  - Total metrics and impact

---

### 2. Repository Management (`repository_management/`)

Documentation related to repository structure, optimization, and organization.

#### Available Documents:
- **REPOSITORY_OPTIMIZATION_ANALYSIS.md** - Comprehensive repository analysis
  - File organization recommendations
  - Duplicate identification
  - 3-phase optimization plan
  - Storage optimization strategies

- **STRUCTURE.md** - Repository structure overview
  - Directory layout
  - Module organization
  - File categorization

---

## Other Documentation Locations

### Technical Documentation
Located in `/documentation/` directory:

- **`disturbance_system/`** - Disturbance injection documentation
  - DISTURBANCE_REVIEW.md
  - DISTURBANCE_COMPENSATION.md
  - DISTURBANCE_EXPLANATION_CORRECTED.md
  - DISTURBANCE_QUICK_REF.md
  - DISTURBANCE_FINDINGS.md

- **`trajectory_planning/`** - Trajectory planning documentation
  - RL_ALGORITHMS.md
  - TRAJECTORY_CUSTOMIZATION.md
  - TRAJECTORY_PLANNING.md

- **`training_guides/`** - Training workflow documentation
  - TIMEOUT_EXPLANATION.md
  - AUTOMATIC_TRAINING_COMPLETE.md
  - TRAINING_WORKFLOW.md

- **`project_overview/`** - Project overview and summaries
  - ARCHIVE_ORGANIZATION_PLAN_V2.md
  - PROJECT_TITLE_SUGGESTIONS.md
  - DOCUMENTATION_INDEX.md
  - IMPLEMENTATION_SUMMARY.md

- **`academic/`** - Academic papers and publications
  - ACADEMIC_PAPER_DRAFT.md

### Module Documentation
Located in source directories:

- **`src/README.md`** - Main source module overview
- **`src/simulation/README.md`** - Simulation module documentation
- **`src/planning/README.md`** - Planning module documentation
- **`src/config/README.md`** - Configuration module documentation

### Component Documentation
Located in component directories:

- **`launchers/README.md`** - Launch scripts documentation
- **`tools/README.md`** - Utility tools documentation
- **`test_scripts/README.md`** - Testing framework documentation
- **`visualization_tools/README.md`** - Visualization tools documentation
- **`training_data/*/README.md`** - Training data documentation

---

## Quick Access

### For New Developers
1. Start with **`/README.md`** (project root)
2. Read **`src/README.md`** for module overview
3. Review **`docs/repository_management/STRUCTURE.md`** for organization
4. Explore specific module READMEs as needed

### For Training
1. **`documentation/training_guides/TRAINING_WORKFLOW.md`**
2. **`src/simulation/README.md`** - RL agents and environment
3. **`tools/README.md`** - Training utilities
4. **`launchers/README.md`** - How to launch training

### For Disturbance System
1. **`documentation/disturbance_system/DISTURBANCE_QUICK_REF.md`**
2. **`documentation/disturbance_system/DISTURBANCE_REVIEW.md`**
3. **`src/simulation/README.md`** - Disturbance implementation

### For Repository Management
1. **`docs/repository_management/REPOSITORY_OPTIMIZATION_ANALYSIS.md`**
2. **`docs/repository_management/STRUCTURE.md`**
3. **`.gitignore`** - Files excluded from version control

---

## Documentation Standards

All documentation in this repository follows these standards:

### File Naming
- **ALL_CAPS_WITH_UNDERSCORES.md** - Major documents (phases, analyses)
- **README.md** - Module/directory overviews
- **lowercase_with_underscores.md** - Technical guides

### Structure
- Clear section hierarchy with headers
- Code examples with syntax highlighting
- Usage examples for all features
- Troubleshooting sections
- Cross-references to related docs

### Content
- Purpose and overview at the top
- Table of contents for long documents
- Visual elements (emojis, tables, diagrams)
- Practical examples
- Links to related documentation

---

## Contributing to Documentation

When adding new documentation:

1. **Choose the right location**:
   - Phase reports → `docs/phases/`
   - Repository management → `docs/repository_management/`
   - Technical guides → `documentation/`
   - Module docs → `src/*/README.md`
   - Component docs → `*/README.md`

2. **Follow naming conventions**:
   - Use descriptive names
   - Follow existing patterns
   - Use appropriate case

3. **Update this index**:
   - Add new documents to relevant sections
   - Maintain cross-references
   - Update quick access guides

4. **Include**:
   - Clear purpose/overview
   - Code examples
   - Cross-references
   - Last updated date

---

## Documentation Metrics

- **Total Directories**: 2 (phases, repository_management)
- **Phase Documents**: 2
- **Repository Management Docs**: 2
- **Last Updated**: November 2, 2025

---

## Related Files

- **Root README**: `/README.md` - Project overview and getting started
- **Main Documentation**: `/documentation/` - Technical documentation
- **Module READMEs**: `/src/*/README.md` - Source code documentation
- **Component READMEs**: Various directories - Component-specific docs

---

**Last Updated**: November 2, 2025  
**Location**: `/home/marcoreis/robust_mm_control_ws/docs/`  
**Status**: Organized ✅
