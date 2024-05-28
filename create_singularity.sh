docker build -f docker/Dockerfile -t hubmap/ome-tiff-pyramid .
podman save --format oci-archive hubmap/ome-tiff-pyramid:latest -o ome-tiff-pyramid.tar
singularity build ome-tiff-pyramid.sif oci-archive://ome-tiff-pyramid.tar
