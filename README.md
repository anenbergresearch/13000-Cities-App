# Dockerize a dash app
### 1.	Build the docker image
    docker build --platform linux/amd64 -t <image-name> .
### 2.	Tag the image to the docker hub (13000cities repository)
    docker tag <image-name> srunkel/13000cities:<tag>
### 3.	Push to remote repository:
    docker push srunkel/13000cities:<tag>

# Run Docker Image on Remote Server
### 1.	ssh into remote server (currently on Kamatera)— password:XXXX
    ssh root@194.113.211.229
### 2.	Log-in to docker (will request username and password)
    docker login
### 3.	pull remote repository (13000cities)
    docker pull srunkel/13000cities:<tag>
### 4.	Run the docker on remote server and specify port
    docker run -p 8050:8050 srunkel/13000cities:<tag>
### 5.	Access app from browser using IP address and port: http://194.113.211.229:8050/cities


# Example:
    docker build --platform linux/amd64 -t 13000-app .
    docker tag 13000-app srunkel/13000cities:multipage
    docker push srunkel/13000cities:multipage


# Update input files
#### To update the data read into the website, you do not need to update the website, just push a new dataset version (unified_data_sr-v2.csv) to the app-files repository
