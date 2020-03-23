# google-docs-example
Using google docs APIs, populate Wikipedia content on **COVID-19 (A pandamic, causing worldwide lockdown)**

# Installation
Very well documented steps can be found here. As the steps on the page suggest please enable the APIs so that you can start using cloud services. 
## Step 1: 
Follow the button links to gain access to Google documents APIs. Download the credentials.json to your work area where you will be creating your google client project. 

## Step 2:
Install Google's python client for cloud APIs. 

```pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib```

## Step 3: (Optional)
We are scrapping content from Wikipedia and hence we need this python package, otherwise its optional. 

```pip3 install wikipedia-api```

# Running the project
By default, the project use my template but feel free to change the tamplate and respective code. To run the code: 

```python google-docs-example.py```

# Debugging
As an example, if you would like to see the JSON dump of requests structure, please set 'DEBUG = 1'. Likewise you can dump requests as any stage in the document. 
