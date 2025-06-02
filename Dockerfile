FROM node:alpine

WORKDIR /betterself

RUN npm install -g @angular/cli

COPY . .

RUN npm install

CMD [ "ng", "serve", "--host", "0.0.0.0" ]
