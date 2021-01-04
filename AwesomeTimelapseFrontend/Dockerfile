FROM node:10-alpine

# Create app directory
RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app
WORKDIR /home/node/app

# or just use default?
#WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./

USER node

RUN npm install

#COPY --chown=node:node . .
COPY . .

EXPOSE 8080
CMD [ "node", "frontend.js" ]