import base64
import uuid
import oss2
import os

myAccessKeyId = 'LTAI4GK13jH25e6fTAudS4Hj'
myAccessKeySecret = 'cbxYaYCx9icIo23AUSayeNBrV72uFg'
EndPoint = 'oss-cn-qingdao.aliyuncs.com'
myBucketName = 'sunlingfeng'
myBucketUrl = 'http://sunlingfeng.0431zy.com/'


def upload(filename: object, cloud_name: object) -> object:
    auth = oss2.Auth(myAccessKeyId, myAccessKeySecret)
    bucket = oss2.Bucket(auth, EndPoint, myBucketName)
    with open(oss2.to_unicode(filename), 'rb') as f:
        bucket.put_object(cloud_name, f)
    meta = bucket.get_object_meta(cloud_name)
    print(meta)
    if meta:
        return myBucketUrl + cloud_name
    else:
        return ''


def uploadBase64(base64STR):
    imgData = base64.b64decode(str(base64STR))
    filename = str(uuid.uuid4()) + '.jpg'
    file = open(filename, 'wb')
    file.write(imgData)
    file.close()
    fileUrl = upload(filename, filename)
    os.remove(filename)
    return fileUrl
