# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 20:27:50 2023

@author: RDxR10
"""
from selenium.common.exceptions import NoSuchElementException
import time
from selenium import webdriver
import csv
import requests
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

query = input("Enter job query: ")
location = input("Enter job location: ")
num_pages = int(input("Number of pages: "))
start_list = [page * 10 for page in range(num_pages)]
base_url = 'https://pk.indeed.com'
#base_url = "https://www.indeed.com'

driver = webdriver.Chrome()
# driver = webdriver.Chrome(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

for start in start_list:
    url = base_url + f'/jobs?q={query}&l={location}&start={start}'
    driver.execute_script(f"window.open('{url}', 'tab{start}');")
    time.sleep(1)

with open(f'{query}_{location}_job_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Job Title', 'Company', 'Location', 'Job Link', 'Salary','Job Type','Posted Date','Vacancy','Description'])
    for start in start_list:
        driver.switch_to.window(f'tab{start}')

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('td', {'class': 'resultContent'})

        for job in items:
            s_link = job.find('a').get('href')
            # job_title = job.find('span', title=True).text.strip()
            job_title = job.find('h2',class_='jobTitle').text.strip()
            company = job.find('span', class_='companyName').text.strip()
            location = job.find('div', class_='companyLocation').text.strip()
            if job.find('div', class_='metadata salary-snippet-container'):
                salary = job.find('div', class_='metadata salary-snippet-container').text
            elif job.find('div', class_='metadata estimated-salary-container'):
                salary = job.find('div', class_='metadata estimated-salary-container').text
            else:
                salary = ""
            
            job_link = base_url + s_link

            driver.get(job_link)
            page_sourse = driver.page_source
            soup = BeautifulSoup(page_sourse, 'html.parser')
            Detail = soup.find('div',class_='jobsearch-ViewJobLayout-innerContent') 
            JobType = ""
            vacancy = ""
            PostedDate = ""
            JobDescription = ""
            FullDescription = ""
            HiringInsights = ""
            vacancySight  = ""
            JobActivity = ""
            try:
                job_type_element = Detail.select_one('div.css-rr5fiy > div:last-child')
                if job_type_element:
                    JobType = job_type_element.text
                else:
                    JobType = "N/A"
                FullDescription = Detail.find('div', class_='jobsearch-jobDescriptionText')
                JobDescription = FullDescription.text
                # p_tags = FullDescription.find_all('p')
                # try:
                #     shortDescription = p_tags[0].text
                # except NoSuchElementException:
                #     print("Short Description not found")
                # try:
                #     secondParaDescription = p_tags[1].text
                # except NoSuchElementException:
                #     print("Second P is not found")
                # try:
                #     thirdParaDescription = p_tags[2].text
                # except NoSuchElementException:
                #     print("Third P is not found")
                # print(shortDescription + " " + secondParaDescription + " " + thirdParaDescription)
                HiringInsights = Detail.find('div',class_='css-q7fux')
                vacancySight = HiringInsights.find_all('p')
                if vacancySight:
                    try:
                        vacancy = vacancySight[0].text
                    except NoSuchElementException:
                        print("Vacancy Not Found")
                else:
                    print("Not Found")
                JobActivity = HiringInsights.find('ul')
                try:
                    PostedDate = JobActivity.find('span',class_='css-kyg8or').text
                except NoSuchElementException:
                    print("Not Found")
                print(PostedDate)
                # print(vacancy)

            except AttributeError:
                print("Not Found")
            print(" ")

            writer.writerow([job_title, company, location, job_link, salary, JobType, PostedDate, vacancy, JobDescription])

        driver.close()


driver.quit()
