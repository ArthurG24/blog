from sys import argv
from math import ceil, floor

list = [1,2,3,4,5,6,7,8,9,10]  # pages

length = len(list)  # nb_pages

page = int(argv[1])  # page_selected



# This define the range
displayed = 5

start = ceil(displayed/2)
end = floor(displayed/2)

if page > start:
    print("???")

if page < start:
    print(list[:displayed])
elif page > length-end:
    print(list[length-displayed:])
else:
    print(list[page-start:page+end])

if page < length - end:
    print("...")