# Setup Environment 

1. If you haven't already, create a conda environment with Python version 3.9 and activate it.
```
conda create --name cloud python=3.9
conda activate cloud
```

2. Install all Python dependencies.
```
pip install -r requirements.txt
```

3. Install and configure the TTN command-line interface. This will generate a file named `.ttn-lw-cli.yml`, which is used to connect to your The Things Stack deployment.
```
brew install TheThingsNetwork/lorawan-stack/ttn-lw-cli
ttn-lw-cli use symrec.nam1.cloud.thethings.industries
```

Then, login to TTN using the CLI. This will open a browser window where you can login with your credentials.
```
ttn-lw-cli login --callback=false
```
4. Upload your .env file containing values for TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TTN_API_KEY into the root folder of this project.
   
6. Make and run django data model migrations:
```
python3 manage.py makemigrations cloud_app
python3 manage.py migrate
```

# Running the project
1. Launch the server.
```
python ./manage.py runserver
```
Now, you should be able to access your development server at `http://127.0.0.1:8000/`!
