# UFC Downloader

This project is a personal tool for downloading UFC content.

## Setup

1. **Install Poetry**:

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. **Install Dependencies**:

    ```sh
    poetry install
    ```

## Usage

1. **Update the Index**:

    ```sh
    poetry run ufc_downloader index-events
    ```

2. **Import Downloads**:

    ```sh
    poetry run ufc_downloader import-downloads
    ```
