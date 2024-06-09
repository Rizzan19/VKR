
def product_image_upload(instance, filename):
    filename = '.'.join([instance.slug, filename.split('.')[-1]])
    return f"products/{instance.slug}/{filename}"
