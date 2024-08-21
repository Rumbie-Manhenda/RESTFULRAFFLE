from django import template
import random

register = template.Library()

@register.simple_tag
def random_image():
    images = ['raffle.jpg', 'raffle1.jpg', 'raffle2.jpg', 'raffle3.jpg', 'raffle4.jpg', 'raffle5.jpg', 'raffle6.jpg', 'raffle7.jpg']
    return random.choice(images)
