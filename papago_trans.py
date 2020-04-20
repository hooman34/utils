import time
from selenium import webdriver
import click
from tika import parser
import tika

def get_article(file_name):
    """
    Parse text from PDF

    Args:
        file_name (str): File name, except the extension '.pdf'
    
    Returns:
        article (str): Long string, with all the text from pdf file

    """
    article = parser.from_file(file_name+'.pdf')
    article = article['content']
    return article

def start_driver():
    """
    Start chrome webdriver, and go to papago website.
    """
    global driver
    driver = webdriver.Chrome()
    driver.get('https://papago.naver.com/')

def end_driver():
    """
    Close the chrome driver
    """
    driver.close()

def article2lists(article, delim='.', max_length=2000):
    """
    Split the article into list, which will be the input for translation.

    Args:
        article (str): Input is a string. The whole string that needs to be translated.
        delim (str): Delimeter for splitting the article into lists.
        max_length (int): Max length for each input string

    Raises:
        assertionError: If any of the element of the list exceeds length 5000.
                        This is because papago only accepts upto 5000 characters per input.

    Returns:
        papa_list (list): Article, splitted into list
    
    """

    papa_list = dict()
    key = 'key'
    papa_list[key] = ''
    splitted_article = article.split('.')
    for i in range(len(splitted_article)):
        if len(papa_list[key]) < max_length:
            outstring = papa_list[key] + splitted_article[i] + '.'
            papa_list[key] = outstring
        else:
            key = 'key'+str(i)
            papa_list[key] = splitted_article[i]
    papa_list = list(papa_list.values())

    if max([len(_) for _ in papa_list]) > 5000:
        assert False, ("One of the elements in the papa_list is too long.") 

    print("Good to go")
    return papa_list


def papa_translate(papa_list, sleep_time=5):
    """
    The input is a list of sentences.
    Output is the translated version of those sentences.

    Arguments:
        papa_list (list): Article, splitted into list.
        sleep_time (numeric): Time sleeping between translations.

    Returns:
        clean_translate (list): Translated version of article.

    """
    clean_translate = list()
    error_list = list()
    time.sleep(10)
    inputElement = driver.find_element_by_id("sourceEditArea")
    print("Start translating")
    process = 0
    for i, n in zip(papa_list, range(len(papa_list))):
        if i != '':
            try:
                inputElement.send_keys('a' + i)
                time.sleep(sleep_time)
                outputElement = driver.find_element_by_id("targetEditArea")
                print(str(int(round(n/len(papa_list), 2)*100)) + '%', end="\r")
                clean_translate.append(outputElement.text)
                driver.find_element_by_xpath('//*[@id="sourceEditArea"]/button').click()
                time.sleep(1)
            except:
                driver.find_element_by_xpath('//*[@id="sourceEditArea"]/button').click()
                error_list.append(n)
    print('Errors occurred:', error_list)
    return clean_translate

def papa_save(clean_translate, encoding = 'utf-8', delim='\n\n', file_name = 'translatedFile.txt'):
    """
    Saves the translated list.
    
    Arguments:
        clean_translate (list): Translated list
        encoding (str): Encoding type
        delim (str): Delimiter
        file_name (str): File name I want to save as
    
    Returns:
        None

    """
    t = ''
    for i in clean_translate:
        t += i+ delim
    file = open(file_name, 'w', encoding = 'utf-8')
    file.write(t)
    print("Done. The file name is:", file_name)
    
def papa_fix_saved(file_name):
    """
    After initial saving, the text will contain some English version of Korean pronounciation.
    Eliminate those English.

    Args:
        file_name (str): File name to work with

    Returns:
        None

    """
    
    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.split('\n')
    content = [_ for _ in content if _!='']

    end = ''
    for i in range(len(content)):
        if i%2==0:
            end = end + '\n\n' + content[i]

    with open(file_name, 'w', encoding = 'utf-8') as file:
        file.write(end)