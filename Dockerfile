FROM node:24.11.1 AS ui-builder

WORKDIR /app/ui

COPY codeair-ui/package.json codeair-ui/yarn.lock ./

RUN yarn install --frozen-lockfile

COPY codeair-ui/ ./

RUN yarn build

FROM python:3.12.12

WORKDIR /app/api

COPY codeair-api/requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install git+https://github.com/qodo-ai/pr-agent.git@v0.29

COPY codeair-api/ ./

# Copy built UI from the first stage to the static directory
COPY --from=ui-builder /app/ui/dist/ ./codeair/static/

EXPOSE 80

CMD ["python", "-m", "uvicorn", "codeair.start_server:app", "--host", "0.0.0.0", "--port", "80"]
