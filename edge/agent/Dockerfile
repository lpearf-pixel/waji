FROM rust:1.88-bookworm AS builder
WORKDIR /build
COPY Cargo.toml Cargo.lock* ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --home-dir /var/lib/waji waji
COPY --from=builder /build/target/release/waji-edge-agent /usr/local/bin/waji-edge-agent
USER waji
WORKDIR /var/lib/waji
ENTRYPOINT ["/usr/local/bin/waji-edge-agent"]
CMD ["--config", "/etc/waji/edge.toml"]
