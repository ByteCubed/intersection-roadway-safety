# Baseline Code courtesy of https://stackoverflow.com/questions/41656176/tkinter-canvas-zoom-move-pan
# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.
import os
import random
import tkinter as tk
from os.path import exists
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random

classifier_name_key = 'name'
classifier_value_mapping = 'value_mapping'

MODE_ANNOTATE = 0
MODE_CLASSIFY = 1

class AutoScrollbar(ttk.Scrollbar):
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class Zoom_Advanced(ttk.Frame):
    x, y = 0,0
    box_in_focus = None
    box_in_progress = None
    box_in_progress_outline_color = '#000000' # black
    saved_nonfinal_box_outline_color = '#ff7518' # pumpkin
    box_in_focus_outline_color = '#0000FF' # blue
    finalized_box_outline_color = '#000fff000' # green
    center_dot_color = None
    center_dot_id = None
    saved_boxes = {}
    finalized_box_json = []
    saved_text = None
    saved_text_label = None
    label_padding = {'padx': 5, 'pady': 5}
    defaultFont = None

    im_path = "base_images/"
    json_path = "json/"
    images = []
    image_idx = 0
    valid_image_extensions = ['.png','.jpg']

    classification_criteria = []
    criteria_index = 0
    classification_output = {}
    classifier_descriptor_text = None
    classifier_descriptor_label = None
    classification_json = ''

    MODE = MODE_CLASSIFY

    ''' Advanced zoom of the image '''
    def __init__(self, mainframe, json, shuffle=False, paint_center=None, mode=None):
        # Set Mode
        if mode is not None:
            self.MODE = mode

        # Set Classifier JSON
        self.classification_json = json
        self.classification_criteria = load_json(self.classification_json)["criteria"]
        print(self.classification_criteria)

        # load Output JSON if it exists
        json_out_path = self.json_path + os.path.basename(self.classification_json)
        if exists(json_out_path):
            self.classification_output = load_json(json_out_path)[1]

        # Load list of images
        self.images = [os.path.splitext(f)[0] + os.path.splitext(f)[1] for f in os.listdir(self.im_path)
                       if os.path.isfile(os.path.join(os.getcwd(), self.im_path, f)) and os.path.splitext(f)[1] in self.valid_image_extensions]
        if shuffle:
            random.shuffle(self.images)

        self.center_dot_color = paint_center
        self.defaultFont = font.nametofont("TkDefaultFont")
        mainframe.protocol("WM_DELETE_WINDOW", self.on_closing)
        ''' Initialize the main Frame '''
        ttk.Frame.__init__(self, master=mainframe)
        self.master.title('Zoom with mouse wheel')

        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')

        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        self.classifier_descriptor_text = tk.StringVar(value="") # add text label variable
        self.classifier_descriptor_label = Label(self.canvas, textvariable=self.classifier_descriptor_text) # and text label
        self.classifier_descriptor_label.pack()
        self.saved_text = tk.StringVar(value="") # add text label variable
        self.saved_text_label = Label(self.canvas, textvariable=self.saved_text) # and text label
        self.saved_text_label.pack()
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.focus_set() # give the canvas focus to pick up key events
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.draw_from) # Mac left-click to draw box
        self.canvas.bind('<ButtonPress-2>', self.move_from) # Mac right-click to drag around
        self.canvas.bind('<B1-Motion>',     self.draw_to)
        self.canvas.bind('<B2-Motion>',     self.move_to)
        self.canvas.bind('<ButtonRelease-1>', self.draw_box) # Releasing the mouse makes the box stick
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        self.canvas.bind('<Return>',   self.return_pressed)  # when the return (enter) key is pressed
        self.canvas.bind('<BackSpace>',   self.backspace)  # when the backspace key is pressed
        self.canvas.bind('<Left>',   self.left_key)  # catchall for keys entering
        self.canvas.bind('<Right>',   self.right_key)  # catchall for keys entering
        self.canvas.bind('<Key>',   self.key_entered)  # catchall for keys entering
        self.image = Image.open(self.im_path + self.images[self.image_idx])  # open image
        self.width, self.height = self.image.size
        self.imscale = 3  # scale for the canvas image
        self.delta = 1.0  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width * self.imscale, self.height * self.imscale, width=0)

        if self.center_dot_color is not None:
            self.draw_center(self.width * self.imscale / 2, self.height * self.imscale / 2, 2)
        self.show_image()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.MODE == MODE_ANNOTATE and len(self.finalized_box_json) > 0:
                save_json(self.json_path + self.images[self.image_idx] + ".json", self.finalized_box_json)
            if self.MODE == MODE_CLASSIFY and len(self.classification_output) > 0:
                save_json(self.json_path + os.path.basename(self.classification_json), [self.classification_criteria, self.classification_output])
            self.master.destroy()

    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        flag = False
        mytuple = args
        for x in args:
            if flag:
                mytuple = ('moveto', str(min(float(args[1]), 0.31965)))
            if x == "moveto":
                flag = True
        self.canvas.yview(*mytuple, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        print(args)
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def draw_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.x, self.y = event.x, event.y

    def draw_to(self, event):
        ''' Drag textbox to new position '''
        if self.box_in_progress is not None:
            self.canvas.delete(self.box_in_progress)
        self.box_in_progress = self.canvas.create_rectangle((self.x, self.y), (event.x, event.y),
                                    dash=[3, 2], tags='no', outline=self.box_in_progress_outline_color)
        self.show_image()  # redraw the image

    def draw_box(self, event):
        ''' Finalize drawn box, add it to list of targets '''
        rect_id = self.canvas.create_rectangle((self.x, self.y), (event.x, event.y),
                                     dash=[3, 2], outline=self.saved_nonfinal_box_outline_color)
        self.saved_boxes[rect_id] = [self.x, self.y, event.x, event.y]
        print(self.saved_boxes)
        self.show_image()

    def draw_center(self, height, width, radius):
        if self.center_dot_id is not None:
            self.canvas.delete(self.center_dot_id)
        self.center_dot_id =  self.canvas.create_rectangle((width - radius, height - radius), (width + radius, height + radius), fill=self.center_dot_color)

    def return_pressed(self, event):
        ''' Handle the 'enter' key, which commits text '''
        if self.MODE == MODE_ANNOTATE:
            if len(self.saved_boxes) > 0:
                key, box = self.saved_boxes.popitem()
                if self.saved_text.get() == "":
                    # remove the box from the saved list and the canvas in one fell swoop
                    self.canvas.delete(key)
                else:
                    self.finalized_box_json.append({'label': self.saved_text.get(), 'x': box[0], 'y': box[1],
                                                    'width': box[2] - box[0], 'height': box[3] - box[1]})
                    self.canvas.create_rectangle((box[0], box[1]), (box[2], box[3]),
                                                 dash=[3, 2], outline=self.finalized_box_outline_color)
                    self.canvas.delete(key)
                    self.canvas.create_text((box[2]+box[0])/2, (box[3]+box[1])/2,
                                            fill=self.finalized_box_outline_color, text=self.saved_text.get())
                    self.update()
                    print(self.finalized_box_json)
            if self.box_in_progress is not None:
                self.canvas.delete(self.box_in_progress)
        elif self.MODE == MODE_CLASSIFY:
            classification = {}
            # write data to classification output
            # if we've already got a record for this file, pull it
            if self.images[self.image_idx] in self.classification_output.keys():
                # load whatever we've already got
                classification = self.classification_output[self.images[self.image_idx]]
            key = self.classification_criteria[self.criteria_index][classifier_name_key]
            # overwrite our key/value with the key + whatever our current value is
            classification[key] = self.saved_text.get()
            # then load it back into our output, overwriting
            self.classification_output[self.images[self.image_idx]] = classification

            # Advance to the next classification criteria, or if that was the last one, to the next page
            if self.criteria_index < len(self.classification_criteria) - 1:
                self.criteria_index = self.criteria_index + 1
            else:
                self.criteria_index = 0
                if self.image_idx >= len(self.images) - 1:
                    # if we're on the last image, close
                    self.on_closing()
                    return
                else:
                    # otherwise advance to the next image
                    self.right_key(None)
        self.saved_text.set("")  # clear saved text
        self.show_image()

    def left_key(self, event):
        if self.image_idx > 0:
            self.image_idx = self.image_idx - 1
            self.image = Image.open(self.im_path + self.images[self.image_idx])  # open image
            self.show_image()

    def right_key(self, event):
        if self.image_idx < len(self.images) - 1:
            self.image_idx = self.image_idx + 1
            self.image = Image.open(self.im_path + self.images[self.image_idx])  # open image
            self.show_image()

    def key_entered(self, event):
        ''' Handle key logging - add it to the label '''
        self.saved_text.set(self.saved_text.get() + event.char)
        if self.saved_text_label is None:
            self.saved_text_label = Label(self, textvariable=self.saved_text)

    def backspace(self, event):
        ''' Handle key logging - add it to the label '''
        if len(self.saved_text.get()) > 0:
            self.saved_text.set(self.saved_text.get()[:-1])
        else:
            if self.MODE == MODE_CLASSIFY:
                if self.criteria_index > 0:
                    # if there's a prior criteria, back up to it
                    self.criteria_index = self.criteria_index - 1
                    self.show_image()
                else:
                    # Otherwise try to go back a page
                    self.left_key(None)

    def printout(self, event):
        ''' Print Event for debugging '''
        print(event)

    def draw_classification_labels(self):
        if self.MODE == MODE_CLASSIFY:
            # Set the description
            current_classifier = self.classification_criteria[self.criteria_index]
            if classifier_name_key in current_classifier.keys():
                classifier_description = current_classifier[classifier_name_key]
            if classifier_value_mapping in current_classifier.keys():
                for value in current_classifier[classifier_value_mapping].keys():
                    classifier_description = classifier_description + '\n' + value + ': ' + \
                                             current_classifier[classifier_value_mapping][value]
            self.classifier_descriptor_text.set(classifier_description)

            # If the user has already entered text, display it
            if self.images[self.image_idx] in self.classification_output.keys():
                print(f"We have image {self.images[self.image_idx]} in the output")
                key = self.classification_criteria[self.criteria_index][classifier_name_key]
                if key in self.classification_output[self.images[self.image_idx]].keys():
                    print(f"We have key {classifier_name_key}  in the output.")
                    print(f"And the prior saved text is {self.classification_output[self.images[self.image_idx]][key]}")
                    self.saved_text.set(self.classification_output[self.images[self.image_idx]][key])
                else:
                    # Clear it if we haven't yet encountered this key
                    self.saved_text.set('')
            else:
                # Clear it if we haven't yet encountered this image
                self.saved_text.set('')

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if self.MODE == MODE_CLASSIFY:
            self.draw_classification_labels()
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection


def save_json(filename, data, indent=4):
    with open(filename, 'w+') as f:
        f.write(json.dumps(data, indent=indent))


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    return data


#img_name = 'g-639-1'  # place image name (in base_images) here
criteria_json = os.getcwd() + '\\classification_criteria\\intersection_classification_criteria2.json'
#criteria_json = os.getcwd() + '\\classification_criteria\\intersection_feature_classification_criteria.json'
root = tk.Tk()
root.geometry("1200x800") # set initial window size
app = Zoom_Advanced(root, criteria_json, shuffle=True, paint_center='#FF0000')
root.mainloop()
