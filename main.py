import json
import os
import ollama
import requests
from typing import List, Optional
from config import SERP_API_KEY

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
        # File not found
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        # Invalid JSON
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return None
    except Exception as e:
        # Unexpected error
        print(f"An unexpected error occurred: {e}")
        return None


def find_founders(company: str, url: str, file_name: str) -> List[str]:
    """
    Find the founders of a company from a given URL and text file, and return the list of founders.
    """
    # Extract snippets from the text file, or return an empty list if there is an error
    snippets = extract_and_concatenate_snippets(file_name)
    if not snippets:
        return []
    
    # Obtain, split, strip, and return the list of founders from Gemma3, 4B model, using the snippets from the text file
    response = ollama.generate(model='gemma3:4b', prompt=f"Write a comma-separated list of the founders of {company} ({url}). Only include the first and last names of the founders, with particles like 'Van' or 'De' but without suffixes like Ph.D. and without additional context: {snippets}")
    founders = [founder.strip() for founder in response['response'].split(',') if founder.strip()]
    return founders


def search_companies(file_name: str):
    """
    Search for the founders of the companies in the text file.
    Opens the text file, extracts each line (company + URL), uses Google Search Engine Results API
    to search for "{LINE} founders", saves results to info/info-[COMPANY-NAME].json, calls find_founders,
    and assembles all results into founders.json.
    """
    # Initialize an empty dictionary to store the results
    all_founders = {}
    
    # Create info directory if it doesn't exist
    info_dir = "info"
    if not os.path.exists(info_dir):
        os.makedirs(info_dir)
        print(f"Created directory: {info_dir}")
    
    try:
        # Read the companies file
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Iterate over the lines in the file
        for line in lines:
            # Strip whitespace and skip empty lines
            line = line.strip()
            if not line:
                continue
                
            # Parse company name and URL from line format: "Company Name (URL)"
            if '(' in line and line.endswith(')'):
                company_part = line[:line.rfind('(')].strip()
                url_part = line[line.rfind('(')+1:-1].strip()
            else:
                print(f"Skipping malformed line: {line}")
                continue
            
            print(f"Processing: {company_part}")
            
            # Search for company founders using SerpApi
            search_query = f"{company_part} ({url_part}) founders"
            
            # SerpApi request
            params = {
                'api_key': SERP_API_KEY,
                'engine': 'google',
                'q': search_query,
                'num': 10
            }
            
            try:
                # Perform a SerpApi request, and store the response
                response = requests.get('https://serpapi.com/search', params=params)
                response.raise_for_status()
                search_results = response.json()
                
                # Create a safe filename for the company
                safe_company_name = "".join(c for c in company_part if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_company_name = safe_company_name.replace(' ', '-')
                info_file_path = os.path.join(info_dir, f"info-{safe_company_name}.json")
                
                # Save search results to info/info-[COMPANY-NAME].json
                with open(info_file_path, 'w', encoding='utf-8') as f:
                    json.dump(search_results, f, indent=2)
                print(f"Saved search results to: {info_file_path}")
                
                # Call find_founders to extract founder names
                founders = find_founders(company_part, url_part, info_file_path)
                
                # Store results
                if founders:
                    all_founders[company_part] = founders
                    print(f"Found founders for {company_part}: {founders}")
                else:
                    print(f"No founders found for {company_part}")
                    
            except requests.RequestException as e:
                # Request exception
                print(f"Error searching for {company_part}: {e}")
                continue
            except Exception as e:
                # Unexpected error
                print(f"Unexpected error processing {company_part}: {e}")
                continue
    
    except FileNotFoundError:
        # File not found
        print(f"Error: The file '{file_name}' was not found.")
        return
    except Exception as e:
        # Unexpected error
        print(f"An unexpected error occurred: {e}")
        return
    
    # Save all results to founders.json
    try:
        with open('founders.json', 'w', encoding='utf-8') as f:
            json.dump(all_founders, f, indent=2)
        print(f"Successfully saved founders data for {len(all_founders)} companies to founders.json")
    except Exception as e:
        # Unexpected error
        print(f"Error saving founders.json: {e}")


if __name__ == "__main__":
    # Search for the founders of the companies in the text file
    search_companies("companies.txt")
