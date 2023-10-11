# gemma-middle-server

# gemma-middle-server

## Installation

To run the application, you will need to install the following requirements:

- Python 3
- pip3
- boto3
- Flask

You can install Python 3 and pip3 using your operating system's package manager. For example, on Ubuntu, you can run the following command:
  
  ```bash
  sudo apt install python3 python3-pip
  ```

Once you have installed Python 3 and pip3, you can use pip3 to install the required Python packages:


This will install the boto3 and Flask packages, which are required by the application:
  
  ```bash
  pip3 install boto3 Flask gunicorn
  ```

Note that you may need to use `sudo` or run the commands as an administrator depending on your operating system and user permissions.


## Configuration

Before running the application on your local machine, make sure to configure the following environment variables:

- `ACCESS_KEY_ID`: The access key ID for your AWS account.
- `ACCESS_SECRET_KEY`: The secret access key for your AWS account.
- `BUCKET_NAME`: The name of the S3 bucket where your files are stored.

You can set these environment variables in your shell or in a configuration file. Refer to the documentation for your operating system for more information on how to set environment variables.