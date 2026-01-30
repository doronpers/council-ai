# Apache Superset Integration for Council-AI

Complete guide for integrating Apache Superset with council-ai for powerful consultation analytics and visualization.

## Overview

This integration enables council-ai to export consultation data to a SQL database that Apache Superset can query and visualize. The system provides a pre-configured dashboard:

- **Consultation Analytics Dashboard**: Agent performance, consultation quality metrics, and persona effectiveness analysis

## Quick Start

### 1. Export Consultation Data

```bash
cd council-ai/config/superset/scripts
python export_to_db.py --format sqlite --output ../../council_ai_consultations.db
```

### 2. Connect Superset

1. Add database connection in Superset UI
2. Create datasets for `consultations` and `member_responses` tables
3. Import dashboard JSON from `config/superset/dashboards/`

## Documentation

See [SUPERSET_INTEGRATION.md](./SUPERSET_INTEGRATION.md) for complete setup instructions.
