import tweepy
import smtplib
from textblob import TextBlob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure 
import re
from wordcloud import WordCloud
import os
import pandas as pd
from email.message import EmailMessage
import snscrape.modules.twitter as sntwitter
from flask import Blueprint, render_template, request
plt.style.use('fivethirtyeight')

second = Blueprint("second", __name__, static_folder="static", template_folder="template")
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# consumer_key = "zvghpJLaBrHdUqloJDlcV7rum"
# consumer_sec = "BKvbGtBlMBUPn9ONG1x7LrYkLclA2sRXT5G4KuGZiPgGlnNq2R"
# access_token = "1383703955218132994-lz4OavJh4DLABqVo4SBnjzqSWw72vE"
# access_token_sec = "oj254ngv1FjYnVveQOL1SQuRxOtR88xkROqaXSm8zalPQ"
# # create an authentication object
# auth = tweepy.OAuthHandler(consumer_key, consumer_sec)
# # set the access token and access token secret
# auth.set_access_token(access_token, access_token_sec)
# # create an API object
# api_connect = tweepy.API(auth,wait_on_rate_limit=True)

# text1 = input("enter the subject")
# tweet_data = api_connect.search_tweets(q, count=100)
# df = pd.DataFrame([tweet.text for tweet in tweet_data], columns=['Tweets'])
text1 = ""
def getQuery(q, mail,n):
    text1 = q
    tweets = []
    limit=int(n)
    for tweet in sntwitter.TwitterSearchScraper(text1).get_items():
        
        if len(tweets) == limit:
            break
        else:
            tweets.append([tweet.content])

        

    # tweet_data = api_connect.search_tweets(q, count=100)
    
#   df = pd.DataFrame([tweet.text for tweet in tweet_data], columns=['Tweets'])
    df = pd.DataFrame(tweets, columns=['Tweets'])
    df['Tweets'] = df['Tweets'].apply(cleantxt)
    df['Subjectivity'] = df['Tweets'].apply(getsubjectivity)
    df['Polarity'] = df['Tweets'].apply(getpolarity)
    pos=neu=neg=pol=sub=0
    with PdfPages("static/data/Sentiments_visualizations.pdf") as pdf:
        df['Analysis'] = df['Polarity'].apply(getAnalysis)
    # plot the graph between Subjectivity and polarity
        plt.figure(figsize=(8, 8))
        for i in range(0, df.shape[0]):
            plt.scatter(df['Polarity'][i], df['Subjectivity'][i], color='Blue')
            pol+=df['Polarity'][i]
            sub+=df['Subjectivity'][i]
            if(df['Polarity'][i]>0):
                pos=pos+1
            elif(df['Polarity'][i]==0):
                neu=neu+1
            else:
                neg=neg+1
        plt.title('Sentiment Analysis (Scatter Plot)')
        plt.xlabel('Polarity')
        plt.ylabel('Subjectivity')
        pdf.savefig()
        # plt.show()

        df['Analysis'].value_counts()
        plt.figure(figsize=(8, 14))
        plt.title('Sentiment Analysis (Bar Graph)')
        plt.xlabel('Sentiment')
        plt.ylabel('Counts')
        df['Analysis'].value_counts().plot(kind='bar')
        pdf.savefig()
        # plt.show()

    # plotting of wordcloud
        wrds = ' '.join([twts for twts in df['Tweets']])
        plt.figure(figsize=(10,10))
        plt.title('Sentiment Analysis (WordCloud Analysis)')
        wordCloud = WordCloud(width=500, height=300, random_state=21, max_font_size=119).generate(wrds)
        plt.imshow(wordCloud, interpolation="bilinear")
        plt.axis('off')
        pdf.savefig()
        # plt.show()

        plt.figure(figsize=(8, 14))
        # plt.rcParams["figure.figsize"] = [7.50, 3.50]
        # plt.rcParams["figure.autolayout"] = True
        # dir_name = "C:\\wamp64\\www\\Social_media_sentiment_analysis\\static\\images"
        # plt.rcParams["savefig.directory"] = os.chdir(os.path.dirname(dir_name))
        plt.xlabel("tags")
        plt.ylabel("polarity")
        plt.title('Tender Anatomy (Piechart)')
        # plt.bar(['pos','neg','neu'],[pos,neg,neu])
        plt.pie([pos, neg, neu], labels=['pos', 'neg', 'neu'], autopct="%1.1f%%")
        pdf.savefig()
        plt.savefig("static/img/graph.png")
    
    df.to_csv("static/data/sentimental_analysis.csv", header=False, index=False)
    sendMail(mail)
    sub=sub/(int)(n)
    pol=pol/(int)(n)
    return pos,neu,neg,pol,sub

def cleantxt(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'RT[\s]+', '', text)
    text = re.sub(r'https?:\/\/\S+', '', text)
    return text

# print(df)
# function to get subjectivity
def getsubjectivity(text):
    return TextBlob(text).sentiment.subjectivity


# function to get polarity
def getpolarity(text):
    return TextBlob(text).sentiment.polarity

# function to get analysis
def getAnalysis(x):  # polarity
    if (x < 0):
        return 'Negative'
    elif (x == 0):
        return 'Neutral'
    elif (x > 0):
        return 'Positive'

def sendMail(mail):
    msg = EmailMessage()
    msg['Subject'] = 'Tender Anatomy'
    msg['From'] = 'Automation Team'
    msg['To'] = mail
    with open("static/data/email.txt") as myfile:
        data = myfile.read()
        msg.set_content(data)

    with open("static/data/sentimental_analysis.csv", "rb") as f:
        file_data = f.read()
        file_name = f.name
        msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name)
    with open("static/data/Sentiments_visualizations.pdf", "rb") as f:
        file_data1 = f.read()
        file_name1 = f.name
        msg.add_attachment(file_data1, maintype="application", subtype="pdf", filename=file_name1)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('abhishekjain9638@gmail.com', 'ftqvalczzvehitgf')
        server.send_message(msg)
#     print("email sent!!!")