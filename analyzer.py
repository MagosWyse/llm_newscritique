import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def analyze_coverage(all_url_contents):
    """
    Send the scraped content to Claude for analysis and comparison.
    
    Args:
    all_url_contents (dict): The nested dictionary containing scraped content from different news outlets.
    
    Returns:
    str: Claude's analysis of the coverage.
    """
    # Prepare the system prompt for Claude
    system = """You are a professional media expert tasked with comparing and contrasting news articles about the same event from different news outlets. Your goal is to provide a well-structured and analyzed report that highlights key similarities and differences between the two texts. Your report should revolve mainly around 1. Area of focus, 2. Tone of coverage, 3. Depth of coverage, 4. Potential biases, 5. Humanitarian effect. You are not restricted with these topics. Add or remove topics based on your expertise. 
                Format your output with numerated topics and bullet points to improve readability. Make a section for Key Differences.  """
    
    # Prepare the prompt for Claude
    prompt = "I have scraped content from two different news outlets on a specific topic. Please analyze and compare the coverage from these outlets. Here's the data:\n\n"
    
    for main_url, sub_urls in all_url_contents.items():
        prompt += f"Outlet: {main_url}\n"
        for sub_url, content in sub_urls.items():
            prompt += f"Article: {content}\n"

    prompt += "\nBased only on this data given to you, please provide an in depth analysis that compares and contrasts the coverage of this specific topic from these different news outlets. Consider factors such as tone, focus, depth of coverage, potential biases, and any other relevant aspects you notice. Please structure your response as follows:\n\nOutlet 1:\n[Analysis for the first outlet]\n\nOutlet 2:\n[Analysis for the second outlet]"

    print("This is the prompt:/n")
    print(prompt)

    # Send the prompt to Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        system = system,
        max_tokens=4000,
        messages=[
        {"role": "user", "content": prompt}
    ]
    )
    print(response.content)
    return response.content

def main():
    # ... (previous code for scraping remains the same)

    # After scraping and storing data in all_url_contents
    print("\nSending data to Claude for analysis...")
    analysis = analyze_coverage(all_url_contents)
    
    print("\nClaude's Analysis:")
    print(analysis)

if __name__ == "__main__":
    main()