# truPrompt

> **AI-Powered System Prompt Generator for Law Enforcement RMS Integration**

truPrompt is a sophisticated Python CLI application designed for law enforcement agencies to generate customized AI system prompts for the "dataPull Agent" - an AI system that interacts with Records Management Systems (RMS) through GUI automation.

---

## Features

- 🎯 **Interactive Setup Wizard**: 7-step guided process for configuring agency-specific prompts
- 🏛️ **Pre-configured RMS Support**: Built-in configurations for 7+ major RMS platforms
- 📋 **16+ Command Workflows**: Comprehensive data extraction workflows (person lookup, case lookup, address intelligence, etc.)
- 🔐 **Signature Generation**: SHA256-based digital signatures for prompt authenticity
- 💾 **Master Agency Database**: JSON-based persistence with automatic metadata extraction
- 🎨 **Colorized Terminal UI**: ANSI-styled interface with motivational quotes
- ♻️ **Batch Generation**: Auto-generate prompts for all agencies from database

---

## Quick Start

### Prerequisites
- Python 3.8 or higher (tested with Python 3.13)
- No external dependencies required (uses Python standard library)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd truPrompt

# Optional: Install enhanced features
pip install -r requirements.txt  # For encryption support

# Run the application
python truPrompt.py
```

### Basic Usage

```bash
# Launch interactive menu
python truPrompt.py

# Menu Options:
# [1] Interactive Setup - Create new agency prompt
# [2] Auto-generate from existing data - Regenerate prompts
# [3] Exit
```

---

## Interactive Setup Workflow

### Step 1: Basic Agency Information
- Agency name, abbreviation
- City, county, state
- Operating system (Windows/Linux/macOS)

### Step 2: RMS System Selection
Choose from pre-configured systems:
- **RIMS** (Butte County Sheriff's Office)
- **Spillman Flex** (North Platte PD)
- **New World** (Casa Grande PD, Findlay PD, Lancaster County SO)
- **Cody** (Muhlenberg Township PD)
- **Zuercher** (Kershaw County SO)
- **OneSolutionRMS** (Burlington PD)
- **Tritech** (Web-based)
- **Custom RMS** (Enter your own)

### Step 3: Collect Categorized Notes (Optional)
Add RMS-specific tips in 11 categories:
- Quirk, Workflow, Navigation, Search, Data
- Error, Performance, Security, Integration
- Training, Other

### Step 4: RMS Credentials
- Username and password (stored in generated prompt)

### Step 5: Other Systems Integration (Optional)
- Add credentials for additional systems beyond primary RMS

### Step 6: Signature Configuration
- Use existing signature or generate new SHA256 signature

### Step 7: Workflow Selection
- Choose from 16+ core workflows
- Option to add custom workflows

**Navigation**: Type `back` to return to previous step, `skip` for optional steps

---

## Command Workflows

truPrompt includes 16+ pre-configured workflows:

| Workflow | Description |
|----------|-------------|
| `_PERSON_LOOKUP` | Search person by name |
| `_CASE_LOOKUP` | Search case by number |
| `_VEHICLE_LOOKUP` | Search vehicle by VIN/plate |
| `_PROPERTY_LOOKUP` | Search stolen/lost property |
| `_ADDRESS_LOOKUP` | Search address |
| `_ADDRESS_FULL_REPORT` | Comprehensive address intelligence |
| `_ADDRESS_CFS_HISTORY` | Call-for-service history |
| `_ADDRESS_PERSONS` | Persons associated with address |
| `_ADDRESS_VEHICLES` | Vehicles at address |
| `_ADDRESS_WEAPONS` | Registered weapons at address |
| `_ADDRESS_HAZARDS` | Safety hazards and warnings |
| `_OSINT_LOOKUP` | Open-source intelligence gathering |
| `_DIAGNOSTIC_INPUT_CHECK` | Hardware diagnostics |
| `_EXPLORE_RMS` | Heuristic RMS exploration |
| `_BATCH` | Execute multiple commands |
| `_UNKNOWN_QUERY_NLP` | Natural language query parsing |

### Global Workflow Flags

```bash
--narrative, -n              # Extract detailed narratives
--information-degree <1-3>   # 1=immediate, 2=incident, 3=secondary
--debug-vvv, -d             # Detailed debug output
--unformatted-context, -u   # Additional raw context
--do-it-now, -din           # Execute immediately to fullest extent
--tell-me-now, -tmn         # Answer completely without confirmation
--find-me-anything, -fma    # OSINT fallback if not in RMS
--prompt-improvement, -pi   # Return prompt improvement suggestions
```

---

## Generated Output

### File Format
Generated prompts are saved to: `outputs/[AGENCY_ABBR]_truPrompt_v7.0.txt`

### Prompt Structure (11 Sections)
1. **Agency and System Configuration** - Basic metadata
2. **RMS-Specific Notes and Procedures** - System-specific guidance
3. **Credential Management** - Username/password (plaintext)
4. **Mission Identity and Critical Rules** - AI agent mission
5. **Situational Tool Use & Logic** - When to use GUI automation
6. **GUI Interaction Principles** - Best practices
7. **Standard Operating Procedure** - 5-phase operational workflow
8. **Command Workflows** - All workflow definitions
9. **Required Output Schema** - JSON format specification
10. **Appendix** - Troubleshooting and contingencies
11. **Signature and Documentation Policy** - Digital signature

---

## Master Agency Database

**Location**: `outputs/agency_data.json`

### Database Structure
```json
{
  "processed_files": {
    "filename": {
      "processed_at": "ISO timestamp",
      "file_path": "absolute path",
      "file_hash": "SHA256",
      "agency_abbr": "ABBR"
    }
  },
  "agencies": {
    "ABBR": {
      "agency_name": "Full Name",
      "city": "City",
      "county": "County",
      "state": "ST",
      "rms_name": "RMS System",
      "os_name": "Operating System",
      "rms_username": "username",
      "rms_password": "password",
      "signature": "SHA256 hash",
      "last_updated": "ISO timestamp",
      "source_files": ["file.txt"]
    }
  }
}
```

### Agency Metadata Extraction

```bash
# Extract metadata from generated prompts
python util/agency_extractor.py
```

This utility:
- Scans `outputs/` directory for prompt files
- Extracts agency metadata using regex
- Updates `agency_data.json` with processed file tracking
- Prevents duplicate processing with file hash tracking

---

## Project Structure

```
truPrompt/
├── truPrompt.py              # Main application (1,368 lines)
├── util/
│   └── agency_extractor.py  # Metadata extraction utility
├── outputs/
│   ├── agency_data.json     # Master agency database
│   └── *.txt                # Generated prompt files
├── archived/                 # Historical versions
├── README.md                # This file
├── LICENSE                  # MIT License
├── requirements.txt         # Optional dependencies
└── .gitignore              # Git ignore rules
```

---

## Architecture

### Design Patterns
- **Template Method Pattern**: Prompt generation uses predefined sections
- **Strategy Pattern**: Different RMS systems have different procedures
- **Builder Pattern**: `SetupStepManager` constructs agency data incrementally
- **Repository Pattern**: `AgencyDataManager` handles JSON persistence
- **Factory Pattern**: `TruPromptGenerator` creates prompts from templates

### Key Classes
| Class | Purpose |
|-------|---------|
| `TruPromptGenerator` | Core prompt generation from templates |
| `SetupStepManager` | Multi-step setup wizard with navigation |
| `WorkflowSelector` | Workflow command selection menu |
| `AgencyDataExtractor` | Regex-based metadata extraction |
| `AgencyDataManager` | Load/save agency database |
| `SignatureRecorder` | Digital signature management |

---

## Security Considerations

### Credential Storage
- **By Design**: Credentials stored in plaintext in generated prompts
- System prompts embed username/password for AI agent access
- Generated prompts contain sensitive information - **protect accordingly**

### Critical Rules
- AI agents are PROHIBITED from using search engines (enforced in prompts)
- Must rely solely on provided RMS credentials
- No external data sources beyond configured systems

### Signature System
- SHA256 hashing with random salt
- Tracks prompt authenticity and versioning
- Stored in agency database for audit trail

---

## Development

### Adding a New RMS System

1. Edit `RMS_CONFIG` dictionary in `truPrompt.py` (line 369):
```python
'YourRMS': {
    'general_notes': 'System quirks and tips',
    'procedures': 'Step-by-step procedures',
    'module_overview': 'Description of modules (optional)',
    'prioritization_logic': 'Query prioritization (optional)'
}
```

2. Documentation auto-generates in Section 2 of prompts

### Adding a New Workflow

1. Edit `WORKFLOWS_DATABASE` in `truPrompt.py` (line 350):
```python
{
    'Full Command': '_YOUR_COMMAND|$PARAM1|$PARAM2:',
    'Short Form': '_YC',
    'Description': 'What this workflow does',
    'Procedure': 'Step-by-step execution instructions',
    'Flags': ['--flag1', '--flag2'],  # Optional
    'Modes': ['mode1', 'mode2']        # Optional
}
```

2. Workflow auto-integrates into Section 8 of generated prompts

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests (when added)
pytest

# Code formatting
black truPrompt.py

# Linting
flake8 truPrompt.py
```

---

## Troubleshooting

### Common Issues

**Issue**: "No module named 'cryptography'"
**Solution**: Cryptography is optional. Install with `pip install cryptography` or ignore.

**Issue**: Colors not displaying correctly
**Solution**: Ensure terminal supports ANSI colors. Windows users may need Windows Terminal.

**Issue**: JSON decode error in agency_data.json
**Solution**: Delete corrupted `agency_data.json` and regenerate with agency_extractor.py

**Issue**: Permission denied writing to outputs/
**Solution**: Check directory permissions or run with appropriate privileges

---

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd truPrompt

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
```

### Code Style
- Follow PEP 8 guidelines
- Use Black for formatting
- Add docstrings to all functions
- Keep functions focused and small

### Submitting Changes
1. Create a feature branch
2. Make your changes
3. Add tests if applicable
4. Submit a pull request

---

## Version History

- **v7.0** (Current): Multi-step wizard, 16+ workflows, master database
- **v6.x**: Enhanced RMS configurations
- **v5.x**: Initial workflow system
- **Earlier**: Basic prompt generation

See `archived/` directory for historical versions.

---

## License

MIT License - Copyright (c) 2025 MJ

See [LICENSE](LICENSE) file for full license text.

---

## Support

For issues, questions, or contributions:
- Review [CLAUDE.md](CLAUDE.md) for development guidance
- Check existing issues on GitHub
- Submit new issues with detailed descriptions

---

## Acknowledgments

- Built for law enforcement agencies
- Designed for the "dataPull Agent" AI system
- Supports 7+ major RMS platforms
- 200+ motivational quotes for user experience

---

## Roadmap

### Planned Features
- [ ] Web-based UI option
- [ ] Encrypted credential storage
- [ ] Multi-user collaboration
- [ ] Version control for prompts
- [ ] Automated testing suite
- [ ] Export to multiple formats
- [ ] Integration with CI/CD
- [ ] Prompt template library

---

**truPrompt** - Empowering law enforcement with AI-optimized system prompts

*Version 7.0 | Python 3.13+ | MIT License*
