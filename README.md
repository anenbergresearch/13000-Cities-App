# Dockerize a dash app (replace <tag> with your own tag name)
### 1.	Build the docker image
    docker build --platform linux/amd64 -t <image-name> .
### 2.	Tag the image to the docker hub (13000cities repository)
    docker tag <image-name> srunkel/13000cities:<tag>
### 3.	Push to remote repository:
    docker push srunkel/13000cities:<tag>

# Run Docker Image on Remote Server
### 1.	ssh into remote server (currently on Kamatera)— password:XXXX
    ssh root@83.229.112.187
### 2.	Log-in to docker (will request username and password)
    docker login
### 3.	pull remote repository (13000cities)
    docker pull srunkel/13000cities:<tag>
### 4. Check for running instances on port 8050 and stop it
    docker ps -a
    docker remove <name>    
### 4.	Run the docker on remote server and specify port. Set to automatically restart if crashed
    docker run --name multipage -p 443:8050 srunkel/13000cities:<tag>
    docker update --restart unless-stopped multipage
### 5.	Access app from browser using IP address and port: http://83.229.112.187:8050/cities

# Refresh SSL Certificate
To refresh the SSL certificate, log into ssl.IONOS.com and generate one with the domain name.

# Example:
    docker build --platform linux/amd64 -t 13000-app .
    docker tag 13000-app srunkel/13000cities:multipage
    docker push srunkel/13000cities:multipage


# Update input files
#### To update the data read into the website, you do not need to update the website, just push a new dataset version (unified_data_sr-v2.csv) to the app-files repository
