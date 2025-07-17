# --- Base image ---
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./

# --- Dependencies ---
FROM base AS deps
RUN npm install

# --- Build ---
FROM deps AS build
COPY . .
RUN npm run build

# --- Production ---
FROM node:20-alpine AS prod
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/build ./build
COPY . .
EXPOSE 4173
CMD ["npm", "run", "preview", "--", "--host"]

# --- Development ---
FROM deps AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"] 