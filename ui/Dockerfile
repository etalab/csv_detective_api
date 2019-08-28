FROM node:latest

# Create app dir
#RUN mkdir -p /usr/src/app
COPY . /app
WORKDIR /app


RUN npm install
EXPOSE 3000

CMD ["npm", "start"]