# Craigslist-Fraud-Detection
Python code to detect fraudulent apartment rental posts

This project scrapes NYC apartment rental posts from Craigslist, generates features from the post's components (i.e. amenities, price, location), from the text in the title and body of the post, and several time-based features.

The project has a few additional steps that have yet to be implemented.  These ideas include the commented-out phone number retreival element, breaking location down by neighborhood, identifying price outliers and calculating whehter a post falls within a normal range based on its location (since prices vary widely), and text based classifications such as number of (or percentage of) upper case letters, special characters, and length of text.  NLP characteristics like n-grams can be implemented to detect sentence structure anomalies. Lastly, tweaking of the ensemble method can be done to increase the prediction accuracy.
