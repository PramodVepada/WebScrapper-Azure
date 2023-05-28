from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
import logging
logging.basicConfig(filename="scrapper.log",level=logging.INFO)
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://pramodvepada99:ineuron@cluster0.2me4xpf.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
database = client['webscrapper']
coll = database['flipkart']
application = Flask(__name__)
app = application 

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/review",methods = ["POST","GET"])
def index():
    if request.method == "POST":
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uclient = uReq(flipkart_url)
            flipkartPage = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartPage,"html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:1]
            box = bigboxes[2]
            productlink = "https://www.flipkart.com"+box.div.div.div.a['href']
            productreq = requests.get(productlink)
            productreq.encoding='utf-8'
            product_html= bs(productreq.text,"html.parser")
            comment_box=product_html.find_all("div",{"class":"_16PBlm"})
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []

            for comment in comment_box:
                try:
                    rating = comment.div.div.div.div.text
                except:
                    rating = "No rating"
                    logging.info(rating)
                try:
                    opinion = comment.div.div.div.p.text
                except:
                    opinion = "No opinion"
                    logging.info(opinion)
                try:
                    commtag = comment.div.div.find_all("div",{"class":""})[0].div.text
                except Exception as e:
                    logging.info(e)
                
                try:
                    name = comment.div.div.find_all("div",{"class":"row _3n8db9"})[0].div.p.text
                except:
                    name = "no name"
                    logging.info(name)
                mydict = {"Product": searchString, "Name": name, "Rating": rating, "opinion": opinion,
                          "Comment": commtag}
                coll.insert_one(mydict)
                
                reviews.append(mydict)
                logging.info(reviews)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    else:
        return render_template('index.html')
            


if __name__=="__main__":
    app.run(host="0.0.0.0")
