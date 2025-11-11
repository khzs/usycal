import os

def get_secret_url():
    secret_url = os.environ.get("SECRET_URL")

    if not secret_url and os.path.exists("secret_url.txt"):
        with open("secret_url.txt", "r", encoding="utf-8") as f:
            secret_url = f.read().strip()

    if not secret_url:
        raise RuntimeError(
            "Secret URL not found. Set SECRET_URL env variable or create secret_url.txt."
        )

    return secret_url

def main():
    url = get_secret_url()
    print("Loaded secret URL (not printing for security).")


if __name__ == "__main__":
    main()
