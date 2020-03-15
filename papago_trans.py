import time
from selenium import webdriver
import click

def start_driver():
    global driver
    driver = webdriver.Chrome()
    driver.get('https://papago.naver.com/')

def papa_list(string, delim = "\n\n"):
    """
    Input is a string. The whole string that I want to translate.
    Specify the delimiter to get a list of sentences.
    This output could be an input to the `papa_translate` function.
    """
    ls = string.split(delim)
    ls = [_.replace('\n', '') for _ in ls]
    
    if max([len(_) for _ in ls]) > 5000:
        print("WARNING: Length of one string is too long!!!!!")
    else:
        print("Good to go")
    return ls

def papa_translate(papa_list, sleep_time=5):
    """
    The input is a list of sentences.
    Output is the translated version of those sentences.
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

def papa_save(papa_list, encoding = 'utf-8', delim='\n\n', file_name = 'translatedFile.txt'):
    """
    Saves the translated list.
    Doesn't return anything.
    """
    t = ''
    for i in papa_list:
        t += i+ delim
    file = open(file_name, 'w', encoding = 'utf-8')
    file.write(t)
    print("Done. The file name is:", file_name)
    


@click.command()
@click.option('--delim', default="\n\n", type=str)
@click.option('--sleep_time', default=5, type=int)
@click.option('--input_dir', prompt='text file directory')
@click.option('--output_dir', default='translatedFile.txt', type=str)

def main(input_dir, delim, sleep_time, output_dir):

    start_driver()

    with open(input_dir, 'r', encoding='utf-8') as f:
        text = f.read()

    delimmed_text = papa_list(text, delim=delim)
    translated_text = papa_translate(delimmed_text, sleep_time=sleep_time)
    papa_save(translated_text, file_name=output_dir)

    driver.close()

if __name__ == "__main__":
    main()
