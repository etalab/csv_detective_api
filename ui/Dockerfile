FROM node:latest

# Create app dir
#RUN mkdir -p /usr/src/app
COPY . /app
WORKDIR /app


RUN npm install
EXPOSE 3000

ENV REACT_APP_API_URL "http://localhost:5000/csv_detective/"
CMD ["npm", "start"]