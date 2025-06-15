FROM nvidia/cuda:11.2.0-base-ubuntu20.04
WORKDIR /app

# Install Rust and Cargo
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

# Copy Cargo.toml first to leverage Docker cache when dependencies don't change
COPY ./Cargo.toml ./
RUN cargo build --release

# Copy the rest of the application
COPY ./src ./src
COPY ./shaders ./shaders

# Build the final binary for running
RUN cargo build --release

ENTRYPOINT ["./target/release/shader_reloader"]