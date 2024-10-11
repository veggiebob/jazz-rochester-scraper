from selenium import webdriver
from selenium.webdriver.common.by import By

# use firefox webdriver
driver = webdriver.Firefox()

def get_event_entries(url: str) -> list[str]:
    driver.get(url)
    # get all event entries
    body = driver.find_elements(By.CSS_SELECTOR, 'article .entry-more>*')
    contents = [ (x, x.tag_name, x.text) for x in body ]
    flattened_entries = []
    current_header = ''
    for e, tag, content in contents:
        if tag.startswith('h'):
            current_header = content
        else:
            for child in e.find_elements(By.CSS_SELECTOR, 'li'):
                flattened_entries.append(f'{current_header}: {child.text}')
    driver.close()
    return flattened_entries

# url = 'https://www.jazzrochester.com/2024/10/rochester-jazz-listings-20241009.html'
# get_event_entries(url)