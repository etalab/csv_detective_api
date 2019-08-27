FROM node:latest

# Create app dir
RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app


RUN npm install

CMD ["npm", "start"]