# Base Image
FROM biocontainers/biocontainers:latest

# Metadata
LABEL base.image="biocontainers:latest"
LABEL version="1"
LABEL software="DiffExpIRWeb"
LABEL software.version="0.0.1"
LABEL description="This is a Django web app to visualize differentially expressed intron retention dettected by DiffExpIR"
LABEL website="https://github.com/r78v10a07/DiffExpIRWeb"
LABEL documentation="https://github.com/r78v10a07/DiffExpIRWeb"
LABEL license="http://www.gnu.org/licenses/"
LABEL tags="RNA-seq"

# Maintainer
MAINTAINER Roberto Vera Alvarez <r78v10a07@gmail.com>

USER root

ENV URL=https://github.com/r78v10a07/DiffExpIRWeb
ENV DOCKYARD_SRC=DiffExpIRWeb
ENV DOCKYARD_SRVHOME=/home/biodocker
ENV DOCKYARD_SRVPROJ=$DOCKYARD_SRVHOME/$DOCKYARD_SRC
ENV PYTHONPATH=$DOCKYARD_SRVHOME/$DOCKYARD_SRC/src:$PYTHONPATH

WORKDIR $DOCKYARD_SRVHOME
RUN git clone $URL

WORKDIR $DOCKYARD_SRVPROJ
RUN mkdir logs
VOLUME ["$DOCKYARD_SRVPROJ/logs/"]

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3 python3-pip nodejs npm
RUN pip3 install -r $DOCKYARD_SRVPROJ/requirements/base.txt
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g bower


# Port to expose
EXPOSE 8000

# Copy entrypoint script into the image
#COPY /$DOCKYARD_SRVPROJ/bin/docker-entrypoint.sh /
ENTRYPOINT ["/home/biodocker/DiffExpIRWeb/bin/docker-entrypoint.sh"]
