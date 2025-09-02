# Backend Dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY backend/go.mod backend/go.sum ./
RUN go mod download

COPY backend/ .
RUN go build -o idrac-monitor main.go config.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/idrac-monitor .

EXPOSE 8080

CMD ["./idrac-monitor"]