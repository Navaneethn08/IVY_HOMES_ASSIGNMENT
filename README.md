# IVY_HOMES_ASSIGNMENT

# API Extractor

A Python utility for retrieving names from multiple autocomplete API endpoints with balanced load distribution.

## Purpose

This script interfaces with several autocomplete APIs to gather all available name suggestions through recursive querying. It employs a round-robin strategy to evenly distribute requests across endpoints and offers comprehensive performance metrics.

## Key Features

- **Multiple Endpoints**: Supports v1, v2, and v3 API versions
- **Balanced Load**: Distributes requests using a cycling approach
- **Error Resilience**: Switches to alternate endpoints on failure or rate limits
- **Recursive Search**: Explores all name suggestions dynamically
- **Performance Tracking**: Logs request counts, error rates, and timings
- **Data Export**: Outputs results to a timestamped JSON file

## Prerequisites

- Python 3.6 or higher
- `requests` package

## Setup

1. Obtain the script from this repository
2. Install dependencies:

```bash
pip install requests
