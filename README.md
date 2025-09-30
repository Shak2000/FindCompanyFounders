# FindFounders

A Python application that automatically searches for and extracts the names of founders for each company listed in a given text file using [SerpApi's Google Search Engine Results API](https://serpapi.com/search-api) and Ollama's AI models.

## Features

- Reads company names and URLs from a text file
- Searches Google for founder information using SerpApi
- Extracts founder names from the search results using Ollama's Gemma3 4B model
- Outputs results to a structured JSON file
- Handles multiple companies in batch processing

## Prerequisites

- Python 3.7+
- Ollama installed and running locally
- SerpApi account and API key, with a free tier of 250 searches each month
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
   - Display an accuracy analysis table comparing results to `correct_founders.json`

## Output

The application generates the following output files:

- `info/info-[COMPANY-NAME].json` - Contains search results from SerpApi for each company (one file per company)
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
- `correct_founders.json` - Answer key with the correct list of names of the founders of each company
- `info/` - Directory containing search results for each company

## Functions

### `extract_and_concatenate_snippets(file_path: str)`
Extracts and concatenates snippet text from SerpApi search results.

### `find_founders(company: str, url: str, file_name: str)`
Uses Ollama's AI model to extract founder names from search result snippets.

### `search_companies(file_name: str)`
Main function that orchestrates the entire process for all companies in the input file.

### `load_correct_founders(file_path: str)`
Loads the correct founders from the answer key file for accuracy comparison.

### `analyze_accuracy(found_founders: dict, correct_founders: dict)`
Compares found founders against correct founders and calculates accuracy metrics.

### `print_accuracy_table(analysis_results: dict)`
Prints a formatted table showing accuracy metrics for each company with three dimensions:
- **All Correct**: Whether all correct founders were identified
- **≥1 Correct**: Whether at least one correct founder was identified  
- **No Incorrect**: Whether no incorrect founders were listed

## Results

In the current results for the current implementation, 8 companies had their founders correctly identified without any errors, 1 company (Profound) had its founders correctly identified in addition to an incorrect name, and 1 company had one out of two of its founders identified.

## Error Handling

The application includes comprehensive error handling for:
- Missing or malformed input files
- API request failures
- JSON parsing errors
- AI model response issues

## Notes

- The application processes companies sequentially to avoid overwhelming the APIs
- Search results are stored in separate files within the `info/` directory, one per company
- Only first and last names are extracted, excluding titles and suffixes
- The application will skip malformed lines in the companies file and continue processing
- Company names in filenames are sanitized to remove special characters for filesystem compatibility

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
