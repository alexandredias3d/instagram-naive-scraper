# Instagram Naive Scraper

This program uses ``playwright`` to scrape photos, videos and captions from Instagram posts.

## How to Use

1. Install Python 3.11 or greater.
2. Install [poetry](https://python-poetry.org/docs/#installation).
3. Clone this repository and run the following command: 
    ```
    $ poetry install
    ```
4. Create a configuration JSON file with the following tags:
   - username: username of account that will be used to scrape the posts.
   - password: password of account that will be used to scrape the posts.
   - browser: string that could be either:
     - __"gui"__: runs the scraper with the browser open.
     - __"headless"__: runs the browser in headless mode, i.e. without the user interface.
   - action_delay: floating number that represents the delay between the browser actions, in seconds.
   - loading_delay: integer number that represents the delay after loading the page, in seconds.
   - scrolling_delay: integer number that represents the delay between each scrolling down, in seconds.
   - scraping_delay: integer number that represents the delay after scraping one post, in seconds.
   - max_retries: integer number that represents the maximum number of retries if the page load or scrape fails.
5. Run the following command:
   ``` 
   $ main.py <profile_to_scrape> <path_to_configuration_file>
   ```