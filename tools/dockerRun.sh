# Starts decanlp docker environment
# Docker doesn't support symbolic links
# Fix by finding all links and mounting them as volumes
volumes="-v $(pwd):/decaNLP "

for f in *; do
    if [ -d "$f" ]; then
        if [ -d "$(readlink $f)" ]; then
            echo "Mounting symbolic link: '$f' as volume"
            volumes+="-v $(realpath $f):/decaNLP/$f "
        fi
    fi
done
docker run --runtime=nvidia -it --rm --memory 50g --memory-swap -1 $volumes -u $(id -u):$(id -g) bmccann/decanlp:cuda10_torch1latest bash

