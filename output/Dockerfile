FROM node:22-slim AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev
COPY . .
RUN npm run build

FROM node:22-slim

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm install --omit=dev

ENV NODE_ENV production
ENV PORT 8080

USER node

EXPOSE 8080

CMD ["node", "dist/index.js"]