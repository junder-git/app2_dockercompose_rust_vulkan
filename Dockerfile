# Stage 1: Build dependencies
FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04 AS builder

WORKDIR /app

# Install system dependencies (this layer will be cached if nothing changes here)
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

# First step: build dependencies
# Copy only Cargo.toml and Cargo.lock for dependency caching
COPY ./Cargo.toml ./Cargo.toml

# Create a dummy file with a main function to allow compilation to succeed
RUN mkdir -p src && echo 'fn main() { println!("Hello, world!"); }' > src/main.rs

# Build the dependencies (this step will be cached if nothing changes in Cargo.toml and Cargo.lock)
RUN cargo build --release
RUN rm -Rf src

# Second step: build local crate(s)
COPY src src

# Rebuild only if source files change
RUN cargo build --release

# Stage 2: Runtime stage
FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu24.04

WORKDIR /app

# Copy only the built binary from the builder stage
COPY --from=builder /app/target/release/jproj_vulkan ./

ENTRYPOINT ["./jproj_vulkan"]