# FindFounders

A Python application that automatically searches for and extracts the names of founders for each company listed in a given text file using SerpApi's Google Search Engine Results API and Ollama's AI models.

## Features

- Reads company names and URLs from a text file
- Searches Google for founder information using SerpApi
- Extracts founder names using Ollama's Gemma3 4B model
- Outputs results to a structured JSON file
- Handles multiple companies in batch processing

## Prerequisites

- Python 3.7+
- Ollama installed and running locally
- SerpApi account and API key
- Gemma3 4B model available in Ollama

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your SerpApi API key in `config.py`:
   ```python
   SERP_API_KEY = "your_serpapi_key_here"
   ```
4. Ensure Ollama is running and has the Gemma3 4B model available:
   ```bash
   ollama pull gemma3:4b
   ```

## Usage

1. Prepare your companies list in `companies.txt` with the format:
   ```
   Company Name (https://company-url.com/)
   Another Company (https://another-company.com/)
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. The application will:
   - Process each company from `companies.txt`
   - Search for founder information using Google via SerpApi
   - Extract founder names using AI
   - Save all results to `founders.json`

## Output

The application generates two main output files:

- `info.json` - Contains the latest search results from SerpApi (overwritten for each company)
- `founders.json` - Contains the final structured results with all company founders

Example `founders.json` structure:
```json
{
  "Approval AI": ["Arjun Lalwani", "Helly Shah"],
  "Meteor": ["Farhan Khan", "Pranav Madhukar"],
  "Read AI": ["David Shim", "Robert Williams", "Elliott Waldron"]
}
```

## File Structure

- `main.py` - Main application logic
- `config.py` - Configuration file containing API keys
- `companies.txt` - Input file with company names and URLs
- `requirements.txt` - Python dependencies
- `founders.json` - Output file with founder information
- `info.json` - Temporary file with search results

## Functions

### `extract_and_concatenate_snippets(file_path: str)`
Extracts and concatenates snippet text from SerpApi search results.

### `find_founders(company: str, url: str, file_name: str)`
Uses Ollama's AI model to extract founder names from search result snippets.

### `search_companies(file_name: str)`
Main function that orchestrates the entire process for all companies in the input file.

## Error Handling

The application includes comprehensive error handling for:
- Missing or malformed input files
- API request failures
- JSON parsing errors
- AI model response issues

## Notes

- The application processes companies sequentially to avoid overwhelming the APIs
- Search results are temporarily stored in `info.json` and overwritten for each company
- Only first and last names are extracted, excluding titles and suffixes
- The application will skip malformed lines in the companies file and continue processing

## Troubleshooting

- Ensure your SerpApi key is valid and has sufficient credits
- Verify Ollama is running and the Gemma3 4B model is available
- Check that your `companies.txt` file follows the correct format
- Review console output for specific error messages during processing

## Future Improvements

- Support generic input text formats by using Ollama's Gemma3 4B model to extract company names and corresponding URLs.
- Run multiple searches for the same company and keep founder names that appear multiple times.
- Use reference websites like CrunchBase and/or LinkedIn to verify founder names.
- Use another API like Google's Custom Search JSON API to verify founder names.
- Examine organic results beyond the first 10 in case the founder name is missing from those first 10.
