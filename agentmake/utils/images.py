import os, base64, requests
from PIL import Image

# image

def encode_image(image_path, size_limit_in_MB=None):
    image_file_size = os.path.getsize(image_path) / (1024 * 1024)
    if size_limit_in_MB is not None and image_file_size > size_limit_in_MB:
        return None
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    ext = os.path.splitext(os.path.basename(image_path))[1][1:]
    return f"data:image/{ext};base64,{base64_image}"

def is_valid_image_url(url): 
    try: 
        response = requests.head(url, timeout=30)
        content_type = response.headers['content-type'] 
        if 'image' in content_type: 
            return True 
        else: 
            return False 
    except requests.exceptions.RequestException: 
        return False

def is_valid_image_file(file_path):
    try:
        # Open the image file
        with Image.open(file_path) as img:
            # Check if the file format is supported by PIL
            img.verify()
            return True
    except (IOError, SyntaxError) as e:
        # The file path is not a valid image file path
        return False