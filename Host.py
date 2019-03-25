import requests, os
import math
from flask import Flask, request, render_template, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
env=Environment(loader=FileSystemLoader("templates/"), autoescape=select_autoescape(["html", "xml"]))

app=Flask(__name__)

##All Functions Below Here are Supplementary to Displaying Webpage##
#Finds the jpeg link within the json collection for that result
def findJPGLink(image): 
    firstIndex=image.find("[")
    lastIndex=image.find(",")
    image=image[firstIndex+2:lastIndex-1]
    #The original image link seems to always be the first one in list
    return image
    
#Finds the video link within the json collection for that result    
def findVideo(video): 
    video=video[1:len(video)-1]
    videoLst=video.split(",")
    videoLink=""
    #The video link is the mp4 file in the list
    for i in range(len(videoLst)): 
        if "mp4" in videoLst[i]:
            videoLink=videoLst[i]
        #Determining the final link since there are extra quotations in the list
        #index
    videoLink=videoLink[2:len(videoLink)-1]
    return videoLink
 
#Stores all the media links for the search query to be displayed in html file 
def storeResponses(jsonTxt): 
    mediaLinks=[]
    links=jsonTxt["collection"]["items"]
    for item in range(len(links)): 
        jsonLink=links[item]["href"]
        response=requests.get(jsonLink)
        if response.status_code==200:
            #Redirects to helper function for finding the image link
            if "image" in jsonLink:
                jpeg=findJPGLink(response.text)
                mediaLinks.append(jpeg)
            #Redirects to helper function for finding the video link 
            if "video" in jsonLink: 
                mp4=findVideo(response.text)
                mediaLinks.append(mp4)
    return mediaLinks

##All Functions Below Here Display Webpage Results##
def display_results(numRows, numLinks, queryResponse, mediaLinks): 
    template=env.get_template("searchquery.html")
    cssUrl=url_for('static', filename="styles.css")
    return template.render(rows=numRows, numLinks=numLinks,  searchQuery=queryResponse,mediaLinks=mediaLinks, cssurl=cssUrl)

@app.route("/")
def my_form(): 
    return render_template("index.html")

@app.route("/", methods=['POST'])
def my_form_post():
    queryResponse=request.form["searchbox"] 
    #Sets the number of images wanted per row
    numImageRow=3
    #Accessing the API
    response=requests.get("http://images-api.nasa.gov/search?q="+queryResponse)
    mediaLinks=storeResponses(response.json())
    numLinks=len(mediaLinks)
    #Determines the number of rows required
    numRows=numLinks/numImageRow
    numRows=math.ceil(numRows)
    if request.method=="POST": 
        return display_results(numRows, numLinks, queryResponse, mediaLinks)
    
    

##Runs the main file##
if __name__ == '__main__':
  app.run()