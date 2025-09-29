import json
import ollama
from typing import List, Optional

def extract_and_concatenate_snippets(file_path: str) -> Optional[str]:
    """
    Reads a JSON file, extracts the 'snippet' field from all items 
    in the 'organic_results' list, and concatenates them with a newline separator.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A single string of concatenated snippets separated by newlines, 
        or None if an error occurs (e.g., file not found, invalid JSON, 
        or required keys missing).
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Access the 'organic_results' list
        organic_results: Optional[List[dict]] = data.get('organic_results')
        
        if not organic_results:
            print("Error: 'organic_results' key not found or is empty.")
            return None

        # Extract all 'snippet' fields
        snippets: List[str] = []
        for result in organic_results:
            # Safely get the 'snippet' field
            snippet: Optional[str] = result.get('snippet')
            if snippet:
                snippets.append(snippet)

        # Concatenate the extracted snippets with a "\n" separator
        return "\n".join(snippets)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def find_founders(company: str, url: str, file_name: str):
    """
    Find the founders of a company from a given URL and text file, and save the results to a file.
    """
    snippets = extract_and_concatenate_snippets(file_name)
    response = ollama.generate(model='gemma3:4b', prompt=f"Write a comma-separated list of the founders of {company} ({url}). Only include the first and last names of the founders, with particles like 'Van' or 'De' but without suffixes like Ph.D. and without additional context: {snippets}")
    data = {
        company: [founder.strip() for founder in response['response'].split(',')]
    }
    with open('founders.json', 'w') as f:
        json.dump(data, f)


if __name__ == "__main__":
    find_founders("Approval AI", "https://www.getapproval.ai/founders", "info.json")
