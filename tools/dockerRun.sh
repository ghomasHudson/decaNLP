docker run --runtime=nvidia -it --rm --memory 30g --memory-swap -1 -v "$(pwd):/decaNLP" -u $(id -u):$(id -g) bmccann/decanlp:cuda10_torch1latest bash
