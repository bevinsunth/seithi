FROM alpine:latest

WORKDIR /app

# Copy the cross-compiled binary
COPY seithi-backend-x86 .

# Expose port
EXPOSE 8080

# Run the binary
CMD ["./seithi-backend-x86"]
