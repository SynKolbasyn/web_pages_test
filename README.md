# A test task for Web pages

This is a repository of a test assignment for Web pages


## Prerequests

The only thing you will need to run is [Docker](https://www.docker.com/).

Optionally, you can use [curl](https://curl.se/) or [Postman](https://www.postman.com/) for testing.


## Deploy guide

1. Configure project

    Rename the settings file and specify the configuration in it (you can leave it by default).

    ```bash
    cp template.env .env
    ```

2. Launch

    Using the following command, you will run the project with the configuration specified in the `.env` file

    Optionally, you can specify the `-d` flag to keep the terminal active.

    ```bash
    docker compose up --build <-d>
    ```

## API

The service supports the following operations:

- `GET` `/help/`
- `POST` `/user/create/`
- `GET` `/user/get/{user_id}/`
- `PUT` `/user/update/{user_id}/`
- `DELETE` `/user/delete/{user_id}/`
- `POST` `/post/create/`
- `GET` `/post/get/{post_id}/`
- `PUT` `/post/update/{post_id}/`
- `DELETE` `/post/delete/{post_id}/`

etc (you can view them in the file `main.py`).

Each request must be authorized using HTTP basic auth. Operations with users are available only to admins.
