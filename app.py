from flask import Flask, render_template, request, json, jsonify
import logging
from web_scraper import scrape_website
from analyzer import analyze_coverage
import re , os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load URLs from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    URLS = config['urls']

@app.route('/')
def index():
    app.logger.info("Rendering index page")
    try:
        return render_template('index.html', urls=URLS)
    except Exception as e:
        app.logger.error(f"Error rendering index page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/scrape', methods=['POST'])
def scrape():
    app.logger.info("Scrape request received")
    try:
        url1 = request.form['url1']
        url2 = request.form['url2']
        keywords = request.form['keywords'].split(',')

        all_url_contents = {}
        all_url_contents = scrape_website(url1, keywords, all_url_contents)
        all_url_contents = scrape_website(url2, keywords, all_url_contents)

        analysis = analyze_coverage(all_url_contents)

        # Extract the message from the TextBlock
        analysis_message = str(analysis)
        match = re.search(r"TextBlock\(text=['\"](.+?)['\"], type='text'\)", analysis_message)
        if match:
            analysis_message = match.group(1)
        else:
            analysis_message = "Analysis not available in the expected format."

        return jsonify({
            'url1_content': all_url_contents.get(url1, {}),
            'url2_content': all_url_contents.get(url2, {}),
            'analysis': analysis_message
        })
    except Exception as e:
        app.logger.error(f"Error during scraping: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
        host = os.getenv('FLASK_HOST', 'localhost')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        app.run(host=host, port=port, debug=debug)