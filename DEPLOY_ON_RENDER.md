# Deploying Podcastr on Render

This guide outlines the steps to deploy your **Podcastr** application to [Render](https://render.com/).

## 1. Prerequisites

- A **GitHub** account.
- A **Render** account.
- Your code must be pushed to a GitHub repository.

## 2. Configuration Check

Your project is already configured for Render with the following files:
- **`render.yaml`**: Defines the service, build commands, and persistent disk.
- **`Dockerfile`**: Defines the environment and dependencies.
- **`requirements.txt`**: Lists Python libraries.

> [!NOTE]
> The setup uses **SQLite** with a **persistent disk** (`/app/data`) to store the database and uploads. This requires a paid "Starter" plan or higher on Render to attach the disk, or you might hit limits/costs. If you want a completely free tier, you cannot use the persistent disk (meaning data is lost on restart) or you must switch to Render's Managed PostgreSQL (Free Tier available for 90 days).

## 3. Deployment Steps

1.  **Log in to Render**.
2.  Click the **"New +"** button in the top right and select **"Blueprint"**.
3.  Connect your **GitHub repository**.
4.  Render will detect the `render.yaml` file.
5.  **Service Name**: You can keep `podcastr-ai` or change it.
6.  **Environment Variables**: You will be prompted to enter the values for:
    - `GOOGLE_API_KEY`: Your Gemini/Google AI key.
    - `RAZORPAY_KEY_ID`: Your Razorpay Key ID.
    - `RAZORPAY_KEY_SECRET`: Your Razorpay Key Secret.
    - `RAZORPAY_WEBHOOK_SECRET`: Your Razorpay Webhook Secret.
    - `SECRET_KEY`: (Render might generate this, or you can provide a random string).
7.  **Apply/Create**: Click **Apply** or **Create Service**.

## 4. Post-Deployment

- **Database**: The app attempts to create tables automatically (via `app/main.py`).
- **Uploads**: The `render.yaml` ensures uploaded files are stored on the persistent disk at `/app/data/uploads`, which is symlinked to `static/uploads`.

## 5. Troubleshooting common issues

- **Disk Mounting**: If the deployment fails due to disk issues, ensure you have a payment method added to Render (even for free trials sometimes) or remove the `disk` section from `render.yaml` if you want to test without persistence (NOT recommended for production).
- **Build Failures**: Check the "Logs" tab in Render for Python errors.
