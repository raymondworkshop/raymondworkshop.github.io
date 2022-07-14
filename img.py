from PIL import Image

img = Image.open("~/assets/img/_09.jpg")
img.show()
print(img.size)

resized_img = img.resize((500, round(img.size[1]*0.5)))
resized_img.show()

resized_img.save("~/assets/img/09.jpg")