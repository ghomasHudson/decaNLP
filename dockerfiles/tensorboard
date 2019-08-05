FROM eywalker/tensorflow:v0.11.0rc0
MAINTAINER Edgar Y. Walker <edgar.walker@gmail.com>

# Export port for TensorBoard
EXPOSE 6006

WORKDIR /tensorboard

# Start running tensorboard when container is launched
ENTRYPOINT ["tensorboard", "--logdir=/tensorboard/"]
