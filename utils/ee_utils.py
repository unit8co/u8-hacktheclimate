import ee


def get_image_collection(source, field, from_date, to_date):
    collection = ee.ImageCollection(source)
    image = collection.select(field)

    return image.filterDate(from_date, to_date)


def get_region_image(image, longitude, latitude, point_buffer=1e10):
    point = ee.Geometry.Point(longitude, latitude)
    buffer_square = point.buffer(ee.Number(point_buffer).sqrt().divide(2), 1).bounds()
    return image.getRegion(buffer_square, point_buffer)
