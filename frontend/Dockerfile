FROM node:24-slim

RUN apt-get update && apt-get upgrade -y && apt-get clean

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 4200

CMD ["npm", "start", "--", "--host", "0.0.0.0"]