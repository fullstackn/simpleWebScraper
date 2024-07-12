import argparse
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

TAGS = 'Politics,Mars'
OUTPUT_FILENAME = 'out.csv'
fields_list = ['title', 'text', 'tags', 'comments', 'datetime', 'author']

def get_tag_html(tag: Tag):
    return ''.join([i.decode() if type(i) is Tag else i for i in tag.contents])


def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda l_driver: l_driver.execute_script("return document.readyState") == "complete"
    )


def get_stories(page_url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    driver.get(page_url)
    all_stories = []
    # full load of all stories (through scrolling)
    while True:
        wait_for_page_load(driver)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "stories-feed__message")))
        all_stories += BeautifulSoup(driver.page_source, 'html.parser').find_all(name='article')
        if element.get_attribute('style') == 'display: block;':
            break
    # filter out duplicates
    all_stories_filtered = []
    for st in all_stories:
        if st.get('data-story-id') not in [s.get('data-story-id') for s in all_stories_filtered]:
            all_stories_filtered.append(st)
    return all_stories_filtered


def process_stories(story_list):
    story_data = []
    for story in story_list:
        title_tag = story.find(class_='story__title')
        if title_tag is not None:
            title = title_tag.find(name='a').text
        else:
            title = ''
        story_tags = [t.attrs['data-tag'] for t in story.find(class_='story__tags').find_all(name='a')]

        n_comments = story.find(class_='story__comments-link-count').text
        dt_tag = story.find(class_='story__datetime')
        story_date = dt_tag.attrs['datetime']
        text_tag = story.find(class_='story-block_type_text')
        author = story.find(class_='story__user-link').attrs['data-name']

        if text_tag is not None:
            text = story.find(class_='story-block_type_text').text
        else:
            text = ''
        story_data.append({
            'title': title,
            'text': text,
            'tags': story_tags,
            'comments': n_comments,
            'datetime': story_date,
            'author': author
        })
    return story_data


if __name__ == '__main__':
    # get params
    parser = argparse.ArgumentParser(description='parameters for creating data')
    parser.add_argument('--output_filename', type=str)
    parser.add_argument('--tags', type=str)
    args = parser.parse_args()
    output_filename = args.output_filename or OUTPUT_FILENAME
    tags = args.tags or TAGS

    # read list of stories from the site
    stories = get_stories(f'https://pikabu.ru/tag/{tags}')
    # process this list to get json
    processed = process_stories(stories)
    # write result to csv
    with open(output_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields_list)
        for item in processed:
            writer.writerow([item.get(f) for f in fields_list])
