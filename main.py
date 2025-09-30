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


def load_correct_founders(file_path: str = "correct_founders.json") -> dict:
    """
    Load the correct founders from the answer key file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Correct founders file '{file_path}' not found. Skipping accuracy analysis.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{file_path}'. Skipping accuracy analysis.")
        return {}


def analyze_accuracy(found_founders: dict, correct_founders: dict) -> dict:
    """
    Analyze the accuracy of found founders compared to correct founders.
    Returns a dictionary with analysis results for each company.
    """
    results = {}
    
    for company in correct_founders:
        if company not in found_founders:
            results[company] = {
                'all_correct': False,
                'at_least_one_correct': False,
                'no_incorrect': True,
                'found_founders': [],
                'correct_founders': correct_founders[company]
            }
            continue
            
        found = set(found_founders[company])
        correct = set(correct_founders[company])
        
        # Check if all correct founders are listed
        all_correct = correct.issubset(found)
        
        # Check if at least one correct founder is listed
        at_least_one_correct = len(correct.intersection(found)) > 0
        
        # Check if no incorrect founders are listed (all found founders are correct)
        no_incorrect = found.issubset(correct)
        
        results[company] = {
            'all_correct': all_correct,
            'at_least_one_correct': at_least_one_correct,
            'no_incorrect': no_incorrect,
            'found_founders': found_founders[company],
            'correct_founders': correct_founders[company]
        }
    
    return results


def print_accuracy_table(analysis_results: dict):
    """
    Print a formatted table showing accuracy metrics for each company.
    """
    if not analysis_results:
        print("No accuracy analysis available.")
        return
    
    # Calculate column widths
    company_width = max(len("Company"), max(len(company) for company in analysis_results.keys()))
    
    # Table headers
    headers = ["Company", "All Correct", "≥1 Correct", "No Incorrect"]
    col_widths = [company_width, 12, 11, 13]
    
    # Print table header
    print("\n" + "=" * (sum(col_widths) + len(col_widths) + 1))
    print("FOUNDER IDENTIFICATION ACCURACY")
    print("=" * (sum(col_widths) + len(col_widths) + 1))
    
    # Print column headers
    header_row = "|"
    for i, header in enumerate(headers):
        header_row += f" {header:<{col_widths[i]}} |"
    print(header_row)
    
    # Print separator
    separator = "|"
    for width in col_widths:
        separator += "—" * (width + 2) + "|"
    print(separator)
    
    # Print data rows
    for company, metrics in analysis_results.items():
        row = f"| {company:<{col_widths[0]}} |"
        row += f" {'Yes' if metrics['all_correct'] else 'No':<{col_widths[1]}} |"
        row += f" {'Yes' if metrics['at_least_one_correct'] else 'No':<{col_widths[2]}} |"
        row += f" {'Yes' if metrics['no_incorrect'] else 'No':<{col_widths[3]}} |"
        print(row)
    
    # Print bottom border
    print("=" * (sum(col_widths) + len(col_widths) + 1))
    
    # Print summary statistics
    total_companies = len(analysis_results)
    all_correct_count = sum(1 for metrics in analysis_results.values() if metrics['all_correct'])
    at_least_one_count = sum(1 for metrics in analysis_results.values() if metrics['at_least_one_correct'])
    no_incorrect_count = sum(1 for metrics in analysis_results.values() if metrics['no_incorrect'])
    
    print(f"\nSUMMARY:")
    print(f"Total companies: {total_companies}")
    print(f"All correct founders identified: {all_correct_count}/{total_companies} ({all_correct_count/total_companies*100:.1f}%)")
    print(f"At least one correct founder: {at_least_one_count}/{total_companies} ({at_least_one_count/total_companies*100:.1f}%)")
    print(f"No incorrect founders listed: {no_incorrect_count}/{total_companies} ({no_incorrect_count/total_companies*100:.1f}%)")


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
    
    # Load correct founders and perform accuracy analysis
    correct_founders = load_correct_founders()
    if correct_founders:
        analysis_results = analyze_accuracy(all_founders, correct_founders)
        print_accuracy_table(analysis_results)


if __name__ == "__main__":
    # Search for the founders of the companies in the text file
    search_companies("companies.txt")
