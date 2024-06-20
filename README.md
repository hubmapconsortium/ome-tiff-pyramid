# Local usage

```
# Pull the docker image
docker pull hubmap/ome-tiff-pyramid
# Start a local container
docker run -t -d hubmap/ome-tiff-pyramid
# Mount your data directory to the container
docker run --mount type=bind,source=/your/data/directory,target=/mnt/data hubmap/ome-tiff-pyramid
# Open the docker container
docker exec -it hubmap/ome-tiff-pyramid
# Run the script
./ometiff_to_pyramid.py /mnt/data/your-image.ome.tiff /mnt/data/processed 8
```