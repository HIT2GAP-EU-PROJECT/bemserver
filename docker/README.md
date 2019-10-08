## Docker


### Installation

Docker images and `docker-compose.yml` file are provided to simplify installation process. 

```bash
# In $YOUR_INSTALL_FOLDER
cd $YOUR_INSTALL_FOLDER/

# Get docker-compose.yml file
wget https://raw.githubusercontent.com/HIT2GAP-EU-PROJECT/bemserver/master/deployment/docker-compose.yml

# Run application
docker-compose up -d
```

**Beware, the provided images / configuration should be modified when deploying the solution in production environment to ensure safer access to data.**


### More info

- [Docker doc.](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
