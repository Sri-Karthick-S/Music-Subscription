# Music Subscription Service

This repository contains the implementation of a **Music Subscription Service**. The project is designed to provide users with a seamless experience for subscribing to and accessing music content. It leverages AWS services to ensure scalability, reliability, and performance.

## Project Flow

1. **User Registration and Authentication**:
    - Users can register and log in to the service, detials are stored in **DynamoDB login table**.
    - Authentication is managed using secure tokens.

2. **Music Library Management**:
    - Music files are uploaded and stored in an **S3 Bucket**.
    - Metadata about the music (e.g., title, artist, genre) is stored in **DynamoDB music table**.

3. **Subscription Management**:
    - Users can subscribe to different songs, also the user can modify the song subscription anytime
    - Subscription details are stored and managed using **DynamoDB subscription table**.

4. **Music Streaming**:
    - Users can stream music directly from the **S3 Bucket**.
    - Access to music is controlled based on the user's subscription plan.

5. **API Integration**:
    - All backend operations are exposed via **API Gateway**.
    - APIs are secured and optimized for performance.

6. **Serverless Backend**:
    - Business logic is implemented using **AWS Lambda** functions.
    - These functions handle user requests, interact with DynamoDB, and manage S3 operations.

## AWS Services Used

- **Amazon S3**: For storing music files securely and efficiently.
- **Amazon DynamoDB**: For managing user data, subscription details, and music metadata.
- **AWS Lambda**: For implementing serverless business logic.
- **Amazon API Gateway**: For exposing RESTful APIs to the frontend.
- **AWS EC2**: for hosting the applicattion

## How to Run the Project

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/Music-Subscription.git
    cd Music-Subscription
    ```

2. Deploy the backend services using AWS:
    - Set up S3 buckets for music storage.
    - Create DynamoDB tables for user and music data.
    - Deploy Lambda functions and configure API Gateway.

3. Start the frontend (if applicable) and test the APIs.

4. Enjoy the Music Subscription Service!

