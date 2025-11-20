from .celery_app import celery_app

app = celery_app

if __name__ == "__main__":
    app.worker_main()
    