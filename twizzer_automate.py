"""
Author: Swapnil Shinde <Username:AtmegaBuzz>
By Vscale Consulting LLP
"""

import tweepy 
import json
import requests
import time
import gspread



class TwizzerAutomate():
    def __init__(self,username,spreadsheet,credentials,gform_url,headers):
        
        self.gc = gspread.service_account(filename=credentials)   
        self.spreadsheet = spreadsheet   
        self.new_tweets = []
        self.username = username
        self.gform_url = gform_url
        self.headers = headers
    
    def get_auth(self):
        consumer_key = "hvJ3Mc5hfuw6FbuW0GwsrNail"
        consumer_secret = "77g1My9L2oEyzY137okPsRAlB2hOjkLulyxZRJ00lbVMY8NKwe"
        callback_uri = "oob"
        
        
        auth = tweepy.OAuthHandler(consumer_key,consumer_secret,callback=callback_uri)
        return tweepy.API(auth)
    
    def get_new_tweets(self):
        api = self.get_auth()
        tweets = api.search_tweets(q=f"(from:{self.username}) filter:replies")
        
        gsheet = self.gc.open_by_url(self.spreadsheet)
        row_count = gsheet.sheet1.row_count-100
        prev_tweets = gsheet.values_get(f"Form Responses 1!C{row_count-14}:C")["values"]

        
        self.new_tweets = [] #emptying new tweets for storing new recent tweets
        found = False
        for tweet in tweets:
            for prev_tweet in prev_tweets:      
                status_id_tweet = tweet._json["id_str"]
                status_if_prev_tweet = prev_tweet[0].split("/")[-1]
                
                if(status_id_tweet==status_if_prev_tweet):
                    found = True
                    break
            if(not found):
                self.new_tweets.append(tweet)
                found = False
                

        if(len(self.new_tweets)==0): #if no new tweets are there return false
            return False        
                    
        
        return True
    
    def fill_gform(self,link):
        url = self.gform_url

        payload=f'dlut=1636952109600&entry.1351966323={link}&entry.857122997=Asad%236857&fbzx=5443304911869192861&fvv=1&pageHistory=0&partialResponse=%5Bnull%2Cnull%2C%225443304911869192861%22%5D'
        headers = self.headers
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            print("data submitted")
        except:
            print("error in fillIng form",response.status_code)
       
    def scrape_tweets(self):
       
        
        if(self.get_new_tweets()): #fill new tweets instance variable
            for tweet in self.new_tweets:
                tweet_dict = tweet._json
                
                status_id = tweet_dict["id_str"]
                username = tweet_dict["user"]["screen_name"]
                link = f"twitter.com/{username}/status/{status_id}"
                # print(link)
                self.fill_gform(link)
                
            return
        
        print("no new tweets")
        
            
    def run(self):
        
        while(True):
            self.scrape_tweets()
            time.sleep(10)

import config

username=config.username
spreadsheet=config.spreadsheet
credentials=config.credentials_json
gform_url=config.gform_url
headers = config.headers

bot = TwizzerAutomate(username,spreadsheet,credentials,gform_url,headers)
bot.run()



