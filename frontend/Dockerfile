FROM node:16
WORKDIR /app
COPY ./public /app/public
COPY ./src /app/src
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
RUN npm install
CMD ["npm", "run", "start"]