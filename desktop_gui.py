from tkinter import *
from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
from tkinter import ttk
import time

HSV_Ranges = {'red': [[[0, 120, 70], [10, 255, 255]], [[161, 155, 84], [179, 255, 255]]],
              'blue': [[94, 80, 2], [126, 255, 255]],
              'green': [[25, 52, 72], [102, 255, 255]]}


def stopcam():
    """
    Funtion to stop the camera and destroy the opencv and tkinter windows
    """
    cap.release()
    cv.destroyAllWindows()
    root.destroy()


def startcam():
    """
    Funtion that is called when start camera button is pressed
    """

    # Getting the selected option of color from Combobox
    cloak_color = color.get()

    # Creating a frame for webcam video input to be shown as a tkinter window
    f1 = LabelFrame(root, bg="black")
    f1.pack(pady=5)
    L1 = Label(f1, bg="black")
    L1.pack()

    # Changing the configuration of the start button to perform stop camera function
    startbtn.configure(text="Stop Camera", command=stopcam)

    # To give camera time to capture the background initially.
    time.sleep(1)
    """
        This variable will store background image that will be
        displayed when cloak is used.
    """
    background = 0

    for i in range(30):
        """
            We are reading the input here using video capture object.
            We are giving 30 iterations to capture the background
            initially.
            cap.read() returns - image that is capture 
                and return value(True, If OK otherwise False).
        """
        ret, background = cap.read()

    while(cap.isOpened()):
        """
            This while loop will execute till capture object
            is open OR it is running.
            In other words it means - when webcam is capturing me,
                do following...
        """
        # Capturing image again (to perform operation on it)
        ret, img = cap.read()

        if not ret:
            """
                Terminating condition - 
                When webcam is closed, ret = False
            """
            break

        """
            Color space of image when it is captured.
            Webcame by default captures in BGR colour space.
            Some other color spaces are - RGB, Gray, YCrCb, etc.
            RGB - Linear combination of Red, Blue and Green.
            YCrCb - Y (luminescence), Cr and Cb are certain ranges.

            HSV/HSB- Hue Saturation Value/Brightness.
        """

        # Converting image from BGR -> HSV nad storing it.
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        """
            In HSV, there is a disk and color is distributed according to angle,
            i.e. from 0 - 360. But, in OpenCV, color is stored in 8 bits, 
            i.e. we can store value till 0 to 2^8 - 1 = 255 only.
            So, The size of disk is reduces to  180 degrees and Hue value is 
            increased to twice.
            Normal Hue Range (in degree):
            Red: 0 - 60
            Yellow: 61 - 120
            Green: 121 - 180
            Cyan: 181 - 240
            Blue: 241 - 300
            Magenta: 301 - 360

            Here, if we are using RED cloth, we can use range 0 - 30, 
            but we will use 0 - 10(as after 10 the color will be very light) and 170 - 180
            for RED color.
            
            [0, 120, 70] are H S V values where, H=0, S=120, V=70.
            Saturation - It tells about darkness.

            In lower limit of red, i.e. lower_red, We are using H=120 and B=70,
            as below that the saturation and brightness will be very code will also
            operate on pinkish colors while we want it to operate on RED only.
        """
        mask1 = 0
        """
            Input is hsv - video frame captured by camera.
            We will check whether there is any region having HSB values
            b/w lower_red and upper_red in captured hsv video frame.
            
            inRange() - This is separating the cloak part(here).
        """

        # If color is red then it will have 2 ranges from 0-10 and 170 -180
        if cloak_color.upper() == 'RED':
            # Lower limit of H, S and B
            first_lower_red = np.array(HSV_Ranges[cloak_color.lower()][0][0])
            # Upper Limit of H, S and B
            first_upper_red = np.array(HSV_Ranges[cloak_color.lower()][0][1])
            mask1 = cv.inRange(hsv, first_lower_red, first_upper_red)

            # Repeating with 170-180 degree
            second_lower_red = np.array(HSV_Ranges[cloak_color.lower()][1][0])
            second_upper_red = np.array(HSV_Ranges[cloak_color.lower()][1][1])
            mask2 = cv.inRange(hsv, second_lower_red, second_upper_red)

            # Overloading + operator for Bitwise OR.
            mask1 = mask1 + mask2
        else:
            lower_range = np.array(HSV_Ranges[cloak_color.lower()][0])
            upper_range = np.array(HSV_Ranges[cloak_color.lower()][1])
            mask1 = cv.inRange(hsv, lower_range, upper_range)

        """
            Used for morphological transformations.
            MORPH_OPEN: Removes noise from image.
            @param: input image, cv.MORPH_OPEN, kernel
            kernel: It is a filter
            np.ones(3, 3): Creates a matrix of 3 X 3 with all ones and 
                multiplies it with pixel matrix of image over 2 iterations(as specified).

            MORPH_DILATE: Improves smoothness of image.

            Note: These operations are normally done on Black and White image, but here
                we are doing them on HSV coloured space.
        """

        mask1 = cv.morphologyEx(mask1, cv.MORPH_OPEN,
                                np.ones((3, 3), np.uint8), iterations=2)

        mask1 = cv.morphologyEx(mask1, cv.MORPH_DILATE,
                                np.ones((3, 3), np.uint8), iterations=1)

        """
            Opposite of mask1 i.e. everything except the cloak, rest of the background.
            (mask1 was cloak).
        """
        mask2 = cv.bitwise_not(mask1)

        """
            res1: Bitwise and b/w background and mask1.
            This is used for segmentation of the colour i.e. we are differentiating cloak color
            form rest of the background.

            res2: Bitwise and b/w img and mask2.
            This is used to substitute the cloak part.

            background: Image which is to be displayed when cloak is in frame.
            img: Image captured by camera.
        """
        res1 = cv.bitwise_and(background, background, mask=mask1)
        res2 = cv.bitwise_and(img, img, mask=mask2)

        """
            We are linearly adding two images using addWeighted() function.
            Following equation is generated:
            alpha * source image 1 + beta * source image 2 + gamma = 0

            Here, alpha = beta = 1 and gamma = 0.
        """
        final_output = cv.addWeighted(res1, 1, res2, 1, 0)

        # Converts the final output in RGB format
        img1 = cv.cvtColor(final_output, cv.COLOR_BGR2RGB)

        # Takes the RGB array and converts it into an PIL image object that will be showed in the tkinter window
        img = ImageTk.PhotoImage(Image.fromarray(img1))
        L1['image'] = img
        root.update()


if __name__ == '__main__':
    """
        Creating a video capture object
        Constructors - 
        Video address: To run code on any video.
        Webcam number: To run code based on webcam video.
            (Here 0, as we have only one webcam).

        This object just specifies the video OR which webcam
        will be used to record video(this doesn't start camera).
    """
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    # Initializing tkinker window with given geometry
    root = Tk()
    root.geometry("700x660")
    root.title('Invisibilty Cloak Application')

    # label text for title of the Application
    Label(root, text="Invisible Cloak", font=(
        "Times New Roman", 30, "bold"), fg="black").pack()

    # label text for the dropdown box
    Label(root, text="Select the desired color to hide :",
          font=("Times New Roman", 15)).pack(pady=5)

    """
    Combobox is a combination of Listbox and an entry field. It is one of the Tkinter widgets where it contains a down arrow 
    to select from a list of options. It helps the users to select according to the list of options displayed.
    """
    n = StringVar()
    color = ttk.Combobox(root, font=("Times New Roman", 10),
                         width=27, textvariable=n)

    # Adding combobox drop down list values
    color['values'] = ('Red', 'Blue', 'Green')

    # Setting the state to readonly so that no custom data can be entered in the field
    color['state'] = 'readonly'
    color.pack()

    # Initilizing the combobox with default value at index 0
    color.current(0)

    # Creating the start camera button which will trigger the startcam funtion on clicking
    startbtn = Button(root, text="Start Camera", font=(
        "Times New Roman", 12, "bold"), bg="gray", fg="black", command=startcam)
    startbtn.pack(pady=5)
    root.protocol("WM_DELETE_WINDOW", stopcam)
    root.mainloop()
