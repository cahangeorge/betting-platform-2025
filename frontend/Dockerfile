FROM node:22-alpine AS builder

WORKDIR /app

RUN npm install -g pnpm@10

COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:22-alpine AS runner

WORKDIR /app

RUN addgroup -S -g 1001 nodeuser \
    && adduser -S -u 1001 -G nodeuser nodeuser

COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./

RUN chown -R nodeuser:nodeuser /app

USER nodeuser

EXPOSE 3000

ENV NODE_ENV=production

CMD ["node", "build/index.js"]
