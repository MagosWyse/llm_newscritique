import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# Default list of URLs to scrape
DEFAULT_URLS = [
    "https://bbc.com/news",
    "https://edition.cnn.com",
    #"https://english.news.cn/",
    #"https://www.themoscowtimes.com/", 
]

def scrape_website(url, search_terms, url_contents):
    """
    Scrape a website for given search terms and extract relevant content.
    
    Args:
    url (str): The URL of the website to scrape.
    search_terms (list): A list of keywords or phrases to search for.
    url_contents (dict): The existing nested dictionary to store URL contents.
    
    Returns:
    dict: An updated nested dictionary of URLs and their extracted content.
    """
    if url not in url_contents:
        url_contents[url] = {}  # Initialize nested dictionary for this URL if it doesn't exist
    
    try:
        # Attempt to fetch the webpage
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return url_contents

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Iterate through each search term
        for term in search_terms:
            print(f"\nResults for search term '{term}' in {url}:")
            # Create a case-insensitive regex pattern for the search term
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            # Find all elements containing the search term
            elements = soup.find_all(string=pattern)
            
            if not elements:
                print(f"Search term '{term}' not found.")
                continue
            
            # Process each element containing the search term
            for element in elements:
                current = element
                # Traverse up the DOM tree to find an anchor tag
                while current.parent:
                    if current.name == 'a' and current.has_attr('href'):
                        link = current['href']
                        full_url = urljoin(url, link)
                        print(f"Search term found in link: {full_url}")
                        print(f"Link text: {current.get_text(strip=True)}")
                        
                        # Highlight the search term in the context
                        context = element.string
                        highlighted_context = re.sub(pattern, lambda m: f"**{m.group()}**", context)
                        print(f"Context: ...{highlighted_context[:100]}...")
                        
                        # Extract text from the linked URL if not already done
                        if full_url not in url_contents[url]:
                            url_contents[url][full_url] = extract_text_from_url(full_url)
                        
                        # Highlight the search term in the preview
                        preview = url_contents[url][full_url][:200]
                        highlighted_preview = re.sub(pattern, lambda m: f"**{m.group()}**", preview)
                        print(f"Extracted text preview: {highlighted_preview}...")
                        print('-' * 50)
                        break
                    current = current.parent
                else:
                    # If the search term is not in a link, just print the context
                    context = element.string
                    highlighted_context = re.sub(pattern, lambda m: f"**{m.group()}**", context)
                    print(f"Search term found, but not in a link. Context: ...{highlighted_context[:100]}...")
                    print('-' * 50)

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")

    return url_contents

def extract_text_from_url(url):
    """
    Extract text content from a given URL.
    
    Args:
    url (str): The URL to extract text from.
    
    Returns:
    str: Extracted text content or an error message.
    """
    try:
        # Attempt to fetch the webpage
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all text from <p> tags
            paragraphs = soup.find_all('p')
            text = '\n\n'.join(p.get_text().strip() for p in paragraphs)
            
            # Remove extra whitespace and newlines
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        else:
            return f"Failed to retrieve content. Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error extracting text: {e}"

def main():
    """
    Main function to run the web scraper.
    Handles user input and orchestrates the scraping process.
    """
    # Ask user if they want to use the default URL list
    use_default = input("Do you want to use the default list of URLs? (yes/no): ").lower().strip()
    
    if use_default == 'yes':
        urls = DEFAULT_URLS
    else:
        # Get user-input URLs
        urls = input("Enter the URLs to scrape (comma-separated): ").split(',')
        urls = [url.strip() for url in urls]

    # Get search terms from user
    search_terms = input("Enter search terms (keywords or phrases, comma-separated): ").split(',')
    search_terms = [term.strip() for term in search_terms]
    
    # Dictionary to store all scraped content
    all_url_contents = {}
    
    # Scrape each URL
    for url in urls:
        print(f"\nScraping: {url}")
        all_url_contents = scrape_website(url, search_terms, all_url_contents)
    
    # Print a summary of all extracted contents
    print("\nAll extracted contents:")
    for main_url, sub_urls in all_url_contents.items():
        print(f"\nMain URL: {main_url}")
        for sub_url, content in sub_urls.items():
            print(f"  Sub URL: {sub_url}")
            print(f"  Content preview: {content[:200]}...")
            print('-' * 50)
    return all_url_contents

if __name__ == "__main__":
    main()