from PIL import Image

img = Image.open('/Users/zhaowenlong/workspace/myblog/docs/img/_09.jpg')
img.show()
print(img.size)

resized_img = img.resize((500, round(img.size[1]*0.5)))
resized_img.show()

resized_img.save('/Users/zhaowenlong/workspace/myblog/docs/img/09.jpg')