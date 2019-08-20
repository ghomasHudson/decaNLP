# Starts tensorboard docker env


if [ "$#" -ne 1 ] || ! [ -d "$1" ]; then
    echo "Usage: $0 RESULTS_DIR"
    exit 1
fi


# Docker doesn't support symbolic links
# Fix by finding all links and mounting them as volumes
cd $1
volumes="-v $(pwd):/tensorboard "

for f in $1/*; do
    if [ -d "$f" ]; then
        if [ -d "$(readlink $f)" ]; then
            echo "Mounting symbolic link: '$f' as volume"
            volumes+="-v $(realpath $f):/tensorboard/$f "
        fi
    fi
done

docker run --runtime=nvidia -it --rm --memory 5g --memory-swap -1 $volumes -u $(id -u):$(id -g) eywalker/tensorboard

