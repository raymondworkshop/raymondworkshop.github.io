from PIL import Image

img = Image.open('/Users/zhaowenlong/workspace/myblog/docs/img/02.jpg')
img.show()

resized_img = img.resize((round(img.size[0]*0.5), round(img.size[1]*0.5)))
resized_img.show()

resized_img.save('/Users/zhaowenlong/workspace/myblog/docs/img/_02.jpg')