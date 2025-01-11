#!flask/bin/python
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'utils')))
from env import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, PHOTOGALLERY_S3_BUCKET_NAME, DYNAMODB_TABLE, DYNAMODB_TABLE_USER, HASH_SERIALIZER, CURRENT_URL, SES_EMAIL_SOURCE
from flask import Flask, jsonify, abort, request, make_response, url_for, session
from flask import render_template, redirect
import time
import exifread
import json
import uuid
import boto3  
from boto3.dynamodb.conditions import Key, Attr
import pymysql.cursors
from datetime import datetime
import pytz
import bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import timedelta
"""
    INSERT NEW LIBRARIES HERE (IF NEEDED)
"""





"""
"""

app = Flask(__name__, static_url_path="")
app.secret_key = "dddd"

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name=AWS_REGION)

table = dynamodb.Table(DYNAMODB_TABLE)
photogallery_user_table = dynamodb.Table(DYNAMODB_TABLE_USER)

UPLOAD_FOLDER = os.path.join(app.root_path,'static','media')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getExifData(path_name):
    f = open(path_name, 'rb')
    tags = exifread.process_file(f)
    ExifData={}
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            key="%s"%(tag)
            val="%s"%(tags[tag])
            ExifData[key]=val
    return ExifData

def s3uploading(filename, filenameWithPath, uploadType="photos"):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                       
    bucket = PHOTOGALLERY_S3_BUCKET_NAME
    path_filename = uploadType + "/" + filename

    s3.upload_file(filenameWithPath, bucket, path_filename)  
    s3.put_object_acl(ACL='public-read', Bucket=bucket, Key=path_filename)
    return f'''http://{PHOTOGALLERY_S3_BUCKET_NAME}.s3.amazonaws.com/{path_filename}'''


"""
    INSERT YOUR NEW FUNCTION HERE (IF NEEDED)
"""
def send_email(email, body):
    try:
        ses = boto3.client('ses', aws_access_key_id=AWS_ACCESS_KEY,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                           region_name=AWS_REGION)
        ses.send_email(
            Source = SES_EMAIL_SOURCE,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Photo Gallery: Confirm Account'},
                'Body': {
                    'Text': {'Data': body}
                }
            }
        )
    except Exception as e:
        print(e)
        return False
    else:
        return True


"""
"""

"""
    INSERT YOUR NEW ROUTE HERE (IF NEEDED)
"""

"""
"""

@app.errorhandler(400)
def bad_request(error):
    """ 400 page route.

    get:
        description: Endpoint to return a bad request 400 page.
        responses: Returns 400 object.
    """
    return make_response(jsonify({'error': 'Bad request'}), 400)



@app.errorhandler(404)
def not_found(error):
    """ 404 page route.

    get:
        description: Endpoint to return a not found 404 page.
        responses: Returns 404 object.
    """
    return make_response(jsonify({'error': 'Not found'}), 404)



@app.route('/', methods=['GET'])
def home_page():
    """ Home page route.

    get:
        description: Endpoint to return home page.
        responses: Returns all the albums.
    """
    if 'user' in session:
        response = table.scan(FilterExpression=Attr('photoID').eq("thumbnail"))
        results = response['Items']

        if len(results) > 0:
            for index, value in enumerate(results):
                createdAt = datetime.strptime(str(results[index]['createdAt']), "%Y-%m-%d %H:%M:%S")
                createdAt_UTC = pytz.timezone("UTC").localize(createdAt)
                results[index]['createdAt'] = createdAt_UTC.astimezone(pytz.timezone("US/Eastern")).strftime("%B %d, %Y")

        return render_template('index.html', albums=results)
    else:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup_page():
    if request.method == 'POST':
        userID = uuid.uuid4()
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        password = password.encode('utf-8') 
        hashedPass = bcrypt.hashpw(password, bcrypt.gensalt())
        userResponse = photogallery_user_table.scan(
            FilterExpression=Attr('email').eq(email))
        results = userResponse['Items']
        if len(results) > 0:
            return redirect('/signup')
        else:
            serializer = URLSafeTimedSerializer(HASH_SERIALIZER)
            token = serializer.dumps(email, salt='activation')
            verifyEmail = "Please Click the link below to verify your acount \n" + CURRENT_URL+"/confirm/" + token
            send_email(email, verifyEmail)
            createdAtlocalTime = datetime.now().astimezone()
            createdAtUTCTime = createdAtlocalTime.astimezone(pytz.utc)
            photogallery_user_table.put_item(
                Item={
                    "userID":str(userID),
                    "email": email,
                    "firstName": firstName,
                    "lastName": lastName,
                    "password": hashedPass.decode('utf-8'),
                    "validated": 0,
                    "createdAt": createdAtUTCTime.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            return redirect('/login')
    else:
        return render_template('signup.html')
    
@app.route('/confirm/<string:ID>', methods=['GET'])
def confirm_user(ID):
    try:
        serializer = URLSafeTimedSerializer(HASH_SERIALIZER)
        email = serializer.loads(ID, salt='activation', max_age=600)
        userResponse = photogallery_user_table.scan(
            FilterExpression=Attr('email').eq(email))
        results = userResponse['Items']
        if results:
            user = results[0]
            userID = user['userID']
            photogallery_user_table.update_item(
                Key={
                    'userID': userID,
                    'email': email
                },
                UpdateExpression="set validated = :validated",
                ExpressionAttributeValues={
                    ':validated': 1
                }
            )
            return redirect('/login')
        else:
            return redirect('/signup')
    except (BadSignature, SignatureExpired):
        return redirect('/signup')
    except Exception as e:
        return redirect('/signup')
    
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password = password.encode('utf-8')
        userResponse = photogallery_user_table.scan(
            FilterExpression=Attr('email').eq(email))
        results = userResponse['Items']
        if len(results) > 0:
            passCheck = results[0]['password']
            validated = results[0]['validated']
            userID = results[0]['userID']
            if validated == 1 and bcrypt.checkpw(password, passCheck.encode('utf-8')):
                session['user'] = results[0]['userID']
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
                return redirect('/')
            else:
                return redirect('/login')
        else:
            return redirect('/login')
    else:
        return render_template('login.html')

@app.route('/createAlbum', methods=['GET', 'POST'])
def add_album():
    """ Create new album route.

    get:
        description: Endpoint to return form to create a new album.
        responses: Returns all the fields needed to store new album.

    post:
        description: Endpoint to send new album.
        responses: Returns user to home page.
    """
    if 'user' not in session:
        return redirect ('/login')
    
    if request.method == 'POST':
        uploadedFileURL=''
        file = request.files['imagefile']
        name = request.form['name']
        description = request.form['description']

        if file and allowed_file(file.filename):
            albumID = uuid.uuid4()
            
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filenameWithPath)
            
            uploadedFileURL = s3uploading(str(albumID), filenameWithPath, "thumbnails");

            createdAtlocalTime = datetime.now().astimezone()
            createdAtUTCTime = createdAtlocalTime.astimezone(pytz.utc)

            table.put_item(
                Item={
                    "albumID": str(albumID),
                    "photoID": "thumbnail",
                    "name": name,
                    "description": description,
                    "thumbnailURL": uploadedFileURL,
                    "createdAt": createdAtUTCTime.strftime("%Y-%m-%d %H:%M:%S"),
                    "userID": session['user']
                }
            )

        return redirect('/')
    else:
        return render_template('albumForm.html')

@app.route('/cancelUser', methods=['GET'])
def cancel_user():
    if 'user' not in session:
        return redirect('/login')

    user_id = session['user']

    albums_response = table.scan(
        FilterExpression=Attr('userID').eq(user_id))
    albums = albums_response.get('Items', [])

    for album in albums:
        table.delete_item(
            Key={
                'albumID': album['albumID'],
                'photoID': 'thumbnail'
            }
        )
    session.pop('user', None)
    return redirect('/')

@app.route('/album/<string:albumID>', methods=['GET'])
def view_photos(albumID):
    """ Album page route.

    get:
        description: Endpoint to return an album.
        responses: Returns all the photos of a particular album.
    """
    albumResponse = table.query(KeyConditionExpression=Key('albumID').eq(albumID) & Key('photoID').eq('thumbnail'))
    albumMeta = albumResponse['Items']

    response = table.scan(FilterExpression=Attr('albumID').eq(albumID) & Attr('photoID').ne('thumbnail'))
    items = response['Items']

    return render_template('viewphotos.html', photos=items, albumID=albumID, albumName=albumMeta[0]['name'])



@app.route('/album/<string:albumID>/addPhoto', methods=['GET', 'POST'])
def add_photo(albumID):
    """ Create new photo under album route.

    get:
        description: Endpoint to return form to create a new photo.
        responses: Returns all the fields needed to store a new photo.

    post:
        description: Endpoint to send new photo.
        responses: Returns user to album page.
    """
    if request.method == 'POST':    
        uploadedFileURL=''
        file = request.files['imagefile']
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        if file and allowed_file(file.filename):
            photoID = uuid.uuid4()
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filenameWithPath)            
            
            uploadedFileURL = s3uploading(filename, filenameWithPath);
            
            ExifData=getExifData(filenameWithPath)
            ExifDataStr = json.dumps(ExifData)

            createdAtlocalTime = datetime.now().astimezone()
            updatedAtlocalTime = datetime.now().astimezone()

            createdAtUTCTime = createdAtlocalTime.astimezone(pytz.utc)
            updatedAtUTCTime = updatedAtlocalTime.astimezone(pytz.utc)

            table.put_item(
                Item={
                    "albumID": str(albumID),
                    "photoID": str(photoID),
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "photoURL": uploadedFileURL,
                    "EXIF": ExifDataStr,
                    "createdAt": createdAtUTCTime.strftime("%Y-%m-%d %H:%M:%S"),
                    "updatedAt": updatedAtUTCTime.strftime("%Y-%m-%d %H:%M:%S")
                }
            )

        return redirect(f'''/album/{albumID}''')

    else:

        albumResponse = table.query(KeyConditionExpression=Key('albumID').eq(albumID) & Key('photoID').eq('thumbnail'))
        albumMeta = albumResponse['Items']

        return render_template('photoForm.html', albumID=albumID, albumName=albumMeta[0]['name'])

@app.route('/album/<string:albumID>/delete', methods=['GET'])
def delete_photos(albumID):
    response = table.scan(FilterExpression=Attr('albumID').eq(albumID) & Attr('photoID').ne('thumbnail'))
    items = response['Items']
    for item in items:
        table.delete_item(
        Key={
        'albumID': item['albumID'],
        'photoID': item['photoID']
        }
        )
    return redirect('/album/'+albumID)

@app.route('/album/<string:albumID>/<string:photoID>/delete', methods=['GET'])
def delete_photo(albumID, photoID):
    table.delete_item(
    Key={
        'albumID': albumID,
        'photoID': photoID
    }
        )
    return redirect('/album/'+albumID)

@app.route('/album/<string:albumID>/photo/<string:photoID>', methods=['GET'])
def view_photo(albumID, photoID):
    """ photo page route.

    get:
        description: Endpoint to return a photo.
        responses: Returns a photo from a particular album.
    """ 
    albumResponse = table.query(KeyConditionExpression=Key('albumID').eq(albumID) & Key('photoID').eq('thumbnail'))
    albumMeta = albumResponse['Items']

    response = table.query( KeyConditionExpression=Key('albumID').eq(albumID) & Key('photoID').eq(photoID))
    results = response['Items']

    if len(results) > 0:
        photo={}
        photo['photoID'] = results[0]['photoID']
        photo['title'] = results[0]['title']
        photo['description'] = results[0]['description']
        photo['tags'] = results[0]['tags']
        photo['photoURL'] = results[0]['photoURL']
        photo['EXIF']=json.loads(results[0]['EXIF'])

        createdAt = datetime.strptime(str(results[0]['createdAt']), "%Y-%m-%d %H:%M:%S")
        updatedAt = datetime.strptime(str(results[0]['updatedAt']), "%Y-%m-%d %H:%M:%S")

        createdAt_UTC = pytz.timezone("UTC").localize(createdAt)
        updatedAt_UTC = pytz.timezone("UTC").localize(updatedAt)

        photo['createdAt']=createdAt_UTC.astimezone(pytz.timezone("US/Eastern")).strftime("%B %d, %Y")
        photo['updatedAt']=updatedAt_UTC.astimezone(pytz.timezone("US/Eastern")).strftime("%B %d, %Y")
        
        tags=photo['tags'].split(',')
        exifdata=photo['EXIF']
        
        return render_template('photodetail.html', photo=photo, tags=tags, exifdata=exifdata, albumID=albumID, albumName=albumMeta[0]['name'])
    else:
        return render_template('photodetail.html', photo={}, tags=[], exifdata={}, albumID=albumID, albumName="")



@app.route('/album/search', methods=['GET'])
def search_album_page():
    """ search album page route.

    get:
        description: Endpoint to return all the matching albums.
        responses: Returns all the albums based on a particular query.
    """ 
    query = request.args.get('query', None)    

    response = table.scan(FilterExpression=Attr('name').contains(query) | Attr('description').contains(query))
    results = response['Items']

    items=[]
    for item in results:
        if item['photoID'] == 'thumbnail':
            album={}
            album['albumID'] = item['albumID']
            album['name'] = item['name']
            album['description'] = item['description']
            album['thumbnailURL'] = item['thumbnailURL']
            items.append(album)

    return render_template('searchAlbum.html', albums=items, searchquery=query)

@app.route('/album/<string:albumID>/<string:photoID>/update', methods=['GET', 'POST'])
def update_photo(albumID, photoID):
    if request.method == 'POST': 
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        updatedAtlocalTime = datetime.now().astimezone()
        updatedAtUTCTime = updatedAtlocalTime.astimezone(pytz.utc)
        table.update_item(
        Key={
            'albumID': albumID,
            'photoID': photoID
        },
        UpdateExpression="set title=:title, description=:description, tags=:tags, updatedAt=:updatedAt",
        ExpressionAttributeValues={
            ':title': title,
            ':description': description,
            ':tags': tags,
            ':updatedAt': updatedAtUTCTime.strftime("%Y-%m-%d %H:%M:%S")
        },
        ReturnValues="UPDATED_NEW"
        )
        return redirect('/album/'+albumID +'/photo/'+photoID)
    else:
        return render_template('updatephoto.html', photoID=photoID, albumID=albumID)


@app.route('/album/<string:albumID>/search', methods=['GET'])
def search_photo_page(albumID):
    """ search photo page route.

    get:
        description: Endpoint to return all the matching photos.
        responses: Returns all the photos from an album based on a particular query.
    """ 
    query = request.args.get('query', None)    

    response = table.scan(FilterExpression=Attr('title').contains(query) | Attr('description').contains(query) | Attr('tags').contains(query) | Attr('EXIF').contains(query))
    results = response['Items']

    items=[]
    for item in results:
        if item['photoID'] != 'thumbnail' and item['albumID'] == albumID:
            photo={}
            photo['photoID'] = item['photoID']
            photo['albumID'] = item['albumID']
            photo['title'] = item['title']
            photo['description'] = item['description']
            photo['photoURL'] = item['photoURL']
            items.append(photo)

    return render_template('searchPhoto.html', photos=items, searchquery=query, albumID=albumID)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
