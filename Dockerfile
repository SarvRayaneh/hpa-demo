FROM python:3.12-alpine
WORKDIR /app
COPY app.py .
RUN adduser -D -u 1001 appuser
USER 1001
ENV DATA_DIR=/tmp/counter-data
EXPOSE 8080
CMD ["python", "-u", "app.py"]
