import os, os.path

import Image as PILImage

from datetime import datetime

from paths import *

from node import File, local_to_relative

class Image(File):
    """
    object to hold Image specific meta data for an image locally available

    and rendering thumbnails
    """
    def __init__(self, path):
        File.__init__(self, path)
        self.thumb_dir_name = "sized"
        parent_dir_path = os.path.dirname(self.path)
        self.thumb_dir_path = os.path.join(parent_dir_path, self.thumb_dir_name)
        
        self.sizes = { 'tiny':'_t', 'small':'_s', 'medium':'_m', 'large':'_l' }

        parts = self.name.split('.')
        self.last_four = parts[-2][-4:]

    def size_name(self, size):
        """
        take a size and create the corresponding thumbnail filename
        """
        parts = self.name.split('.')
        new_name = '.'.join(parts[:-1]) + self.sizes[size] + '.' + parts[-1]
        return new_name                  
        
    def size_path(self, size):
        """
        take a size and create the corresponding thumbnail (local) path 
        """
        thumb_path = os.path.join(self.thumb_dir_path, size, self.size_name(size))
        return thumb_path

    def size_path_relative(self, size):
        """
        some overlap here with relative_path,
        but it isn't working for thumbnails anyway
        """            
        if size == 'full':
            return os.path.join(relative_prefix, local_to_relative(self.path))
        else:
            return os.path.join(relative_prefix, os.path.dirname(local_to_relative(self.path)), self.thumb_dir_name, size, self.size_name(size))
        

    def get_size(self, size):
        """
        tiny, small, medium, large
        """
        thumb_path = self.size_path(size)
        if not os.path.isfile(thumb_path):
            self.make_thumbs()
        return self.size_path_relative(size)

    def move(self, rel_destination):
        """
        this utilizes the os.rename function
        but should also move thumbnails
        """
        destination = os.path.join(local_path, rel_destination)
        #new_dir = os.path.join(image_dir, data)
        (new_dir, new_name) = os.path.split(destination)

        #could also use os.renames()   note plural
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)
        os.rename(self.path, destination)

        #move thumbnails
        new_image = Image(destination)
        #self.make_thumb_dirs(os.path.join(new_dir, self.thumb_dir_name))
        new_image.make_thumb_dirs()

        for k in self.sizes.keys():
            os.rename(self.size_path(k), new_image.size_path(k))
            
    def make_thumb_dirs(self, base=None):
        """
        if they don't already exist, create them
        """
        if not base:
            base = self.thumb_dir_path
        if not os.path.isdir(base):
            os.mkdir(base)
            
        #make separate directories for each thumbnail size
        for k in self.sizes.keys():
            size_path = os.path.join(base, k)
            if not os.path.isdir(size_path):
                os.mkdir(size_path)

    def _square_image(self, small):
        if small.size[0] != small.size[1]:
            #lets make it a square:
            if small.size[0] > small.size[1]:
                bigger = small.size[0]
                smaller= small.size[1]
                diff = bigger - smaller
                first = diff/2
                last = bigger - (diff - first)
                box = (first, 0, last, smaller)
            else:
                bigger = small.size[1]
                smaller= small.size[0]
                diff = bigger - smaller
                first = diff/2
                last = bigger - (diff - first)
                box = (0, first, smaller, last)
            region = small.crop(box)
            small = region.copy()
        return small
        
    def make_thumbs(self):
        """
        regenerate all thumbnails from original
        """
        if config.has_key('thumb.l'):
            l = int(config['thumb.l'])
            m = int(config['thumb.m'])
            s = int(config['thumb.s'])
            t = int(config['thumb.t'])
            u = int(config['thumb.u'])
        else:
            l = 800
            m = 200
            s = 150
            t = 100
            u = 25
            

        name = self.name

        
        self.make_thumb_dirs()
        
        #remove exisiting thumbs before regen?
        #or does save overwrite anyway?
        #for s in self.sizes.keys():
        #    if os.path.isdir(self.size_path(s)):
        #        os.remove(self.size_path(s))

        try:
            image = PILImage.open(self.path)
            image.thumbnail((l,l), PILImage.ANTIALIAS)

            medium = image.copy()
            medium = self._square_image(medium)
            medium.thumbnail((m,m), PILImage.ANTIALIAS)
            small = medium.copy()
            small.thumbnail((s,s), PILImage.ANTIALIAS)


            tiny = small.copy()
            tiny.thumbnail((t, t), PILImage.ANTIALIAS)

            image.save(self.size_path('large'), "JPEG")
            medium.save(self.size_path('medium'), "JPEG")
            small.save(self.size_path('small'), "JPEG")
            tiny.save(self.size_path('tiny'), "JPEG")
        except:
            print "error generating thumbs for: %s" % self.name
            pass

    def rotate_pil(self, degrees=90):
        """
        rotate image by number of degrees (clockwise!!)

        use Python Image Library

        PIL is very LOSSY!!

        will also lose original EXIF data

        (but it does work if you don't have access to jhead/jpegtran)
        """
        #standard PIL goes counter-clockwise
        #should adjust here
        degrees = 360 - float(degrees)
        image = PILImage.open(self.path)
        im2 = image.rotate(float(degrees))
        im2.save(self.path, "JPEG")
        self.make_thumbs()
        self.reset_stats()
        
    def rotate(self, degrees=90):
        """
        rotate image by number of degrees (clockwise!!)

        need to reset file timestamp to be original
        especially if not keeping track of that elsewhere

        see also Directory.auto_rotate_images()

        but if you need to tune individually, better to call jpegtrans here

        jhead -cmd "jpegtran -progressive -rotate 90 &i > &o" IMG_4965.JPG
        """
        os.system("jhead -cmd \"jpegtran -progressive -rotate %s &i > &o\" %s" % (degrees, self.path))
        self.make_thumbs()
        self.reset_stats()

