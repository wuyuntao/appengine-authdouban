# -*- coding: UTF-8 -*-

def parse_urls(people_entry):
    url = None
    image_url = None
    blog_url = None

    for link in people_entry.link:
        if link.rel == 'alternate':
            url = force_unicode(link.href)
        elif link.rel == 'icon':
            image_url = force_unicode(link.href)
        elif link.rel == 'homepage':
            blog_url = force_unicode(link.href)

    return url, image_url, blog_url

def parse_id(people_entry):
    return force_unicode(people_entry.id.text.split('/')[4])

def force_unicode(string):
    if string is not None:
        return unicode(string, 'utf-8', errors='ignore')
    else:
        return string
