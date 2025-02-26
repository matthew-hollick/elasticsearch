#!/bin/bash
set -e

# Install Vulcanizer from GitHub
echo "Installing Vulcanizer..."

PROJECT_ROOT="$(git rev-parse --show-toplevel)/aggregate-thresholds"
mkdir -p "${PROJECT_ROOT}/bin"

# Function to build and install vulcanizer
build_vulcanizer() {
    local install_dir
    local temp_dir
    install_dir="$1"
    temp_dir=$(mktemp -d)

    pushd "${temp_dir}"

    # Clone the repository
    git clone https://github.com/github/vulcanizer.git
    cd vulcanizer

    # Build the binary with local GOBIN
    echo "Building Vulcanizer..."
    local GOBIN="${install_dir}"
    echo "Setting GOBIN to ${GOBIN}"
    ./script/build

    popd
    rm -rf "${temp_dir}"

    echo "Vulcanizer has been installed to ${install_dir}/vulcanizer"
}

# Call the function to build vulcanizer
build_vulcanizer "${PROJECT_ROOT}/bin"
