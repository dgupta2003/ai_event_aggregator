Eventbrite Console Scraper
This is a self-contained JavaScript snippet designed to be run directly in your web browser's Developer Console. It scrapes visible event data from an Eventbrite search results page (like the NYC Technology events page) and outputs the results in two formats: a clean Markdown table and a CSV string that is automatically copied to your clipboard.
How to Use the Script
Navigate to the Target Page: Open the Eventbrite search results page you wish to scrape
Scroll Down: Scroll all the way to the bottom of the page. The script includes an auto-scrolling feature, but pre-scrolling helps ensure all content is initially loaded.
Open the Console: Open your browser's Developer Tools (usually by pressing F12 or Ctrl+Shift+I). Click on the Console tab.
Paste and Run
It will print a nicely formatted Markdown table directly to your console, allowing you to quickly read the data.
If the script runs but extracts many N/A values or reports "No events found," it means the internal selectors used to find the event elements are outdated.
