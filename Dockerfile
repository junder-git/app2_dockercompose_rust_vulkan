# Stage 1: Build stage
FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04 AS builder

WORKDIR /app

# Install Rust and Cargo (this layer will be cached if nothing changes here)
RUN apt-get update && \
    apt-get install -y pkg-config cmake curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

ENV PATH="/root/.cargo/bin:${PATH}"

# Copy only the Cargo.toml file for dependency caching
COPY ./Cargo.toml ./

# Create an empty Cargo.lock if it doesn't exist yet (this helps with initial builds)
RUN if [ ! -f Cargo.lock ]; then echo "Generating initial Cargo.lock..."; cargo update --aggressive; fi

# Copy the Cargo.lock file (if present) and build dependencies
COPY ./Cargo.lock ./
RUN cargo build --release

# Copy the rest of the application code, only when necessary
COPY ./src ./src
COPY ./shaders ./shaders

# Build the final binary for running (this step will only re-run if source files change)
RUN cargo build --release

# Stage 2: Runtime stage
FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04

WORKDIR /app

# Copy only the built binary from the builder stage
COPY --from=builder /app/target/release/shader_reloader ./

ENTRYPOINT ["./shader_reloader"]