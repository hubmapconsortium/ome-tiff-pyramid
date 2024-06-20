# Local usage

```
# Pull the docker image
docker pull hubmap/ome-tiff-pyramid
# Start a local container, mounting your data directory to the container
docker run -dit --mount type=bind,source=/your/data/directory,target=/mnt/data hubmap/ome-tiff-pyramid
# Enter the docker container with the container ID returned by the last command
docker exec -it {YOUR_CONTAINER_ID} /bin/sh
# Run the script
./ometiff_to_pyramid.py /mnt/data/your-image.ome.tiff /mnt/data/processed 8
```
