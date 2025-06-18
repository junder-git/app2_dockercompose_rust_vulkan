# Stage 1: Build stage
FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04 AS builder

WORKDIR /app

# Install dependencies (this layer will be cached if nothing changes here)
RUN apt-get update && \
    apt-get install -y git libfontconfig1-dev pkg-config cmake curl build-essential software-properties-common lsb-release bash && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Cargo bin to PATH
ENV PATH="/root/.cargo/bin:${PATH}"
ENV PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig/

# Set Rust version (this layer will be cached if the command doesn't change)
RUN /bin/bash -c "source $HOME/.cargo/env && \
    rustup default stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*"

# Copy only the Cargo.toml file for dependency caching
COPY ./Cargo.toml ./
# Copy the rest of the application code, only when necessary
COPY ./src ./src
COPY ./shaders ./shaders

# Ensure there's a Cargo.lock or generate one (this step will be cached)
RUN cargo update --aggressive

# Build the final binary for running (this step will only re-run if source files change)
RUN cargo build --release

# Stage 2: Runtime stage
FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04

WORKDIR /app

# Copy only the built binary from the builder stage
COPY --from=builder /app/target/release/shader_reloader ./

ENTRYPOINT ["./shader_reloader"]