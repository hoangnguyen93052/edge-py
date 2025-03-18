import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import re
import json
from urllib.parse import urlparse
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

class SEOAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.page_title = ''
        self.meta_description = ''
        self.h1_tags = []
        self.images = []
        self.word_count = 0

    def fetch_page(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
            logging.info(f"Fetched page: {self.url}")
        except requests.RequestException as e:
            logging.error(f"Error fetching {self.url}: {e}")

    def parse_content(self):
        if not self.soup:
            logging.warning("No HTML content to parse.")
            return

        self.page_title = self.soup.title.string if self.soup.title else ''
        self.meta_description = self.soup.find('meta', attrs={'name': 'description'})
        if self.meta_description:
            self.meta_description = self.meta_description['content']
        else:
            self.meta_description = ''

        self.h1_tags = [h1.get_text() for h1 in self.soup.find_all('h1')]
        self.word_count = len(re.findall(r'\w+', self.soup.get_text()))

        self.images = [img['src'] for img in self.soup.find_all('img') if 'src' in img.attrs]

        logging.info(f"Page Title: {self.page_title}")
        logging.info(f"Meta Description: {self.meta_description}")
        logging.info(f"H1 Tags: {self.h1_tags}")
        logging.info(f"Word Count: {self.word_count}")

    def analyze_images(self):
        total_images = len(self.images)
        logging.info(f"Total images found: {total_images}")
        if total_images > 0:
            ext_count = Counter([img.split('.')[-1] for img in self.images])
            logging.info(f"Image extensions: {ext_count}")

    def generate_report(self):
        report = {
            'url': self.url,
            'title': self.page_title,
            'meta_description': self.meta_description,
            'word_count': self.word_count,
            'h1_tags': self.h1_tags,
            'images': self.images,
            'image_count': len(self.images)
        }
        return report


class SEOStatsCollector:
    def __init__(self):
        self.reports = []

    def add_report(self, report):
        self.reports.append(report)

    def export_to_csv(self, filename='seo_reports.csv'):
        df = pd.DataFrame(self.reports)
        df.to_csv(filename, index=False)
        logging.info(f"Reports exported to {filename}")

    def visualize_word_counts(self):
        word_counts = [report['word_count'] for report in self.reports]
        urls = [report['url'] for report in self.reports]

        plt.figure(figsize=(15, 7))
        plt.barh(urls, word_counts, color='skyblue')
        plt.xlabel('Word Count')
        plt.title('Word Count per URL')
        plt.show()


def get_urls_from_file(file_path):
    with open(file_path, 'r') as f:
        urls = f.read().splitlines()
    return urls


def main():
    url_file = 'urls.txt'
    urls = get_urls_from_file(url_file)

    stats_collector = SEOStatsCollector()

    for url in urls:
        analyzer = SEOAnalyzer(url)
        analyzer.fetch_page()
        analyzer.parse_content()
        analyzer.analyze_images()
        
        report = analyzer.generate_report()
        stats_collector.add_report(report)

    stats_collector.export_to_csv()
    stats_collector.visualize_word_counts()

if __name__ == "__main__":
    main()