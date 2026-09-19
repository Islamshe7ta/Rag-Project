from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "File validated successfully"
    FILE_VALIDATION_FAILED = "File validation failed"
    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    FILE_SUCCESSFULLY_UPLOADED = "File successfully uploaded"
    FILE_UPLOAD_FAILED = "File upload failed"
    FILE_PROCESSING_FAILED = "File processing failed"
    FILE_PROCESSING_SUCCESS = "File processing successful"
    


