import requests
import yaml
from bs4 import BeautifulSoup
from fill_csv import remove_punctuation_digit


# URL of the Wikipedia page
url = 'https://en.wikipedia.org/wiki/List_of_academic_fields'

response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')
academic_fields = {}
academic_fields_list = []
content = soup.find('div', {'class': 'mw-parser-output'})


def remove_punctuation_digit_lower(text):
    return remove_punctuation_digit(text.replace(' (*)', '')).lower().strip()


def find_all_ul_siblings(sibling):
    ul_elements = []
    for sib in sibling.find_next_siblings():
        if sib.name in ['h3', 'h4', 'h2']:
            break
        if sib.name == 'ul':
            ul_elements.append(sib)
        if sib.name == 'div':
            ul_in_div = sib.find('ul')
            if ul_in_div:
                ul_elements.append(ul_in_div)
    return ul_elements


for h3 in content.find_all('h3'):
    first_level = h3.find('span', class_='mw-headline').get_text(strip=True)
    academic_fields[first_level] = []
    academic_fields_list.append(remove_punctuation_digit_lower(first_level))

    ul_elements = find_all_ul_siblings(h3)
    for ul in ul_elements:
        li_texts = []
        for li in ul.find_all('li'):
            li_texts.extend(li.get_text(strip=False).split('\n'))
        academic_fields[first_level].extend(li_texts)
        academic_fields_list.extend([remove_punctuation_digit_lower(text) for text in li_texts])

    for sibling in h3.find_next_siblings():
        if sibling.name == 'h3':
            break
        if sibling.name == 'h4':
            second_level = sibling.find('span', class_='mw-headline').get_text(strip=True)
            academic_fields[first_level].append({second_level: []})
            academic_fields_list.append(remove_punctuation_digit_lower(second_level))

            ul_elements = find_all_ul_siblings(sibling)
            for ul in ul_elements:
                li_texts = []
                for li in ul.find_all('li'):
                    li_texts.extend(li.get_text(strip=False).split('\n'))
                academic_fields[first_level][-1][second_level].extend(li_texts)
                academic_fields_list.extend([remove_punctuation_digit_lower(text) for text in li_texts])


# Save the data as a YAML file with hierarchical structure
with open('csv/wiki/academic_fields.yaml', 'w') as file:
    yaml.dump(academic_fields, file, allow_unicode=True, default_flow_style=False)

print("Academic fields have been saved to academic_fields.yaml")

# Save list as a text file
with open('csv/wiki/academic_fields.txt', 'w') as file:
    for field in academic_fields_list:
        file.write(field + '\n')

print("Academic fields have been saved to academic_fields.txt")
