# Serverless AWS S3 File Sync
Simple code to Sync AWS S3 files from source bucket to destination bucket.

## Installation
npm install -g serverless

Fill the config.dev.yml
```
SOURCE_BUCKET: ''
SOURCE_FOLDER: ''
DESTINATION_BUCKET: ''
DESTINATION_FOLDER: ''
CREATE_EMPTY_FILES: 'true'
IMAGE_VIDEO_EXTENSIONS: 'jpg, jpeg, gif, png, svg, mp4'
```

## Deploy
```
serverless deploy --aws-profile profile --stage stage --region region
```

## How it works

#### For uploaded objects:

You can upload a file to the source bucket (e.g. using the AWS S3 console).
The serverless have created an event in S3 bucket to trigger the lambda.
The lambda copy the file inside the destination bucket (or folder).

  - If uploaded object is an image or video we copy the file.
  - If uploaded object is a file:
  
    - If the CREATE_EMPTY_FILES env params is false the file is copied as is.
    - If the CREATE_EMPTY_FILES env params is true the file is created but empty. 
        
        **Note**: We keep the file characteristics but the file content is empty. It works only for some 
        text extensions. The goal is that the file must be keep the characteristics (type, metadata, ...)
        
#### For deleted objects:     
The file is removed in the destination bucket (or folder)    
 

**NOTE:**
The deployment will create two lambda function. 

    - The current python code.
    - Backs-up the Custom S3 Resource which is used to support existing S3 buckets.
    https://www.serverless.com/framework/docs/providers/aws/events/s3/
 

